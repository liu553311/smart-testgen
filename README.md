# 🧪 smart-testgen

> AI-powered test case generator for software testers

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/tests-72%20passed-brightgreen.svg)](#testing)

**smart-testgen** takes your software requirements as input, sends them to an LLM (Claude or GPT), and generates comprehensive, structured test cases covering functional, boundary, negative, edge case, and security scenarios.

## ✨ Features

- 📝 **Multi-format input** — read requirements from `.txt`, `.md` files, or inline text
- 🤖 **Multi-LLM support** — switch between Anthropic Claude and OpenAI GPT
- 📊 **Rich test coverage** — functional, boundary, negative, edge case, security, performance tests
- 📁 **3 export formats** — Markdown, Excel (with color-coded priorities), JSON
- ⚙️ **Configurable** — env vars, `.env` file, or CLI options
- 🎯 **Category filtering** — focus on specific test types

## 🚀 Quick Start

### Installation

```bash
git clone https://github.com/liu553311/smart-testgen.git
cd smart-testgen
pip install -e .
```

### Setup API Key

```bash
# Option 1: Interactive setup
smart-testgen configure --provider openai

# Option 2: Environment variable
export OPENAI_API_KEY=sk-your-key-here

# Option 3: .env file
cp .env.example .env
# Edit .env with your API key
```

### Generate Test Cases

```bash
# From a file
smart-testgen generate examples/requirements_login.txt

# From inline text
smart-testgen generate --text "User login with email and password"

# With options
smart-testgen generate examples/requirements_api.md \
    --provider openai \
    --num-cases 20 \
    --format excel \
    --output api_tests.xlsx \
    --categories functional,boundary,negative
```

## 📋 CLI Reference

### `generate` — Generate test cases

```
smart-testgen generate <INPUT_SOURCE> [OPTIONS]
smart-testgen generate --text "requirements" [OPTIONS]
```

| Option | Short | Description |
|--------|-------|-------------|
| `--text` | `-t` | Inline requirements text |
| `--provider` | `-p` | LLM provider: `anthropic` or `openai` |
| `--model` | `-m` | Model name override |
| `--num-cases` | `-n` | Number of test cases (default: 10) |
| `--format` | `-f` | Export format: `markdown`, `excel`, `json` |
| `--output` | `-o` | Output file path |
| `--categories` | `-c` | Comma-separated categories |

### `configure` — Set up API keys

```bash
smart-testgen configure --provider anthropic
smart-testgen configure --provider openai
```

### `version` — Show version info

```bash
smart-testgen version
```

## ⚙️ Configuration

Settings are loaded with this priority: **CLI options > environment variables > `.env` file > defaults**

| Env Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | — | OpenAI API key |
| `ANTHROPIC_API_KEY` | — | Anthropic API key |
| `SMARTTESTGEN_PROVIDER` | `openai` | Default provider |
| `SMARTTESTGEN_MODEL` | — | Default model |
| `SMARTTESTGEN_NUM_CASES` | `10` | Default test case count |
| `SMARTTESTGEN_FORMAT` | `markdown` | Default export format |

## 🧪 Test Categories

| Category | Description |
|----------|-------------|
| `functional` | Core feature behavior |
| `boundary` | Input limit testing |
| `negative` | Invalid input handling |
| `edge_case` | Unusual but valid scenarios |
| `security` | Auth, injection, XSS tests |
| `performance` | Load and response time |
| `usability` | User experience |
| `accessibility` | Accessibility compliance |

## 📁 Project Structure

```
smart-testgen/
├── src/smart_testgen/
│   ├── cli/main.py          # Click CLI
│   ├── core/
│   │   ├── models.py        # Pydantic data models
│   │   ├── parser.py        # Input parsing
│   │   └── generator.py     # Test case generation
│   ├── llm/
│   │   ├── base.py          # LLMProvider ABC
│   │   ├── anthropic_provider.py
│   │   ├── openai_provider.py
│   │   └── factory.py       # Provider factory
│   ├── prompts/             # Prompt templates
│   ├── exporters/           # Markdown/Excel/JSON
│   └── config.py            # Settings
├── tests/                   # 72 tests, 92% coverage
├── examples/                # Sample requirements
└── docs/                    # Prompt design docs
```

## 🏗️ Architecture

```
Requirements → Parser → PromptBuilder → LLM Provider → Generator → Exporter
     │              │           │              │            │           │
  .txt/.md    Jinja2 template  ABC + Factory   JSON parse   MD/Excel/JSON
```

- **Provider abstraction** — add new LLMs by creating one file + one decorator
- **Pydantic models** — type-safe data contracts with auto-serialization
- **Factory pattern** — runtime provider switching without code changes

## 🧪 Testing

```bash
# Run all tests
python -m pytest -v

# With coverage
python -m pytest --cov=smart_testgen --cov-report=term-missing

# Run specific module
python -m pytest tests/test_generator.py -v
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Run tests: `python -m pytest -v`
4. Commit changes: `git commit -m "feat: add amazing feature"`
5. Push to branch: `git push origin feature/amazing-feature`
6. Open a Pull Request

## 📄 License

This project is licensed under the MIT License — see [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- Built with [Click](https://click.palletsprojects.com/), [Pydantic](https://docs.pydantic.dev/), and [Rich](https://rich.readthedocs.io/)
- Powered by [Anthropic Claude](https://www.anthropic.com/) and [OpenAI GPT](https://openai.com/)
