# MCP Video Downloader Testing Makefile

.PHONY: help build test test-quick test-comprehensive clean setup

# Default target
help:
	@echo "🧪 MCP Video Downloader Test Commands"
	@echo "====================================="
	@echo ""
	@echo "Available commands:"
	@echo "  make build              - Build the Docker image"
	@echo "  make test               - Run quick test suite"
	@echo "  make test-comprehensive - Run comprehensive test suite"
	@echo "  make test-manual        - Run manual MCP client test"
	@echo "  make test-url URL=...   - Test specific video URL"
	@echo "  make setup              - Run setup verification"
	@echo "  make clean              - Clean test artifacts"
	@echo "  make shell              - Open shell in container"
	@echo ""

# Build the Docker image
build:
	@echo "🔨 Building Docker image..."
	docker build -t mcp-video-downloader .

# Quick test - just verify the container works
test: build
	@echo "🚀 Running quick test suite..."
	./test-setup.sh

# Comprehensive test suite
test-comprehensive: build
	@echo "📺 Running comprehensive video download tests..."
	python3 test_video_download.py

# Manual MCP client test
test-manual: build
	@echo "🔌 Running manual MCP client test..."
	python3 minimal_mcp_client.py

# Test specific URL
test-url: build
	@if [ -z "$(URL)" ]; then \
		echo "❌ Please provide a URL: make test-url URL=https://example.com/video.mp4"; \
		exit 1; \
	fi
	@echo "🎯 Testing URL: $(URL)"
	python3 test_video_download.py --url "$(URL)"

# Setup verification
setup:
	@echo "⚙️  Verifying setup..."
	./test-setup.sh

# Clean test artifacts
clean:
	@echo "🧹 Cleaning test artifacts..."
	rm -rf test-downloads/
	docker system prune -f --filter "label=test=mcp-video-downloader" 2>/dev/null || true

# Open shell in container for debugging
shell: build
	@echo "🐚 Opening shell in container..."
	docker run -it --rm \
		-v $(PWD)/test-downloads:/downloads \
		mcp-video-downloader \
		/bin/bash

# Docker Compose tests
compose-test:
	@echo "🐳 Running Docker Compose tests..."
	docker-compose -f docker-compose.test.yml build
	docker-compose -f docker-compose.test.yml run --rm test-runner

# All tests
test-all: test test-comprehensive test-manual
	@echo "🎉 All tests completed!"
