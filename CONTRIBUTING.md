# Contributing to AI Tax Buddy

Thank you for your interest in contributing to AI Tax Buddy! This guide will help you get started.

## 🎯 Project Goals

AI Tax Buddy provides **general Australian tax guidance** while operating within strict legal boundaries. All contributions must maintain:

1. **Legal Compliance**: General advice only, no specific financial advice
2. **Safety First**: PII protection, content guardrails, boundary enforcement
3. **Quality**: Accurate information, well-tested code
4. **Transparency**: Clear reasoning, traceable decisions

## 🚀 Getting Started

### 1. Setup Development Environment

```bash
# Fork and clone the repository
git clone https://github.com/yourusername/aitaxbuddy.git
cd aitaxbuddy

# Run automated setup
chmod +x setup.sh
./setup.sh

# Configure your environment
cp .env.example .env
# Add your API keys to .env

# Verify installation
python main.py info
```

### 2. Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test file
pytest tests/test_tools.py -v

# Run agent evaluation
python main.py evaluate
```

### 3. Code Quality

```bash
# Format code
black src/ tests/

# Check linting
ruff check src/ tests/

# Fix auto-fixable issues
ruff check --fix src/ tests/
```

## 📋 Types of Contributions

### 🐛 Bug Fixes
- Fix incorrect tax calculations
- Resolve guardrail bypasses
- Correct PII detection issues
- Fix test failures

### ✨ New Features
- Add new tools (e.g., CGT calculator)
- Expand knowledge base (new ATO topics)
- Add new nudge scenarios
- Enhance memory capabilities

### 📚 Documentation
- Improve README clarity
- Add code examples
- Create tutorials
- Fix typos and errors

### 🧪 Testing
- Add unit tests
- Expand golden dataset
- Improve test coverage
- Add edge case tests

## 🔧 Development Workflow

### 1. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

### 2. Make Changes

Follow these guidelines:

#### Code Style
- Use **Black** for formatting (100 char line length)
- Follow **PEP 8** conventions
- Use **type hints** everywhere
- Write **docstrings** for all functions

Example:
```python
def calculate_tax(income: float) -> TaxBracketResult:
    """
    Calculate Australian tax bracket and tax payable.
    
    Args:
        income: Annual taxable income in AUD
    
    Returns:
        TaxBracketResult with tax calculation details
    """
    # Implementation
```

#### Project Structure
- Tools go in `src/tools/`
- Tests go in `tests/`
- Documentation goes in root
- Config in `src/config.py`

#### Naming Conventions
- Files: `snake_case.py`
- Classes: `PascalCase`
- Functions: `snake_case`
- Constants: `UPPER_CASE`

### 3. Write Tests

**Every contribution must include tests.**

#### For Tools
```python
# tests/test_tools.py
def test_new_tool():
    result = your_new_tool(input_value)
    assert result.expected_field == expected_value
    assert result.is_valid is True
```

#### For Golden Dataset
```python
# tests/golden_dataset.py
GoldenExample(
    query="Test query here",
    expected_behavior="What should happen",
    required_elements=["must", "include", "these"],
    prohibited_elements=["must", "not", "include"],
    risk_areas=["category"],
)
```

### 4. Test Your Changes

```bash
# Run unit tests
pytest tests/ -v

# Run evaluation
python main.py evaluate

# Test interactively
python main.py chat
```

**Requirements**:
- All unit tests pass
- Evaluation pass rate ≥80%
- No regressions in existing tests

### 5. Update Documentation

If your change affects:
- **Usage**: Update README.md
- **Setup**: Update SETUP.md
- **Architecture**: Update ARCHITECTURE.md
- **API**: Update docstrings and type hints

### 6. Commit Changes

Use descriptive commit messages:

```bash
# Good commit messages
git commit -m "Add CGT calculator tool with tests"
git commit -m "Fix PII detection for phone numbers"
git commit -m "Update README with new tool documentation"

# Bad commit messages
git commit -m "fix bug"
git commit -m "updates"
git commit -m "wip"
```

### 7. Push and Create PR

```bash
git push origin feature/your-feature-name
```

Then create a Pull Request on GitHub with:
- **Clear title** describing the change
- **Description** of what and why
- **Test results** (paste evaluation output)
- **Screenshots** if relevant (for UI changes)

## 🎨 Contribution Guidelines

### Legal Boundaries (CRITICAL)

**NEVER**:
- ❌ Add features that provide specific financial advice
- ❌ Add features that file returns or access myGov
- ❌ Add features that process financial transactions
- ❌ Bypass PII protection
- ❌ Weaken content guardrails

**ALWAYS**:
- ✅ Maintain "general advice only" boundary
- ✅ Include disclaimers
- ✅ Protect user privacy
- ✅ Add appropriate warnings

### Code Quality

**Required**:
- Type hints on all functions
- Docstrings with Args and Returns
- Pydantic models for structured data
- Error handling
- Tests for all new code

**Recommended**:
- Keep functions small (<50 lines)
- Avoid deeply nested logic
- Use descriptive variable names
- Comment complex logic only

### Testing Standards

**Unit Tests**:
- Test one thing per test
- Use descriptive test names
- Include edge cases
- Use pytest fixtures for setup

**Golden Dataset**:
- Focus on critical scenarios
- Include boundary violations
- Cover common misconceptions
- Test audit risk warnings

### Documentation Standards

**Code Documentation**:
```python
def example_function(param: str) -> dict:
    """
    Brief description of what the function does.
    
    Longer explanation if needed. Explain WHY, not just WHAT.
    
    Args:
        param: Description of parameter
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When and why this is raised
    """
```

**Markdown Documentation**:
- Use clear headings
- Include code examples
- Add usage instructions
- Link to related docs

## 🧪 Testing Checklist

Before submitting a PR, verify:

- [ ] All unit tests pass: `pytest tests/`
- [ ] Agent evaluation passes: `python main.py evaluate` (≥80%)
- [ ] Code formatted: `black src/ tests/`
- [ ] Linting clean: `ruff check src/ tests/`
- [ ] Type hints added
- [ ] Docstrings written
- [ ] Tests added for new code
- [ ] Documentation updated
- [ ] Golden dataset updated (if needed)
- [ ] No secrets in code (API keys, passwords)
- [ ] Legal boundaries maintained

## 📝 Examples

### Adding a New Tool

```python
# src/tools/cgt_calculator.py
from pydantic import BaseModel, Field

class CGTResult(BaseModel):
    """Capital gains tax calculation result."""
    capital_gain: float
    discount_applied: bool
    net_capital_gain: float

def calculate_cgt(
    proceeds: float,
    cost_base: float,
    holding_period_days: int,
) -> CGTResult:
    """
    Calculate capital gains tax for an asset.
    
    Args:
        proceeds: Sale proceeds in AUD
        cost_base: Cost base in AUD
        holding_period_days: Days asset was held
    
    Returns:
        CGTResult with calculation details
    """
    capital_gain = proceeds - cost_base
    discount_applied = holding_period_days >= 365
    discount = 0.5 if discount_applied else 0.0
    net_capital_gain = capital_gain * (1 - discount)
    
    return CGTResult(
        capital_gain=capital_gain,
        discount_applied=discount_applied,
        net_capital_gain=net_capital_gain,
    )
```

Add test:
```python
# tests/test_tools.py
def test_cgt_with_discount():
    result = calculate_cgt(
        proceeds=10000,
        cost_base=5000,
        holding_period_days=400,
    )
    assert result.capital_gain == 5000
    assert result.discount_applied is True
    assert result.net_capital_gain == 2500
```

Register in agent:
```python
# src/agent.py
@tool
def calculate_capital_gains(...) -> dict:
    """Calculate CGT for asset sales."""
    result = calculate_cgt(...)
    return result.model_dump()
```

### Adding a New Nudge

```python
# src/nudges.py
"investment_property_warning": {
    "keywords": ["investment property", "depreciation", "claim"],
    "required_count": 2,
    "nudge": TaxNudge(
        title="🏠 Investment Property Reminder",
        message="""Important notes about investment properties:
        
        You can claim:
        • Depreciation on building (capital works)
        • Depreciation on assets (fixtures, fittings)
        • Interest on loans (not principal)
        
        You cannot claim:
        • Capital improvements (must depreciate)
        • Initial repairs before rental
        
        Ensure you have a depreciation schedule from a quantity surveyor.""",
        priority=NudgePriority.INFO,
        ato_reference="https://www.ato.gov.au/...",
    ),
}
```

Add golden test:
```python
# tests/golden_dataset.py
GoldenExample(
    query="Can I claim depreciation on my investment property?",
    expected_behavior="Explain depreciation types, requirements",
    required_elements=["capital works", "assets", "quantity surveyor"],
    prohibited_elements=["you should claim everything"],
    risk_areas=["investment_property"],
)
```

## 🤝 Code Review Process

### What Reviewers Look For

1. **Legal Compliance**
   - Maintains general advice boundary
   - No specific recommendations
   - Appropriate disclaimers

2. **Code Quality**
   - Clean, readable code
   - Proper error handling
   - Type safety

3. **Testing**
   - Tests included
   - Tests pass
   - Good coverage

4. **Documentation**
   - Clear docstrings
   - Updated docs
   - Usage examples

### Response to Feedback

- Be open to suggestions
- Discuss design decisions
- Make requested changes promptly
- Ask questions if unclear

## 🐛 Reporting Bugs

When reporting bugs, include:

1. **Description**: What happened vs what should happen
2. **Steps to Reproduce**: Exact steps to trigger the bug
3. **Environment**: OS, Python version, model used
4. **Logs**: Relevant error messages
5. **Expected Behavior**: What should have happened

Example:
```
**Bug**: PII filter misses phone numbers without spaces

**Steps**:
1. Input: "My phone is 0412345678"
2. Run through guardrails
3. Observe: Not redacted

**Environment**: 
- Python 3.10
- macOS 14

**Expected**: Should be redacted as [PHONE_REDACTED]
```

## 📞 Getting Help

- **Questions**: Open a GitHub Discussion
- **Bugs**: Open a GitHub Issue
- **Security**: Email (don't open public issue)
- **Ideas**: Open a GitHub Discussion

## 📜 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## 🙏 Recognition

All contributors will be recognized in the project README.

---

**Thank you for contributing to AI Tax Buddy! Together we can help Australians navigate their taxes more confidently.**
