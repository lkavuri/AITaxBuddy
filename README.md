# 🇦🇺 AI Tax Buddy

[![Tests](https://github.com/yourusername/aitaxbuddy/workflows/Tests/badge.svg)](https://github.com/yourusername/aitaxbuddy/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

An open-source, production-grade AI assistant that provides **general taxation advice** to help Australians navigate their taxes. Built with LangGraph, it operates within strict legal boundaries to avoid requiring Tax Practitioners Board (TPB) registration.

> **⚠️ Important**: This provides general advice only, not specific financial recommendations. Consult a registered tax agent for personalized guidance.

## 🎯 Core Value Proposition

AI Tax Buddy acts as your proactive "tax buddy," helping you understand:
- Australian tax rules and regulations
- Common deductions and their requirements
- ATO audit focus areas and compliance tips
- Tax obligations for side hustles, crypto, rental properties, and more

**Legal Boundary**: This agent provides **general advice only**. It does NOT provide specific financial advice, file returns with the ATO, or access your myGov account.

## ⚖️ Legal & Ethical Design

This system is designed to operate **safely and legally**:

1. **General Advice Only**: Provides information applicable to broad categories of taxpayers, not personalized recommendations
2. **Constitutional Guardrails**: Built-in checks prevent the agent from crossing into registered tax agent territory
3. **PII Protection**: Automatically redacts Tax File Numbers, ABNs, and other sensitive information
4. **Proactive Warnings**: Alerts users about ATO audit priority areas before they make mistakes
5. **Transparent Reasoning**: Uses ReAct pattern to show its thinking process
6. **Full Traceability**: Every decision logged through Langfuse for accountability

## 🏗️ Architecture

### Tech Stack

- **Orchestration**: LangGraph (stateful, cyclic workflows with precise control)
- **Memory**: Mem0 (episodic, semantic, and state memory)
- **Knowledge**: GraphRAG with Neo4j (for complex tax relationship queries)
- **Tools**: Model Context Protocol (MCP) standard
- **Sandbox**: E2B (for isolated code execution)
- **Observability**: Langfuse (complete tracing and monitoring)
- **LLM**: OpenAI GPT-4o or Anthropic Claude (configurable)

### Core Design Patterns

1. **ReAct Loop**: Thought → Action → Observation → Response
2. **Tool Separation**: LLM handles judgment, deterministic tools handle calculations
3. **Constitutional AI**: Guardrails enforce legal boundaries
4. **Proactive Nudging**: Warns about ATO audit targets based on 2025 hitlist

## 🚀 Quick Start

### Prerequisites

- **Python 3.11+** (3.11, 3.12, or 3.13 recommended)
- OpenAI API key OR Anthropic API key ([Get one here](#getting-api-keys))
- (Optional) Langfuse account for observability

### Installation

1. **Clone the repository**:
```bash
git clone https://github.com/yourusername/aitaxbuddy.git
cd aitaxbuddy
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Install global commands**:
```bash
./install.sh
source ~/.zshrc  # or source ~/.bashrc
```

5. **Configure environment variables**:
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required environment variables:
```bash
# Choose your LLM provider
OPENAI_API_KEY=sk-...          # OR
ANTHROPIC_API_KEY=sk-ant-...

MODEL_PROVIDER=openai           # or anthropic
MODEL_NAME=gpt-4o              # or claude-3-5-sonnet-20241022

# Optional but recommended
LANGFUSE_PUBLIC_KEY=pk-lf-...
LANGFUSE_SECRET_KEY=sk-lf-...
```

### Running the Agent

After installation, you can use simple commands like `claude`:

**Interactive Chat Mode**:
```bash
taxbuddy chat
# or
aitax chat
```

**Single Query**:
```bash
taxbuddy query "Can I claim my home office expenses?"
```

**Run Evaluation Tests**:
```bash
taxbuddy evaluate
```

**Check Configuration**:
```bash
taxbuddy info
```

See [COMMANDS.md](COMMANDS.md) for all available commands and options.

## 📋 Features

### 🛠️ Available Tools

The agent has access to these deterministic tools:

1. **calculate_tax_bracket**: Calculate Australian tax payable for a given income (FY 2024-25)
2. **calculate_medicare_levy**: Calculate Medicare levy with thresholds
3. **query_ato_guidelines**: Retrieve general ATO guidance on topics:
   - Work-related expenses
   - Home office deductions
   - Cryptocurrency
   - Side hustles & gig economy
   - Rental properties
4. **validate_deduction**: Assess if a deduction qualifies and flag audit risks

### 🚨 Proactive Tax Nudges

The agent automatically warns about **ATO 2025 audit priority areas**:

- **Work-Related Expenses**: Over-claiming, commuting, conventional clothing
- **Home Office**: Double-dipping (67c rate + separate bills)
- **Cryptocurrency**: Undeclared transactions, ATO data matching
- **Rental Properties**: Over-claiming interest, private use
- **Side Hustles**: Uber, DoorDash, Airbnb, platform data sharing
- **Capital Gains**: Unreported property/share sales

### 🔒 Safety Features

1. **PII Filtering**: Automatically redacts:
   - Tax File Numbers (TFN)
   - Australian Business Numbers (ABN)
   - Email addresses
   - Phone numbers
   - Large dollar amounts (to maintain general advice)

2. **Content Guardrails**: Blocks prohibited requests:
   - Filing tax returns
   - Accessing myGov
   - Financial transactions
   - Specific investment advice

3. **Mandatory Disclaimers**: All responses include appropriate disclaimers

### 🧠 Memory System

The agent remembers:
- Previous conversations (episodic memory)
- User context (e.g., "User is a sole trader")
- Relevant tax facts from past discussions

This prevents repetitive questions and provides more contextual guidance.

## 🧪 Testing & Evaluation

The project includes a comprehensive test suite and golden dataset:

```bash
# Run unit tests
pytest tests/

# Run full agent evaluation
python main.py evaluate
```

**Golden Dataset**: 13 carefully crafted test cases covering:
- Boundary violations (filing returns, myGov access)
- Common misconceptions (commuting, conventional clothing)
- Audit risks (double-dipping, crypto)
- PII handling
- General guidance quality

**Evaluation Criteria**:
- Required elements present
- Prohibited elements absent
- Risk area compliance
- Overall pass rate ≥80%

## 📊 Observability

If Langfuse is configured, every interaction is traced:
- LLM prompts and responses
- Tool calls and outputs
- Reasoning steps
- Token usage and costs
- Response quality scores

Access your traces at: https://cloud.langfuse.com

## 🎯 2025 ATO Audit Focus Areas

The agent is pre-loaded with knowledge of ATO's publicly announced audit priorities:

1. **Work-Related Expenses** - Over-claiming, especially car and clothing
2. **Working From Home** - Double-dipping fixed rate and actual costs
3. **Cryptocurrency** - Data matching from Australian exchanges
4. **Rental Properties** - Interest deductions and private use
5. **Side Hustles** - Platform data sharing (Uber, Airbnb, etc.)
6. **Capital Gains** - Unreported property and share sales

The agent proactively warns users when their queries relate to these areas.

## 🔑 Getting API Keys

### OpenAI (Recommended)
1. Go to https://platform.openai.com/signup
2. Add a payment method in Settings → Billing
3. Create an API key at https://platform.openai.com/api-keys
4. Copy the key (starts with `sk-...`)

### Anthropic Claude (Alternative)
1. Go to https://console.anthropic.com/
2. Create an API key in Settings → API Keys
3. Copy the key (starts with `sk-ant-...`)

**Cost**: ~$0.01-0.05 per conversation (very affordable for testing)

## 🛠️ Development

### Project Structure

```
aitaxbuddy/
├── src/
│   ├── agent.py              # Main LangGraph agent
│   ├── config.py             # Configuration management
│   ├── observability.py      # Langfuse tracing
│   ├── memory.py             # Mem0 memory management
│   ├── guardrails.py         # PII filtering & content safety
│   ├── prompts.py            # System prompts & ATO hitlist
│   ├── nudges.py             # Proactive warning system
│   └── tools/
│       ├── tax_calculator.py # Tax calculations
│       ├── ato_knowledge.py  # ATO guidelines
│       └── deduction_validator.py # Deduction validation
├── tests/
│   ├── test_tools.py         # Tool unit tests
│   ├── test_guardrails.py    # Guardrail tests
│   ├── golden_dataset.py     # Golden examples
│   └── evaluate_agent.py     # Full evaluation script
├── main.py                    # CLI entry point
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
└── README.md                 # This file
```

### Running Tests

```bash
# Unit tests
pytest tests/test_tools.py
pytest tests/test_guardrails.py

# Full agent evaluation
python tests/evaluate_agent.py

# Or via CLI
python main.py evaluate
```

### Code Quality

```bash
# Format code
black src/ tests/

# Lint code
ruff check src/ tests/
```

## 🤝 Contributing

Contributions are welcome! Please ensure:

1. All tests pass: `pytest tests/`
2. Agent evaluation passes: `python main.py evaluate`
3. Code is formatted: `black .`
4. Legal boundaries are maintained (general advice only)

## ⚠️ Important Disclaimers

**This is General Advice Only**: AI Tax Buddy provides general taxation information applicable to broad categories of Australian taxpayers. It does NOT provide specific financial advice tailored to your individual circumstances.

**Not a Registered Tax Agent**: This system is not a registered tax agent and cannot:
- Lodge or file your tax return
- Access your myGov account
- Provide specific investment or financial advice
- Conduct financial transactions

**Consult a Professional**: For complex situations or personalized advice, please consult:
- A registered tax agent
- A licensed financial adviser
- The ATO directly (ato.gov.au or 13 28 61)

**No Warranty**: This software is provided "as is" without warranty of any kind. Users are responsible for the accuracy of their tax returns.

## 📄 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Orchestration framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Mem0](https://github.com/mem0ai/mem0) - Memory management
- [Langfuse](https://langfuse.com) - Observability platform
- Australian Taxation Office (ATO) public guidance

## 📞 Support

For issues, questions, or contributions:
- GitHub Issues: [Create an issue](https://github.com/yourusername/aitaxbuddy/issues)
- Discussions: [GitHub Discussions](https://github.com/yourusername/aitaxbuddy/discussions)

## 🗺️ Roadmap

Future enhancements:
- [ ] GraphRAG integration with Neo4j for complex queries
- [ ] E2B sandbox for hypothetical tax scenarios
- [ ] Web interface (Streamlit/Gradio)
- [ ] Mobile app
- [ ] Multi-year tax planning
- [ ] Integration with accounting software
- [ ] Voice interface
- [ ] Multi-language support (for non-English speaking Australian taxpayers)

---

**Made with 🇦🇺 for Australian taxpayers**

*Remember: Lodge by October 31st!*
