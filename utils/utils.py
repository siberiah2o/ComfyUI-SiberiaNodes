"""
SiberiaNodes 工具类 / SiberiaNodes Utils
"""


class AlwaysEqualProxy(str):
    """代理类，允许与任何类型匹配 / Proxy class that allows matching with any type"""

    def __eq__(self, _):
        return True

    def __ne__(self, _):
        return False


# 通用类型代理 / Universal type proxy
any_type = AlwaysEqualProxy("*")