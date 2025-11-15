"""
ComfyUI-SiberiaNodes - Custom nodes for ComfyUI with Ollama integration

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""

from .nodes import NODE_CLASS_MAPPINGS, NODE_DISPLAY_NAME_MAPPINGS

__all__ = ['NODE_CLASS_MAPPINGS', 'NODE_DISPLAY_NAME_MAPPINGS', 'WEB_DIRECTORY']

WEB_DIRECTORY = "./web"

print(f'\033[34m[ComfyUI-SiberiaNodes]\033[0m Loaded successfully with {len(NODE_CLASS_MAPPINGS)} nodes')
print(f'\033[34m[ComfyUI-SiberiaNodes]\033[0m Web directory: {WEB_DIRECTORY}')