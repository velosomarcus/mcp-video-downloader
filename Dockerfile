# Use a Python image with uv pre-installed
FROM ghcr.io/astral-sh/uv:python3.13-bookworm-slim AS uv

# Install the project into `/app`
WORKDIR /app

# Enable bytecode compilation
ENV UV_COMPILE_BYTECODE=1

# Copy from the cache instead of linking since it's a mounted volume
ENV UV_LINK_MODE=copy

# Install the project's dependencies using the lockfile and settings
RUN --mount=type=cache,target=/root/.cache/uv \
    --mount=type=bind,source=uv.lock,target=uv.lock \
    --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
    uv sync --frozen --no-install-project --no-dev --no-editable

# Then, add the rest of the project source code and install it
# Installing separately from its dependencies allows optimal layer caching
ADD . /app
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-editable

FROM python:3.13-slim-bookworm

WORKDIR /app

COPY --from=uv /root/.local /root/.local
COPY --from=uv /app/.venv /app/.venv

# Place executables in the environment at the front of the path
ENV PATH="/app/.venv/bin:$PATH"

# Create downloads directory for video files (to be mounted as volume)
RUN mkdir -p /downloads && chmod 755 /downloads

# Set environment variables to suppress output and ensure proper JSON communication
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Create wrapper script for JSON-safe execution
RUN echo '#!/bin/bash\n# Wrapper script to ensure clean JSON output for MCP protocol\n# Redirect any potential stderr output to /dev/null to prevent JSON contamination\nexec python -m mcp_video_downloader 2>/dev/null' > /usr/local/bin/mcp_wrapper.sh && \
    chmod +x /usr/local/bin/mcp_wrapper.sh

# Create a selector script that can run either mode
RUN echo '#!/bin/bash\n# MCP Video Downloader Entry Point\n# Usage: docker run ... [--safe-mode]\nif [ "$1" = "--safe-mode" ]; then\n    exec /usr/local/bin/mcp_wrapper.sh\nelse\n    exec python -m mcp_video_downloader "$@"\nfi' > /usr/local/bin/mcp_entrypoint.sh && \
    chmod +x /usr/local/bin/mcp_entrypoint.sh

# Default entry point (direct execution)
# For Claude IDE compatibility issues, use: docker run ... --safe-mode
ENTRYPOINT ["/usr/local/bin/mcp_entrypoint.sh"]
