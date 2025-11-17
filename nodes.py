"""
ComfyUI-SiberiaNodes - Main node definitions for ComfyUI custom nodes

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""

import json
import time
from .config_manager import manager
from server import PromptServer
from aiohttp import web
import pathlib
from .llm import (
    SiberiaOllamaConnector,
    SiberiaOllamaChatNode,
    SiberiaOllamaVisionNode,
    register_endpoints
)
from .utils import (
    UTIL_NODE_CLASS_MAPPINGS,
    UTIL_NODE_DISPLAY_NAME_MAPPINGS,
    IMAGE_LOADER_NODE_CLASS_MAPPINGS,
    IMAGE_LOADER_NODE_DISPLAY_NAME_MAPPINGS
)

# Register Ollama endpoints
register_endpoints(PromptServer)


# Node mappings / 节点映射
NODE_CLASS_MAPPINGS = {
    "SiberiaOllamaConnector": SiberiaOllamaConnector,
    "SiberiaOllamaChatNode": SiberiaOllamaChatNode,
    "SiberiaOllamaVisionNode": SiberiaOllamaVisionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SiberiaOllamaConnector": "Siberia Ollama连接器 / Ollama Connector",
    "SiberiaOllamaChatNode": "Siberia Ollama聊天 / Ollama Chat",
    "SiberiaOllamaVisionNode": "Siberia Ollama视觉分析 / Ollama Vision",
}

# 合并工具模块节点映射 / Merge utils module node mappings
NODE_CLASS_MAPPINGS.update(UTIL_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(UTIL_NODE_DISPLAY_NAME_MAPPINGS)

# 合并图片加载器节点映射 / Merge image loader node mappings
NODE_CLASS_MAPPINGS.update(IMAGE_LOADER_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(IMAGE_LOADER_NODE_DISPLAY_NAME_MAPPINGS)

# 注册JavaScript扩展文件 / Register JavaScript extension file
WEB_DIRECTORY = "./web"

@PromptServer.instance.routes.get("/siberia_ollama.js")
async def get_siberia_ollama_js(request):
    """提供Siberia Ollama JavaScript文件 / Serve Siberia Ollama JavaScript file"""
    js_path = pathlib.Path(__file__).parent / "web" / "js" / "siberiaOllama.js"
    if js_path.exists():
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        return web.Response(text=js_content, content_type='application/javascript')
    else:
        return web.Response(text="console.error('Siberia Ollama JS file not found at expected location');", content_type='application/javascript')

@PromptServer.instance.routes.get("/siberia_multi_image_loader.js")
async def get_siberia_multi_image_loader_js(_):
    """提供Siberia Multi Image Loader JavaScript文件 / Serve Siberia Multi Image Loader JavaScript file"""
    js_path = pathlib.Path(__file__).parent / "web" / "js" / "siberiaMultiImageLoader.js"
    if js_path.exists():
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        return web.Response(text=js_content, content_type='application/javascript')
    else:
        return web.Response(text="console.error('Siberia Multi Image Loader JS file not found at expected location');", content_type='application/javascript')

@PromptServer.instance.routes.get("/siberia_dynamic_inputs.js")
async def get_siberia_dynamic_inputs_js(_):
    """提供Siberia Dynamic Inputs JavaScript文件 / Serve Siberia Dynamic Inputs JavaScript file"""
    js_path = pathlib.Path(__file__).parent / "web" / "js" / "siberiaDynamicInputs.js"
    if js_path.exists():
        with open(js_path, 'r', encoding='utf-8') as f:
            js_content = f.read()
        return web.Response(text=js_content, content_type='application/javascript')
    else:
        return web.Response(text="console.error('Siberia Dynamic Inputs JS file not found at expected location');", content_type='application/javascript')

# 注册自定义资源路径 / Register custom asset path
try:
    import importlib
    importlib.import_module("web")
except ImportError:
    pass
