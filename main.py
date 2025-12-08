import os
import random
import json
from fastmcp import FastMCP

mcp = FastMCP("Simple Calculator Server")

# Tool to add two numbers
@mcp.tool
def add(a: int, b: int) -> int:
    """Add two numbers together.
    
    Args:
        a (int): The first number.
        b (int): The second number.
        
    Returns:
        int: The sum of a and b.
    """
    return a + b

# Tool: generate a random number
@mcp.tool
def random_number(min_value: int = 1, max_value: int = 100) -> int:
    """Generate a random number between min_value and max_value.
    
    Args:
        min_value (int): The minimum value (inclusive).
        max_value (int): The maximum value (inclusive).
    
    Returns:
        int: A random integer between min_value and max_value.
    """
    return random.randint(min_value, max_value)

# Resource: Server Information
@mcp.resource("info://server")
def server_info() -> str:
    """Get information about the server.
    
    Returns:
        str: A string containing server information.
    """

    info = {
        "name": "Simple Calculator Server",
        "version": "1.0.0",
        "description": "A basic MCP server with math tools.",
        "tools": ["add", "random_number"],
        "author": "Ankit Thummar"
    }
    return json.dumps(info, indent=2)

# Start the server
if __name__ == "__main__":
    mcp.run(transport="http", host="0.0.0.0", port=8000)