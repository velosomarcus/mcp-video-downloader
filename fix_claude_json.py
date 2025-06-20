#!/usr/bin/env python3
"""
Fix and test script for Claude IDE JSON issues.
This script provides solutions for the "Unexpected token 'd', '[download]' is not valid JSON" error.
"""

import json
import subprocess
import tempfile
import time
from pathlib import Path

def create_fixed_claude_config():
    """Create a Claude Desktop configuration with proper error handling."""
    config = {
        "mcpServers": {
            "video-downloader-streaming": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "--env", "PYTHONUNBUFFERED=1",
                    "mcp-video-downloader"
                ],
                "env": {
                    "PYTHONUNBUFFERED": "1"
                }
            }
        }
    }
    
    with open("claude_desktop_config_fixed.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created fixed Claude Desktop configuration: claude_desktop_config_fixed.json")
    return config

def test_mcp_protocol():
    """Test the MCP protocol with the fixed container."""
    print("🧪 Testing MCP protocol...")
    
    try:
        # Test basic JSON communication
        cmd = ["docker", "run", "-i", "--rm", "--env", "PYTHONUNBUFFERED=1", "mcp-video-downloader"]
        
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=False
        )
        
        # Send initialize request
        init_request = {
            "jsonrpc": "2.0",
            "id": "1",
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {"tools": {}},
                "clientInfo": {"name": "test-client", "version": "1.0.0"}
            }
        }
        
        request_json = json.dumps(init_request) + "\n"
        process.stdin.write(request_json.encode())
        process.stdin.flush()
        
        # Read response
        response_line = process.stdout.readline().decode().strip()
        
        if not response_line:
            stderr_output = process.stderr.read().decode()
            print(f"❌ No response received. Stderr: {stderr_output}")
            return False
        
        try:
            response = json.loads(response_line)
            print("✅ MCP initialize response is valid JSON")
            
            # Send initialized notification
            initialized_request = {
                "jsonrpc": "2.0",
                "method": "notifications/initialized"
            }
            
            request_json = json.dumps(initialized_request) + "\n"
            process.stdin.write(request_json.encode())
            process.stdin.flush()
            
            # Test tools list
            tools_request = {
                "jsonrpc": "2.0",
                "id": "2",
                "method": "tools/list"
            }
            
            request_json = json.dumps(tools_request) + "\n"
            process.stdin.write(request_json.encode())
            process.stdin.flush()
            
            response_line = process.stdout.readline().decode().strip()
            response = json.loads(response_line)
            print("✅ Tools list response is valid JSON")
            
            process.terminate()
            return True
            
        except json.JSONDecodeError as e:
            print(f"❌ Response is not valid JSON: {e}")
            print(f"Raw response: {response_line}")
            
            # Check stderr for any leaked output
            stderr_output = process.stderr.read().decode()
            if stderr_output:
                print(f"Stderr output: {stderr_output}")
            
            process.terminate()
            return False
            
    except Exception as e:
        print(f"❌ Error testing MCP protocol: {e}")
        return False

def create_wrapper_script():
    """Create a wrapper script that ensures clean JSON output."""
    wrapper_content = '''#!/bin/bash
# Wrapper script to ensure clean JSON output for MCP protocol

# Redirect any potential stderr output to /dev/null to prevent JSON contamination
exec python -m mcp_video_downloader 2>/dev/null
'''
    
    with open("mcp_wrapper.sh", "w") as f:
        f.write(wrapper_content)
    
    # Make executable
    Path("mcp_wrapper.sh").chmod(0o755)
    print("✅ Created wrapper script: mcp_wrapper.sh")

def create_docker_wrapper():
    """Create a Docker image with the wrapper script."""
    dockerfile_content = '''FROM mcp-video-downloader

# Copy wrapper script
COPY mcp_wrapper.sh /usr/local/bin/mcp_wrapper.sh
RUN chmod +x /usr/local/bin/mcp_wrapper.sh

# Use wrapper as entrypoint
ENTRYPOINT ["/usr/local/bin/mcp_wrapper.sh"]
'''
    
    with open("Dockerfile.wrapper", "w") as f:
        f.write(dockerfile_content)
    
    print("✅ Created wrapper Dockerfile: Dockerfile.wrapper")
    
    # Build the wrapper image
    try:
        result = subprocess.run([
            "docker", "build", 
            "-f", "Dockerfile.wrapper",
            "-t", "mcp-video-downloader-wrapper",
            "."
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Built wrapper Docker image: mcp-video-downloader-wrapper")
            return True
        else:
            print(f"❌ Failed to build wrapper image: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error building wrapper image: {e}")
        return False

def create_claude_config_with_wrapper():
    """Create Claude config using the wrapper image."""
    config = {
        "mcpServers": {
            "video-downloader-wrapper": {
                "command": "docker",
                "args": [
                    "run", "-i", "--rm",
                    "mcp-video-downloader-wrapper"
                ]
            }
        }
    }
    
    with open("claude_desktop_config_wrapper.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print("✅ Created wrapper-based Claude Desktop configuration: claude_desktop_config_wrapper.json")
    return config

def main():
    """Main function to fix Claude IDE JSON issues."""
    print("🔧 MCP Video Downloader - Claude IDE JSON Fix")
    print("=" * 60)
    
    print("\n📋 Applying fixes for 'Unexpected token' JSON error...")
    
    # Step 1: Create basic fixed config
    create_fixed_claude_config()
    
    # Step 2: Test basic protocol
    if test_mcp_protocol():
        print("\n✅ Basic MCP protocol works! The issue might be during video downloads.")
    else:
        print("\n❌ Basic MCP protocol failed. Creating wrapper solution...")
        
        # Step 3: Create wrapper script
        create_wrapper_script()
        
        # Step 4: Create wrapper Docker image
        if create_docker_wrapper():
            # Step 5: Create config with wrapper
            create_claude_config_with_wrapper()
            
            print("\n🎯 Solution Summary:")
            print("1. Use the wrapper-based configuration: claude_desktop_config_wrapper.json")
            print("2. This configuration uses mcp-video-downloader-wrapper image")
            print("3. The wrapper suppresses any stderr output that could interfere with JSON")
    
    print("\n📝 Instructions for Claude IDE:")
    print("1. Copy the content from claude_desktop_config_fixed.json (or claude_desktop_config_wrapper.json)")
    print("2. Paste it into your Claude Desktop configuration file:")
    print("   • macOS: ~/Library/Application Support/Claude/claude_desktop_config.json")
    print("   • Windows: %APPDATA%\\Claude\\claude_desktop_config.json")
    print("   • Linux: ~/.config/claude/claude_desktop_config.json")
    print("3. Restart Claude Desktop")
    print("4. Test with: 'Download this video: https://youtu.be/dQw4w9WgXcQ'")

if __name__ == "__main__":
    main()
