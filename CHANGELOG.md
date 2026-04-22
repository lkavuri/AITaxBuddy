# Changelog

All notable changes to AI Tax Buddy will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2026-04-22

### Added
- Initial release of AI Tax Buddy
- LangGraph-based ReAct agent for Australian tax guidance
- Four deterministic tax calculation tools:
  - Tax bracket calculator (FY 2024-25)
  - Medicare levy calculator
  - ATO guidelines knowledge base
  - Deduction validator with risk assessment
- Memory system using Mem0 for conversation context
- Content guardrails with PII filtering (TFN, ABN, email, phone)
- Proactive tax nudges for 2025 ATO audit priority areas
- Comprehensive test suite with golden dataset evaluation
- CLI interface with multiple modes (chat, query, evaluate, info)
- Full documentation (README, SETUP, QUICKSTART, ARCHITECTURE, CONTRIBUTING)
- Langfuse observability integration
- Support for OpenAI and Anthropic LLM providers

### Security
- Multi-layer guardrails prevent crossing legal boundaries
- Automatic PII redaction
- Mandatory disclaimers on all responses
- Constitutional AI design ensures general advice only

### Documentation
- Comprehensive setup guides
- Architecture documentation
- Contribution guidelines
- Golden dataset with 13 test scenarios

## [Unreleased]

### Planned
- GraphRAG integration with Neo4j for complex tax queries
- E2B sandbox for hypothetical scenario calculations
- Web interface (Streamlit/Gradio)
- Mobile app
- Additional ATO knowledge topics
- More tax calculation tools (CGT, depreciation, etc.)
- Multi-year tax planning features
