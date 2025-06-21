#!/usr/bin/env python3
"""
Comprehensive Test Client for MCP Video Downloader
Tests all functionality of the video downloader MCP server.
"""

import json
import subprocess
import sys
import os
import time
import glob
from typing import Dict, Any, Optional
from pathlib import Path

class VideoDownloadTester:
    def __init__(self, test_downloads_dir: str = "test-downloads"):
        """
        Initialize the video download tester.
        
        Args:
            test_downloads_dir: Directory for test downloads
        """
        self.test_dir = Path(test_downloads_dir)
        self.test_dir.mkdir(exist_ok=True)
        self.docker_cmd = f"docker run -i --rm -v {self.test_dir.absolute()}:/downloads mcp-video-downloader --safe-mode"
        self.request_id_counter = 0
    
    def _get_next_id(self) -> str:
        """Generate unique request ID."""
        self.request_id_counter += 1
        return str(self.request_id_counter)
    
    def _send_mcp_request(self, method: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Send a single MCP request and get response."""
        request = {
            "jsonrpc": "2.0",
            "id": self._get_next_id(),
            "method": method
        }
        
        if params:
            request["params"] = params
        
        # Prepare the full request sequence
        requests = []
        
        # Always start with initialize if this is the first request
        if method != "initialize":
            init_request = {
                "jsonrpc": "2.0",
                "id": self._get_next_id(),
                "method": "initialize",
                "params": {
                    "protocolVersion": "2024-11-05",
                    "capabilities": {"tools": {}},
                    "clientInfo": {"name": "video-test-client", "version": "1.0.0"}
                }
            }
            requests.append(json.dumps(init_request))
            
            # Send initialized notification
            initialized = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            requests.append(json.dumps(initialized))
        
        requests.append(json.dumps(request))
        
        # Send all requests
        input_data = "\n".join(requests) + "\n"
        
        try:
            process = subprocess.run(
                self.docker_cmd.split(),
                input=input_data,
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if process.returncode != 0:
                raise Exception(f"Docker process failed: {process.stderr}")
            
            # Parse the last JSON response (our actual response)
            responses = [line.strip() for line in process.stdout.split('\n') if line.strip()]
            if not responses:
                raise Exception("No response from MCP server")
            
            # Find our response (matching our request ID)
            target_id = request["id"]
            for response_line in responses:
                try:
                    response = json.loads(response_line)
                    if response.get("id") == target_id:
                        return response
                except json.JSONDecodeError:
                    continue
            
            # If we didn't find our response, return the last valid response
            for response_line in reversed(responses):
                try:
                    return json.loads(response_line)
                except json.JSONDecodeError:
                    continue
            
            raise Exception("No valid JSON response found")
            
        except subprocess.TimeoutExpired:
            raise Exception("Request timed out")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def test_server_startup(self) -> bool:
        """Test that the MCP server starts up properly."""
        print("🚀 Testing server startup...")
        try:
            response = self._send_mcp_request("initialize", {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "startup-test", "version": "1.0.0"}
            })
            
            if "result" in response:
                print("✅ Server startup successful")
                print(f"   Server capabilities: {response['result'].get('capabilities', {})}")
                return True
            else:
                print(f"❌ Server startup failed: {response}")
                return False
        except Exception as e:
            print(f"❌ Server startup failed: {e}")
            return False
    
    def test_list_tools(self) -> bool:
        """Test listing available tools."""
        print("🔧 Testing tools list...")
        try:
            response = self._send_mcp_request("tools/list")
            
            if "result" in response and "tools" in response["result"]:
                tools = response["result"]["tools"]
                print(f"✅ Tools list successful: {len(tools)} tools found")
                for tool in tools:
                    print(f"   • {tool.get('name', 'Unknown')}: {tool.get('description', 'No description')}")
                return True
            else:
                print(f"❌ Tools list failed: {response}")
                return False
        except Exception as e:
            print(f"❌ Tools list failed: {e}")
            return False
    
    def test_video_download(self, url: str, description: str) -> bool:
        """Test downloading a specific video."""
        print(f"📺 Testing video download: {description}")
        print(f"   URL: {url}")
        
        # Clear test directory
        for file in self.test_dir.glob("*"):
            if file.is_file():
                file.unlink()
        
        try:
            response = self._send_mcp_request("tools/call", {
                "name": "download_video",
                "arguments": {
                    "url": url,
                    "quality": "worst",  # Use worst quality for faster testing
                    "output_format": "mp4"
                }
            })
            
            if "result" in response:
                print(f"✅ Download request successful")
                print(f"   Response: {response['result']}")
                
                # Check if files were actually downloaded
                downloaded_files = list(self.test_dir.glob("*"))
                if downloaded_files:
                    print(f"✅ {len(downloaded_files)} file(s) downloaded:")
                    for file in downloaded_files:
                        size = file.stat().st_size
                        print(f"   • {file.name} ({size} bytes)")
                    return True
                else:
                    print("⚠️  Download succeeded but no files found")
                    return False
            else:
                print(f"❌ Download failed: {response}")
                return False
                
        except Exception as e:
            print(f"❌ Download failed: {e}")
            return False
    
    def run_all_tests(self):
        """Run all tests and provide a summary."""
        print("🧪 MCP Video Downloader Comprehensive Test Suite")
        print("=" * 50)
        
        tests_passed = 0
        total_tests = 0
        
        # Test 1: Server startup
        total_tests += 1
        if self.test_server_startup():
            tests_passed += 1
        print()
        
        # Test 2: List tools
        total_tests += 1
        if self.test_list_tools():
            tests_passed += 1
        print()
        
        # Test 3: Video download tests
        test_videos = [
            # Short test video from Internet Archive (public domain)
            ("https://archive.org/download/SampleVideo1280x7205mb/SampleVideo_1280x720_5mb.mp4", 
             "Sample video (5MB, public domain)"),
        ]
        
        for url, description in test_videos:
            total_tests += 1
            if self.test_video_download(url, description):
                tests_passed += 1
            print()
        
        # Summary
        print("=" * 50)
        print(f"📊 Test Summary: {tests_passed}/{total_tests} tests passed")
        
        if tests_passed == total_tests:
            print("🎉 All tests passed! Your MCP video downloader is working correctly.")
            return True
        else:
            print(f"⚠️  {total_tests - tests_passed} test(s) failed. Check the output above for details.")
            return False

def main():
    """Main function to run the test suite."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Test MCP Video Downloader")
    parser.add_argument("--test-dir", default="test-downloads", 
                       help="Directory for test downloads (default: test-downloads)")
    parser.add_argument("--url", help="Test a specific URL")
    args = parser.parse_args()
    
    tester = VideoDownloadTester(args.test_dir)
    
    if args.url:
        # Test specific URL
        print(f"🎯 Testing specific URL: {args.url}")
        success = tester.test_video_download(args.url, "User-provided URL")
        sys.exit(0 if success else 1)
    else:
        # Run full test suite
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()
