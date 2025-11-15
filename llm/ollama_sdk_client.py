"""
Siberia Ollama SDK Client - 完全基于Ollama SDK的客户端实现
Siberia Ollama SDK Client - Complete Ollama SDK-based Implementation
"""

import re
import tempfile
import os
import base64
import io
from typing import Dict, List, Tuple, Optional, Union
import torch
import numpy as np
from ollama import Client, ResponseError, RequestError

try:
    from PIL import Image
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False
    print("Warning: PIL not available, image processing will be limited")


class SiberiaOllamaSDKClient:
    """
    Siberia Ollama SDK Client - 完全基于Ollama官方SDK的客户端
    Siberia Ollama SDK Client - Client based entirely on official Ollama SDK
    """

    def __init__(self, server_url: str = "http://127.0.0.1:11434", model: str = "llama2", timeout: int = 30):
        """
        初始化客户端 / Initialize client

        Args:
            server_url: Ollama服务器URL
            model: 默认模型名称
            timeout: 请求超时时间(秒)
        """
        self.server_url = self._normalize_server_url(server_url)
        self.model = model
        self.timeout = max(5, min(300, int(timeout)))  # 限制在5-300秒之间

        # 连接状态
        self._connected = False
        self._available_models = []

        # 创建Ollama SDK客户端实例，延迟初始化
        self._client = None

    def _normalize_server_url(self, url: str) -> str:
        """标准化服务器URL / Normalize server URL"""
        if not url or not isinstance(url, str):
            return "http://127.0.0.1:11434"

        # 移除尾部斜杠
        url = url.rstrip('/')

        # 如果没有协议前缀，添加http://
        if not url.startswith(('http://', 'https://')):
            url = f'http://{url}'

        # 基本URL格式验证
        pattern = r'^https?://[a-zA-Z0-9.-]+(?::\d{1,5})?$'
        if not re.match(pattern, url):
            print(f"Warning: Invalid URL format '{url}', using default")
            return "http://127.0.0.1:11434"

        return url

    def _get_client(self) -> Client:
        """获取Ollama SDK客户端实例 / Get Ollama SDK client instance"""
        if self._client is None:
            # Ollama SDK 需要主机部分，不包含协议
            host = self._extract_host_from_url(self.server_url)
            self._client = Client(host=host, timeout=self.timeout)
        return self._client

    def _extract_host_from_url(self, url: str) -> str:
        """从URL提取主机部分 / Extract host part from URL"""
        if url.startswith('http://'):
            return url[7:]
        elif url.startswith('https://'):
            return url[8:]
        else:
            return url

    def test_connection(self) -> bool:
        """
        测试连接并获取可用模型列表 / Test connection and get available models

        Returns:
            bool: 连接是否成功
        """
        try:
            print(f"Testing connection to: {self.server_url}")

            client = self._get_client()

            # 使用Ollama SDK的list方法获取模型
            models_response = client.list()

            # 处理不同的响应格式
            models = []
            if isinstance(models_response, dict):
                models = models_response.get('models', [])
            elif hasattr(models_response, 'models'):
                models = models_response.models

            # 提取模型名称
            self._available_models = []
            for model in models:
                if isinstance(model, dict):
                    name = model.get('name', '') or model.get('model', '')
                elif hasattr(model, 'name'):
                    name = model.name
                elif hasattr(model, 'model'):
                    name = model.model
                else:
                    continue

                if name:  # 确保名称不为空
                    self._available_models.append(name)

            self._connected = True
            print(f"Connection successful. Found {len(self._available_models)} models")

            if self._available_models:
                print(f"Available models: {', '.join(self._available_models[:5])}" +
                      (f" and {len(self._available_models) - 5} more..." if len(self._available_models) > 5 else ""))

            return True

        except (ResponseError, RequestError) as e:
            error_msg = f"Ollama API error: {e}"
            print(error_msg)
        except Exception as e:
            error_msg = f"Connection error: {type(e).__name__}: {e}"
            print(error_msg)

        self._connected = False
        self._available_models = []
        return False

    def generate_text(self, prompt: str, system_prompt: str = "You are a helpful assistant.",
                     temperature: float = 0.7, max_tokens: int = 500) -> Tuple[str, str]:
        """
        生成文本 / Generate text

        Args:
            prompt: 用户提示词
            system_prompt: 系统提示词
            temperature: 生成温度 (0.0-2.0)
            max_tokens: 最大生成token数

        Returns:
            Tuple[str, str]: (生成的文本, 状态信息)
        """
        try:
            # 验证输入
            if not prompt or not prompt.strip():
                return "", "Error: Empty prompt"

            # 限制参数范围
            temperature = max(0.0, min(2.0, float(temperature)))
            max_tokens = max(1, min(8192, int(max_tokens)))

            # 检查连接
            if not self._connected:
                if not self.test_connection():
                    return "", "Error: Failed to connect to Ollama server"

            if not self._available_models:
                return "", "Error: No models available on server"

            client = self._get_client()
            print(f"Generating text with model: {self.model}")

            # 使用Ollama SDK生成文本
            response = client.generate(
                model=self.model,
                prompt=prompt.strip(),
                system=system_prompt.strip(),
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )

            # 处理响应
            generated_text = ""
            if isinstance(response, dict):
                generated_text = response.get('response', '')
            elif hasattr(response, 'response'):
                generated_text = response.response

            if generated_text:
                status_msg = f"Successfully generated {len(generated_text)} characters"
                return generated_text, status_msg
            else:
                return "", "Error: Empty response from model"

        except (ResponseError, RequestError) as e:
            error_msg = f"Ollama API error: {e}"
            return "", error_msg
        except Exception as e:
            error_msg = f"Generation error: {type(e).__name__}: {e}"
            return "", error_msg

    def chat(self, messages: List[Dict], temperature: float = 0.7, max_tokens: int = 4096) -> Tuple[str, str, List[Dict]]:
        """
        聊天对话 / Chat conversation

        Args:
            messages: 消息历史列表
            temperature: 生成温度 (0.0-2.0)
            max_tokens: 最大生成token数

        Returns:
            Tuple[str, str, List[Dict]]: (回复文本, 状态信息, 更新后的消息列表)
        """
        try:
            # 验证输入
            if not messages or not isinstance(messages, list):
                return "", "Error: Invalid or empty messages", []

            # 验证消息格式
            valid_roles = {'system', 'user', 'assistant'}
            for msg in messages:
                if not isinstance(msg, dict) or 'role' not in msg or 'content' not in msg:
                    return "", "Error: Invalid message format", messages
                if msg['role'] not in valid_roles:
                    return "", f"Error: Invalid role '{msg['role']}'", messages

            # 限制参数范围
            temperature = max(0.0, min(2.0, float(temperature)))
            max_tokens = max(1, min(8192, int(max_tokens)))

            # 检查连接
            if not self._connected:
                if not self.test_connection():
                    return "", "Error: Failed to connect to Ollama server", messages

            if not self._available_models:
                return "", "Error: No models available on server", messages

            client = self._get_client()
            print(f"Chat request with {len(messages)} messages using model: {self.model}")

            # 使用Ollama SDK进行聊天
            response = client.chat(
                model=self.model,
                messages=messages,
                options={
                    "temperature": temperature,
                    "num_predict": max_tokens
                }
            )

            # 处理响应
            response_text = ""
            if isinstance(response, dict):
                message = response.get('message', {})
                if isinstance(message, dict):
                    response_text = message.get('content', '')
            elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                response_text = response.message.content

            if response_text:
                # 更新消息历史
                updated_messages = messages + [{"role": "assistant", "content": response_text}]
                status_msg = f"Chat successful: {len(response_text)} characters generated"
                return response_text, status_msg, updated_messages
            else:
                return "", "Error: Empty response from model", messages

        except (ResponseError, RequestError) as e:
            error_msg = f"Ollama API error: {e}"
            return "", error_msg, messages
        except Exception as e:
            error_msg = f"Chat error: {type(e).__name__}: {e}"
            return "", error_msg, messages

    def analyze_image(self, prompt: str, image_data, system_prompt: str = "You are a helpful assistant.",
                     temperature: float = 0.7, max_tokens: int = 500) -> Tuple[str, str]:
        """
        分析图片 / Analyze image

        Args:
            prompt: 图片分析提示词
            image_data: 图片数据 (torch.Tensor或文件路径)
            system_prompt: 系统提示词
            temperature: 生成温度 (0.0-2.0)
            max_tokens: 最大生成token数

        Returns:
            Tuple[str, str]: (分析结果, 状态信息)
        """
        try:
            # 验证输入
            if not prompt or not prompt.strip():
                return "", "Error: Empty prompt"

            if image_data is None:
                return "", "Error: No image data provided"

            # 限制参数范围
            temperature = max(0.0, min(2.0, float(temperature)))
            max_tokens = max(1, min(8192, int(max_tokens)))

            # 检查连接
            if not self._connected:
                if not self.test_connection():
                    return "", "Error: Failed to connect to Ollama server"

            if not self._available_models:
                return "", "Error: No models available on server"

            # 准备图片路径
            image_path = self._prepare_image_for_sdk(image_data)
            if not image_path:
                return "", "Error: Failed to prepare image for analysis"

            try:
                client = self._get_client()
                print(f"Analyzing image with model: {self.model}")

                # 准备消息
                messages = [
                    {
                        'role': 'system',
                        'content': system_prompt.strip()
                    },
                    {
                        'role': 'user',
                        'content': prompt.strip(),
                        'images': [image_path]
                    }
                ]

                # 使用Ollama SDK分析图片
                response = client.chat(
                    model=self.model,
                    messages=messages,
                    options={
                        'temperature': temperature,
                        'num_predict': max_tokens
                    }
                )

                # 处理响应
                response_text = ""
                if isinstance(response, dict):
                    message = response.get('message', {})
                    if isinstance(message, dict):
                        response_text = message.get('content', '')
                elif hasattr(response, 'message') and hasattr(response.message, 'content'):
                    response_text = response.message.content

                if response_text:
                    status_msg = f"Successfully analyzed image"
                    return response_text, status_msg
                else:
                    return "", "Error: Empty response from vision model"

            finally:
                # 清理临时文件
                self._cleanup_temp_file(image_path)

        except (ResponseError, RequestError) as e:
            error_msg = f"Ollama API error: {e}"
            return "", f"Image analysis failed: {error_msg}"
        except Exception as e:
            error_msg = f"Image analysis error: {type(e).__name__}: {e}"
            return "", error_msg

    def _prepare_image_for_sdk(self, image_data) -> Optional[str]:
        """
        为Ollama SDK准备图片 / Prepare image for Ollama SDK

        Args:
            image_data: 图片数据 (torch.Tensor或文件路径或base64字符串)

        Returns:
            Optional[str]: 图片文件路径，失败时返回None
        """
        if not PIL_AVAILABLE:
            print("Error: PIL not available for image processing")
            return None

        try:
            # 处理torch.Tensor
            if isinstance(image_data, torch.Tensor):
                return self._tensor_to_temp_file(image_data)

            # 处理文件路径
            elif isinstance(image_data, str):
                if os.path.exists(image_data):
                    return image_data
                else:
                    # 尝试解码base64
                    try:
                        img_bytes = base64.b64decode(image_data)
                        img_pil = Image.open(io.BytesIO(img_bytes))
                        return self._pil_to_temp_file(img_pil)
                    except Exception as e:
                        print(f"Failed to decode base64 image: {e}")
                        return None

            else:
                print(f"Error: Unsupported image data type: {type(image_data)}")
                return None

        except Exception as e:
            print(f"Error preparing image: {e}")
            return None

    def _tensor_to_temp_file(self, tensor: torch.Tensor) -> Optional[str]:
        """将torch.Tensor转换为临时文件 / Convert torch.Tensor to temporary file"""
        try:
            # 处理批次维度
            if len(tensor.shape) == 4:
                tensor = tensor[0]  # 移除批次维度

            # 转换数据类型
            if tensor.dtype in [torch.float32, torch.float64]:
                tensor = (tensor * 255).clamp(0, 255).to(torch.uint8)

            # 转换为numpy数组
            img_np = tensor.cpu().numpy()

            # 处理不同的通道格式
            if len(img_np.shape) == 2:  # 灰度图
                img_np = np.stack([img_np] * 3, axis=-1)
            elif len(img_np.shape) == 3:
                if img_np.shape[2] == 1:  # 单通道
                    img_np = np.concatenate([img_np] * 3, axis=2)
                elif img_np.shape[2] > 3:  # 超过3通道
                    img_np = img_np[:, :, :3]

            # 创建PIL图像
            img_pil = Image.fromarray(img_np.astype(np.uint8), mode='RGB')
            return self._pil_to_temp_file(img_pil)

        except Exception as e:
            print(f"Error converting tensor to image: {e}")
            return None

    def _pil_to_temp_file(self, img_pil) -> Optional[str]:
        """将PIL图像保存为临时文件 / Save PIL image as temporary file"""
        try:
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.png')
            temp_file.close()
            img_pil.save(temp_file.name, 'PNG')
            return temp_file.name
        except Exception as e:
            print(f"Error saving PIL image to temp file: {e}")
            return None

    def _cleanup_temp_file(self, file_path: str):
        """清理临时文件 / Cleanup temporary file"""
        if file_path and os.path.exists(file_path):
            try:
                os.unlink(file_path)
            except OSError as e:
                print(f"Warning: Failed to delete temp file {file_path}: {e}")

    @property
    def connected(self) -> bool:
        """连接状态 / Connection status"""
        return self._connected

    @property
    def available_models(self) -> List[str]:
        """可用模型列表 / Available models list"""
        return self._available_models.copy()

    def to_connection_info(self) -> Dict:
        """
        转换为连接信息字典 / Convert to connection info dict
        """
        return {
            "server_url": self.server_url,
            "model": self.model,
            "timeout": self.timeout,
            "available_models": self.available_models,
            "connected": self.connected
        }

    @classmethod
    def from_connection_info(cls, connection_info: Dict) -> 'SiberiaOllamaSDKClient':
        """
        从连接信息创建客户端 / Create client from connection info
        """
        if not connection_info:
            return cls()

        client = cls(
            server_url=connection_info.get("server_url", "http://127.0.0.1:11434"),
            model=connection_info.get("model", "llama2"),
            timeout=connection_info.get("timeout", 30)
        )

        # 恢复连接状态
        client._connected = connection_info.get("connected", False)
        client._available_models = connection_info.get("available_models", [])

        return client