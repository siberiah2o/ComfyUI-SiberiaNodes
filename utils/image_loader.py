"""
ComfyUI-SiberiaNodes - Image loading utilities

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-17
"""

import torch
import numpy as np
import os
from PIL import Image
import folder_paths


class SiberiaMultiImageLoaderNode:
    """
    Siberia Multi Image Loader - Enhanced multi-image input node with dynamic input support
    增强版多图片输入节点，支持动态输入和多种媒体类型
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "input_count": ("INT", {
                    "default": 2,
                    "min": 1,
                    "max": 8,  # Limited to 8 image inputs as requested
                    "step": 1,
                    "tooltip": "输入数量 / Number of image inputs (1-8)"
                }),
            },
            "optional": {
                "image_1": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("IMAGE",)  # Simplified to single IMAGE output
    RETURN_NAMES = ("图片张量列表 / Images Tensor List",)
    FUNCTION = "process_inputs"
    CATEGORY = "Siberia Nodes/Image"

    @classmethod
    def IS_CHANGED(cls, input_count):
        # Force re-evaluation when parameters change
        return hash(input_count)


    def process_inputs(self, input_count, **kwargs):
        """
        Simplified image input processing - only handles IMAGE inputs
        Always outputs images list (stacked tensor)
        简化的图片输入处理 - 只处理IMAGE输入，始终输出图片列表
        """
        try:
            images = []
            valid_count = 0

            print(f"🎯 [SiberiaMultiImageLoader] Processing {input_count} image inputs")

            for i in range(1, input_count + 1):
                input_key = f"image_{i}"
                tensor = kwargs.get(input_key, None)
                if tensor is not None and len(tensor.shape) == 4:
                    images.append(tensor)
                    valid_count += 1
                    print(f"  ✓ {input_key}: image processed (shape: {tensor.shape})")
                else:
                    print(f"  ❌ {input_key}: Invalid or missing tensor")

            if not images:
                print(f"⚠️ [SiberiaMultiImageLoader] No valid images found")
                return (torch.zeros((1, 64, 64, 3)),)  # Return default tensor

            # Always output images list - stack all images into a single tensor
            stacked_tensor = torch.stack(images, dim=0)
            print(f"✅ [SiberiaMultiImageLoader] Stacked {len(images)} images (shape: {stacked_tensor.shape})")
            return (stacked_tensor,)

        except Exception as e:
            print(f"❌ [SiberiaMultiImageLoader] Error processing image inputs: {str(e)}")
            import traceback
            traceback.print_exc()
            return (torch.zeros((1, 64, 64, 3)),)


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


# Node mappings for image loading nodes / 图片加载节点的映射
IMAGE_LOADER_NODE_CLASS_MAPPINGS = {
    "SiberiaMultiImageLoaderNode": SiberiaMultiImageLoaderNode,
    "SiberiaImageLoaderNode": SiberiaImageLoaderNode,
}

IMAGE_LOADER_NODE_DISPLAY_NAME_MAPPINGS = {
    "SiberiaMultiImageLoaderNode": "Siberia 多图片输入器 / Multi Image Input",
    "SiberiaImageLoaderNode": "Siberia 图片加载器 / Image Loader",
}