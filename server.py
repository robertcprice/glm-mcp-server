#!/usr/bin/env python3
"""
GLM-4.7 MCP Server for Claude Code

A Model Context Protocol server that routes tasks to Z.ai's GLM-4.7 model,
providing significant cost savings while maintaining high-quality output.

Author: GLM MCP Server Contributors
Version: 2.0.0
License: MIT
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

from mcp.server.fastmcp import FastMCP

# =============================================================================
# Configuration
# =============================================================================

__version__ = "2.0.0"
ZAI_BASE_URL = "https://api.z.ai/api/anthropic"
SERVER_NAME = "glm-agent"
SERVER_DESCRIPTION = "GLM-4.7 MCP Server - Cost-efficient AI agent delegation"

# Model mappings
MODEL_MAP = {
    "haiku": "glm-4.5-air",   # Fast, lightweight
    "sonnet": "glm-4.7",      # Balanced quality/speed
    "opus": "glm-4.7",        # Highest quality
}

# Cost comparison (approximate, per million tokens)
COST_COMPARISON = {
    "claude_opus": 15.0,
    "glm_47": 2.0,
    "savings": "87%"
}


# =============================================================================
# Environment Setup
# =============================================================================

def load_env() -> None:
    """Load environment variables from .env file."""
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    key, value = line.split("=", 1)
                    value = value.strip().strip('"').strip("'")
                    if key and value:
                        os.environ.setdefault(key, value)


load_env()


# =============================================================================
# MCP Server Initialization
# =============================================================================

mcp = FastMCP(
    name=SERVER_NAME,
    instructions=f"""
You are GLM-4.7, a cost-efficient AI model accessed through the MCP server.
You provide the same quality as Claude at approximately 1/7th the cost.

Available models:
- haiku (glm-4.5-air): Fast, lightweight tasks
- sonnet (glm-4.7): Balanced quality and speed
- opus (glm-4.7): Highest quality output

When users ask for quick tasks, use haiku. For complex tasks, use sonnet/opus.
"""
)


# =============================================================================
# Utility Functions
# =============================================================================

def get_api_key() -> str:
    """Get Z.ai API key from environment."""
    return os.environ.get("ZAI_API_KEY", "")


def get_glm_env() -> dict:
    """Get environment variables for GLM-backed Claude Code."""
    api_key = get_api_key()
    if not api_key:
        raise ValueError("ZAI_API_KEY not configured")

    env = os.environ.copy()
    env["ANTHROPIC_AUTH_TOKEN"] = api_key
    env["ANTHROPIC_BASE_URL"] = ZAI_BASE_URL
    env["API_TIMEOUT_MS"] = "300000"
    env["ANTHROPIC_DEFAULT_HAIKU_MODEL"] = MODEL_MAP["haiku"]
    env["ANTHROPIC_DEFAULT_SONNET_MODEL"] = MODEL_MAP["sonnet"]
    env["ANTHROPIC_DEFAULT_OPUS_MODEL"] = MODEL_MAP["opus"]
    return env


def check_prerequisites() -> tuple[bool, str]:
    """Check if all prerequisites are met."""
    if not get_api_key():
        return False, "ZAI_API_KEY not set"
    if not shutil.which("claude"):
        return False, "'claude' CLI not found in PATH"
    return True, "OK"


def run_glm_agent(
    prompt: str,
    cwd: Optional[str] = None,
    model: str = "sonnet",
    allowed_tools: Optional[str] = None,
    timeout: int = 300,
    skip_permissions: bool = True,
) -> str:
    """
    Run a GLM-backed Claude Code agent.

    Args:
        prompt: The prompt to send to the agent
        cwd: Working directory for the agent
        model: Model to use (haiku, sonnet, opus)
        allowed_tools: Comma-separated list of allowed tools
        timeout: Timeout in seconds
        skip_permissions: Skip permission prompts

    Returns:
        The agent's output
    """
    ok, msg = check_prerequisites()
    if not ok:
        return f"Error: {msg}"

    work_dir = cwd or os.getcwd()

    cmd = ["claude", "--print"]
    if skip_permissions:
        cmd.append("--dangerously-skip-permissions")
    cmd.extend(["--model", model])

    if allowed_tools:
        cmd.extend(["--allowedTools", allowed_tools])

    cmd.extend(["-p", prompt])

    try:
        result = subprocess.run(
            cmd,
            cwd=work_dir,
            env=get_glm_env(),
            capture_output=True,
            text=True,
            timeout=timeout,
        )

        output = result.stdout.strip()
        if result.stderr:
            stderr = result.stderr.strip()
            if stderr and "experimentalGitDiff" not in stderr:
                output += f"\n\n[stderr]: {stderr}"

        return output if output else "Agent completed with no output"

    except subprocess.TimeoutExpired:
        return f"Error: Agent timed out after {timeout // 60} minutes"
    except FileNotFoundError:
        return "Error: 'claude' command not found. Install Claude Code first."
    except Exception as e:
        return f"Error: {str(e)}"


# =============================================================================
# MCP Tools - Quick Tasks
# =============================================================================

@mcp.tool()
def glm_ask(
    question: str,
    model: str = "haiku",
) -> str:
    """
    Quick question to GLM - no tools, fast response.

    Use for: explanations, analysis, brainstorming, quick answers.
    Does NOT have access to files or tools - pure generation.

    Cost: ~10x cheaper than Claude Haiku. Use liberally.

    Args:
        question: Your question or prompt
        model: "haiku" (fastest) or "sonnet" (better quality)

    Returns:
        GLM's response
    """
    return run_glm_agent(
        prompt=question,
        model=model,
        allowed_tools="",
        timeout=120,
    )


@mcp.tool()
def glm_summarize(
    text: str,
    style: str = "concise",
    model: str = "haiku",
) -> str:
    """
    Summarize text using GLM.

    Use for: document summaries, meeting notes, code explanations.

    Args:
        text: The text to summarize
        style: "concise", "detailed", "bullet-points", "executive"
        model: "haiku" or "sonnet"

    Returns:
        Summarized text
    """
    style_prompts = {
        "concise": "Summarize this concisely in 2-3 sentences:",
        "detailed": "Provide a detailed summary:",
        "bullet-points": "Summarize as bullet points:",
        "executive": "Executive summary - key insights only:",
    }

    prompt = f"{style_prompts.get(style, style_prompts['concise'])}\n\n{text}"
    return run_glm_agent(prompt=prompt, model=model, allowed_tools="", timeout=120)


@mcp.tool()
def glm_explain(
    code_or_concept: str,
    context: str = "",
    model: str = "haiku",
) -> str:
    """
    Explain code or a concept using GLM.

    Use for: understanding code, learning concepts, documentation.

    Args:
        code_or_concept: Code snippet or concept to explain
        context: Additional context (e.g., language, framework)
        model: "haiku" or "sonnet"

    Returns:
        Explanation
    """
    prompt = f"Explain this{': ' + context if context else ''}:\n\n{code_or_concept}"
    return run_glm_agent(prompt=prompt, model=model, allowed_tools="", timeout=120)


# =============================================================================
# MCP Tools - Code Analysis
# =============================================================================

@mcp.tool()
def glm_analyze(
    task: str,
    working_directory: str = "",
    model: str = "sonnet",
) -> str:
    """
    Analyze codebase using GLM with read access.

    Use for: understanding code structure, finding patterns,
    architecture analysis, dependency mapping.

    Has READ-ONLY access: Read, Glob, Grep, LS, Bash (safe commands).

    Args:
        task: Analysis task to perform
        working_directory: Project directory (defaults to current)
        model: "haiku" or "sonnet"

    Returns:
        Analysis results
    """
    return run_glm_agent(
        prompt=task,
        cwd=working_directory or None,
        model=model,
        allowed_tools="Read,Glob,Grep,LS,Bash",
        timeout=300,
    )


@mcp.tool()
def glm_review(
    code_or_file: str,
    review_focus: str = "general",
    working_directory: str = "",
    model: str = "sonnet",
) -> str:
    """
    Code review by GLM agent.

    Use for: security review, performance analysis, best practices.

    Args:
        code_or_file: Inline code or file path to review
        review_focus: "general", "security", "performance", "style", "bugs"
        working_directory: Directory context for file paths
        model: "haiku" or "sonnet"

    Returns:
        Code review with findings and suggestions
    """
    focus_prompts = {
        "general": "Review this code for clarity, correctness, and best practices.",
        "security": "Security audit: find vulnerabilities, injection risks, auth issues.",
        "performance": "Performance review: find bottlenecks, inefficiencies.",
        "style": "Style review: naming, formatting, documentation.",
        "bugs": "Bug hunt: find logic errors, edge cases, potential crashes.",
        "refactor": "Refactoring suggestions: improve code structure.",
    }

    focus = focus_prompts.get(review_focus, focus_prompts["general"])

    # Check if it's a file path
    if "\n" not in code_or_file and len(code_or_file) < 200:
        prompt = f"{focus}\n\nFile to review: {code_or_file}\n\nRead the file and provide your review."
        return run_glm_agent(
            prompt=prompt,
            cwd=working_directory or None,
            model=model,
            allowed_tools="Read,Glob,Grep",
            timeout=300,
        )
    else:
        prompt = f"{focus}\n\nCode to review:\n```\n{code_or_file}\n```"
        return run_glm_agent(
            prompt=prompt,
            model=model,
            allowed_tools="",
            timeout=180,
        )


@mcp.tool()
def glm_find_bugs(
    code_or_file: str,
    working_directory: str = "",
    model: str = "sonnet",
) -> str:
    """
    Find potential bugs in code using GLM.

    Use for: bug detection, edge case analysis, error prone patterns.

    Args:
        code_or_file: Inline code or file path to analyze
        working_directory: Directory context for file paths
        model: "haiku" or "sonnet"

    Returns:
        List of potential bugs with explanations
    """
    return glm_review(
        code_or_file=code_or_file,
        review_focus="bugs",
        working_directory=working_directory,
        model=model,
    )


# =============================================================================
# MCP Tools - Implementation
# =============================================================================

@mcp.tool()
def glm_implement(
    task: str,
    working_directory: str,
    allowed_tools: str = "Read,Glob,Grep,Write,Edit,Bash",
    model: str = "sonnet",
) -> str:
    """
    GLM agent with write access for implementation tasks.

    Use for: writing code, creating files, making changes, refactoring.

    Has FULL access including Write and Edit.
    WARNING: This can modify files.

    Args:
        task: Implementation task to perform
        working_directory: Project directory (REQUIRED)
        allowed_tools: Tools to allow (default: full coding set)
        model: "haiku" or "sonnet"

    Returns:
        Agent's output including changes made
    """
    if not working_directory:
        return "Error: working_directory is required for implementation tasks"

    return run_glm_agent(
        prompt=task,
        cwd=working_directory,
        model=model,
        allowed_tools=allowed_tools,
        timeout=600,
    )


@mcp.tool()
def glm_refactor(
    file_path: str,
    instructions: str,
    working_directory: str,
    model: str = "sonnet",
) -> str:
    """
    Refactor code using GLM.

    Use for: improving code structure, applying patterns, cleanup.

    Args:
        file_path: Path to file to refactor
        instructions: Refactoring instructions
        working_directory: Project directory
        model: "haiku" or "sonnet"

    Returns:
        Refactored code and explanation
    """
    prompt = f"""Refactor the file at {file_path}.

Instructions: {instructions}

1. Read the file
2. Apply the refactoring
3. Explain the changes made
"""
    return run_glm_agent(
        prompt=prompt,
        cwd=working_directory,
        model=model,
        allowed_tools="Read,Write,Edit",
        timeout=600,
    )


@mcp.tool()
def glm_write_tests(
    file_path: str,
    test_framework: str = "pytest",
    working_directory: str = "",
    model: str = "sonnet",
) -> str:
    """
    Generate unit tests for a file using GLM.

    Use for: test generation, coverage improvement, TDD support.

    Args:
        file_path: Path to file to test
        test_framework: "pytest", "jest", "vitest", "unittest"
        working_directory: Project directory
        model: "haiku" or "sonnet"

    Returns:
        Generated test file
    """
    prompt = f"""Generate comprehensive unit tests for {file_path}.

Test framework: {test_framework}

1. Read the file
2. Generate tests covering:
   - Happy path cases
   - Edge cases
   - Error handling
3. Create the test file
"""
    return run_glm_agent(
        prompt=prompt,
        cwd=working_directory or None,
        model=model,
        allowed_tools="Read,Write,Edit,Glob,Grep",
        timeout=600,
    )


# =============================================================================
# MCP Tools - Documentation
# =============================================================================

@mcp.tool()
def glm_document(
    file_path: str,
    style: str = "google",
    working_directory: str = "",
    model: str = "haiku",
) -> str:
    """
    Add or update documentation for a file using GLM.

    Use for: adding docstrings, generating README, documenting APIs.

    Args:
        file_path: Path to file to document
        style: "google", "sphinx", "numpy", "javadoc"
        working_directory: Project directory
        model: "haiku" or "sonnet"

    Returns:
        File with added documentation
    """
    style_guide = {
        "google": "Google style docstrings",
        "sphinx": "Sphinx/reStructuredText style",
        "numpy": "NumPy style docstrings",
        "javadoc": "Javadoc style comments",
    }

    prompt = f"""Add documentation to {file_path}.

Documentation style: {style_guide.get(style, "standard")}

1. Read the file
2. Add appropriate docstrings to functions/classes
3. Add inline comments where needed
4. Update the file in place
"""
    return run_glm_agent(
        prompt=prompt,
        cwd=working_directory or None,
        model=model,
        allowed_tools="Read,Edit",
        timeout=300,
    )


@mcp.tool()
def glm_generate_readme(
    working_directory: str,
    style: str = "standard",
    model: str = "sonnet",
) -> str:
    """
    Generate a README.md for a project using GLM.

    Use for: creating project documentation, onboarding.

    Args:
        working_directory: Project directory
        style: "standard", "comprehensive", "minimal"
        model: "haiku" or "sonnet"

    Returns:
        Generated README.md content
    """
    style_instructions = {
        "standard": "Include: description, installation, usage, license",
        "comprehensive": "Include: badges, description, features, installation, usage, API docs, contributing, license",
        "minimal": "Brief description and quick start only",
    }

    prompt = f"""Generate a README.md for this project.

Style: {style_instructions.get(style, style_instructions["standard"])}

1. Explore the project structure
2. Read key files (package.json, setup.py, etc.)
3. Generate an appropriate README.md
4. Write the README.md file
"""
    return run_glm_agent(
        prompt=prompt,
        cwd=working_directory,
        model=model,
        allowed_tools="Read,Glob,Grep,LS,Write",
        timeout=600,
    )


# =============================================================================
# MCP Tools - Status & Info
# =============================================================================

@mcp.tool()
def glm_status() -> str:
    """
    Check GLM MCP server status and configuration.

    Returns:
        Status information about the GLM server setup
    """
    api_key = get_api_key()
    claude_installed = shutil.which("claude") is not None
    api_key_configured = bool(api_key)
    key_hint = f"{api_key[:4]}...{api_key[-4:]}" if api_key else "N/A"

    status_parts = [
        "╔════════════════════════════════════════════════════════════════════╗",
        "║                    GLM-4.7 MCP Server Status                        ║",
        "╚════════════════════════════════════════════════════════════════════╝",
        "",
        f"Version: {__version__}",
        f"Server Name: {SERVER_NAME}",
        "",
        "─── Configuration ───",
        f"API Key: {'✓ Configured (' + key_hint + ')' if api_key_configured else '✗ NOT SET'}",
        f"Claude CLI: {'✓ Found' if claude_installed else '✗ NOT FOUND'}",
        f"Base URL: {ZAI_BASE_URL}",
        "",
        "─── Model Mappings ───",
        f"  haiku  → {MODEL_MAP['haiku']} (fast, lightweight)",
        f"  sonnet → {MODEL_MAP['sonnet']} (balanced)",
        f"  opus   → {MODEL_MAP['opus']} (highest quality)",
        "",
        "─── Cost Savings ───",
        f"  Claude Opus: ${COST_COMPARISON['claude_opus']}/M tokens",
        f"  GLM-4.7:     ${COST_COMPARISON['glm_47']}/M tokens",
        f"  Savings:     {COST_COMPARISON['savings']}",
        "",
    ]

    if not api_key:
        status_parts.extend([
            "─── Setup Needed ───",
            "1. Get API key from https://z.ai/subscribe",
            "2. Set ZAI_API_KEY environment variable",
            "3. Or add to .env file in server directory",
            "",
        ])

    if not claude_installed:
        status_parts.extend([
            "─── Claude CLI Not Found ───",
            "Install from: https://claude.ai/download",
            "Or: npm install -g @anthropic-ai/claude-code",
            "",
        ])

    status_parts.extend([
        "─── Available Tools ───",
        "  glm_ask         - Quick questions (no tools)",
        "  glm_summarize   - Summarize text",
        "  glm_explain     - Explain code/concepts",
        "  glm_analyze     - Analyze codebase (read-only)",
        "  glm_review      - Code review",
        "  glm_find_bugs   - Find potential bugs",
        "  glm_implement   - Implementation tasks (write)",
        "  glm_refactor    - Refactor code",
        "  glm_write_tests - Generate unit tests",
        "  glm_document    - Add documentation",
        "  glm_generate_readme - Generate README.md",
        "  glm_status      - Show this status",
    ])

    return "\n".join(status_parts)


@mcp.tool()
def glm_compare_costs(
    tokens_input: int = 1000,
    tokens_output: int = 1000,
) -> str:
    """
    Compare costs between Claude and GLM.

    Args:
        tokens_input: Input tokens to compare
        tokens_output: Output tokens to compare

    Returns:
        Cost comparison table
    """
    claude_opus_input = 15.0  # per million
    claude_opus_output = 75.0
    glm_47_input = 2.0
    glm_47_output = 8.0

    claude_cost = (tokens_input / 1_000_000) * claude_opus_input + \
                  (tokens_output / 1_000_000) * claude_opus_output
    glm_cost = (tokens_input / 1_000_000) * glm_47_input + \
               (tokens_output / 1_000_000) * glm_47_output
    savings = claude_cost - glm_cost
    savings_pct = (savings / claude_cost * 100) if claude_cost > 0 else 0

    return f"""
╔════════════════════════════════════════════════════════════════════╗
║                      Cost Comparison                                 ║
╠════════════════════════════════════════════════════════════════════╣
║  Tokens: {tokens_input:,} input, {tokens_output:,} output                         ║
╠════════════════════════════════════════════════════════════════════╣
║  Claude Opus:  ${claude_cost:.4f}                                           ║
║  GLM-4.7:      ${glm_cost:.4f}                                           ║
║  Savings:      ${savings:.4f} ({savings_pct:.1f}%)                          ║
╚════════════════════════════════════════════════════════════════════╝
"""


# =============================================================================
# Main Entry Point
# =============================================================================

def main():
    """Run the MCP server."""
    mcp.run()


if __name__ == "__main__":
    main()
