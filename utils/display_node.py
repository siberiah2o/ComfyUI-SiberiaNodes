"""
Siberia 通用展示节点 / Siberia Universal Display Node

这个节点可以接收并显示任何类型的数据，包括字符串、数字、列表、字典等。
This node can receive and display any type of data, including strings, numbers, lists, dicts, etc.
"""

import json
from typing import Any, Dict, List, Tuple, Optional
from .utils import any_type


class SiberiaUniversalDisplayNode:
    """
    通用展示节点 - 可以显示任何类型的数据
    Universal Display Node - Display any type of data
    
    功能特性 / Features:
    - 支持任意类型输入 / Support any type input
    - 自动格式化显示 / Auto-format display
    - 支持列表和嵌套数据 / Support lists and nested data
    - 实时更新显示 / Real-time display update
    """

    @classmethod
    def INPUT_TYPES(cls) -> Dict[str, Any]:
        """
        定义节点输入类型
        Define node input types
        """
        return {
            "required": {},
            "optional": {
                "anything": (any_type, {"tooltip": "任何类型的数据 / Any type of data"}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            }
        }

    RETURN_TYPES = (any_type,)
    RETURN_NAMES = ("output",)
    FUNCTION = "display_data"
    OUTPUT_NODE = True
    INPUT_IS_LIST = True  # 启用列表输入模式
    OUTPUT_IS_LIST = (False,)  # 输出为单个值而非列表
    CATEGORY = "Siberia Nodes/Utility"

    @classmethod
    def IS_CHANGED(cls, **kwargs) -> bool:
        """
        控制节点缓存行为
        Control node caching behavior
        
        返回 False 表示每次都重新执行
        Return False to re-execute every time
        """
        return False

    def display_data(
        self,
        unique_id: Optional[List[str]] = None,
        extra_pnginfo: Optional[List[Dict]] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        显示数据的主函数
        Main function to display data
        
        Args:
            unique_id: 节点唯一ID / Node unique ID
            extra_pnginfo: 工作流元信息 / Workflow metadata
            **kwargs: 包含输入数据的关键字参数 / Keyword args containing input data
            
        Returns:
            包含UI更新和结果的字典 / Dict containing UI update and result
        """
        try:
            # 转换输入数据为可显示格式
            display_values = self._convert_input_to_display_format(kwargs.get("anything", []))
            
            # 更新工作流中的节点显示
            self._update_workflow_node_display(unique_id, extra_pnginfo, display_values)
            
            # 返回UI更新和输出结果
            return self._build_response(display_values)
            
        except Exception as e:
            return self._build_error_response(e)

    def _convert_input_to_display_format(self, input_data: List[Any]) -> List[str]:
        """
        将输入数据转换为可显示的字符串格式
        Convert input data to displayable string format
        
        Args:
            input_data: 输入数据列表 / Input data list
            
        Returns:
            转换后的字符串列表 / Converted string list
        """
        display_values = []
        
        for value in input_data:
            converted = self._convert_single_value(value)
            
            # 如果转换结果是列表，直接使用（保持原有行为）
            if isinstance(converted, list):
                display_values = converted
            else:
                display_values.append(converted)
        
        return display_values

    def _convert_single_value(self, value: Any) -> Any:
        """
        转换单个值为可显示格式
        Convert single value to displayable format
        
        Args:
            value: 要转换的值 / Value to convert
            
        Returns:
            转换后的值 / Converted value
        """
        try:
            # 字符串直接返回
            if isinstance(value, str):
                return value
            
            # 列表直接返回（用于替换整个显示列表）
            elif isinstance(value, list):
                return value
            
            # 基本类型转为字符串
            elif isinstance(value, (int, float, bool)):
                return str(value)
            
            # 复杂类型尝试JSON序列化
            else:
                return self._serialize_to_json(value)
                
        except Exception:
            # 转换失败时使用字符串表示
            return str(value)

    def _serialize_to_json(self, value: Any) -> str:
        """
        将值序列化为JSON字符串
        Serialize value to JSON string
        
        Args:
            value: 要序列化的值 / Value to serialize
            
        Returns:
            JSON字符串 / JSON string
        """
        try:
            return json.dumps(value, ensure_ascii=False, indent=2)
        except Exception:
            return str(value)

    def _update_workflow_node_display(
        self,
        unique_id: Optional[List[str]],
        extra_pnginfo: Optional[List[Dict]],
        display_values: List[str]
    ) -> None:
        """
        更新工作流中节点的显示内容
        Update node display in workflow
        
        Args:
            unique_id: 节点唯一ID / Node unique ID
            extra_pnginfo: 工作流元信息 / Workflow metadata
            display_values: 要显示的值列表 / Values to display
        """
        # 验证参数有效性
        if not self._validate_workflow_params(extra_pnginfo):
            return
        
        # 获取工作流和节点
        workflow = extra_pnginfo[0]["workflow"]
        node = self._find_node_in_workflow(workflow, unique_id[0])
        
        # 更新节点的widget值
        if node:
            node["widgets_values"] = [display_values]

    def _validate_workflow_params(self, extra_pnginfo: Optional[List[Dict]]) -> bool:
        """
        验证工作流参数是否有效
        Validate workflow parameters
        
        Args:
            extra_pnginfo: 工作流元信息 / Workflow metadata
            
        Returns:
            是否有效 / Whether valid
        """
        if not extra_pnginfo:
            return False
        
        if not isinstance(extra_pnginfo, list) or len(extra_pnginfo) == 0:
            return False
        
        if not isinstance(extra_pnginfo[0], dict):
            return False
        
        if "workflow" not in extra_pnginfo[0]:
            return False
        
        return True

    def _find_node_in_workflow(self, workflow: Dict, node_id: str) -> Optional[Dict]:
        """
        在工作流中查找指定ID的节点
        Find node with specified ID in workflow
        
        Args:
            workflow: 工作流数据 / Workflow data
            node_id: 节点ID / Node ID
            
        Returns:
            找到的节点或None / Found node or None
        """
        nodes = workflow.get("nodes", [])
        return next((node for node in nodes if str(node["id"]) == node_id), None)

    def _build_response(self, display_values: List[str]) -> Dict[str, Any]:
        """
        构建响应数据
        Build response data
        
        Args:
            display_values: 显示值列表 / Display values list
            
        Returns:
            响应字典 / Response dict
        """
        # 如果只有一个值，返回该值；否则返回整个列表
        if isinstance(display_values, list) and len(display_values) == 1:
            result = display_values[0]
        else:
            result = display_values
        
        return {
            "ui": {"text": display_values},
            "result": (result,)
        }

    def _build_error_response(self, error: Exception) -> Dict[str, Any]:
        """
        构建错误响应
        Build error response
        
        Args:
            error: 异常对象 / Exception object
            
        Returns:
            错误响应字典 / Error response dict
        """
        error_msg = f"Display Error: {type(error).__name__}: {str(error)}"
        print(f"[SiberiaUniversalDisplayNode] {error_msg}")
        
        return {
            "ui": {"text": [error_msg]},
            "result": (error_msg,)
        }


# 节点映射 / Node mappings
UTIL_NODE_CLASS_MAPPINGS = {
    "SiberiaUniversalDisplayNode": SiberiaUniversalDisplayNode,
}

UTIL_NODE_DISPLAY_NAME_MAPPINGS = {
    "SiberiaUniversalDisplayNode": "Siberia 通用展示 / Universal Display",
}
