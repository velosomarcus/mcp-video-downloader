#!/usr/bin/env python3
"""
MCP Client for Streaming Video Downloader Server
Connects to the MCP video downloader server and handles streaming file downloads.
The server now streams file content as base64-encoded data instead of using Docker volumes.
"""

import base64
import json
import subprocess
import sys
import uuid
from pathlib import Path
from typing import Dict, Any, Optional
import re

class MCPStreamingVideoClient:
    def __init__(self, server_command: str, local_downloads_dir: Optional[str] = None):
        """
        Initialize MCP client for streaming video downloader.
        
        Args:
            server_command: Command to run the MCP server (e.g., "python -m mcp_video_downloader")
            local_downloads_dir: Local directory where downloads should be saved (defaults to ~/Downloads/mcp-videos)
        """
        self.server_command = server_command
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
        print(f"🚀 Starting MCP Streaming Video Downloader Server: {self.server_command}")
        print(f"📁 Downloads will be saved to: {self.local_downloads_dir}")
        
        # Start the server process with stdio
        self.process = subprocess.Popen(
            self.server_command.split(),
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
                "name": "streaming-video-downloader-mcp-client",
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
    
    def _extract_file_data_from_response(self, response_text: str) -> Optional[Dict[str, Any]]:
        """
        Extract base64 file data and metadata from server response.
        
        Args:
            response_text: The text response from the server
            
        Returns:
            Dictionary with file_data, filename, mime_type, and size if found, None otherwise
        """
        # Look for file data markers
        file_data_match = re.search(r'FILE_DATA_START\n(.*?)\nFILE_DATA_END', response_text, re.DOTALL)
        if not file_data_match:
            return None
            
        file_data = file_data_match.group(1).strip()
        
        # Extract metadata
        filename_match = re.search(r'FILENAME: (.+)', response_text)
        mime_type_match = re.search(r'MIME_TYPE: (.+)', response_text)
        size_match = re.search(r'SIZE: (\d+)', response_text)
        
        return {
            'file_data': file_data,
            'filename': filename_match.group(1) if filename_match else 'downloaded_file',
            'mime_type': mime_type_match.group(1) if mime_type_match else 'application/octet-stream',
            'size': int(size_match.group(1)) if size_match else 0
        }
    
    def _save_file_from_base64(self, file_data: str, filename: str) -> Path:
        """
        Decode base64 data and save to local file.
        
        Args:
            file_data: Base64 encoded file content
            filename: Name of the file to save
            
        Returns:
            Path to the saved file
        """
        try:
            # Decode base64 data
            decoded_data = base64.b64decode(file_data)
            
            # Save to local file
            file_path = self.local_downloads_dir / filename
            
            # Handle filename conflicts
            counter = 1
            original_path = file_path
            while file_path.exists():
                stem = original_path.stem
                suffix = original_path.suffix
                file_path = self.local_downloads_dir / f"{stem}_{counter}{suffix}"
                counter += 1
            
            with open(file_path, 'wb') as f:
                f.write(decoded_data)
            
            return file_path
            
        except Exception as e:
            raise Exception(f"Failed to decode and save file: {str(e)}")
    
    def download_video(self, 
                      url: str, 
                      quality: str = "720p",
                      audio_only: bool = False) -> Dict[str, Any]:
        """Download a video using the download_video tool and save it locally."""
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
        result = response.get("result", {})
        
        # Extract response text
        response_text = ""
        if "content" in result:
            for content in result["content"]:
                if content.get("type") == "text":
                    response_text = content.get("text", "")
                    break
        
        # Try to extract and save file data
        file_info = self._extract_file_data_from_response(response_text)
        local_file_path = None
        
        if file_info:
            try:
                print("💾 Saving streamed file locally...")
                local_file_path = self._save_file_from_base64(
                    file_info['file_data'], 
                    file_info['filename']
                )
                print(f"✅ File saved to: {local_file_path}")
                
                # Add local file info to result for client use
                result["local_file_path"] = str(local_file_path)
                result["local_file_size"] = local_file_path.stat().st_size
                
                # Remove the base64 data from response text for cleaner output
                clean_response = re.sub(r'📦 File Data \(Base64\):.*?📝 Metadata:', 
                                      '📦 File Streaming: ✅ Complete\n\n📝 Local File:', 
                                      response_text, flags=re.DOTALL)
                clean_response = re.sub(r'FILENAME: .*?\nMIME_TYPE: .*?\nSIZE: \d+', 
                                      f'Path: {local_file_path}\nSize: {file_info["size"]} bytes', 
                                      clean_response)
                
                # Update the result content
                if "content" in result:
                    for content in result["content"]:
                        if content.get("type") == "text":
                            content["text"] = clean_response
                
            except Exception as e:
                print(f"❌ Failed to save file locally: {str(e)}")
                result["file_save_error"] = str(e)
        else:
            print("⚠️  No file data found in server response")
        
        return result
    
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
    """Main function to demonstrate the streaming video client."""
    if len(sys.argv) < 2:
        print("Usage: python streaming_video_client.py <server_command> [video_url]")
        print("Example: python streaming_video_client.py 'python -m mcp_video_downloader' 'https://youtu.be/dQw4w9WgXcQ'")
        sys.exit(1)
    
    server_command = sys.argv[1]
    test_url = sys.argv[2] if len(sys.argv) > 2 else "https://youtu.be/dQw4w9WgXcQ"
    
    # Create and use the client
    client = MCPStreamingVideoClient(server_command)
    
    try:
        # Connect to server
        client.connect()
        
        # List available tools
        print_divider("Available Tools")
        tools = client.list_tools()
        print_result(tools)
        
        # Test video download
        print_divider("Video Download Test")
        result = client.download_video(test_url, quality="720p", audio_only=False)
        print_result(result)
        
        # Test audio-only download
        print_divider("Audio-Only Download Test")
        result = client.download_video(test_url, quality="best", audio_only=True)
        print_result(result)
        
        print_divider("Downloads Directory")
        print(f"📁 Your files are saved in: {client.get_downloads_directory()}")
        
    except KeyboardInterrupt:
        print("\n🛑 Interrupted by user")
    except Exception as e:
        print(f"❌ Error: {str(e)}")
    finally:
        client.disconnect()

if __name__ == "__main__":
    main()
