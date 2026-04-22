# AI Tax Buddy Architecture

This document describes the architecture and design decisions behind AI Tax Buddy.

## System Overview

AI Tax Buddy is a production-grade agentic AI system designed to provide general Australian tax guidance while operating within strict legal and ethical boundaries. The system uses LangGraph for orchestration, implements a ReAct reasoning pattern, and includes comprehensive safety mechanisms.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Interface                          │
│                     (CLI / Future: Web UI)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Content Guardrails                         │
│           (PII Filtering, Policy Enforcement)                   │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      LangGraph Agent                            │
│                     (ReAct Pattern)                             │
│                                                                 │
│  ┌─────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │   Agent     │─────>│  Tool Node   │─────>│   Agent      │  │
│  │   Node      │<─────│              │<─────│   Node       │  │
│  └─────────────┘      └──────────────┘      └──────────────┘  │
│        │                     │                      │          │
│        │                     ▼                      │          │
│        │              ┌──────────────┐              │          │
│        │              │    Tools     │              │          │
│        │              └──────────────┘              │          │
│        │                                            │          │
└────────┼────────────────────────────────────────────┼──────────┘
         │                                            │
         ▼                                            ▼
┌──────────────────┐                        ┌──────────────────┐
│  Memory (Mem0)   │                        │ Observability    │
│  - Episodic      │                        │  (Langfuse)      │
│  - Semantic      │                        │  - Traces        │
│  - State         │                        │  - Metrics       │
└──────────────────┘                        └──────────────────┘
         │
         ▼
┌──────────────────┐
│  Vector Store    │
│   (ChromaDB)     │
└──────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Tools Layer                             │
├─────────────────────────────────────────────────────────────────┤
│  • calculate_tax_bracket     • query_ato_guidelines            │
│  • calculate_medicare_levy   • validate_deduction              │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                      Knowledge Base                             │
│  • ATO Guidelines (Mock GraphRAG ready)                        │
│  • Tax Nudge Rules (2025 ATO Hitlist)                         │
│  • Deduction Validation Logic                                  │
└─────────────────────────────────────────────────────────────────┘
```

## Core Components

### 1. Content Guardrails (`src/guardrails.py`)

**Purpose**: First line of defense to maintain legal boundaries and protect PII.

**Key Features**:
- **PII Detection & Redaction**: Automatically removes TFNs, ABNs, emails, phone numbers
- **Policy Enforcement**: Blocks requests for filing returns, account access, financial transactions
- **Disclaimer Injection**: Adds mandatory disclaimers to all responses

**Design Pattern**: Middleware pattern - all user input passes through guardrails before reaching the agent.

**Why This Matters**: Prevents the system from accidentally crossing into "specific advice" territory and ensures user privacy.

### 2. LangGraph Agent (`src/agent.py`)

**Purpose**: Core reasoning engine implementing the ReAct pattern.

**Graph Structure**:
```python
Agent Node → [Decision] → Tool Node → Agent Node → ... → END
```

**State Management**:
```python
class AgentState(TypedDict):
    messages: Sequence[BaseMessage]  # Conversation history
    iterations: int                  # Loop counter
    user_id: str                     # For memory persistence
```

**ReAct Loop**:
1. **Thought**: Agent analyzes the query and decides what it needs
2. **Action**: Agent selects and calls appropriate tools
3. **Observation**: Agent receives tool outputs
4. **Response**: Agent formulates final answer with reasoning

**Why LangGraph**: 
- Precise control over agent loops
- Built-in cycle detection
- State persistence across iterations
- Better than simple chains for complex, multi-step reasoning

### 3. Memory System (`src/memory.py`)

**Purpose**: Maintain context across conversations and prevent repetitive questions.

**Memory Types**:
- **Episodic**: Conversation history ("User asked about home office last time")
- **Semantic**: Key facts extracted ("User is a sole trader", "User has rental property")
- **State**: Current session context

**Technology**: Mem0 with ChromaDB backend
- Vector embeddings for semantic search
- Automatic memory consolidation
- Temporal tracking (knowing when facts change)

**Why Mem0**:
- Production-grade memory management
- Better than raw vector databases
- Handles memory scoring and consolidation
- Built for agentic AI systems

### 4. Tools Layer (`src/tools/`)

**Design Principle**: **Strict separation of concerns**
- LLM handles judgment and language
- Deterministic Python functions handle all calculations
- No hallucination in mathematical operations

**Tool Architecture**:
```python
@tool
def calculate_tax_bracket(income: float) -> TaxBracketResult:
    """Deterministic calculation, no LLM involved"""
    # Pure Python logic
    return result
```

**Available Tools**:
1. **Tax Calculator** (`tax_calculator.py`)
   - Bracket calculations (FY 2024-25)
   - Medicare levy calculations
   - 100% deterministic, no LLM

2. **ATO Knowledge** (`ato_knowledge.py`)
   - Retrieves general ATO guidelines
   - Mock implementation (GraphRAG-ready)
   - Topics: work expenses, home office, crypto, etc.

3. **Deduction Validator** (`deduction_validator.py`)
   - Validates deduction scenarios
   - Flags audit risks
   - Returns structured risk assessments

**Why This Matters**: Tax calculations must be accurate and auditable. LLMs should never perform arithmetic.

### 5. Nudge System (`src/nudges.py`)

**Purpose**: Proactively warn users about ATO audit risks BEFORE they make mistakes.

**Architecture**:
```python
Keyword Triggers → Nudge Engine → Risk-Prioritized Warnings
```

**2025 ATO Audit Focus Areas**:
- Home office double-dipping (67c + separate bills)
- Commuting claims (home to work)
- Conventional clothing (suits, business wear)
- Crypto transactions (data matching)
- Side hustle income (platform data sharing)

**Design Pattern**: Rule-based system with keyword matching and priority scoring.

**Example**:
```
User: "I claim 67c rate and also my internet bill"
       ↓
Nudge Engine detects: ["67c", "internet bill"]
       ↓
Triggers: CRITICAL WARNING about double-dipping
       ↓
Agent includes warning in response
```

**Why Proactive**: Better to prevent mistakes than explain ATO penalties later.

### 6. Observability (`src/observability.py`)

**Purpose**: Complete traceability for legal compliance and debugging.

**What's Traced**:
- Every LLM prompt and response
- All tool calls and outputs
- Reasoning steps (Thought → Action → Observation)
- Token usage and costs
- Response quality scores

**Technology**: Langfuse
- Cloud-based trace visualization
- Prompt management
- Cost tracking
- Quality evaluation

**Why This Matters**: 
- Legal traceability ("Why did the agent say that?")
- Debugging complex reasoning chains
- Cost monitoring
- Continuous improvement through analytics

## Data Flow

### Typical User Interaction

```
1. User Input
   "Can I claim my home office expenses?"
   
2. Guardrails Check
   ✓ No prohibited requests
   ✓ No PII detected
   → Pass through
   
3. Nudge Analysis
   Keywords: ["home office", "claim"]
   → Load home office nudge (potential double-dip warning)
   
4. Memory Retrieval
   Search: "home office"
   → Find: "User works from home 3 days/week" (from previous conversation)
   
5. Agent Reasoning (ReAct Loop)
   
   Iteration 1:
   Thought: "User asking about home office. Should explain methods and warn about double-dipping."
   Action: query_ato_guidelines("home_office")
   Observation: [ATO guidelines about 67c vs actual cost]
   
   Iteration 2:
   Thought: "I have the guidelines. User works 3 days/week (from memory). Can provide informed general guidance."
   Action: None (ready to respond)
   Response: [Detailed explanation with nudge warning]
   
6. Guardrails Post-Processing
   → Add disclaimer
   → Final safety check
   
7. Memory Storage
   Store: ["User asked about home office expenses", "Provided general guidance on methods"]
   
8. Observability
   → Trace logged to Langfuse
   → Token usage recorded
   
9. User Receives Response
   "Here's general guidance about home office expenses..."
```

## Design Patterns

### 1. ReAct Pattern (Reasoning + Acting)

**Traditional Agent**:
```
Query → LLM → Response
```

**ReAct Agent**:
```
Query → Thought → Action → Observation → Thought → Action → ... → Response
```

**Benefits**:
- Transparent reasoning
- Fewer hallucinations
- Better tool selection
- Traceable decision-making

### 2. Constitutional AI

**Concept**: Build constraints INTO the system architecture, not just prompts.

**Implementation**:
- **Hard Boundaries**: Code-level blocks for prohibited actions
- **Soft Boundaries**: Prompt engineering for general vs specific advice
- **Defense in Depth**: Multiple layers (guardrails, prompts, nudges)

**Example**:
```python
if "file my return" in query:
    return PROHIBITED_RESPONSE  # Hard boundary
else:
    # Proceed with soft boundaries (prompts)
```

### 3. Tool-Augmented Generation

**Concept**: LLM decides WHEN to use tools, tools provide WHAT data.

**Flow**:
```
LLM: "I need to calculate tax for $80,000"
     ↓
Tool: calculate_tax_bracket(80000)
     ↓
Result: {tax: $17,467, bracket: "32.5%"}
     ↓
LLM: "Based on $80,000 income, tax would be approximately $17,467 in the 32.5% bracket..."
```

**Why**: Separates reasoning from calculation, preventing math hallucinations.

### 4. Memory-Augmented Conversation

**Traditional Chatbot**: Stateless, no context between sessions

**AI Tax Buddy**: Stateful, remembers user context
```
Session 1: "I'm a sole trader"
Session 2: "Can I claim my car?" → Agent knows user is sole trader
```

**Benefits**:
- No repetitive questions
- More contextual guidance
- Better user experience

## Security & Privacy

### PII Protection

**Detection Methods**:
- Regex patterns for TFN, ABN, email, phone
- Context-aware redaction
- Large amount filtering (prevents specific advice)

**Why Regex**: Fast, deterministic, no model latency

### Legal Boundaries

**Three-Layer Defense**:
1. **Guardrails**: Block prohibited requests (filing, account access)
2. **System Prompt**: Reinforce general advice boundary
3. **Response Filtering**: Add disclaimers, remove specific recommendations

**Design Principle**: Fail-safe defaults - if uncertain, don't cross the boundary.

## Scalability Considerations

### Current Architecture
- Single-user mode (CLI)
- Local ChromaDB for memory
- Synchronous processing

### Production Scale (Future)
- Multi-user with user_id isolation
- Distributed vector store (Pinecone, Weaviate)
- Async processing with queue (Celery, RabbitMQ)
- Rate limiting per user
- Caching for common queries
- Horizontal scaling with load balancer

## Testing Strategy

### Test Pyramid

```
         /\
        /  \  Unit Tests (Tools, Guardrails)
       /    \
      /------\
     / Golden \ Agent Evaluation (End-to-End)
    /  Dataset\
   /____________\
```

**Unit Tests** (`tests/test_*.py`):
- Tool calculations accuracy
- Guardrail detection
- PII redaction
- Fast, isolated

**Golden Dataset** (`tests/golden_dataset.py`):
- 13 critical scenarios
- Boundary violations
- Common misconceptions
- Audit risks
- End-to-end agent behavior

**Evaluation Criteria**:
- Required elements present (must include)
- Prohibited elements absent (must not include)
- Risk area compliance
- Pass threshold: ≥80%

**LLM-as-a-Judge** (Future):
- Use GPT-4 to score response quality
- Check adherence to boundaries
- Evaluate reasoning quality

## Future Enhancements

### Short Term
- [ ] GraphRAG with Neo4j for complex tax relationship queries
- [ ] E2B sandbox for hypothetical scenario calculations
- [ ] Streamlit web interface
- [ ] Enhanced golden dataset (50+ examples)

### Medium Term
- [ ] Multi-year tax planning
- [ ] Integration with accounting software APIs
- [ ] Automated knowledge base updates from ATO website
- [ ] Voice interface

### Long Term
- [ ] Personalized tax optimization (staying within general advice)
- [ ] Multi-jurisdiction support (beyond Australia)
- [ ] Mobile app
- [ ] Real-time ATO policy updates

## Key Decisions & Trade-offs

### Why LangGraph over LangChain Chains?
- **Need**: Complex, cyclic reasoning with state management
- **Trade-off**: More complexity vs better control
- **Decision**: LangGraph for production-grade agent orchestration

### Why Mem0 over Raw Vector DB?
- **Need**: Production-grade memory with consolidation and scoring
- **Trade-off**: Additional dependency vs better memory management
- **Decision**: Mem0 for robust memory layer

### Why Rule-Based Nudges over LLM-Generated?
- **Need**: Deterministic, reliable warnings
- **Trade-off**: Less flexible vs more reliable
- **Decision**: Rule-based for critical audit warnings

### Why Separate Tools from LLM?
- **Need**: Accurate, auditable calculations
- **Trade-off**: More code vs no math hallucinations
- **Decision**: Strict separation for legal compliance

### Why General Advice Only?
- **Legal**: Avoids TPB registration requirements
- **Ethical**: Prevents harm from bad personalized advice
- **Scalable**: One system serves all users
- **Decision**: Non-negotiable boundary

## Maintenance & Operations

### Monitoring
- Langfuse dashboards for trace analysis
- Error rate tracking
- Token usage and cost monitoring
- User feedback collection

### Updates Required
- Annual: Tax bracket updates (July 1)
- Quarterly: ATO priority area updates
- Ad-hoc: New deduction rules, policy changes

### Knowledge Base Maintenance
- Subscribe to ATO updates
- Review tax law changes
- Update golden dataset
- Re-run evaluations after updates

---

**For questions about architecture decisions, open a GitHub discussion.**
