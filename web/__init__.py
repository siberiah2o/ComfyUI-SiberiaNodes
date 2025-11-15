import os
import sys
from pathlib import Path

# 获取web目录路径
web_dir = Path(__file__).parent
js_file = web_dir / "js" / "siberiaOllama.js"

# 确保JavaScript文件存在
if js_file.exists():
    print(f"Siberia Ollama Web: Found JavaScript file at {js_file}")
else:
    print(f"Siberia Ollama Web: JavaScript file not found at {js_file}")
    print(f"Available files in web/js: {list((web_dir / 'js').glob('*.js')) if (web_dir / 'js').exists() else 'Directory not found'}")