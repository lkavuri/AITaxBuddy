# 🚀 Quick Start Guide

Get AI Tax Buddy running in 5 minutes!

## Prerequisites

- Python 3.11+ (not 3.14)
- OpenAI or Anthropic API key

## Installation

```bash
# 1. Run automated setup
cd aitaxbuddy
./setup.sh

# 2. Configure your API key
nano .env  # Add: OPENAI_API_KEY=sk-your-key-here

# 3. Install global commands
./install.sh
source ~/.zshrc  # or source ~/.bashrc

# 4. Done! Test it:
taxbuddy info
```

## First Run

```bash
# Test configuration
taxbuddy info

# Start chatting
taxbuddy chat
```

## Example Queries

Try these questions:

```
Can I claim my home office expenses?
I earned $80,000 this year. How much tax will I pay?
Can I claim travel between home and work?
I sold some Bitcoin. Do I need to declare it?
What deductions can I claim for my rental property?
```

## Quick Commands

```bash
# Interactive chat
python main.py chat

# Single question
python main.py query "Your question here"

# Run tests
python main.py evaluate

# Check configuration
python main.py info
```

## What to Expect

The agent will:
- ✅ Provide general Australian tax guidance
- ✅ Warn about ATO audit risks
- ✅ Show its reasoning process (Thought → Action → Observation)
- ✅ Remember context from previous questions
- ✅ Protect your privacy (PII redaction)

The agent will NOT:
- ❌ File your tax return
- ❌ Access your myGov account
- ❌ Give specific financial advice
- ❌ Process financial transactions

## Need Help?

- **Full Documentation**: See `README.md`
- **Setup Guide**: See `SETUP.md`
- **Architecture**: See `ARCHITECTURE.md`
- **Issues**: [GitHub Issues](https://github.com/yourusername/aitaxbuddy/issues)

## Next Steps

1. Try example queries above
2. Read the full README
3. Review the golden dataset in `tests/golden_dataset.py`
4. Customize for your needs

---

**Remember: This provides general advice only. Consult a registered tax agent for specific advice.**
