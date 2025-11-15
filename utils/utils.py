"""
ComfyUI-SiberiaNodes - Utility classes and functions

Author: siberiah0h
Email: siberiah0h@gmail.com
Technical Blog: www.dataeast.cn
Last Updated: 2025-11-15
"""


class AlwaysEqualProxy(str):
    """代理类，允许与任何类型匹配 / Proxy class that allows matching with any type"""

    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False


# 通用类型代理 / Universal type proxy
any_type = AlwaysEqualProxy("*")