import sys
import pathlib

# Add parent directory to path for imports
sys.path.insert(0, str(pathlib.Path(__file__).parent.parent))

from .ollama_sdk_client import SiberiaOllamaSDKClient
from config_manager import manager


def register_endpoints(PromptServer):
    """
    注册Ollama相关的HTTP端点 / Register Ollama-related HTTP endpoints
    """

    @PromptServer.instance.routes.post("/siberia_ollama/get_models")
    async def get_models_endpoint(request):
        try:
            data = await request.json()
            server_url = data.get("server_url", "http://127.0.0.1:11434")

            # Create temporary client to fetch models using SDK
            client = SiberiaOllamaSDKClient(server_url)
            print(f"Using Ollama SDK client for server: {server_url}")

            connection_success = client.test_connection()

            if client.connected:
                from aiohttp import web
                return web.json_response({
                    "models": client.available_models,
                    "success": True
                })
            else:
                from aiohttp import web
                return web.json_response({
                    "models": [],
                    "success": False,
                    "error": "Failed to connect to Ollama server"
                })

        except Exception as e:
            from aiohttp import web
            return web.json_response({
                "models": [],
                "success": False,
                "error": str(e)
            })

    @PromptServer.instance.routes.post("/siberia_ollama/get_models_by_name")
    async def get_models_by_name_endpoint(request):
        """获取指定服务器的模型列表 / Get model list for specified server"""
        try:
            # Validate JSON data
            if not request.content_type or 'application/json' not in request.content_type:
                from aiohttp import web
                return web.json_response({
                    "models": [],
                    "success": False,
                    "error": "Content-Type must be application/json"
                }, status=400)

            data = await request.json()
            if not isinstance(data, dict):
                from aiohttp import web
                return web.json_response({
                    "models": [],
                    "success": False,
                    "error": "Invalid JSON data"
                }, status=400)

            server_name = data.get("server_name", "").strip()
            if not server_name:
                from aiohttp import web
                return web.json_response({
                    "models": [],
                    "success": False,
                    "error": "Server name is required"
                }, status=400)

            # Convert server name to URL
            config_manager = manager()
            servers = config_manager.get_server_options()
            server_url = None

            for server in servers:
                if server.get('name') == server_name:
                    server_url = server.get('url')
                    break

            # Fallback to default URL if server not found
            if not server_url:
                server_url = "http://127.0.0.1:11434"
                print(f"Warning: Server '{server_name}' not found in config, using default URL")

            # Create temporary client to fetch models using SDK
            client = SiberiaOllamaSDKClient(server_url)
            print(f"Using Ollama SDK client for server: {server_url}")

            connection_success = client.test_connection()

            if connection_success:
                from aiohttp import web
                return web.json_response({
                    "models": client.available_models,
                    "success": True,
                    "server_name": server_name,
                    "server_url": server_url,
                    "model_count": len(client.available_models)
                })
            else:
                from aiohttp import web
                return web.json_response({
                    "models": [],
                    "success": False,
                    "error": f"Failed to connect to server '{server_name}' at {server_url}",
                    "server_name": server_name,
                    "server_url": server_url
                })

        except Exception as client_error:
                from aiohttp import web
                return web.json_response({
                    "models": [],
                    "success": False,
                    "error": f"Client error: {str(client_error)}",
                    "server_name": server_name,
                    "server_url": server_url
                })

        except Exception as e:
            print(f"Error in get_models_by_name_endpoint: {type(e).__name__}: {e}")
            from aiohttp import web
            return web.json_response({
                "models": [],
                "success": False,
                "error": f"Server error: {str(e)}"
            }, status=500)