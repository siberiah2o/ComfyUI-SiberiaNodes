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
                "image": ("IMAGE", {
                    "tooltip": "要分析的图片 / Image to Analyze"
                }),
                "prompt": ("STRING", {
                    "default": "请详细描述这张图片的内容 / Please describe the content of this image in detail",
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
    FUNCTION = "analyze_image"
    CATEGORY = "Siberia Nodes/Ollama"

    @classmethod
    def IS_CHANGED(cls, **kwargs):
        """ComfyUI动态更新机制 / ComfyUI Dynamic Update Mechanism"""
        return False

    def analyze_image(self, connection, image, prompt, clear_history, temperature, max_tokens, language):
        """分析图片 / Analyze Image"""
        try:
            # 清除历史记录 / Clear history if requested
            if clear_history:
                self.chat_history = []

            # Validate inputs
            if not connection:
                error_msg = "错误：未提供Ollama连接 / Error: No Ollama connection provided"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            if image is None:
                error_msg = "错误：未提供图片 / Error: No image provided"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            if not prompt or not prompt.strip():
                error_msg = "错误：空提示词 / Error: Empty prompt"
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

            # Validate and clamp parameters
            temperature = max(0.0, min(2.0, float(temperature)))
            max_tokens = max(1, min(4096, int(max_tokens)))

            # Create client from connection
            client = SiberiaOllamaSDKClient.from_connection_info(connection)

            # Check if model supports vision (simple heuristic)
            vision_keywords = ['vision', 'vl', 'multimodal', 'llava', 'bakllava', 'moondream']
            model_name = client.model.lower()
            supports_vision = any(keyword in model_name for keyword in vision_keywords)

            if not supports_vision:
                print(f"Warning: Model '{client.model}' may not support vision. Vision keywords: {vision_keywords}")
            system_prompt = f"You are a professional image analysis assistant, please answer in {language}, only output description, do not output other content."
            # Analyze image
            response_text, info_msg = client.analyze_image(
                prompt=prompt.strip(),
                image_data=image,
                system_prompt=system_prompt.strip(),
                temperature=temperature,
                max_tokens=max_tokens
            )

            if response_text and not response_text.startswith("Error"):
                # Success
                return {"ui": {"text": [response_text]}, "result": (response_text,)}
            else:
                # Error occurred
                error_msg = f"图片分析失败 / Image Analysis Failed: {response_text or info_msg}"
                print(error_msg)
                return {"ui": {"text": [error_msg]}, "result": (error_msg,)}

        except Exception as e:
            error_msg = f"图片分析错误 / Image Analysis Error: {type(e).__name__}: {str(e)}"
            print(error_msg)
            return {"ui": {"text": [error_msg]}, "result": (error_msg,)}