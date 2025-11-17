"""
ComfyUI-SiberiaNodes - Web assets and JavaScript extensions

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""

import os
import sys
from pathlib import Path

# 获取web目录路径
web_dir = Path(__file__).parent
js_files = [
    web_dir / "js" / "siberiaOllama.js",
    web_dir / "js" / "siberiaMultiImageLoader.js",
    web_dir / "js" / "siberiaDisplay.js"
]

# 检查JavaScript文件
for js_file in js_files:
    if js_file.exists():
        print(f"Siberia Web: Found JavaScript file at {js_file}")
    else:
        print(f"Siberia Web: JavaScript file not found at {js_file}")

# 自动发现所有JavaScript文件
all_js_files = list((web_dir / 'js').glob('*.js'))
print(f"Siberia Web: Available JavaScript files: {[f.name for f in all_js_files]}")
print(f"Siberia Web: JavaScript directory exists: {(web_dir / 'js').exists()}")