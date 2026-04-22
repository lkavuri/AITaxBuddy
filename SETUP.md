# Setup Guide for AI Tax Buddy

This guide will walk you through setting up AI Tax Buddy from scratch.

## Prerequisites

Before you begin, ensure you have:

- **Python 3.10 or higher** installed
- **Git** (for cloning the repository)
- An **OpenAI** or **Anthropic** API key
- (Optional) A **Langfuse** account for observability
- (Optional) **Neo4j** database for advanced knowledge retrieval

## Step-by-Step Setup

### 1. Clone and Setup Environment

```bash
# Clone the repository
git clone https://github.com/yourusername/aitaxbuddy.git
cd aitaxbuddy

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Upgrade pip
pip install --upgrade pip
```

### 2. Install Dependencies

```bash
# Install all required packages
pip install -r requirements.txt
```

### 3. Configure Environment Variables

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your preferred editor
nano .env  # or vim, code, etc.
```

**Minimum required configuration**:

```bash
# Choose ONE LLM provider:

# Option 1: OpenAI
OPENAI_API_KEY=sk-your-key-here
MODEL_PROVIDER=openai
MODEL_NAME=gpt-4o

# Option 2: Anthropic
# ANTHROPIC_API_KEY=sk-ant-your-key-here
# MODEL_PROVIDER=anthropic
# MODEL_NAME=claude-3-5-sonnet-20241022

# Basic settings
ENVIRONMENT=development
LOG_LEVEL=INFO
```

**Recommended additional configuration**:

```bash
# Langfuse (for observability)
LANGFUSE_PUBLIC_KEY=pk-lf-your-key
LANGFUSE_SECRET_KEY=sk-lf-your-secret
LANGFUSE_HOST=https://cloud.langfuse.com

# Security (enabled by default)
ENABLE_PII_FILTERING=true
ENABLE_CONTENT_GUARDRAILS=true
```

### 4. Verify Installation

```bash
# Check configuration
python main.py info

# You should see output like:
# 🇦🇺 AI Tax Buddy Configuration
# Model Provider: openai
# Model: gpt-4o
# ...
```

### 5. Run Tests

```bash
# Run unit tests
pytest tests/

# Run full agent evaluation
python main.py evaluate
```

### 6. Try It Out!

```bash
# Start interactive chat
python main.py chat

# Or ask a single question
python main.py query "Can I claim my home office expenses?"
```

## Optional: Advanced Setup

### Setting Up Langfuse (Recommended)

Langfuse provides tracing and observability for your agent:

1. **Sign up**: Go to [https://cloud.langfuse.com](https://cloud.langfuse.com)
2. **Create project**: Create a new project for AI Tax Buddy
3. **Get credentials**: Copy your public and secret keys
4. **Add to .env**:
   ```bash
   LANGFUSE_PUBLIC_KEY=pk-lf-...
   LANGFUSE_SECRET_KEY=sk-lf-...
   LANGFUSE_HOST=https://cloud.langfuse.com
   ```

### Setting Up Neo4j (Advanced)

For enhanced knowledge retrieval with GraphRAG:

1. **Install Neo4j**:
   - **Option A**: Use Neo4j Desktop ([download](https://neo4j.com/download/))
   - **Option B**: Use Docker:
     ```bash
     docker run -d \
       --name neo4j \
       -p 7474:7474 -p 7687:7687 \
       -e NEO4J_AUTH=neo4j/password \
       neo4j:latest
     ```

2. **Configure in .env**:
   ```bash
   NEO4J_URI=bolt://localhost:7687
   NEO4J_USERNAME=neo4j
   NEO4J_PASSWORD=your-password
   ```

3. **Initialize knowledge graph**:
   ```bash
   python scripts/init_knowledge_graph.py
   ```
   (Note: This script needs to be created for production use)

### Setting Up E2B Sandbox (Advanced)

For safe code execution in tax calculations:

1. **Sign up**: Go to [https://e2b.dev](https://e2b.dev)
2. **Get API key**: Create a new API key
3. **Add to .env**:
   ```bash
   E2B_API_KEY=e2b_...
   ```

## Configuration Options

### Environment Variables Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `OPENAI_API_KEY` | Yes* | - | OpenAI API key |
| `ANTHROPIC_API_KEY` | Yes* | - | Anthropic API key |
| `MODEL_PROVIDER` | Yes | `openai` | LLM provider (`openai` or `anthropic`) |
| `MODEL_NAME` | Yes | `gpt-4o` | Model name |
| `TEMPERATURE` | No | `0.0` | Model temperature (0.0-1.0) |
| `LANGFUSE_PUBLIC_KEY` | No | - | Langfuse public key |
| `LANGFUSE_SECRET_KEY` | No | - | Langfuse secret key |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse host URL |
| `NEO4J_URI` | No | `bolt://localhost:7687` | Neo4j connection URI |
| `NEO4J_USERNAME` | No | `neo4j` | Neo4j username |
| `NEO4J_PASSWORD` | No | `password` | Neo4j password |
| `E2B_API_KEY` | No | - | E2B API key |
| `ENVIRONMENT` | No | `development` | Environment (`development` or `production`) |
| `LOG_LEVEL` | No | `INFO` | Logging level |
| `MAX_ITERATIONS` | No | `5` | Max agent reasoning iterations |
| `ENABLE_PII_FILTERING` | No | `true` | Enable PII redaction |
| `ENABLE_CONTENT_GUARDRAILS` | No | `true` | Enable content safety |

\* One LLM provider key is required (either OpenAI or Anthropic)

### Model Options

**OpenAI Models**:
- `gpt-4o` (recommended) - Most capable, balanced cost
- `gpt-4o-mini` - Faster, lower cost
- `gpt-4-turbo` - Previous generation

**Anthropic Models**:
- `claude-3-5-sonnet-20241022` (recommended) - Most capable
- `claude-3-5-haiku-20241022` - Faster, lower cost
- `claude-3-opus-20240229` - Most powerful

### Temperature Settings

- `0.0` (default, recommended) - Deterministic, consistent responses
- `0.1-0.3` - Slight variation while maintaining accuracy
- `0.4-0.7` - More creative, less predictable
- `0.8-1.0` - Very creative (not recommended for tax advice)

## Troubleshooting

### Common Issues

**1. Import Errors**

```
ModuleNotFoundError: No module named 'langgraph'
```

**Solution**: Ensure virtual environment is activated and dependencies are installed:
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**2. API Key Errors**

```
Error: OpenAI API key not found
```

**Solution**: Check your `.env` file has the correct API key and is in the project root:
```bash
cat .env | grep API_KEY
```

**3. spaCy Model Missing**

```
OSError: [E050] Can't find model 'en_core_web_sm'
```

**Solution**: Download the spaCy model:
```bash
python -m spacy download en_core_web_sm
```

**4. Memory/ChromaDB Issues**

```
Error: Cannot access chroma_db directory
```

**Solution**: Ensure write permissions:
```bash
mkdir -p chroma_db
chmod 755 chroma_db
```

**5. Rate Limit Errors**

```
Error: Rate limit exceeded
```

**Solution**: 
- Check your API key has sufficient quota
- Reduce `MAX_ITERATIONS` in `.env`
- Add retry logic or use exponential backoff

### Getting Help

If you encounter issues:

1. **Check logs**: Set `LOG_LEVEL=DEBUG` in `.env` for detailed logs
2. **Run tests**: `pytest tests/ -v` to identify specific failures
3. **Check configuration**: `python main.py info` to verify setup
4. **GitHub Issues**: [Create an issue](https://github.com/yourusername/aitaxbuddy/issues)

## Production Deployment

For production deployment:

1. **Use production environment**:
   ```bash
   ENVIRONMENT=production
   LOG_LEVEL=WARNING
   ```

2. **Enable observability**:
   - Set up Langfuse for tracing
   - Configure error monitoring (Sentry, etc.)

3. **Secure API keys**:
   - Use environment variables or secrets manager
   - Never commit `.env` to version control

4. **Set resource limits**:
   - Configure `MAX_ITERATIONS` appropriately
   - Monitor token usage and costs

5. **Enable rate limiting**:
   - Add rate limiting middleware
   - Set up request quotas per user

6. **Data privacy**:
   - Ensure `ENABLE_PII_FILTERING=true`
   - Implement data retention policies
   - Add user consent mechanisms

7. **Testing**:
   - Run full evaluation suite: `python main.py evaluate`
   - Achieve ≥80% pass rate before deployment

## Next Steps

Once setup is complete:

1. **Read the README**: Understand the system architecture
2. **Try example queries**: Test different tax scenarios
3. **Review golden dataset**: See expected behaviors in `tests/golden_dataset.py`
4. **Customize**: Add your own tools, knowledge, or nudges
5. **Deploy**: Follow production deployment guidelines above

---

**Need help?** Open an issue on GitHub or check the documentation.
