# ComfyUI-SiberiaNodes / ComfyUI西伯利亚节点

一个为 ComfyUI 开发的简单图片加载自定义插件。
A simple image loading custom plugin developed for ComfyUI.

## 功能特性 / Features

### Siberia 图片加载器 / Image Loader
- 简单高效的图片加载功能 / Simple and efficient image loading functionality
- 类似 ComfyUI 核心的文件浏览器 / File browser similar to ComfyUI core
- 自动扫描 ComfyUI input 文件夹 / Auto-scan ComfyUI input folder
- 下拉菜单选择图片文件 / Dropdown menu for image file selection
- 自动转换为 RGB 格式 / Automatic RGB format conversion
- 提供加载信息反馈 / Provide loading information feedback

### Siberia Ollama 连接器 / Ollama Connector
- 连接到 Ollama 本地或远程服务器 / Connect to Ollama local or remote servers
- 动态加载可用模型列表 / Dynamically load available model list
- 下拉选择模型而非手动输入 / Dropdown model selection instead of manual input
- 自动刷新模型列表 / Auto-refresh model list
- 可配置超时时间 / Configurable timeout settings
- 连接状态验证 / Connection status validation

### Siberia Ollama 生成器 / Ollama Generator
- 文本生成功能 / Text generation functionality
- 可配置系统提示词和用户提示词 / Configurable system and user prompts
- 支持温度和生成长度参数 / Support temperature and generation length parameters
- 错误处理和状态反馈 / Error handling and status feedback

### Siberia Ollama 聊天 / Ollama Chat
- 多轮对话支持 / Multi-turn conversation support
- 聊天历史管理 / Chat history management
- 可清除历史记录功能 / Clear history functionality
- 上下文感知对话 / Context-aware conversations

## 安装方法 / Installation

1. 确保已安装 ComfyUI / Make sure ComfyUI is installed
2. 将此文件夹复制到 `ComfyUI/custom_nodes/` 目录下 / Copy this folder to `ComfyUI/custom_nodes/` directory
3. 安装依赖 / Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. 重启 ComfyUI / Restart ComfyUI

## 使用方法 / Usage

1. 启动 ComfyUI / Start ComfyUI
2. 确保 Ollama 服务器正在运行 / Ensure Ollama server is running
3. 在节点菜单中找到 "Siberia Nodes" 分类及其子分类 / Find "Siberia Nodes" category and its subcategories:
   - **Siberia Nodes/Image** - 图片加载相关节点 / Image loading related nodes
   - **Siberia Nodes/Ollama** - Ollama AI 相关节点 / Ollama AI related nodes
4. 根据需要拖入相应的节点 / Drag in appropriate nodes as needed

### Ollama 使用流程 / Ollama Usage Workflow
1. 添加 "Siberia Ollama连接器 / Ollama Connector" 节点 / Add "Siberia Ollama连接器 / Ollama Connector" node
2. 配置服务器地址 / Configure server URL
3. 在模型下拉列表中选择可用模型 / Select available model from dropdown list
   - 模型列表会自动从Ollama服务器加载 / Models automatically load from Ollama server
   - 如需刷新列表，选择"refresh"选项 / To refresh list, select "refresh" option
4. 添加 "Siberia Ollama生成器 / Ollama Generator" 或 "Siberia Ollama聊天 / Ollama Chat" 节点 / Add "Siberia Ollama生成器 / Ollama Generator" or "Siberia Ollama聊天 / Ollama Chat" node
5. 将连接器输出连接到生成器/聊天节点的连接输入 / Connect connector output to generator/chat node's connection input
6. 配置提示词和参数 / Configure prompts and parameters
7. 执行节点 / Execute nodes

## 节点说明 / Node Description

### Siberia 图片加载器 / Image Loader
- **输入 / Inputs**:
  - `image`: 图片选择 / Image Selection（必需 / required）- 从 ComfyUI input 文件夹中选择 / Select from ComfyUI input folder
- **输出 / Outputs**:
  - `图片 / Image`: 加载的图片张量 / Loaded image tensor
  - `信息 / Info`: 加载信息字符串 / Loading information string

### Siberia Ollama 连接器 / Ollama Connector
- **输入 / Inputs**:
  - `server_url`: 服务器地址 / Server URL（必需 / required）- Ollama服务器地址 / Ollama server address
  - `model`: 模型选择 / Model Selection（必需 / required）- 从下拉列表选择模型，选择"refresh"刷新列表 / Select model from dropdown, select "refresh" to reload list
  - `timeout`: 超时时间 / Timeout（必需 / required）- 请求超时时间(秒) / Request timeout in seconds
- **输出 / Outputs**:
  - `连接 / Connection`: 连接信息对象 / Connection information object

### Siberia Ollama 生成器 / Ollama Generator
- **输入 / Inputs**:
  - `prompt`: 用户提示词 / User Prompt（必需 / required）- 用户输入的提示词 / User input prompt
  - `system_prompt`: 系统提示词 / System Prompt（必需 / required）- 系统角色设定 / System role setting
  - `max_tokens`: 最大生成长度 / Max Tokens（必需 / required）- 生成的最大token数 / Maximum number of tokens to generate
  - `temperature`: 温度参数 / Temperature（必需 / required）- 控制生成随机性 / Control generation randomness
  - `connection`: Ollama连接 / Ollama Connection（可选 / optional）- 连接信息 / Connection information
- **输出 / Outputs**:
  - `生成结果 / Generated Text`: 生成的文本内容 / Generated text content
  - `状态 / Status`: 执行状态信息 / Execution status information

### Siberia Ollama 聊天 / Ollama Chat
- **输入 / Inputs**:
  - `message`: 用户消息 / User Message（必需 / required）- 用户输入的消息 / User input message
  - `clear_history`: 清除历史 / Clear History（必需 / required）- 是否清除聊天历史 / Whether to clear chat history
  - `connection`: Ollama连接 / Ollama Connection（可选 / optional）- 连接信息 / Connection information
  - `system_prompt`: 系统提示词 / System Prompt（可选 / optional）- 系统角色设定 / System role setting
- **输出 / Outputs**:
  - `回复 / Response`: AI回复内容 / AI response content
  - `历史 / History`: 聊天历史记录 / Chat history record

## 技术细节 / Technical Details

- 基于 PyTorch 和 PIL/Pillow / Based on PyTorch and PIL/Pillow
- 使用 requests 库进行 HTTP 通信 / Use requests library for HTTP communication
- 支持 GPU 加速 / Support GPU acceleration
- 自动错误处理和回退机制 / Automatic error handling and fallback mechanism
- 兼容 ComfyUI 图片格式规范 / Compatible with ComfyUI image format specifications
- 兼容 Ollama REST API / Compatible with Ollama REST API

## Ollama 服务器要求 / Ollama Server Requirements

- 需要运行 Ollama 服务器 / Need Ollama server running
- 默认地址: http://127.0.0.1:11434 / Default URL: http://127.0.0.1:11434
- 支持本地和远程服务器 / Support local and remote servers
- 需要安装相应的模型 / Need to install appropriate models

### 安装 Ollama / Install Ollama
```bash
# Linux / macOS
curl -fsSL https://ollama.ai/install.sh | sh

# 或访问 https://ollama.ai/download 获取其他平台的安装方法
# Or visit https://ollama.ai/download for other platforms
```

### 拉取模型 / Pull Models
```bash
ollama pull llama2
ollama pull mistral
ollama pull codellama
```

## 兼容性 / Compatibility

- ComfyUI 最新版本 / Latest ComfyUI version
- Python 3.8+ / Python 3.8+
- CUDA 兼容 (如可用) / CUDA compatible (if available)

## 开发说明 / Development Notes

### 文件结构 / File Structure
```
ComfyUI-SiberiaNodes/
├── __init__.py         # 插件入口 / Plugin entry
├── nodes.py           # 节点实现 / Node implementation
├── ollama_client.py   # Ollama客户端抽象类 / Ollama Client Abstraction
├── requirements.txt   # 依赖列表 / Dependency list
├── web/               # 前端扩展 / Frontend extensions
│   └── js/
│       └── siberiaOllama.js  # 动态模型选择功能 / Dynamic model selection
└── README.md         # 说明文档 / Documentation
```

### 代码架构 / Code Architecture

- **SiberiaOllamaClient** (`ollama_client.py`):
  - 抽象的Ollama客户端类 / Abstract Ollama client class
  - 封装所有Ollama API交互 / Encapsulates all Ollama API interactions
  - 提供连接管理、文本生成、聊天功能 / Provides connection management, text generation, chat functionality

- **节点类** (`nodes.py`):
  - 调用SiberiaOllamaClient进行具体操作 / Call SiberiaOllamaClient for specific operations
  - 专注于ComfyUI节点接口 / Focus on ComfyUI node interface
  - 处理UI输入输出 / Handle UI inputs and outputs

## 许可证 / License

MIT License
