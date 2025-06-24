# 🔫 Shotgun Terminal

Terminal version of Shotgun - Generate comprehensive project context for LLM workflows with automatic translation support and Google Gemini AI integration.

## 📋 Table of Contents

- [Features](#features)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Usage](#usage)
- [Prompt Types](#prompt-types)
- [Configuration](#configuration)
- [Translation](#translation)
- [Gemini Integration](#gemini-integration)
- [Advanced Usage](#advanced-usage)
- [Examples](#examples)
- [Development](#development)
- [Requirements](#requirements)

## ✨ Features

- **🎯 Interactive Workflow**: Step-by-step guidance through context generation
- **📁 Smart File Selection**: Interactive file tree with customizable ignore patterns
- **🌍 Automatic Translation**: Translate tasks and rules from Portuguese to English
- **📝 Multiline Input**: Easy "END" termination for tasks and custom rules
- **🎨 Rich Terminal Interface**: Beautiful, colorful terminal experience
- **⚡ Multiple Prompt Types**: Specialized templates for different use cases
- **📊 Project Tree Generation**: Visual project structure in output
- **🔧 Session-based Rules**: Custom rules without persistent storage
- **💾 Smart Settings**: XDG-compliant configuration storage
- **🤖 Gemini AI Integration**: Automated prompt processing with Google Gemini API
- **🚀 Minimal Dependencies**: Clean Python implementation with optional AI features

## 📦 Installation

### Using pipx (Recommended)
```bash
pipx install shotgun-terminal
```

### Using pip
```bash
pip install shotgun-terminal
```

### Development Installation
```bash
git clone <repository>
cd shotgun-terminal
pip install -e .
```

## 🚀 Quick Start

1. **Basic Usage**
   ```bash
   shotgun-terminal
   ```

2. **Quick Setup with Translation**
   ```bash
   shotgun-terminal --quick-setup
   ```

3. **Configure API for Translation**
   ```bash
   shotgun-terminal --config
   ```

## 📖 Usage

### Basic Workflow

The application guides you through an 8-step process:

1. **📂 Directory Selection**
   - Choose your project directory
   - Option to use current or last used directory

2. **📝 Task Description**
   - Describe what you want to achieve
   - Multiline input with "END" to finish
   ```
   > Implement user authentication system
   > with JWT tokens and password hashing
   > END
   ```

3. **⚙️ Custom Rules** (Optional)
   - Add specific guidelines for the AI
   - Session-based (not stored permanently)
   ```
   > Use TypeScript for all components
   > Follow SOLID principles
   > END
   ```

4. **🌍 Translation** (If configured)
   - Automatic translation to English
   - Smart detection of already-English text

5. **📁 File Selection**
   - Interactive file tree navigation
   - Customizable ignore patterns
   - Manual file review option

6. **🎯 Prompt Type Selection**
   - Choose from Dev, Architect, or Bug modes

7. **📄 Context Generation**
   - Generate structured output file
   - Includes project tree and file contents

8. **🤖 Gemini Processing** (If enabled)
   - Automatically send prompt to Google Gemini API
   - Receive AI-processed response
   - Save to timestamped output file

### Command Line Options

```bash
shotgun-terminal [OPTIONS]

Options:
  -d, --directory PATH     Project directory to analyze
  -o, --output PATH       Output file path 
  -p, --prompt-type TYPE  Prompt type (dev/architect/bug)
  --config               Configure API settings (translation, Gemini, etc.)
  --quick-setup          Quick setup with test credentials
  --help                 Show help message
```

## 🎯 Prompt Types

### 1. Dev Mode (Default)
**Output**: Git diff format
- Generate precise code changes
- Follow existing patterns
- Implement features and fixes
- **Best for**: Feature implementation, bug fixes, code modifications

### 2. Architect Mode  
**Output**: Markdown planning document
- High-level system design
- Refactoring strategies
- Architecture analysis
- **Best for**: System design, refactoring plans, architecture reviews

### 3. Bug Mode
**Output**: Markdown analysis report
- Root cause analysis
- Debugging strategies
- Code execution tracing
- **Best for**: Bug investigation, debugging, error analysis

## ⚙️ Configuration

### API Configuration for Translation

```bash
shotgun-terminal --config
```

**Interactive Menu Options:**
- Configure API credentials
- Test API connection  
- Toggle translation on/off
- View current settings
- Reset to defaults

**Settings Storage**: `~/.config/shotgun-code/settings.json`

### Gemini API Configuration

```bash
shotgun-terminal --config
```

**Interactive Menu Options:**
- Configure Gemini API credentials
- Test Gemini API connection
- Configure parameters (temperature, thinking budget)
- Toggle Gemini on/off
- View current Gemini settings
- Reset Gemini to defaults

### Quick Setup

```bash
shotgun-terminal --quick-setup
```
Sets up with provided test credentials for immediate use.

## 🌍 Translation

Shotgun Terminal includes automatic translation from Portuguese to English:

### Features
- **Smart Detection**: Automatically detects if text is already in English
- **API Integration**: Uses OpenAI-compatible APIs
- **Session-based**: Translates tasks and rules for each session
- **Fallback**: Uses original text if translation fails

### Supported APIs
- OpenAI-compatible endpoints
- Custom base URLs
- Configurable models

### Configuration
```json
{
  "apiSettings": {
    "api_key": "your-api-key",
    "base_url": "https://api.example.com",
    "model": "gpt-4.1",
    "enable_translation": true
  }
}
```

## 🤖 Gemini Integration

Shotgun Terminal includes optional integration with Google Gemini AI for automated prompt processing:

### Features
- **🚀 Automated Processing**: Send generated prompts directly to Gemini API
- **⚙️ Configurable Parameters**: Fine-tune temperature and thinking budget
- **📊 Real-time Streaming**: Live progress feedback during API calls
- **🔄 Fallback Support**: Graceful degradation when API is unavailable
- **📁 Smart Output**: Timestamped response files with clear naming

### Configuration Parameters
- **Temperature**: 0.0 - 2.0 (controls response randomness)
- **Thinking Budget**: 0 - 32768 (reasoning computation budget)
- **API Key**: Your Google Gemini API key

### Workflow Integration
When Gemini is enabled, the workflow becomes:
1. Generate project context (standard process)
2. **Automatically send to Gemini API**
3. **Stream response with progress indicator**
4. **Save both original context and AI response**

### Output Files
- **Gemini Disabled**: `shotgun_context_{prompt_type}.txt` (standard behavior)
- **Gemini Enabled**: 
  - `shotgun_context_{prompt_type}.txt` (original context)
  - `shotgun_response_{timestamp}.txt` (Gemini AI response)

### Configuration Example
```json
{
  "geminiSettings": {
    "api_key": "your-gemini-api-key",
    "enable_gemini": true,
    "temperature": 0.35,
    "thinking_budget": 32768
  }
}
```

### Installation Requirements
```bash
# Install optional Gemini dependency
pip install google-genai
```

## 🔧 Advanced Usage

### File Selection

**Ignore Patterns**: Customize which files to exclude
```
*.pyc
__pycache__
.git
node_modules
*.log
```

**Manual Review**: Fine-tune file selection
- Remove files by pattern
- Add back excluded files
- Interactive file tree navigation

### Output Formats

**Git Diff (Dev Mode)**:
```diff
diff --git a/file.py b/file.py
index abc123..def456 100644
--- a/file.py
+++ b/file.py
@@ -1,3 +1,4 @@
 def function():
+    # New functionality
     pass
```

**Markdown Plan (Architect Mode)**:
```markdown
# Refactoring Plan: Authentication System

## 1. Executive Summary & Goals
- Implement secure authentication
- Add JWT token support

## 2. Proposed Solution
...
```

### Project Tree Generation

Automatic visual project structure:
```
project-name\
├── src/
│   ├── components/
│   │   └── auth.py
│   └── utils/
│       └── helpers.py
└── tests/
    └── test_auth.py
```

## 📚 Examples

### Example 1: Feature Implementation
```bash
shotgun-terminal -p dev -d ./my-project
```
1. Task: "Add user registration endpoint"
2. Rules: "Use FastAPI, include validation"
3. Output: Git diff with implementation

### Example 2: Architecture Review
```bash
shotgun-terminal -p architect
```
1. Task: "Redesign authentication system"
2. Output: Detailed refactoring plan

### Example 3: Bug Analysis
```bash
shotgun-terminal -p bug -o bug-report.txt
```
1. Task: "Login endpoint returns 500 error"
2. Output: Debugging analysis report

### Example 4: Automated AI Processing
```bash
shotgun-terminal -p dev
```
1. Task: "Add user authentication system"
2. Rules: "Use JWT tokens and bcrypt hashing"
3. **Gemini enabled**: Automatically processes prompt
4. Output: 
   - `shotgun_context_dev.txt` (original context)
   - `shotgun_response_20241224_143052.txt` (AI response)

## 🛠️ Development

### Setup Development Environment
```bash
git clone <repository>
cd shotgun-terminal
pip install -e .
```

### Development Commands
```bash
# Reinstall after changes
./reinstall.bat  # Windows
# or
pipx uninstall shotgun-terminal && pipx install -e .

# Run with development changes
shotgun-terminal
```

### Project Structure
```
shotgun-terminal/
├── shotgun_terminal/
│   ├── __init__.py
│   ├── cli.py              # Main CLI interface
│   ├── config.py           # API configuration
│   ├── context_generator.py # Context generation
│   ├── file_selector.py    # File selection logic
│   ├── gemini_service.py   # Gemini AI integration
│   ├── prompts.py          # Prompt templates
│   ├── settings.py         # Settings management
│   ├── translator.py       # Translation service
│   ├── tree_generator.py   # Project tree generation
│   └── user_input.py       # User input collection
├── setup.py
├── pyproject.toml
├── requirements.txt
└── README.md
```

## 📋 Requirements

- **Python**: 3.8 or higher
- **Terminal**: Interactive terminal with color support
- **Dependencies**:
  - `click` >= 8.0.0
  - `rich` >= 10.0.0
  - `inquirer` >= 2.8.0
  - `openai` >= 1.0.0 (for translation)
  - `requests` >= 2.25.0
  - `google-genai` >= 1.0.0 (optional, for Gemini integration)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## 🆘 Support

- **Issues**: Report bugs and request features
- **Documentation**: Check this README for detailed usage
- **API Configuration**: Use `--config` to set up translation and Gemini.

---

**Made with ❤️ for developers who love clean, structured LLM prompts**