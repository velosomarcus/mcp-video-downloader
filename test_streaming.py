#!/usr/bin/env python3
"""
Test script for the streaming video downloader.
This script runs basic tests to ensure the streaming functionality works correctly.
"""

import tempfile
import json
import base64
from pathlib import Path
import sys
import os

# Add the src directory to path so we can import the server module
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_base64_encoding():
    """Test base64 encoding/decoding functionality."""
    print("🧪 Testing base64 encoding/decoding...")
    
    try:
        from mcp_video_downloader.server import encode_file_to_base64
        
        # Create a test file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as f:
            test_content = "Hello, this is a test file for streaming!"
            f.write(test_content)
            test_file_path = f.name
        
        # Encode the file
        encoded_data = encode_file_to_base64(test_file_path)
        print(f"   ✅ Encoded file to base64 ({len(encoded_data)} characters)")
        
        # Decode and verify
        decoded_data = base64.b64decode(encoded_data).decode('utf-8')
        assert decoded_data == test_content, "Decoded content doesn't match original"
        print("   ✅ Decoded content matches original")
        
        # Clean up
        os.unlink(test_file_path)
        print("   ✅ Base64 encoding/decoding test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Base64 test failed: {e}")
        return False

def test_mime_type_detection():
    """Test MIME type detection."""
    print("🧪 Testing MIME type detection...")
    
    try:
        from mcp_video_downloader.server import get_mime_type
        
        test_cases = [
            ('/path/to/video.mp4', 'video/mp4'),
            ('/path/to/audio.mp3', 'audio/mpeg'),
            ('/path/to/video.webm', 'video/webm'),
            ('/path/to/unknown.xyz', 'application/octet-stream'),
        ]
        
        for file_path, expected_mime in test_cases:
            actual_mime = get_mime_type(file_path)
            assert actual_mime == expected_mime, f"Expected {expected_mime}, got {actual_mime}"
            print(f"   ✅ {file_path} -> {actual_mime}")
        
        print("   ✅ MIME type detection test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ MIME type test failed: {e}")
        return False

def test_server_imports():
    """Test that all required server modules can be imported."""
    print("🧪 Testing server imports...")
    
    try:
        from mcp_video_downloader.server import (
            encode_file_to_base64,
            get_mime_type,
            get_file_extension,
            VideoDownloadError,
            ProgressLogger
        )
        print("   ✅ All server functions imported successfully")
        return True
        
    except ImportError as e:
        print(f"   ❌ Import test failed: {e}")
        print("   💡 Note: Some imports may fail if MCP dependencies aren't installed")
        print("       This is expected in development/testing environments")
        return False

def test_client_response_parsing():
    """Test client response parsing functionality."""
    print("🧪 Testing client response parsing...")
    
    try:
        from streaming_video_client import MCPStreamingVideoClient
        
        # Create a mock client
        client = MCPStreamingVideoClient("dummy_command")
        
        # Test response with file data
        mock_response = """
✅ Video downloaded successfully!

📹 Title: Test Video
👤 Uploader: Test Channel

📦 File Data (Base64):
FILE_DATA_START
SGVsbG8gV29ybGQ=
FILE_DATA_END

📝 Metadata:
FILENAME: test_video.mp4
MIME_TYPE: video/mp4
SIZE: 1024
"""
        
        # Extract file info
        file_info = client._extract_file_data_from_response(mock_response)
        
        assert file_info is not None, "Failed to extract file info"
        assert file_info['filename'] == 'test_video.mp4', "Incorrect filename"
        assert file_info['mime_type'] == 'video/mp4', "Incorrect MIME type"
        assert file_info['size'] == 1024, "Incorrect file size"
        assert file_info['file_data'] == 'SGVsbG8gV29ybGQ=', "Incorrect file data"
        
        print("   ✅ Response parsing test passed!")
        return True
        
    except Exception as e:
        print(f"   ❌ Response parsing test failed: {e}")
        return False

def test_file_saving():
    """Test file saving functionality."""
    print("🧪 Testing file saving...")
    
    try:
        from streaming_video_client import MCPStreamingVideoClient
        
        # Create a temporary directory for testing
        with tempfile.TemporaryDirectory() as temp_dir:
            client = MCPStreamingVideoClient("dummy_command", temp_dir)
            
            # Test data (base64 encoded "Hello World")
            test_data = "SGVsbG8gV29ybGQ="
            test_filename = "test_file.txt"
            
            # Save the file
            saved_path = client._save_file_from_base64(test_data, test_filename)
            
            # Verify file was saved
            assert saved_path.exists(), "File was not saved"
            
            # Verify content
            with open(saved_path, 'r') as f:
                content = f.read()
                assert content == "Hello World", "File content is incorrect"
            
            print(f"   ✅ File saved successfully to {saved_path}")
            print("   ✅ File saving test passed!")
            return True
            
    except Exception as e:
        print(f"   ❌ File saving test failed: {e}")
        return False

def main():
    """Run all tests."""
    print("🚀 Starting MCP Video Downloader Streaming Tests")
    print("=" * 60)
    
    tests = [
        ("Server Imports", test_server_imports),
        ("Base64 Encoding", test_base64_encoding),
        ("MIME Type Detection", test_mime_type_detection),
        ("Client Response Parsing", test_client_response_parsing),
        ("File Saving", test_file_saving),
    ]
    
    passed = 0
    total = len(tests)
    
    for name, test_func in tests:
        print(f"\n📝 {name}")
        print("-" * 40)
        
        if test_func():
            passed += 1
        else:
            print(f"   ⚠️  {name} test failed")
    
    print("\n" + "=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Streaming functionality is working correctly.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    exit(main())
