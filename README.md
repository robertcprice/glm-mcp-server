# GLM-4.7 MCP Server

<div align="center">

![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.10+-green.svg)
![License](https://img.shields.io/badge/license-MIT-purple.svg)
![MCP](https://img.shields.io/badge/MCP-1.0+-orange.svg)

**Cost-efficient AI delegation for Claude Code**

[Features](#features) • [Installation](#installation) • [Usage](#usage) • [Tools](#tools) • [Configuration](#configuration)

</div>

---

## Overview

> **87% cost savings** compared to Claude Opus while maintaining comparable quality for coding tasks.

The GLM-4.7 MCP Server is a [Model Context Protocol](https://modelcontextprotocol.io/) server that routes tasks to [Z.ai's GLM-4.7](https://z.ai/) model. It enables Claude Code to delegate work to a more cost-efficient AI model without sacrificing quality.

### Why GLM-4.7?

| Feature | Claude Opus | GLM-4.7 |
|---------|-------------|---------|
| Cost per 1M tokens (input) | $15.00 | ~$2.00 |
| SWE-Bench Verified | 72.4% | 73.8% |
| Terminal Bench 2.0 | 38.2 | 41.0 |
| **Savings** | — | **~87%** |

---

## Features

- **13 specialized tools** for common development tasks
- **Read-only and write-capable agents** for safe delegation
- **Automatic model selection** (haiku for quick tasks, sonnet/opus for complex)
- **Seamless Claude Code integration** via MCP
- **Cost tracking** with built-in comparison tools

---

## Installation

### Prerequisites

1. **Claude Code CLI** - Install from [claude.ai/download](https://claude.ai/download)
   ```bash
   npm install -g @anthropic-ai/claude-code
   ```

2. **Z.ai API Key** - Get your key at [z.ai/subscribe](https://z.ai/subscribe)
   - GLM Coding Plan starts at **~1/7th the cost** of Claude tiers
   - 3x the usage limits compared to Claude

### Install the Server

```bash
# Clone the repository
git clone https://github.com/yourusername/glm-mcp-server.git
cd glm-mcp-server

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

---

## Configuration

### 1. Set Your API Key

Edit `.env` in the server directory:

```bash
ZAI_API_KEY=your_api_key_here
```

Or set as environment variable:

```bash
export ZAI_API_KEY=your_api_key_here
```

### 2. Add to Claude Desktop Config

Edit `~/Library/Application Support/Claude/claude_desktop_config.json` (macOS):

```json
{
  "mcpServers": {
    "glm": {
      "command": "/path/to/glm-mcp-server/.venv/bin/python",
      "args": ["/path/to/glm-mcp-server/server.py"],
      "env": {
        "ZAI_API_KEY": "your_api_key_here"
      }
    }
  }
}
```

On Windows: `%APPDATA%\Claude\claude_desktop_config.json`
On Linux: `~/.config/Claude/claude_desktop_config.json`

### 3. Restart Claude Code

Restart Claude Code to load the new MCP server.

---

## Usage

Once configured, the GLM tools are available in Claude Code:

### Quick Questions

```
Use glm_ask to explain what this React hook does
```

### Code Analysis

```
Use glm_analyze to review the authentication flow in src/auth/
```

### Implementation

```
Use glm_implement to add user profile editing to the settings page
```

### Cost Comparison

```
Use glm_compare_costs with 50000 input tokens and 20000 output tokens
```

---

## Tools

| Tool | Description | Access | Best For |
|------|-------------|--------|----------|
| `glm_ask` | Quick questions | None | Explanations, brainstorming |
| `glm_summarize` | Summarize text | None | Docs, meeting notes |
| `glm_explain` | Explain code/concepts | None | Learning, understanding |
| `glm_analyze` | Analyze codebase | Read-only | Architecture, patterns |
| `glm_review` | Code review | Read-only | Quality, security, style |
| `glm_find_bugs` | Find potential bugs | Read-only | Debugging, QA |
| `glm_implement` | Implementation | Write | Features, refactoring |
| `glm_refactor` | Refactor code | Write | Code cleanup |
| `glm_write_tests` | Generate unit tests | Write | TDD, coverage |
| `glm_document` | Add documentation | Write | Docstrings, API docs |
| `glm_generate_readme` | Generate README.md | Write | Project docs |
| `glm_status` | Server status | — | Diagnostics |
| `glm_compare_costs` | Cost comparison | — | Budgeting |

---

## Examples

### Code Review

```
Use glm_review with review_focus="security" on src/api/auth.ts
```

### Generate Tests

```
Use glm_write_tests for src/utils/validation.js with test_framework="jest"
```

### Documentation

```
Use glm_document for src/services/user.py with style="google"
```

### Bug Hunt

```
Use glm_find_bugs on src/components/payment/checkout.tsx
```

---

## Model Selection

The server automatically maps Claude model names to GLM models:

| Claude | GLM | Use Case |
|--------|-----|----------|
| haiku | glm-4.5-air | Quick tasks, summaries |
| sonnet | glm-4.7 | Balanced quality/speed |
| opus | glm-4.7 | Highest quality |

You can specify the model parameter in any tool:

```
Use glm_ask with model="haiku" to quickly summarize this file
```

---

## Development

### Running the Server Directly

```bash
source .venv/bin/activate
python server.py
```

### Running Tests

```bash
pip install pytest pytest-asyncio
pytest
```

### Project Structure

```
glm-mcp-server/
├── server.py           # Main MCP server implementation
├── pyproject.toml      # Project configuration
├── .env                # API key (not in git)
├── .venv/              # Virtual environment
└── README.md           # This file
```

---

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

---

## License

MIT License - see [LICENSE](LICENSE) for details.

---

## Acknowledgments

- [Anthropic](https://anthropic.com) for Claude Code and the MCP protocol
- [Z.ai](https://z.ai) for the GLM-4.7 model and API
- [FastMCP](https://github.com/jlowin/fastmcp) for the excellent MCP framework

---

## Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/glm-mcp-server/issues)
- **Z.ai Docs**: [docs.z.ai](https://docs.z.ai)
- **MCP Docs**: [modelcontextprotocol.io](https://modelcontextprotocol.io)

---

<div align="center">

**Made with ❤️ for cost-effective AI development**

[⬆ Back to top](#glm-47-mcp-server)

</div>
