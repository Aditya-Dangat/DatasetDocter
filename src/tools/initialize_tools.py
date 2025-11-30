"""
Initialize all MCP tools and register them

This module sets up the tool registry with all available tools
"""

from src.tools.mcp_registry import get_registry
from src.tools.data_tools import register_data_tools
from src.tools.validation_tools import register_validation_tools
from src.tools.file_tools import register_file_tools


def initialize_all_tools():
    """
    Initialize and register all MCP tools
    
    Returns:
        MCPToolRegistry instance with all tools registered
    """
    registry = get_registry()
    
    # Register tools from each category
    register_data_tools(registry)
    register_validation_tools(registry)
    register_file_tools(registry)
    
    return registry


# Auto-initialize on import
_initialized = False

def ensure_tools_initialized():
    """Ensure tools are initialized (lazy initialization)"""
    global _initialized
    if not _initialized:
        initialize_all_tools()
        _initialized = True

