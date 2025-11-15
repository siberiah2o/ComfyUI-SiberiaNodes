"""
ComfyUI-SiberiaNodes - Configuration manager for Ollama server settings

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""

import yaml
import os
from pathlib import Path
from typing import Dict, List, Optional


class manager:
    """
    配置读取管理器 / Configuration Read Manager
    负责读取Ollama服务器配置 / Handles reading Ollama server configuration
    """

    def __init__(self):
        # 配置文件路径 / Configuration file path
        self.config_dir = Path(__file__).parent
        self.config_file = self.config_dir / "config.yaml"
        self.default_config = {
            "ollama_servers": [
                {
                    "name": "Local Server / 本地服务器",
                    "url": "http://127.0.0.1:11434"
                }
            ]
        }

    def load_config(self) -> Dict:
        """加载YAML配置文件 / Load YAML configuration file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = yaml.safe_load(f)

                # 确保配置结构完整 / Ensure configuration structure is complete
                if not config:
                    config = self.default_config.copy()
                if "ollama_servers" not in config:
                    config["ollama_servers"] = self.default_config["ollama_servers"]

                return config
            else:
                # 如果配置文件不存在，返回默认配置 / Return default config if file doesn't exist
                return self.default_config
        except Exception as e:
            print(f"配置文件加载失败，使用默认配置 / Failed to load config, using default: {e}")
            return self.default_config

    def get_servers(self) -> List[Dict]:
        """获取所有服务器列表 / Get all servers list"""
        config = self.load_config()
        return config.get("ollama_servers", [])

    
    def get_server_options(self) -> List[Dict]:
        """获取服务器选项列表，用于ComfyUI下拉菜单 / Get server options list for ComfyUI dropdown"""
        return self.get_servers()

    def get_server_display_options(self) -> List[str]:
        """获取服务器显示选项列表，用于ComfyUI下拉菜单显示 / Get server display options for ComfyUI dropdown"""
        servers = self.get_servers()
        options = []

        for server in servers:
            # 使用服务器名称作为显示 / Use server name for display
            options.append(server['name'])

        return options

    def get_default_server(self) -> str:
        """获取默认服务器 / Get default server"""
        servers = self.get_servers()

        # 使用第一个服务器 / Use first server
        if servers:
            return servers[0]['url']

        # 返回默认URL / Return default URL
        return "http://127.0.0.1:11434"