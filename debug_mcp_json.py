#!/usr/bin/env python3
"""
Debug tool for MCP Video Downloader JSON issues.
This script helps diagnose problems with Claude IDE integration.
"""

import json
import subprocess
import sys
import tempfile
import time
from pathlib import Path

class MCPDebugger:
    """Debug tool for MCP JSON communication issues."""
    
    def __init__(self):
        self.test_url = "https://youtu.be/dQw4w9WgXcQ"  # Rick Roll for testing
    
    def test_mcp_server_directly(self, command_args):
        """Test MCP server directly to check for JSON issues."""
        print("🔍 Testing MCP server directly...")
        print(f"Command: {' '.join(command_args)}")
        
        try:
            # Start the MCP server process
            process = subprocess.Popen(
                command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False  # Handle encoding ourselves
            )
            
            # Send MCP initialize request
            init_request = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "debug-client", "version": "1.0.0"}
                }
            }
            
            request_line = json.dumps(init_request) + "\n"
            process.stdin.write(request_line.encode())
            process.stdin.flush()
            
            # Read response
            response_line = process.stdout.readline().decode().strip()
            print(f"Init response: {response_line[:200]}...")
            
            try:
                response = json.loads(response_line)
                print("✅ Initialize response is valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ Initialize response is not valid JSON: {e}")
                print(f"Raw response: {response_line}")
                return False
            
            # Send initialized notification
            initialized_request = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            request_line = json.dumps(initialized_request) + "\n"
            process.stdin.write(request_line.encode())
            process.stdin.flush()
            
            # Test tool listing
            tools_request = {
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/list"
            }
            
            request_line = json.dumps(tools_request) + "\n"
            process.stdin.write(request_line.encode())
            process.stdin.flush()
            
            response_line = process.stdout.readline().decode().strip()
            print(f"Tools response: {response_line[:200]}...")
            
            try:
                response = json.loads(response_line)
                print("✅ Tools list response is valid JSON")
            except json.JSONDecodeError as e:
                print(f"❌ Tools list response is not valid JSON: {e}")
                print(f"Raw response: {response_line}")
                return False
            
            # Clean up
            process.terminate()
            process.wait()
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing MCP server: {e}")
            return False
    
    def test_download_request(self, command_args):
        """Test a video download request to see where JSON breaks."""
        print("🎬 Testing video download request...")
        
        try:
            # Start the MCP server process
            process = subprocess.Popen(
                command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=False
            )
            
            # Initialize
            init_request = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "debug-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write((json.dumps(init_request) + "\n").encode())
            process.stdin.flush()
            process.stdout.readline()  # Skip init response
            
            # Send initialized notification
            initialized_request = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            process.stdin.write((json.dumps(initialized_request) + "\n").encode())
            process.stdin.flush()
            
            # Test download request
            download_request = {
                "jsonrpc": "2.0",
                "id": "3",
                "method": "tools/call",
                "params": {
                    "name": "download_video",
                    "arguments": {
                        "url": self.test_url,
                        "quality": "360p",  # Use small quality for testing
                        "audio_only": True  # Audio only to reduce download size
                    }
                }
            }
            
            print(f"Sending download request for: {self.test_url}")
            request_line = json.dumps(download_request) + "\n"
            process.stdin.write(request_line.encode())
            process.stdin.flush()
            
            # Read response and check for JSON validity
            print("Waiting for download response...")
            
            # Set a timeout for the download
            start_time = time.time()
            timeout = 60  # 60 seconds timeout
            
            response_data = b""
            while time.time() - start_time < timeout:
                try:
                    # Read with a short timeout
                    import select
                    ready, _, _ = select.select([process.stdout], [], [], 1)
                    if ready:
                        chunk = process.stdout.read1(1024)
                        if not chunk:
                            break
                        response_data += chunk
                        
                        # Try to find complete JSON lines
                        lines = response_data.decode('utf-8', errors='ignore').split('\n')
                        for line in lines[:-1]:  # All but the last (potentially incomplete) line
                            line = line.strip()
                            if line:
                                print(f"Received line: {line[:100]}...")
                                try:
                                    json.loads(line)
                                    print("✅ Line is valid JSON")
                                except json.JSONDecodeError as e:
                                    print(f"❌ Line is not valid JSON: {e}")
                                    print(f"Problematic line: {line}")
                                    return False
                        
                        # Keep the last potentially incomplete line
                        response_data = lines[-1].encode('utf-8')
                        
                except Exception as e:
                    print(f"Error reading response: {e}")
                    break
            
            # Clean up
            process.terminate()
            process.wait()
            
            return True
            
        except Exception as e:
            print(f"❌ Error testing download: {e}")
            return False
    
    def capture_stderr_output(self, command_args):
        """Capture stderr to see if yt-dlp is outputting to stderr."""
        print("📡 Capturing stderr output...")
        
        try:
            process = subprocess.Popen(
                command_args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Send a simple request and see what comes out of stderr
            init_request = {
                "jsonrpc": "2.0",
                "id": "1",
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "debug-client", "version": "1.0.0"}
                }
            }
            
            process.stdin.write(json.dumps(init_request) + "\n")
            process.stdin.close()
            
            # Wait a bit and capture stderr
            time.sleep(2)
            
            stdout_data, stderr_data = process.communicate(timeout=10)
            
            if stderr_data:
                print(f"❌ Found stderr output: {stderr_data}")
                return False
            else:
                print("✅ No stderr output detected")
                return True
                
        except subprocess.TimeoutExpired:
            print("⚠️  Process timed out")
            process.kill()
            return False
        except Exception as e:
            print(f"❌ Error capturing stderr: {e}")
            return False

def main():
    """Main debug function."""
    print("🐛 MCP Video Downloader JSON Debug Tool")
    print("=" * 50)
    
    debugger = MCPDebugger()
    
    # Test different command configurations
    test_commands = [
        {
            "name": "Docker Command",
            "args": ["docker", "run", "-i", "--rm", "mcp-video-downloader"]
        },
        {
            "name": "Python Module",
            "args": ["python", "-m", "mcp_video_downloader"]
        }
    ]
    
    for test in test_commands:
        print(f"\n🧪 Testing: {test['name']}")
        print("-" * 40)
        
        # Check if command is available
        try:
            result = subprocess.run([test["args"][0], "--version"], 
                                  capture_output=True, timeout=5)
            if result.returncode != 0:
                print(f"❌ {test['args'][0]} not available, skipping")
                continue
        except:
            print(f"❌ {test['args'][0]} not available, skipping")
            continue
        
        print(f"✅ {test['args'][0]} is available")
        
        # Test MCP protocol basics
        if debugger.test_mcp_server_directly(test["args"]):
            print("✅ Basic MCP protocol works")
            
            # Test stderr capture
            if debugger.capture_stderr_output(test["args"]):
                print("✅ No unwanted stderr output")
                
                # Test download (only if basics work)
                debugger.test_download_request(test["args"])
            else:
                print("❌ Found unwanted stderr output")
        else:
            print("❌ Basic MCP protocol failed")

if __name__ == "__main__":
    main()
