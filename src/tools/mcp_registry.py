"""
MCP Tool Registry - Manages all available tools following MCP specification

MCP (Model Context Protocol) defines a standard way to describe tools that agents can use.
Each tool has:
- name: Unique identifier
- description: What the tool does
- inputSchema: JSON schema defining parameters
- handler: Function that executes the tool
"""

from typing import Dict, List, Any, Callable, Optional
from dataclasses import dataclass
import json


@dataclass
class MCPTool:
    """
    MCP Tool Definition
    
    Follows MCP specification for tool definitions
    """
    name: str
    description: str
    input_schema: Dict[str, Any]  # JSON Schema
    handler: Callable  # Function that executes the tool
    version: str = "1.0.0"
    category: str = "general"  # data, validation, file, etc.


class MCPToolRegistry:
    """
    Registry for MCP-style tools
    
    Manages tool discovery, registration, and execution
    """
    
    def __init__(self):
        self.tools: Dict[str, MCPTool] = {}
    
    def register(self, tool: MCPTool):
        """Register a tool in the registry"""
        self.tools[tool.name] = tool
    
    def get_tool(self, name: str) -> Optional[MCPTool]:
        """Get a tool by name"""
        return self.tools.get(name)
    
    def list_tools(self, category: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        List all tools (optionally filtered by category)
        
        Returns tools in MCP format
        """
        tools_list = []
        for tool in self.tools.values():
            if category is None or tool.category == category:
                tools_list.append({
                    "name": tool.name,
                    "description": tool.description,
                    "inputSchema": tool.input_schema,
                    "version": tool.version,
                    "category": tool.category
                })
        return tools_list
    
    def execute(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute a tool with given arguments
        
        Args:
            tool_name: Name of the tool to execute
            arguments: Arguments for the tool (must match inputSchema)
        
        Returns:
            Tool execution result
        """
        tool = self.get_tool(tool_name)
        if not tool:
            raise ValueError(f"Tool '{tool_name}' not found")
        
        # Validate arguments against schema (basic validation)
        self._validate_arguments(arguments, tool.input_schema)
        
        # Execute tool
        return tool.handler(**arguments)
    
    def _validate_arguments(self, arguments: Dict[str, Any], schema: Dict[str, Any]):
        """Basic validation of arguments against JSON schema"""
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        
        # Check required fields
        for field in required:
            if field not in arguments:
                raise ValueError(f"Missing required argument: {field}")
        
        # Check types (basic)
        for field, value in arguments.items():
            if field in properties:
                expected_type = properties[field].get("type")
                if expected_type:
                    # Basic type checking
                    type_map = {
                        "string": str,
                        "integer": int,
                        "number": (int, float),
                        "boolean": bool,
                        "array": list,
                        "object": dict
                    }
                    if expected_type in type_map:
                        expected_python_type = type_map[expected_type]
                        if not isinstance(value, expected_python_type):
                            raise TypeError(
                                f"Argument '{field}' should be {expected_type}, "
                                f"got {type(value).__name__}"
                            )
    
    def get_tool_spec(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get full tool specification in MCP format"""
        tool = self.get_tool(tool_name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.input_schema,
            "version": tool.version,
            "category": tool.category
        }
    
    def export_tools_json(self) -> str:
        """Export all tools as JSON (for documentation/integration)"""
        tools_list = self.list_tools()
        return json.dumps(tools_list, indent=2)


# Global registry instance
_global_registry = None

def get_registry() -> MCPToolRegistry:
    """Get the global tool registry instance"""
    global _global_registry
    if _global_registry is None:
        _global_registry = MCPToolRegistry()
    return _global_registry

