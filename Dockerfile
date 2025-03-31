FROM python:3.11-slim

# Install the package directly from PyPI
RUN pip install --no-cache-dir mcp-think-tool

# Find where the executable is installed
RUN which mcp-think-tool

# Set the MCP think tool as the entrypoint
ENTRYPOINT ["mcp-think-tool"]