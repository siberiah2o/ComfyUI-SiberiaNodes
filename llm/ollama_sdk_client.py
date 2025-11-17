"""
ComfyUI-SiberiaNodes - Complete Ollama SDK-based client implementation

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
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

    # 支持视觉的已知模型关键词和完整模型名
    VISION_MODEL_KEYWORDS = [
        'vision', 'vl', 'multimodal', 'llava', 'bakllava', 'moondream',
        'qwen2-vl', 'qwen-vl', 'llama3.2-vision', 'minicpm-v',
        'cogvlm', 'internvl', 'xverse-v'
    ]

    VISION_MODELS_EXACT = [
        'llava:latest', 'llava:13b', 'llava:34b', 'llava:7b',
        'bakllava:latest', 'moondream:latest', 'qwen2-vl:latest',
        'qwen2-vl:7b', 'qwen2-vl:2b', 'llama3.2-vision:latest',
        'llama3.2-vision:11b', 'llama3.2-vision:90b'
    ]

    def __init__(self, server_url: str = "http://127.0.0.1:11434", model: str = "llama2", timeout: int = 30,
                 use_base64: bool = True):
        """
        初始化客户端 / Initialize client

        Args:
            server_url: Ollama服务器URL
            model: 默认模型名称
            timeout: 请求超时时间(秒)
            use_base64: 是否使用base64格式传输图片
        """
        self.server_url = self._normalize_server_url(server_url)
        self.model = model
        self.timeout = max(5, min(300, int(timeout)))  # 限制在5-300秒之间
        self.use_base64 = use_base64

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

    def is_vision_model(self, model_name: str = None) -> bool:
        """
        检查模型是否支持视觉功能 / Check if model supports vision capabilities

        Args:
            model_name: 模型名称，如果为None则使用当前模型

        Returns:
            bool: 是否支持视觉功能
        """
        if model_name is None:
            model_name = self.model

        if not model_name:
            return False

        model_name_lower = model_name.lower()

        # 检查精确匹配
        if model_name_lower in [m.lower() for m in self.VISION_MODELS_EXACT]:
            return True

        # 检查关键词匹配
        return any(keyword in model_name_lower for keyword in self.VISION_MODEL_KEYWORDS)

    @classmethod
    def is_vision_model_static(cls, model_name: str) -> bool:
        """
        静态方法检查模型是否支持视觉功能 / Static method to check if model supports vision

        Args:
            model_name: 模型名称

        Returns:
            bool: 是否支持视觉功能
        """
        if not model_name:
            return False

        model_name_lower = model_name.lower()

        # 检查精确匹配
        if model_name_lower in [m.lower() for m in cls.VISION_MODELS_EXACT]:
            return True

        # 检查关键词匹配
        return any(keyword in model_name_lower for keyword in cls.VISION_MODEL_KEYWORDS)

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

            # 验证模型是否支持视觉功能
            if not self.is_vision_model():
                return "", f"Error: Model '{self.model}' does not support vision. Please use a vision model."

            # 限制参数范围
            temperature = max(0.0, min(2.0, float(temperature)))
            max_tokens = max(1, min(8192, int(max_tokens)))

            # 检查连接
            if not self._connected:
                if not self.test_connection():
                    return "", "Error: Failed to connect to Ollama server"

            if not self._available_models:
                return "", "Error: No models available on server"

            # 准备图片数据
            image_data_processed = self._prepare_image_for_sdk(image_data)
            if not image_data_processed:
                return "", "Error: Failed to prepare image for analysis"

            try:
                client = self._get_client()
                print(f"Analyzing image with model: {self.model} (format: {'base64' if self.use_base64 else 'file path'})")

                # 准备消息
                if self.use_base64:
                    # 使用base64数据
                    messages = [
                        {
                            'role': 'system',
                            'content': system_prompt.strip()
                        },
                        {
                            'role': 'user',
                            'content': prompt.strip(),
                            'images': [image_data_processed]
                        }
                    ]
                else:
                    # 使用文件路径
                    messages = [
                        {
                            'role': 'system',
                            'content': system_prompt.strip()
                        },
                        {
                            'role': 'user',
                            'content': prompt.strip(),
                            'images': [image_data_processed]
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
                # 清理临时文件（仅在非base64模式下）
                if not self.use_base64:
                    self._cleanup_temp_file(image_data_processed)

        except (ResponseError, RequestError) as e:
            error_msg = f"Ollama API error: {e}"
            return "", f"Image analysis failed: {error_msg}"
        except Exception as e:
            error_msg = f"Image analysis error: {type(e).__name__}: {e}"
            return "", error_msg

    def analyze_multiple_images(self, prompt: str, images_data: List, system_prompt: str = "You are a helpful assistant.",
                                temperature: float = 0.7, max_tokens: int = 500) -> Tuple[str, str]:
        """
        分析多张图片 / Analyze multiple images in a single request

        Args:
            prompt: 图片分析提示词
            images_data: 图片数据列表 (List[torch.Tensor]或文件路径列表)
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

            if not images_data or len(images_data) == 0:
                return "", "Error: No images data provided"

            # 验证模型是否支持视觉功能
            if not self.is_vision_model():
                return "", f"Error: Model '{self.model}' does not support vision. Please use a vision model."

            # 限制参数范围 (多图片时使用更保守的参数)
            temperature = max(0.0, min(1.0, float(temperature)))
            max_tokens = max(1, min(8192, int(max_tokens)))

            # 限制图片数量以避免内存问题
            if len(images_data) > 10:
                return "", "Error: Too many images provided (maximum 10 allowed per request)"

            # 检查连接
            if not self._connected:
                if not self.test_connection():
                    return "", "Error: Failed to connect to Ollama server"

            if not self._available_models:
                return "", "Error: No models available on server"

            # 准备所有图片数据
            image_data_list = []
            temp_files = []

            for i, image_data in enumerate(images_data):
                if image_data is None:
                    continue

                image_data_processed = self._prepare_image_for_sdk(image_data)
                if image_data_processed:
                    image_data_list.append(image_data_processed)
                    # 如果不是base64模式且是临时文件，记录下来以便清理
                    if not self.use_base64 and isinstance(image_data_processed, str) and os.path.exists(image_data_processed):
                        temp_files.append(image_data_processed)

            if not image_data_list:
                return "", "Error: Failed to prepare any images for analysis"

            try:
                client = self._get_client()

                # 准备消息 - 包含多张图片
                messages = [
                    {
                        'role': 'system',
                        'content': system_prompt.strip()
                    },
                    {
                        'role': 'user',
                        'content': prompt.strip(),
                        'images': image_data_list
                    }
                ]

                # 使用Ollama SDK分析多张图片
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
                    status_msg = f"Successfully analyzed {len(image_data_list)} images"
                    return response_text, status_msg
                else:
                    return "", "Error: Empty response from vision model"

            finally:
                # 清理临时文件（仅在非base64模式下）
                if not self.use_base64:
                    for temp_file in temp_files:
                        self._cleanup_temp_file(temp_file)

        except (ResponseError, RequestError) as e:
            error_msg = f"Ollama API error: {e}"
            return "", f"Multi-image analysis failed: {error_msg}"
        except Exception as e:
            error_msg = f"Multi-image analysis error: {type(e).__name__}: {e}"
            return "", error_msg

    def _prepare_image_for_sdk(self, image_data) -> Optional[str]:
        """
        为Ollama SDK准备图片 / Prepare image for Ollama SDK

        Args:
            image_data: 图片数据 (torch.Tensor或文件路径或base64字符串)

        Returns:
            Optional[str]: base64字符串或文件路径，失败时返回None
        """
        if not PIL_AVAILABLE:
            error_msg = "Error: PIL not available for image processing"
            print(error_msg)
            return None

        try:
            # 处理torch.Tensor
            if isinstance(image_data, torch.Tensor):
                if self.use_base64:
                    return self._tensor_to_base64(image_data)
                else:
                    return self._tensor_to_temp_file(image_data)

            # 处理文件路径
            elif isinstance(image_data, str):
                if os.path.exists(image_data):
                    # 验证文件是否为有效图片
                    if self._is_valid_image_file(image_data):
                        if self.use_base64:
                            # 将文件路径转换为base64
                            with Image.open(image_data) as img_pil:
                                return self._pil_to_base64(img_pil)
                        else:
                            return image_data
                    else:
                        print(f"Error: File exists but is not a valid image: {image_data}")
                        return None
                else:
                    # 尝试解码base64
                    if self._is_base64_string(image_data):
                        if self.use_base64:
                            return image_data  # 直接返回base64字符串
                        else:
                            # 将base64转换为临时文件
                            try:
                                img_bytes = base64.b64decode(image_data)
                                img_pil = Image.open(io.BytesIO(img_bytes))
                                return self._pil_to_temp_file(img_pil)
                            except Exception as e:
                                print(f"Failed to decode base64 image: {e}")
                                return None
                    else:
                        print(f"Error: File does not exist and is not valid base64: {image_data}")
                        return None

            else:
                print(f"Error: Unsupported image data type: {type(image_data)}")
                return None

        except Exception as e:
            print(f"Error preparing image: {e}")
            return None

    def _is_valid_image_file(self, file_path: str) -> bool:
        """
        检查文件是否为有效图片 / Check if file is a valid image

        Args:
            file_path: 文件路径

        Returns:
            bool: 是否为有效图片
        """
        try:
            with Image.open(file_path) as img:
                # 尝试获取图片尺寸来验证文件完整性
                _ = img.size
                return True
        except Exception:
            return False

    def _is_base64_string(self, string: str) -> bool:
        """
        检查字符串是否为有效的base64编码 / Check if string is valid base64

        Args:
            string: 要检查的字符串

        Returns:
            bool: 是否为有效的base64字符串
        """
        try:
            # 简单的长度检查和字符验证
            if len(string) < 100:  # 通常base64图片都比较长
                return False
            base64.b64decode(string, validate=True)
            return True
        except Exception:
            return False

    def _tensor_to_base64(self, tensor: torch.Tensor) -> Optional[str]:
        """将torch.Tensor转换为base64字符串，完全保持原始信息 / Convert torch.Tensor to base64 string preserving all original info"""
        try:
            # 验证tensor
            if not isinstance(tensor, torch.Tensor):
                print(f"Error: Expected torch.Tensor, got {type(tensor)}")
                return None

            if tensor.numel() == 0:
                print("Error: Empty tensor provided")
                return None

            # 验证形状 - 应该是 [H, W, C] 格式的单张图像
            if len(tensor.shape) != 3:
                print(f"Error: Expected 3D tensor [H, W, C], got {len(tensor.shape)}D tensor with shape {tensor.shape}")
                return None

            h, w, c = tensor.shape
            if c not in [1, 3, 4]:
                print(f"Error: Invalid number of channels: {c}")
                return None

            if h < 1 or w < 1:
                print(f"Error: Invalid image dimensions: {h}x{w}")
                return None

            
            # 创建tensor的副本用于转换，避免修改原始数据
            tensor_copy = tensor.clone().detach()

            # 处理数据类型和值范围，仅做必要的转换
            if tensor_copy.dtype in [torch.float16, torch.float32, torch.float64]:
                # 浮点数数据需要确定范围
                if tensor_copy.max() <= 1.0:
                    # 假设是 [0, 1] 范围的浮点数，转换为 [0, 255]
                    tensor_copy = (tensor_copy * 255).clamp(0, 255)
                else:
                    # 假设已经是 [0, 255] 范围
                    tensor_copy = tensor_copy.clamp(0, 255)
                tensor_copy = tensor_copy.to(torch.uint8)
            elif tensor_copy.dtype != torch.uint8:
                # 其他整数类型转为 uint8
                tensor_copy = tensor_copy.to(torch.uint8)

            # 转换到CPU并转为numpy数组
            img_np = tensor_copy.cpu().numpy()

            # 处理通道格式，保持兼容性
            if c == 1:
                # 灰度图转RGB，复制通道
                img_np = np.stack([img_np] * 3, axis=2)
            elif c == 4:
                # RGBA转RGB，保留RGB通道
                img_np = img_np[:, :, :3]
            elif c == 3:
                # 已经是RGB，无需转换
                pass

            # 确保最终是3通道RGB
            if img_np.shape[2] != 3:
                print(f"❌ [SiberiaOllamaSDK] Final image doesn't have 3 channels: {img_np.shape}")
                return None

            # 创建PIL图像
            img_pil = Image.fromarray(img_np.astype(np.uint8), mode='RGB')

            # 转换为base64
            return self._pil_to_base64(img_pil)

        except Exception as e:
            print(f"Error converting tensor to base64: {e}")
            return None

    def _tensor_to_temp_file(self, tensor: torch.Tensor) -> Optional[str]:
        """将torch.Tensor转换为临时文件 / Convert torch.Tensor to temporary file"""
        try:
            # 验证tensor
            if not isinstance(tensor, torch.Tensor):
                print(f"Error: Expected torch.Tensor, got {type(tensor)}")
                return None

            if tensor.numel() == 0:
                print("Error: Empty tensor provided")
                return None

            # 处理批次维度
            if len(tensor.shape) == 5:
                # [N, B, H, W, C] -> [N*H, W, C] 通过重塑
                if tensor.shape[1] == 1:
                    tensor = tensor.squeeze(1)  # [N, H, W, C]
                print(f"Warning: 5D tensor detected, shape: {tensor.shape}")
            elif len(tensor.shape) == 4:
                # [B, H, W, C] -> [H, W, C] 取第一张图片
                if tensor.shape[0] > 1:
                    print(f"Warning: Multiple images in batch, using first image. Batch size: {tensor.shape[0]}")
                tensor = tensor[0]
            elif len(tensor.shape) == 2:
                # [H, W] -> [H, W, 3] 灰度图
                tensor = torch.stack([tensor] * 3, dim=-1)

            # 验证最终形状
            if len(tensor.shape) != 3:
                print(f"Error: Invalid tensor shape after processing: {tensor.shape}")
                return None

            h, w, c = tensor.shape
            if c not in [1, 3, 4]:
                print(f"Error: Invalid number of channels: {c}")
                return None

            if h < 1 or w < 1:
                print(f"Error: Invalid image dimensions: {h}x{w}")
                return None

            # 不限制图片尺寸，保持原始分辨率
            print(f"📸 [SiberiaOllamaSDK] Processing image at original resolution: {h}x{w}x{c}")

            # 转换数据类型
            if tensor.dtype in [torch.float32, torch.float64, torch.float16]:
                # 假设数据在[0,1]范围内
                if tensor.max() <= 1.0:
                    tensor = (tensor * 255).clamp(0, 255)
                else:
                    tensor = tensor.clamp(0, 255)
                tensor = tensor.to(torch.uint8)

            # 转换为numpy数组
            img_np = tensor.cpu().numpy()

            # 处理不同的通道格式
            if len(img_np.shape) == 3:
                if img_np.shape[2] == 1:  # 单通道
                    img_np = np.concatenate([img_np] * 3, axis=2)
                elif img_np.shape[2] == 4:  # RGBA -> RGB
                    img_np = img_np[:, :, :3]
                elif img_np.shape[2] > 3:  # 超过3通道
                    img_np = img_np[:, :, :3]

            # 创建PIL图像
            img_pil = Image.fromarray(img_np.astype(np.uint8), mode='RGB')
            return self._pil_to_temp_file(img_pil)

        except Exception as e:
            print(f"Error converting tensor to image: {e}")
            return None

    def _pil_to_base64(self, img_pil) -> Optional[str]:
        """将PIL图像转换为base64字符串 / Convert PIL image to base64 string"""
        try:
            buffer = io.BytesIO()
            # 使用PNG格式以保持最佳图像质量
            img_pil.save(buffer, format='PNG', compress_level=6)
            img_bytes = buffer.getvalue()
            buffer.close()

            return base64.b64encode(img_bytes).decode('utf-8')
        except Exception as e:
            print(f"Error converting PIL image to base64: {e}")
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
            "use_base64": self.use_base64,
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
            timeout=connection_info.get("timeout", 30),
            use_base64=connection_info.get("use_base64", False)
        )

        # 恢复连接状态
        client._connected = connection_info.get("connected", False)
        client._available_models = connection_info.get("available_models", [])

        return client