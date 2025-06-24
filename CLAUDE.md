# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Shotgun Terminal is a CLI tool that generates comprehensive project context for LLM workflows. It supports multiple prompt types (dev, architect, bug), file selection, automatic translation from Portuguese to English, and integration with both OpenAI-compatible APIs and Gemini AI for automated processing.

## Core Architecture

The codebase follows a modular Python architecture with clear separation of concerns:

- **CLI Entry Point**: `shotgun_terminal/cli.py` - Main command interface and workflow orchestration
- **Context Generation**: `shotgun_terminal/context_generator.py` - Generates project context with file size limits and binary file handling
- **File Selection**: `shotgun_terminal/file_selector.py` - Interactive file tree navigation with ignore patterns
- **Translation Service**: `shotgun_terminal/translator.py` - OpenAI-compatible API integration for Portuguese→English translation
- **Gemini Integration**: `shotgun_terminal/gemini_service.py` - Google Gemini AI processing capabilities
- **Prompt Templates**: `shotgun_terminal/prompts.py` - Three specialized prompt templates (dev/architect/bug modes)
- **Configuration**: `shotgun_terminal/config.py` + `shotgun_terminal/settings.py` - API configuration and XDG-compliant settings storage

## Common Development Commands 

### Installation and Setup
```bash
# Development installation
pip install -e .

# Reinstall after changes (Windows)
./reinstall.bat

# Reinstall after changes (Unix/Linux)
pipx uninstall shotgun-terminal && pipx install -e .
```

### Running the Application
```bash
# Basic usage
shotgun-terminal

# With specific directory and prompt type
shotgun-terminal -d /path/to/project -p dev

# Configure APIs (translation, Gemini)
shotgun-terminal --config

# Quick setup with test credentials
shotgun-terminal --quick-setup
```

### Testing
```bash
# No specific test framework detected - check for test files first
find . -name "*test*" -type f
```

## Key Design Patterns

### Workflow Pipeline
The application follows a 7-step workflow:
1. Directory selection (with memory of last used)
2. Task description collection (multiline with "END" termination)
3. Custom rules collection (optional)
4. Translation processing (if enabled and configured)
5. Interactive file selection with ignore patterns
6. Prompt type selection (dev/architect/bug)
7. Context generation and optional Gemini processing

### File Processing Strategy
- **Size Limits**: 1MB per file, 10MB total to prevent memory issues
- **Binary Detection**: Null byte detection with fallback to encoding attempts
- **Format Support**: Claude XML format (`<file path="">content</file>`) and default format
- **Encoding Handling**: Multiple encoding attempts (utf-8, latin-1, cp1252, iso-8859-1)

### Translation Architecture
- **Smart Detection**: Heuristic-based Portuguese language detection using patterns and common words
- **Force Override**: Option to bypass language detection
- **API Compatibility**: OpenAI-compatible endpoint support with configurable base URLs and models
- **Fallback Strategy**: Uses original text if translation fails

### Prompt Template System
Three specialized templates with strict output format constraints:
- **Dev Mode**: Outputs git diff format for precise code changes
- **Architect Mode**: Outputs structured Markdown planning documents
- **Bug Mode**: Outputs detailed Markdown analysis reports with execution path tracing

## Configuration Management

### Settings Storage
- **Location**: `~/.config/shotgun-code/settings.json` (XDG-compliant)
- **Structure**: Nested JSON with `apiSettings` and service-specific configurations
- **API Keys**: Supports both OpenAI-compatible APIs and Gemini AI

### Key Configuration Areas
- Translation API settings (base_url, api_key, model, enable_translation)
- Gemini API settings (api_key, enable_gemini, temperature, thinking_budget)
- Directory preferences (last_used_directory)

## Important Implementation Notes

### File Safety
- All file operations include encoding detection and error handling
- Binary files are detected and summarized rather than processed as text
- Large files are automatically skipped with user notification

### UI/UX Design
- Rich terminal interface with color coding and progress indicators
- Interactive file tree navigation using inquirer
- Clear separation between configuration and processing phases
- Comprehensive error messages and fallback behaviors

### API Integration Patterns
- Lazy initialization of API clients with connection testing
- Graceful degradation when APIs are unavailable
- Temperature and model configuration support
- Proper error handling and user feedback

## Dependencies

Core dependencies as defined in requirements.txt and setup.py:
- `click>=8.0.0` - CLI framework
- `rich>=10.0.0` - Rich terminal UI
- `inquirer>=2.8.0` - Interactive prompts
- `openai>=1.0.0` - Translation API client
- `requests>=2.25.0` - HTTP client
- `google-genai>=1.0.0` - Gemini AI integration