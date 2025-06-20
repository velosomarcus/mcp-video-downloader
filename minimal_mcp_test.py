#!/usr/bin/env python3
"""
Minimal MCP server test - just echo functionality to test JSON protocol.
"""

import asyncio
import json
import sys
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool

async def serve_minimal():
    """Minimal MCP server for testing JSON protocol."""
    server = Server("test-mcp-server")

    @server.list_tools()
    async def list_tools():
        return [
            Tool(
                name="echo",
                description="Simple echo tool for testing",
                inputSchema={
                    "type": "object",
                    "properties": {
                        "message": {
                            "type": "string",
                            "description": "Message to echo back"
                        }
                    },
                    "required": ["message"]
                }
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict):
        if name == "echo":
            message = arguments.get("message", "No message provided")
            return [TextContent(type="text", text=f"Echo: {message}")]
        else:
            return [TextContent(type="text", text=f"Unknown tool: {name}")]

    options = server.create_initialization_options()
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, options, raise_exceptions=True)

if __name__ == "__main__":
    asyncio.run(serve_minimal())
