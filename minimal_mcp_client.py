#!/usr/bin/env python3
"""
Minimal MCP Client for Hello World Tool
Connects to an MCP server running in Docker via stdio and calls the hello-world tool.
"""

import json
import subprocess
import sys
import uuid
from typing import Dict, Any, Optional

class MCPClient:
    def __init__(self, docker_command: str):
        """
        Initialize MCP client with Docker command to run the MCP server.
        
        Args:
            docker_command: Command to run the MCP server (e.g., "docker run -i mcp-video-downloader").
        """
        self.docker_command = docker_command
        self.process = None
        self.request_id_counter = 0
    
    def _get_next_id(self) -> str:
        """Generate unique request ID."""
        self.request_id_counter += 1
        return str(self.request_id_counter)
    
    def _send_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send JSON-RPC request to MCP server."""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Send request
        request_line = json.dumps(request) + "\n"
        self.process.stdin.write(request_line.encode())
        self.process.stdin.flush()
        
        # Read response
        response_line = self.process.stdout.readline().decode().strip()
        if not response_line:
            raise Exception("No response from MCP server")
        
        try:
            response = json.loads(response_line)
        except json.JSONDecodeError as e:
            raise Exception(f"Invalid JSON response: {response_line}") from e
        
        if "error" in response:
            raise Exception(f"MCP server error: {response['error']}")
        
        return response
    
    def connect(self):
        """Start the MCP server process and initialize connection."""
        print(f"Starting MCP server: {self.docker_command}")
        
        # Start the Docker container with stdio
        self.process = subprocess.Popen(
            self.docker_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False  # We'll handle encoding ourselves
        )
        
        # Initialize the MCP connection
        print("Initializing MCP connection...")
        
        # Send initialize request
        init_response = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "minimal-mcp-client",
                "version": "1.0.0"
            }
        })
        
        print(f"Server capabilities: {init_response.get('result', {}).get('capabilities', {})}")
        
        # Send initialized notification
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        initialized_line = json.dumps(initialized_request) + "\n"
        self.process.stdin.write(initialized_line.encode())
        self.process.stdin.flush()
        
        print("MCP connection established!")
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools from the MCP server."""
        print("Listing available tools...")
        response = self._send_request("tools/list")
        return response.get("result", {})
    
    def call_tool(self, tool_name: str, arguments: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Call a specific tool on the MCP server."""
        print(f"Calling tool '{tool_name}' with arguments: {arguments}")
        
        params = {"name": tool_name}
        if arguments:
            params["arguments"] = arguments
        
        response = self._send_request("tools/call", params)
        return response.get("result", {})
    
    def disconnect(self):
        """Close the connection to the MCP server."""
        if self.process:
            print("Disconnecting from MCP server...")
            self.process.stdin.close()
            self.process.stdout.close()
            self.process.terminate()
            self.process.wait()
            print("Disconnected.")

def main():
    """Main function to demonstrate MCP client usage."""
    # Docker command to run the hello-world MCP server
    # Adjust this command based on your actual Docker setup
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    
    client = MCPClient(docker_cmd)
    
    try:
        # Connect to the MCP server
        client.connect()
        
        # List available tools
        tools = client.list_tools()
        print(f"\nAvailable tools: {json.dumps(tools, indent=2)}")
        
        # Call the hello-world tool
        print("\n" + "="*50)
        print("Calling hello-world tool...")
        print("="*50)
        
        # Try calling with different argument formats
        # Some MCP servers expect arguments in different ways
        try:
            # Try with a simple greeting argument
            result = client.call_tool("hello-world", {"greeting": "Hi there!"})
            print(f"Result: {json.dumps(result, indent=2)}")
        except Exception as e:
            print(f"First attempt failed: {e}")
            
            # Try alternative argument formats
            try:
                result = client.call_tool("hello-world", {"message": "Hi there!"})
                print(f"Result: {json.dumps(result, indent=2)}")
            except Exception as e2:
                print(f"Second attempt failed: {e2}")
                
                # Try with no arguments
                try:
                    result = client.call_tool("hello-world")
                    print(f"Result: {json.dumps(result, indent=2)}")
                except Exception as e3:
                    print(f"All attempts failed. Last error: {e3}")
        
    except Exception as e:
        print(f"Error: {e}")
        
        # Show stderr for debugging
        if client.process and client.process.stderr:
            stderr_output = client.process.stderr.read().decode()
            if stderr_output:
                print(f"Server stderr: {stderr_output}")
    
    finally:
        # Always disconnect
        client.disconnect()

if __name__ == "__main__":
    print("Minimal MCP Client - Hello World Demo")
    print("=====================================")
    main()