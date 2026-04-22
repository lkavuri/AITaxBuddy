"""Content guardrails and PII filtering for AI Tax Buddy."""

import re
import logging
from typing import Any
from pydantic import BaseModel

logger = logging.getLogger(__name__)


class GuardrailResult(BaseModel):
    """Result of guardrail check."""
    
    allowed: bool
    modified_content: str
    violations: list[str]
    warnings: list[str]


class ContentGuardrails:
    """Implements safety guardrails and PII filtering."""
    
    # Australian Tax File Number pattern (9 digits, with specific validation)
    TFN_PATTERN = re.compile(r'\b\d{3}[\s-]?\d{3}[\s-]?\d{3}\b')
    
    # Common PII patterns
    EMAIL_PATTERN = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b')
    PHONE_PATTERN = re.compile(r'\b(?:\+?61|0)[2-478](?:[ -]?\d){8}\b')
    ABN_PATTERN = re.compile(r'\b\d{2}[\s-]?\d{3}[\s-]?\d{3}[\s-]?\d{3}\b')
    
    # Prohibited request patterns
    PROHIBITED_PATTERNS = [
        (r'\b(?:file|lodge|submit)\s+(?:my|the)\s+(?:tax\s+)?return', "filing_service"),
        (r'\bdo\s+my\s+taxes\b', "filing_service"),
        (r'\b(?:open|access|login\s+to)\s+myGov\b', "account_access"),
        (r'\b(?:transfer|send|pay)\s+money\b', "financial_transaction"),
        (r'\b(?:invest|buy|sell)\s+(?:in|for\s+me)', "investment_advice"),
        (r'\b(?:should\s+I|recommend)\s+(?:invest|buy)', "specific_advice"),
    ]
    
    DISCLAIMER = """
    
**IMPORTANT DISCLAIMER**: This is general taxation information only and should not be considered as personal financial advice. For specific advice tailored to your circumstances, please consult a registered tax agent or the ATO directly. I cannot lodge tax returns or access your myGov account.
"""
    
    def check_and_filter(self, content: str, context: str = "user") -> GuardrailResult:
        """
        Check content for PII and policy violations.
        
        Args:
            content: The content to check
            context: Context of the content ("user" or "agent")
        
        Returns:
            GuardrailResult with filtered content
        """
        violations = []
        warnings = []
        modified = content
        
        # Check for prohibited requests (only for user input)
        if context == "user":
            for pattern, violation_type in self.PROHIBITED_PATTERNS:
                if re.search(pattern, content, re.IGNORECASE):
                    violations.append(violation_type)
        
        # If violations found, block the request
        if violations:
            return GuardrailResult(
                allowed=False,
                modified_content=content,
                violations=violations,
                warnings=[],
            )
        
        # Filter PII
        pii_found = False
        
        # Redact TFNs
        if self.TFN_PATTERN.search(modified):
            modified = self.TFN_PATTERN.sub("[TFN_REDACTED]", modified)
            warnings.append("Tax File Number detected and redacted")
            pii_found = True
        
        # Redact ABNs
        if self.ABN_PATTERN.search(modified):
            modified = self.ABN_PATTERN.sub("[ABN_REDACTED]", modified)
            warnings.append("ABN detected and redacted")
            pii_found = True
        
        # Redact emails
        if self.EMAIL_PATTERN.search(modified):
            modified = self.EMAIL_PATTERN.sub("[EMAIL_REDACTED]", modified)
            warnings.append("Email address detected and redacted")
            pii_found = True
        
        # Redact phone numbers
        if self.PHONE_PATTERN.search(modified):
            modified = self.PHONE_PATTERN.sub("[PHONE_REDACTED]", modified)
            warnings.append("Phone number detected and redacted")
            pii_found = True
        
        # Redact exact dollar amounts over $1000 to prevent specific advice
        amount_pattern = re.compile(r'\$\d{1,3}(?:,\d{3})+(?:\.\d{2})?')
        amounts = amount_pattern.findall(modified)
        for amount in amounts:
            amount_value = float(amount.replace('$', '').replace(',', ''))
            if amount_value > 1000:
                modified = modified.replace(amount, "[AMOUNT_REDACTED]")
                warnings.append("Large specific amounts redacted to maintain general advice")
        
        return GuardrailResult(
            allowed=True,
            modified_content=modified,
            violations=[],
            warnings=warnings,
        )
    
    def get_prohibition_response(self, violation_type: str) -> str:
        """
        Get the appropriate response for a prohibited request.
        
        Args:
            violation_type: Type of violation detected
        
        Returns:
            Response message
        """
        responses = {
            "filing_service": """I'm designed to provide general tax guidance only. I cannot:
- Lodge or file your tax return
- Submit forms to the ATO
- Access your myGov account

To lodge your tax return, you can:
1. Use myTax through myGov (free)
2. Use commercial tax software
3. Engage a registered tax agent

I'm happy to provide general guidance about deductions and tax rules to help you prepare!""",
            "account_access": """I cannot access, log in to, or interact with your myGov account or any ATO systems. 

For account access issues, please:
1. Visit my.gov.au directly
2. Call the ATO on 13 28 61
3. Visit an ATO shopfront

I can provide general guidance about what information you'll need when lodging your return.""",
            "financial_transaction": """I cannot process any financial transactions, payments, or transfers.

For ATO payments, visit ato.gov.au/make-a-payment or call 13 28 61.

I can provide general information about payment plans and tax debt options.""",
            "investment_advice": """I cannot provide specific investment advice or recommendations.

I can only provide general information about how investments are taxed in Australia. For personalized investment advice, please consult:
1. A licensed financial adviser
2. A registered tax agent
3. The ATO's investor resources at ato.gov.au""",
            "specific_advice": """I provide general taxation information only. I cannot advise you on what specific actions you should take.

For personalized advice considering your specific circumstances, please consult a registered tax agent.

I can explain general rules and help you understand your options!""",
        }
        
        return responses.get(violation_type, "This request falls outside my scope of general tax guidance.")
    
    def add_disclaimer(self, response: str) -> str:
        """
        Add disclaimer to agent responses.
        
        Args:
            response: The response to add disclaimer to
        
        Returns:
            Response with disclaimer
        """
        if not response.strip():
            return response
        
        # Don't add disclaimer if it's already there
        if "IMPORTANT DISCLAIMER" in response:
            return response
        
        return response + self.DISCLAIMER


# Global guardrails instance
guardrails = ContentGuardrails()
