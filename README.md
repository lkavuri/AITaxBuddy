# 🇦🇺 AI Tax Buddy

A conversational AI agent that helps Australians understand general tax rules, spot common deduction mistakes, and avoid ATO audit traps — before they lodge.

> **General advice only.** Not a registered tax agent. For personalised advice, consult a professional or the ATO directly (ato.gov.au).

---

## What makes this interesting technically

This is a portfolio project built to demonstrate real agentic AI patterns — not just a wrapper around ChatGPT.

### LangGraph — stateful agent loop

The agent runs as a **graph**, not a simple prompt-response. Each user message goes through a cycle:

```
[you ask] → [LLM thinks] → [calls a tool] → [LLM thinks again] → [answers]
```

This is the **ReAct pattern** (Reason + Act). The LLM decides *when* to use tools and *which* ones. LangGraph manages the state (conversation history, iteration count) across each step and prevents infinite loops.

### Tool use — LLM judgment + deterministic code

The LLM handles reasoning. Real calculations are done by actual Python functions, not guessed by the model:

| Tool | Does |
|---|---|
| `calculate_tax_bracket` | Correct ATO tax brackets for FY 2024-25 |
| `calculate_medicare_levy` | Medicare levy with low-income thresholds |
| `query_ato_guidelines` | Retrieves ATO guidance on 5 topic areas |
| `validate_deduction` | Checks deduction validity + flags audit risk level |

### Mem0 — memory across conversations

Uses **Mem0** with a local ChromaDB vector store. After each conversation, facts are stored as embeddings. Next session, the agent searches by semantic similarity to retrieve relevant past context — so it remembers you're a sole trader, or that you asked about crypto last time.

### Langfuse — observability

Every LLM call, tool invocation, and token count is traced via **Langfuse**. This is how you debug AI apps — you need to see *what prompt went in* and *why the model responded the way it did*.

### Guardrails — safety layer before and after the LLM

Before your message reaches the LLM, a filter:
- **Redacts PII** — Tax File Numbers, ABNs, emails, phone numbers are replaced with `[TFN_REDACTED]` etc.
- **Blocks out-of-scope requests** — "file my return", "log into myGov" get a polite refusal without hitting the LLM at all

After the response, a disclaimer is appended automatically.

### Golden dataset evaluation

13 hand-written test cases with required and prohibited response elements. The evaluator scores each response and reports a pass rate. This is how you measure whether an agent is *actually behaving correctly*, not just whether the code runs.

---

## Stack

| Layer | Technology |
|---|---|
| Agent orchestration | LangGraph |
| LLM | OpenAI GPT-4o or Anthropic Claude |
| Memory | Mem0 + ChromaDB |
| Observability | Langfuse |
| Data validation | Pydantic v2 |
| CLI | Typer + Rich |

---

## Quick start

```bash
git clone https://github.com/yourusername/aitaxbuddy.git
cd aitaxbuddy
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your API key
```

```bash
# Chat
taxbuddy chat

# Single question
taxbuddy query "Can I claim my home office internet bill?"

# Run evaluation against golden dataset
taxbuddy evaluate
```

Minimum `.env`:
```
OPENAI_API_KEY=sk-...
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o
```

---

## Project structure

```
src/aitaxbuddy/
├── agent.py          # LangGraph graph — the core loop
├── tools/            # Deterministic calculation tools
├── memory.py         # Mem0 integration
├── guardrails.py     # PII filtering + content safety
├── nudges.py         # Proactive ATO audit warnings
├── observability.py  # Langfuse tracing
└── prompts.py        # System prompt + ATO 2025 audit focus areas

tests/
├── golden_dataset.py # 13 evaluation cases
├── evaluate_agent.py # Scoring script
├── test_tools.py
└── test_guardrails.py
```

---

MIT License • Remember to lodge by October 31st 🇦🇺
