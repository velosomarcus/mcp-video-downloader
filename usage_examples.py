#!/usr/bin/env python3
"""
Usage Examples for MCP Video Downloader Client

This script demonstrates various ways to use the MCP Video Downloader client
with different scenarios and configurations.
"""

import sys
import os
from pathlib import Path

# Add the current directory to the path so we can import our client
sys.path.insert(0, str(Path(__file__).parent))

from video_downloader_client import MCPVideoDownloaderClient, print_divider, print_result

def example_basic_usage():
    """Example 1: Basic usage with default settings."""
    print_divider("Example 1: Basic Usage")
    
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        client.connect()
        
        # List available tools
        tools = client.list_tools()
        print("🔸 Available Tools:")
        for tool in tools.get("tools", []):
            print(f"   • {tool.get('name')}: {tool.get('description', 'No description')[:100]}...")
        
    except Exception as e:
        print(f"❌ Example 1 failed: {e}")
    finally:
        client.disconnect()

def example_video_download():
    """Example 2: Video download with custom settings."""
    print_divider("Example 2: Video Download")
    
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        client.connect()
        
        # Example short video for testing (replace with your preferred test video)
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        print(f"🔸 Downloading video: {test_url}")
        result = client.download_video(
            url=test_url,
            quality="360p",  # Lower quality for faster testing
            audio_only=False
        )
        
        print("🔸 Download Result:")
        print_result(result)
        
    except Exception as e:
        print(f"❌ Example 2 failed: {e}")
    finally:
        client.disconnect()

def example_audio_extraction():
    """Example 3: Audio-only extraction."""
    print_divider("Example 3: Audio Extraction")
    
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        client.connect()
        
        # Example music video for audio extraction
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        print(f"🔸 Extracting audio from: {test_url}")
        result = client.download_video(
            url=test_url,
            audio_only=True
        )
        
        print("🔸 Audio Extraction Result:")
        print_result(result)
        
    except Exception as e:
        print(f"❌ Example 3 failed: {e}")
    finally:
        client.disconnect()

def example_custom_output_path():
    """Example 4: Custom output path."""
    print_divider("Example 4: Custom Output Path")
    
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        client.connect()
        
        # Create a custom output directory (inside the container)
        custom_path = "/tmp/my_downloads"
        test_url = "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
        
        print(f"🔸 Downloading to custom path: {custom_path}")
        result = client.download_video(
            url=test_url,
            output_path=custom_path,
            quality="480p"
        )
        
        print("🔸 Custom Path Download Result:")
        print_result(result)
        
    except Exception as e:
        print(f"❌ Example 4 failed: {e}")
    finally:
        client.disconnect()

def example_error_handling():
    """Example 4: Error handling scenarios."""
    print_divider("Example 4: Error Handling")
    
    docker_cmd = "docker run -i --rm mcp-video-downloader"
    client = MCPVideoDownloaderClient(docker_cmd)
    
    try:
        client.connect()
        
        # Test with invalid URL
        print("🔸 Testing with invalid URL...")
        try:
            result = client.download_video(url="not-a-valid-url")
            print_result(result)
        except Exception as e:
            print(f"   Expected error: {e}")
        
        # Test with empty URL
        print("\n🔸 Testing with empty URL...")
        try:
            result = client.download_video(url="")
            print_result(result)
        except Exception as e:
            print(f"   Expected error: {e}")
        
        # Test with non-existent video
        print("\n🔸 Testing with non-existent video...")
        try:
            result = client.download_video(url="https://www.youtube.com/watch?v=nonexistent123")
            print_result(result)
        except Exception as e:
            print(f"   Expected error: {e}")
        
    except Exception as e:
        print(f"❌ Example 4 failed: {e}")
    finally:
        client.disconnect()

def run_examples():
    """Run all examples."""
    examples = [
        ("Basic Usage", example_basic_usage),
        ("Video Download", example_video_download),
        ("Audio Extraction", example_audio_extraction),
        ("Custom Output Path", example_custom_output_path),
        ("Error Handling", example_error_handling),
    ]
    
    print("🚀 MCP Video Downloader - Usage Examples")
    print("=" * 60)
    print("⚠️  Note: These examples require the Docker image to be built:")
    print("   docker build -t mcp-video-downloader .")
    print("\n📋 Available Examples:")
    
    for i, (name, _) in enumerate(examples, 1):
        print(f"   {i}. {name}")
    
    print("\n" + "=" * 60)
    
    # Ask user which example to run
    while True:
        try:
            choice = input(f"\nEnter example number (1-{len(examples)}) or 'all' to run all: ").strip().lower()
            
            if choice == 'all':
                for name, example_func in examples:
                    print(f"\n🔄 Running: {name}")
                    try:
                        example_func()
                    except KeyboardInterrupt:
                        print("\n⏹️  Interrupted by user")
                        break
                    except Exception as e:
                        print(f"❌ Example failed: {e}")
                break
            
            elif choice.isdigit():
                choice_num = int(choice)
                if 1 <= choice_num <= len(examples):
                    name, example_func = examples[choice_num - 1]
                    print(f"\n🔄 Running: {name}")
                    example_func()
                    break
                else:
                    print(f"❌ Please enter a number between 1 and {len(examples)}")
            
            elif choice in ['q', 'quit', 'exit']:
                print("👋 Goodbye!")
                break
            
            else:
                print("❌ Invalid choice. Please try again.")
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

if __name__ == "__main__":
    run_examples()
