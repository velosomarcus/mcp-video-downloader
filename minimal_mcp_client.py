#!/usr/bin/env python3
"""
Minimal MCP Client for Video Downloader Tool
Connects to an MCP server running in Docker via stdio and calls the download_video tool.
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
    # Docker command to run the video downloader MCP server
    # Mount current directory's test-downloads for testing
    import os
    test_downloads = os.path.join(os.getcwd(), "test-downloads")
    os.makedirs(test_downloads, exist_ok=True)
    
    docker_cmd = f"docker run -i --rm -v {test_downloads}:/downloads mcp-video-downloader --safe-mode"
    
    client = MCPClient(docker_cmd)
    
    try:
        # Connect to the MCP server
        client.connect()
        
        # List available tools
        tools = client.list_tools()
        print(f"\nAvailable tools: {json.dumps(tools, indent=2)}")
        
        # Call the download_video tool with a test video
        print("\n" + "="*50)
        print("Testing video download...")
        print("="*50)
        
        # Test with a short video from the Internet Archive (public domain)
        test_url = "https://archive.org/download/BigBuckBunny_124/Content/big_buck_bunny_720p_surround.mp4"
        
        try:
            # Call download_video tool
            result = client.call_tool("download_video", {
                "url": test_url,
                "quality": "worst",  # Use worst quality for faster testing
                "output_format": "mp4"
            })
            print(f"Download result: {json.dumps(result, indent=2)}")
            
            # Check if file was downloaded
            import glob
            downloaded_files = glob.glob(f"{test_downloads}/*")
            if downloaded_files:
                print(f"\n✅ Files downloaded successfully:")
                for file in downloaded_files:
                    print(f"   - {file}")
            else:
                print(f"\n⚠️  No files found in {test_downloads}")
                
        except Exception as e:
            print(f"Download test failed: {e}")
            
            # Try with a simpler test - just list tools again
            try:
                print("\nFalling back to tools list test...")
                tools_result = client.list_tools()
                print(f"✅ Tools list successful: {len(tools_result.get('tools', []))} tools available")
            except Exception as e2:
                print(f"❌ Even tools list failed: {e2}")
        
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
    print("Minimal MCP Client - Video Downloader Test")
    print("==========================================")
    main()