"""
ComfyUI-SiberiaNodes - Ollama vision node for ComfyUI

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-17
"""

from .ollama_sdk_client import SiberiaOllamaSDKClient


class SiberiaOllamaVisionNode:
    """
    Siberia Ollama Vision Node - 图片分析节点 / Image Analysis Node
    """

    def __init__(self):
        self._last_connection_info = None
        self._last_connected = False
        self.chat_history = []

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "connection": ("OLLAMA_CONNECTION", {
                    "tooltip": "Ollama连接对象 / Ollama Connection Object"
                }),
                "images": ("IMAGE", {
                    "tooltip": "要分析的图片张量列表 / Images Tensor List to Analyze"
                }),
                "prompt": ("STRING", {
                    "default": "请详细描述这些图片的内容 / Please describe the content of these images in detail",
                    "multiline": True,
                    "tooltip": "图片分析提示词 / Image Analysis Prompt"
                }),
                "clear_history": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "清除历史记录 / Clear History"
                }),
                "temperature": ("FLOAT", {
                    "default": 0.7,
                    "min": 0.1,
                    "max": 1.0,
                    "step": 0.1,
                    "tooltip": "生成温度 / Generation Temperature"
                }),
                "max_tokens": ("INT", {
                    "default": 4096,
                    "min": 1024,
                    "max": 32768,
                    "tooltip": "最大生成tokens / Maximum Generation Tokens"
                }),
                "language": (["中文", "English"], {
                    "default": "中文",
                    "tooltip": "语言 / Language"
                }),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("回复 / Response",)
    FUNCTION = "analyze_images"
    CATEGORY = "Siberia Nodes/Ollama"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """ComfyUI动态更新机制 / ComfyUI Dynamic Update Mechanism"""
        return False

    def analyze_images(self, connection, images, prompt, clear_history, temperature, max_tokens, language):
        """分析多张图片 / Analyze Multiple Images"""
        try:
            # 清除历史记录 / Clear history if requested
            if clear_history:
                self.chat_history = []

            # Validate inputs
            if not connection:
                error_msg = "错误：未提供Ollama连接 / Error: No Ollama connection provided"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            if images is None:
                error_msg = "错误：未提供图片 / Error: No images provided"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            if not prompt or not prompt.strip():
                error_msg = "错误：空提示词 / Error: Empty prompt"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            # Validate and clamp parameters with enhanced validation
            try:
                temperature = float(temperature)
                max_tokens = int(max_tokens)
            except (ValueError, TypeError):
                error_msg = "错误：温度和最大tokens必须是数字 / Error: Temperature and max_tokens must be numbers"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            # 更严格的参数范围检查
            if not (0.0 <= temperature <= 2.0):
                print(f"⚠️ [SiberiaOllamaVision] Temperature {temperature} out of range [0.0-2.0], clamping to 0.7")
                temperature = max(0.0, min(2.0, temperature))

            if not (1 <= max_tokens <= 32768):
                print(f"⚠️ [SiberiaOllamaVision] Max tokens {max_tokens} out of range [1-32768], clamping to 4096")
                max_tokens = max(1, min(32768, max_tokens))

            # 多图片分析时的保守参数调整
            if len(images.shape) > 4 and images.shape[0] > 1:  # 多张图片
                if temperature > 1.0:
                    print(f"⚠️ [SiberiaOllamaVision] Reducing temperature from {temperature} to 1.0 for multi-image analysis")
                    temperature = 1.0
                if max_tokens > 8192:
                    print(f"⚠️ [SiberiaOllamaVision] Reducing max_tokens from {max_tokens} to 8192 for multi-image analysis")
                    max_tokens = 8192

            # Create client from connection
            client = SiberiaOllamaSDKClient.from_connection_info(connection)

            # 使用增强的视觉模型验证
            if not client.is_vision_model():
                error_msg = f"错误：模型 '{client.model}' 不支持视觉功能 / Error: Model '{client.model}' does not support vision capabilities"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            # 处理图像张量，支持 ComfyUI 标准格式 [batch, height, width, channels]
            images_list = self._process_image_tensors(images)
            if not images_list:
                error_msg = f"错误：无法处理图片张量 / Error: Cannot process image tensors with shape: {images.shape}"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            # Create system prompt for multi-image analysis
            system_prompt = f"You are a Qwen3-VL Instruct model. Please answer in {language}. "

            # Analyze all images in a single request
            response_text, info_msg = client.analyze_multiple_images(
                prompt=prompt.strip(),
                images_data=images_list,
                system_prompt=system_prompt.strip(),
                temperature=temperature,
                max_tokens=max_tokens
            )

            if response_text and not response_text.startswith("Error"):
                return {"ui": {"text": [response_text]}, "result": (response_text,)}
            else:
                error_msg = f"多图分析失败 / Multi-Image Analysis Failed: {response_text or info_msg}"
                print(error_msg)
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

        except Exception as e:
            error_msg = f"图片分析错误 / Image Analysis Error: {type(e).__name__}: {str(e)}"
            print(error_msg)
            return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

    def _process_image_tensors(self, images) -> list:
        """
        处理 ComfyUI 格式的图像张量，支持 4D 和 5D 张量
        完全保持原始图片信息，不做任何修改

        Args:
            images: ComfyUI 图像张量
                   - 4D: [batch, height, width, channels] (单图像批次或标准图像)
                   - 5D: [num_images, batch, height, width, channels] (多图像堆叠)

        Returns:
            list: 原始图像张量列表，直接传递给 SDK
        """
        try:
            import torch

            if images is None:
                return []

            if not isinstance(images, torch.Tensor):
                return []

            images_list = []

            # 处理 5D 张量 [N, B, H, W, C] - 多图像堆叠格式
            if len(images.shape) == 5:
                num_images, batch_size, height, width, channels = images.shape

                # 验证通道数
                if channels not in [1, 3, 4]:
                    return []

                # 验证图像尺寸
                if height < 1 or width < 1:
                    return []

                # 提取每个图像的 [H, W, C] 格式
                for i in range(num_images):
                    if batch_size == 1:
                        # [1, H, W, C] -> [H, W, C]
                        single_image = images[i, 0]  # 移除批次维度
                    else:
                        # 如果批次大小 > 1，取第一张
                        single_image = images[i, 0]  # 取批次中的第一张

                    images_list.append(single_image)

            # 处理 4D 张量 [B, H, W, C] - 标准图像批次
            elif len(images.shape) == 4:
                batch_size, height, width, channels = images.shape

                # 验证通道数
                if channels not in [1, 3, 4]:
                    return []

                # 验证图像尺寸
                if height < 1 or width < 1:
                    return []

                # 提取每张图像 [H, W, C]
                for i in range(batch_size):
                    single_image = images[i]
                    images_list.append(single_image)

            else:
                return []
            return images_list

        except Exception as e:
            return []