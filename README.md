# Global MCP Server

A modular MCP (Model Context Protocol) server that provides:

- KV cache compression using FreqKV and LoCoCo algorithms
- Smart prompt routing based on complexity classification
- Integration with GitHub Copilot Agent Mode
- Support for Jira, GitHub, and filesystem MCP configurations

## Architecture

- **FreqKV Service**: Frequency-domain compression using DCT
- **LoCoCo Service**: Convolution-based KV fusion
- **Routing Service**: Prompt complexity classification and model routing
- **Model Registry**: Pluggable LLM endpoint management

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python -m mcp.server
```

## Configuration

The server uses `.vscode/mcp.json` for MCP tool configurations including Jira, GitHub, and filesystem integrations.
