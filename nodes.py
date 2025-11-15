import torch
import numpy as np
import os
import json
from PIL import Image
import folder_paths
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
    SiberiaUniversalDisplayNode,
    UTIL_NODE_CLASS_MAPPINGS,
    UTIL_NODE_DISPLAY_NAME_MAPPINGS
)

# Register Ollama endpoints
register_endpoints(PromptServer)


class SiberiaImageLoaderNode:
    """
    Siberia Image Loader - 简单的图片加载节点 / Simple Image Loading Node
    """

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        files = folder_paths.filter_files_content_types(files, ["image"])
        return {
            "required": {
                "image": (sorted(files), {
                    "image_upload": True,
                    "tooltip": "选择图片 / Select Image"
                }),
            },
        }

    RETURN_TYPES = ("IMAGE", "STRING")
    RETURN_NAMES = ("图片 / Image", "信息 / Info")
    FUNCTION = "load_image"
    CATEGORY = "Siberia Nodes/Image"

    def load_image(self, image):
        try:
            if not image:
                error_msg = "Error: No image selected / 错误：未选择图片"
                return (torch.zeros((1, 64, 64, 3)), error_msg)

            # Load image from ComfyUI input folder / 从ComfyUI input文件夹加载图片
            image_path = folder_paths.get_annotated_filepath(image)

            try:
                # Load image / 加载图片
                img = Image.open(image_path)

                # Convert to RGB / 转换为RGB
                if img.mode != 'RGB':
                    img = img.convert('RGB')

                # Convert to numpy array / 转换为numpy数组
                img_array = np.array(img).astype(np.float32) / 255.0

                # Add batch dimension / 添加批次维度
                img_array = np.expand_dims(img_array, axis=0)

                # Convert to tensor / 转换为tensor
                image_tensor = torch.from_numpy(img_array)

                info_msg = f"Successfully loaded image / 成功加载图片: {image_path} (Size: {img.size}, Mode: {img.mode})"

                return (image_tensor, info_msg)

            except Exception as e:
                error_msg = f"Error loading image '/ 加载图片错误 '{image}': {str(e)}"
                return (torch.zeros((1, 64, 64, 3)), error_msg)

        except Exception as e:
            error_msg = f"Error in image loading / 图片加载中发生错误: {str(e)}"
            return (torch.zeros((1, 64, 64, 3)), error_msg)








# Node mappings / 节点映射
NODE_CLASS_MAPPINGS = {
    "SiberiaImageLoaderNode": SiberiaImageLoaderNode,
    "SiberiaOllamaConnector": SiberiaOllamaConnector,
    "SiberiaOllamaChatNode": SiberiaOllamaChatNode,
    "SiberiaOllamaVisionNode": SiberiaOllamaVisionNode,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "SiberiaImageLoaderNode": "Siberia 图片加载器 / Image Loader",
    "SiberiaOllamaConnector": "Siberia Ollama连接器 / Ollama Connector",
    "SiberiaOllamaChatNode": "Siberia Ollama聊天 / Ollama Chat",
    "SiberiaOllamaVisionNode": "Siberia Ollama视觉分析 / Ollama Vision",
}

# 合并工具模块节点映射 / Merge utils module node mappings
NODE_CLASS_MAPPINGS.update(UTIL_NODE_CLASS_MAPPINGS)
NODE_DISPLAY_NAME_MAPPINGS.update(UTIL_NODE_DISPLAY_NAME_MAPPINGS)

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

# 注册自定义资源路径 / Register custom asset path
try:
    import importlib
    importlib.import_module("web")
except ImportError:
    pass
