#!/usr/bin/env python3
"""
Usage examples for the streaming MCP Video Downloader.
This script demonstrates how to use the streaming video client that receives
file data directly instead of using Docker volume mounts.
"""

import sys
from pathlib import Path
from streaming_video_client import MCPStreamingVideoClient, print_divider, print_result

def example_basic_usage():
    """Example: Basic video download with streaming."""
    print_divider("Basic Video Download (Streaming)")
    
    # Command to run the MCP server (no volume mount needed!)
    server_command = "python -m mcp_video_downloader"
    
    # Create client
    client = MCPStreamingVideoClient(server_command)
    
    try:
        # Connect to server
        client.connect()
        
        # Download a video (it will be streamed and saved locally)
        print("📹 Downloading video with streaming...")
        result = client.download_video(
            url="https://youtu.be/dQw4w9WgXcQ",  # Rick Roll for testing
            quality="720p",
            audio_only=False
        )
        
        print_result(result)
        
        # Show where files are saved
        print(f"\n📁 Files saved to: {client.get_downloads_directory()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

def example_audio_only():
    """Example: Audio-only download with streaming."""
    print_divider("Audio-Only Download (Streaming)")
    
    server_command = "python -m mcp_video_downloader"
    client = MCPStreamingVideoClient(server_command)
    
    try:
        client.connect()
        
        # Download audio only
        print("🎵 Downloading audio only with streaming...")
        result = client.download_video(
            url="https://youtu.be/dQw4w9WgXcQ",
            quality="best",
            audio_only=True
        )
        
        print_result(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

def example_custom_directory():
    """Example: Download to custom directory."""
    print_divider("Custom Directory Download")
    
    # Set custom downloads directory
    custom_dir = Path.home() / "Documents" / "StreamedVideos"
    server_command = "python -m mcp_video_downloader"
    
    client = MCPStreamingVideoClient(server_command, str(custom_dir))
    
    try:
        client.connect()
        
        print(f"📁 Using custom directory: {custom_dir}")
        
        result = client.download_video(
            url="https://youtu.be/dQw4w9WgXcQ",
            quality="480p"
        )
        
        print_result(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

def example_docker_usage():
    """Example: Using with Docker (no volume mount required)."""
    print_divider("Docker Usage (No Volume Mount)")
    
    # Note: No volume mount needed since files are streamed!
    docker_command = "docker run -i mcp-video-downloader"
    
    client = MCPStreamingVideoClient(docker_command)
    
    try:
        client.connect()
        
        print("🐳 Using Docker container (streaming mode)")
        print("   No volume mounts required!")
        
        result = client.download_video(
            url="https://youtu.be/dQw4w9WgXcQ",
            quality="360p"
        )
        
        print_result(result)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

def example_list_tools():
    """Example: List available tools."""
    print_divider("List Available Tools")
    
    server_command = "python -m mcp_video_downloader"
    client = MCPStreamingVideoClient(server_command)
    
    try:
        client.connect()
        
        # List tools
        tools = client.list_tools()
        print_result(tools)
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

def example_multiple_downloads():
    """Example: Download multiple videos in sequence."""
    print_divider("Multiple Downloads")
    
    server_command = "python -m mcp_video_downloader"
    client = MCPStreamingVideoClient(server_command)
    
    urls = [
        "https://youtu.be/dQw4w9WgXcQ",  # Rick Roll
        # Add more URLs as needed for testing
    ]
    
    try:
        client.connect()
        
        for i, url in enumerate(urls, 1):
            print(f"\n📹 Download {i}/{len(urls)}: {url}")
            result = client.download_video(url, quality="480p")
            
            # Show just the success status for brevity
            if "content" in result:
                for content in result["content"]:
                    if content.get("type") == "text":
                        text = content.get("text", "")
                        if "✅ Video downloaded successfully!" in text:
                            print("✅ Success!")
                        else:
                            print("❌ Failed")
                        break
        
        print(f"\n📁 All files saved to: {client.get_downloads_directory()}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        client.disconnect()

def main():
    """Main function to run examples."""
    print("🎬 MCP Video Downloader - Streaming Examples")
    print("=" * 50)
    print("These examples show how to use the streaming video downloader")
    print("that transfers files directly instead of using Docker volumes.")
    print()
    
    examples = {
        "1": ("Basic Video Download", example_basic_usage),
        "2": ("Audio-Only Download", example_audio_only),
        "3": ("Custom Directory", example_custom_directory),
        "4": ("Docker Usage (No Volume)", example_docker_usage),
        "5": ("List Tools", example_list_tools),
        "6": ("Multiple Downloads", example_multiple_downloads),
    }
    
    if len(sys.argv) > 1:
        # Run specific example
        choice = sys.argv[1]
        if choice in examples:
            name, func = examples[choice]
            print(f"Running example: {name}")
            func()
        else:
            print(f"Unknown example: {choice}")
            print("Available examples:", ", ".join(examples.keys()))
    else:
        # Show menu
        print("Available examples:")
        for key, (name, _) in examples.items():
            print(f"  {key}: {name}")
        print()
        print("Usage: python streaming_usage_examples.py <example_number>")
        print("Example: python streaming_usage_examples.py 1")

if __name__ == "__main__":
    main()
