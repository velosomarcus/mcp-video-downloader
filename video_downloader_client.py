#!/usr/bin/env python3
"""
MCP Client for Video Downloader Server
Connects to the MCP video downloader server running in Docker via stdio and tests the video downloading functionality.
"""

import json
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional

class MCPVideoDownloaderClient:
    def __init__(self, docker_command: str, local_downloads_dir: Optional[str] = None):
        """
        Initialize MCP client with Docker command to run the video downloader server.
        
        Args:
            docker_command: Command to run the MCP server (e.g., "docker run -i mcp-video-downloader")
            local_downloads_dir: Local directory where downloads should be saved (defaults to ~/Downloads/mcp-videos)
        """
        self.docker_command = docker_command
        self.process = None
        self.request_id_counter = 0
        
        # Set up local downloads directory
        if local_downloads_dir is None:
            home_dir = Path.home()
            self.local_downloads_dir = home_dir / "Downloads" / "mcp-videos"
        else:
            self.local_downloads_dir = Path(local_downloads_dir)
        
        # Create the directory if it doesn't exist
        self.local_downloads_dir.mkdir(parents=True, exist_ok=True)
        self.container_downloads_dir = "/downloads"
    
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
        print(f"🚀 Starting MCP Video Downloader Server: {self.docker_command}")
        print(f"📁 Downloads will be saved to: {self.local_downloads_dir}")
        
        # Modify Docker command to include volume mount
        docker_parts = self.docker_command.split()
        
        # Find the position to insert volume mount (after "docker run")
        run_index = -1
        for i, part in enumerate(docker_parts):
            if part == "run":
                run_index = i
                break
        
        if run_index != -1:
            # Insert volume mount after "docker run"
            volume_mount = f"-v{self.local_downloads_dir}:{self.container_downloads_dir}"
            docker_parts.insert(run_index + 1, volume_mount)
            modified_command = " ".join(docker_parts)
            print(f"🔧 Modified Docker command: {modified_command}")
        else:
            modified_command = self.docker_command
            print("⚠️  Warning: Could not modify Docker command to add volume mount")
        
        # Start the Docker container with stdio
        self.process = subprocess.Popen(
            modified_command.split(),
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False  # We'll handle encoding ourselves
        )
        
        # Initialize the MCP connection
        print("🔌 Initializing MCP connection...")
        
        # Send initialize request
        init_response = self._send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {}
            },
            "clientInfo": {
                "name": "video-downloader-mcp-client",
                "version": "1.0.0"
            }
        })
        
        print(f"✅ Server capabilities: {init_response.get('result', {}).get('capabilities', {})}")
        
        # Send initialized notification
        initialized_request = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        initialized_line = json.dumps(initialized_request) + "\n"
        self.process.stdin.write(initialized_line.encode())
        self.process.stdin.flush()
        
        print("🎉 MCP connection established!")
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools from the MCP server."""
        print("🛠️  Listing available tools...")
        response = self._send_request("tools/list")
        return response.get("result", {})
    
    def download_video(self, 
                      url: str, 
                      quality: str = "720p",
                      audio_only: bool = False) -> Dict[str, Any]:
        """Download a video using the download_video tool."""
        print(f"📹 Downloading video from: {url}")
        print(f"   Quality: {quality}, Audio only: {audio_only}")
        
        arguments = {
            "url": url,
            "quality": quality,
            "audio_only": audio_only
        }
        
        params = {
            "name": "download_video",
            "arguments": arguments
        }
        
        response = self._send_request("tools/call", params)
        return response.get("result", {})
    
    def get_downloads_directory(self) -> str:
        """Get the local downloads directory path."""
        return str(self.local_downloads_dir)
    
    def disconnect(self):
        """Close the connection to the MCP server."""
        if self.process:
            print("🔌 Disconnecting from MCP server...")
            self.process.stdin.close()
            self.process.stdout.close()
            self.process.terminate()
            self.process.wait()
            print("✅ Disconnected.")

def print_divider(title: str):
    """Print a formatted divider with title."""
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

def print_result(result: Dict[str, Any]):
    """Pretty print the tool result."""
    if "content" in result:
        for content in result["content"]:
            if content.get("type") == "text":
                print("📋 Result:")
                print(content.get("text", "No text content"))
    else:
        print("📋 Raw result:")
        print(json.dumps(result, indent=2))

def main():
    """Main function to demonstrate video downloader MCP client usage."""
    
    # Docker command to run the video downloader MCP server
    # This should match your actual Docker image name
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        print_divider("MCP Video Downloader Client - Demo")
        print(f"📁 Local downloads directory: {client.get_downloads_directory()}")
        
        # Connect to the MCP server
        client.connect()
        
        # List available tools
        print_divider("Available Tools")
        tools = client.list_tools()
        print("🛠️  Available tools:")
        for tool in tools.get("tools", []):
            print(f"   • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
        
        # Test video download with a sample video
        print_divider("Testing Video Download Tool")
        
        # You can replace this with any video URL you want to test
        # This is a short, free video for testing purposes
        test_urls = [
            # Example short video URLs for testing
            "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll (classic test video)
            # Add more test URLs here if desired
        ]
        
        for test_url in test_urls:
            print(f"\n🎬 Testing with URL: {test_url}")
            
            try:
                # Test with default settings (720p, video download)
                download_result = client.download_video(
                    url=test_url,
                    quality="360p",  # Use lower quality for faster testing
                    audio_only=False
                )
                print_result(download_result)
                
                print("\n" + "-" * 40)
                
                # Test audio-only download
                print("🎵 Testing audio-only download...")
                audio_result = client.download_video(
                    url=test_url,
                    quality="best",  # Quality doesn't matter for audio-only
                    audio_only=True
                )
                print_result(audio_result)
                
            except Exception as e:
                print(f"❌ Video download test failed: {e}")
                print("💡 This might be due to network issues, invalid URL, or missing dependencies.")
        
        print_divider("Test Summary")
        print("✅ MCP Video Downloader client testing completed!")
        print(f"📁 Downloaded files can be found in: {client.get_downloads_directory()}")
        print("💡 If downloads failed, check:")
        print("   • Network connectivity")
        print("   • Video URL validity")
        print("   • yt-dlp dependencies in Docker container")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        
        # Show stderr for debugging
        if client.process and client.process.stderr:
            stderr_output = client.process.stderr.read().decode()
            if stderr_output:
                print(f"🐛 Server stderr output:")
                print(stderr_output)
    
    finally:
        # Always disconnect
        client.disconnect()

def interactive_mode():
    """Interactive mode for testing custom URLs."""
    print_divider("Interactive Video Downloader")
    
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        print(f"📁 Downloads will be saved to: {client.get_downloads_directory()}")
        client.connect()
        
        while True:
            print("\n" + "-" * 40)
            print("🎬 Interactive Video Downloader")
            print("Commands:")
            print("  1. Download video")
            print("  2. Download audio only")
            print("  3. List tools")
            print("  4. Show downloads directory")
            print("  q. Quit")
            
            choice = input("\nEnter your choice: ").strip().lower()
            
            if choice == 'q':
                break
            elif choice == '1':
                url = input("Enter video URL: ").strip()
                quality = input("Enter quality (best/720p/480p/360p) [720p]: ").strip() or "720p"
                try:
                    result = client.download_video(url, quality=quality, audio_only=False)
                    print_result(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == '2':
                url = input("Enter video URL: ").strip()
                try:
                    result = client.download_video(url, audio_only=True)
                    print_result(result)
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == '3':
                try:
                    tools = client.list_tools()
                    print("🛠️  Available tools:")
                    for tool in tools.get("tools", []):
                        print(f"   • {tool.get('name', 'Unknown')}")
                        print(f"     {tool.get('description', 'No description')}")
                except Exception as e:
                    print(f"❌ Error: {e}")
            
            elif choice == '4':
                print(f"📁 Downloads directory: {client.get_downloads_directory()}")
                print(f"🔍 Use 'open {client.get_downloads_directory()}' to view in Finder")
            
            else:
                print("❌ Invalid choice. Please try again.")
    
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        client.disconnect()

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        main()
