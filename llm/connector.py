"""
ComfyUI-SiberiaNodes - Ollama connector node for ComfyUI

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""

import os
import sys
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from .ollama_sdk_client import SiberiaOllamaSDKClient
from config_manager import manager


class SiberiaOllamaConnector:
    """
    Siberia Ollama Connector - 连接到Ollama服务器 / Connect to Ollama Server
    """

    def __init__(self):
        self._last_server_url = ""
        self._last_available_models = []
        self._last_connected = False
        self._config_manager = manager()

    @classmethod
    def INPUT_TYPES(cls):
        config_manager = manager()

        # 获取服务器选项 / Get server options
        servers = config_manager.get_server_options()
        server_display_options = config_manager.get_server_display_options()

        # 获取默认服务器名称 / Get default server name
        default_server_url = config_manager.get_default_server()
        default_server_name = None
        for server in servers:
            if server['url'] == default_server_url:
                default_server_name = server['name']
                break
        if not default_server_name and server_display_options:
            default_server_name = server_display_options[0]

        # 使用自定义验证函数而不是预定义列表 / Use custom validation instead of predefined list
        # 接受任何模型名称，由JavaScript动态管理选项 / Accept any model name, managed dynamically by JavaScript

        # 如果没有配置的服务器，添加默认选项
        if not server_display_options:
            server_display_options = ["Local Server / 本地服务器"]
            if not default_server_name:
                default_server_name = "Local Server / 本地服务器"

        return {
            "required": {
                "server_name": (server_display_options, {
                    "default": default_server_name or server_display_options[0],
                    "tooltip": "Ollama服务器 / Ollama Server"
                }),
                "model": ("STRING", {
                    "default": "刷新 / refresh",
                    "multiline": False,
                    "tooltip": "选择模型 / Select Model (由下拉列表动态管理选项 / Options managed dynamically by dropdown)"
                }),
                "timeout": ("INT", {
                    "default": 30,
                    "min": 5,
                    "max": 300,
                    "tooltip": "请求超时时间(秒) / Request Timeout (seconds)"
                }),
            },
        }

    RETURN_TYPES = ("OLLAMA_CONNECTION",)
    RETURN_NAMES = ("连接 / Connection",)
    FUNCTION = "connect_ollama"
    CATEGORY = "Siberia Nodes/Ollama"

    @classmethod
    def IS_CHANGED(cls, server_name, model, timeout):
        """ComfyUI动态更新机制 / ComfyUI Dynamic Update Mechanism"""
        try:
            # If refresh selected, need to update
            if model == "刷新 / refresh":
                print("Refresh selected, triggering update")
                return True

            # For simplicity, always return False to avoid excessive updates
            # ComfyUI will call this method to check if node needs to be re-executed
            return False

        except Exception as e:
            print(f"Error in IS_CHANGED: {e}")
            return True  # Force update on error


    def connect_ollama(self, server_name, model, timeout):
        """连接到Ollama服务器 / Connect to Ollama server"""
        try:
            # Convert server name to URL
            config_manager = manager()
            servers = config_manager.get_server_options()
            server_url = None

            # Find URL corresponding to server name
            for server in servers:
                if server.get('name') == server_name:
                    server_url = server.get('url')
                    break

            # If no corresponding URL found, use default
            if not server_url:
                server_url = "http://127.0.0.1:11434"
                print(f"Warning: Server '{server_name}' not found, using default URL")

            # Validate timeout
            timeout = max(5, min(300, int(timeout)))

            # Check if server changed
            server_changed = server_url != self._last_server_url
            if server_changed:
                print(f"Server changed from {self._last_server_url} to {server_url}")

            # Use Ollama SDK client
            client = SiberiaOllamaSDKClient(server_url, model, timeout)
            connection_success = client.test_connection()

            # Save last used server URL
            try:
                config_manager.set_last_used_server(server_url)
            except Exception as config_error:
                print(f"Warning: Failed to save last used server: {config_error}")

            # Update internal state
            self._last_server_url = server_url
            self._last_timeout = timeout
            self._last_available_models = client.available_models.copy()
            self._last_connected = connection_success

            # Enhanced model selection logic
            actual_model = model
            auto_selected = False

            if model == "刷新 / refresh":
                # When refresh selected, use first available model
                if client.available_models:
                    client.model = client.available_models[0]
                    actual_model = client.available_models[0]
                    auto_selected = True
                    print(f"Auto-selected first available model: {actual_model}")
                else:
                    # No models available - keep as refresh
                    client.model = "refresh"
                    actual_model = "refresh"
                    print("No models available, keeping refresh mode")
            elif server_changed and connection_success:
                # When server changed and connection successful, auto-select first model if current model is not available
                if model not in client.available_models:
                    if client.available_models:
                        client.model = client.available_models[0]
                        actual_model = client.available_models[0]
                        auto_selected = True
                        print(f"Server changed - auto-switched to first available model: {actual_model}")
                    else:
                        print("Server changed but no models available")
                else:
                    # Keep user's model if it's available on new server
                    client.model = model
                    print(f"Server changed - keeping user's model: {model}")
            else:
                # Use user-selected model
                client.model = model
                if model not in client.available_models and client.available_models:
                    print(f"Warning: Model '{model}' not found in available models")
                    # Auto-select first available model
                    client.model = client.available_models[0]
                    actual_model = client.available_models[0]
                    auto_selected = True
                    print(f"Auto-switching to: {actual_model}")
                elif not client.available_models:
                    print("No available models to switch to")

            # Create connection info
            connection_info = client.to_connection_info()
            connection_info.update({
                "selected_model": actual_model,
                "user_selected_model": model,
                "server_name": server_name,
                "server_url": server_url,
                "connection_status": "connected" if connection_success else "failed",
                "server_changed": server_changed,
                "auto_selected": auto_selected,
                "available_models_count": len(client.available_models)
            })

            return (connection_info,)

        except Exception as e:
            print(f"Error in connect_ollama: {type(e).__name__}: {e}")
            # Return a safe fallback connection info
            error_connection_info = {
                "server_url": server_url or "http://127.0.0.1:11434",
                "model": model,
                "timeout": timeout,
                "available_models": [],
                "connected": False,
                "selected_model": model,
                "user_selected_model": model,
                "server_name": server_name,
                "server_url": server_url or "http://127.0.0.1:11434",
                "connection_status": "error",
                "error": str(e),
                "server_changed": False,
                "auto_selected": False,
                "available_models_count": 0
            }
            return (error_connection_info,)