"""
ComfyUI-SiberiaNodes - Ollama chat node for ComfyUI

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""

from .ollama_sdk_client import SiberiaOllamaSDKClient


class SiberiaOllamaChatNode:
    """
    Siberia Ollama Chat Node - 聊天对话节点 / Chat Conversation Node
    """

    def __init__(self):
        self.chat_history = []

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "message": ("STRING", {
                    "multiline": True,
                    "default": "Hello!",
                    "tooltip": "用户消息 / User Message"
                }),
                "clear_history": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "清除历史记录 / Clear History"
                }),
            },
            "optional": {
                "connection": ("OLLAMA_CONNECTION", {
                    "forceInput": False,
                    "tooltip": "Ollama连接 / Ollama Connection"
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
    FUNCTION = "chat"
    CATEGORY = "Siberia Nodes/Ollama"

    @classmethod
    def IS_CHANGED(cls, message, clear_history, connection=None, temperature=0.7, max_tokens=4096, language="中文"):
        """ComfyUI动态更新机制 / ComfyUI Dynamic Update Mechanism"""
        return False

    def chat(self, message, clear_history, connection=None, temperature=0.7, max_tokens=4096, language="中文"):
        # 使用Ollama SDK客户端 / Use Ollama SDK client
        client = SiberiaOllamaSDKClient.from_connection_info(connection)

        # 清除历史记录 / Clear history if requested
        if clear_history:
            self.chat_history = []

        # 准备消息 / Prepare messages
        if language == "中文":
            system_content = "请使用中文进行对话。"
        else:
            system_content = "Please use English for conversation."
        messages = [{"role": "system", "content": system_content}]
        messages.extend(self.chat_history)
        messages.append({"role": "user", "content": message})

        # 使用客户端进行聊天 / Use client for chat
        response_text, _, updated_messages = client.chat(messages, temperature=temperature, max_tokens=max_tokens)

        # 更新聊天历史 / Update chat history
        if response_text and not response_text.startswith("Error"):
            self.chat_history = updated_messages

        return (response_text,)