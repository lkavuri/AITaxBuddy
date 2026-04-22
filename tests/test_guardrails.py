"""Tests for content guardrails and PII filtering."""

import pytest
from src.guardrails import ContentGuardrails


class TestPIIFiltering:
    """Tests for PII detection and redaction."""
    
    def setUp(self):
        self.guardrails = ContentGuardrails()
    
    def test_tfn_redaction(self):
        """Test TFN detection and redaction."""
        guardrails = ContentGuardrails()
        content = "My TFN is 123 456 789"
        result = guardrails.check_and_filter(content)
        
        assert result.allowed is True
        assert "123 456 789" not in result.modified_content
        assert "[TFN_REDACTED]" in result.modified_content
        assert any("Tax File Number" in w for w in result.warnings)
    
    def test_email_redaction(self):
        """Test email detection and redaction."""
        guardrails = ContentGuardrails()
        content = "Contact me at john.doe@example.com"
        result = guardrails.check_and_filter(content)
        
        assert result.allowed is True
        assert "john.doe@example.com" not in result.modified_content
        assert "[EMAIL_REDACTED]" in result.modified_content
    
    def test_phone_redaction(self):
        """Test phone number detection and redaction."""
        guardrails = ContentGuardrails()
        content = "Call me on 0412 345 678"
        result = guardrails.check_and_filter(content)
        
        assert result.allowed is True
        assert "0412 345 678" not in result.modified_content
        assert "[PHONE_REDACTED]" in result.modified_content
    
    def test_abn_redaction(self):
        """Test ABN detection and redaction."""
        guardrails = ContentGuardrails()
        content = "My ABN is 51 824 753 556"
        result = guardrails.check_and_filter(content)
        
        assert result.allowed is True
        assert "51 824 753 556" not in result.modified_content
        assert "[ABN_REDACTED]" in result.modified_content


class TestProhibitedRequests:
    """Tests for prohibited request detection."""
    
    def test_file_return_prohibited(self):
        """Test that filing return requests are blocked."""
        guardrails = ContentGuardrails()
        content = "Can you file my tax return?"
        result = guardrails.check_and_filter(content, context="user")
        
        assert result.allowed is False
        assert "filing_service" in result.violations
    
    def test_lodge_return_prohibited(self):
        """Test that lodge return requests are blocked."""
        guardrails = ContentGuardrails()
        content = "Please lodge my return with ATO"
        result = guardrails.check_and_filter(content, context="user")
        
        assert result.allowed is False
        assert "filing_service" in result.violations
    
    def test_do_my_taxes_prohibited(self):
        """Test that 'do my taxes' requests are blocked."""
        guardrails = ContentGuardrails()
        content = "Can you do my taxes for me?"
        result = guardrails.check_and_filter(content, context="user")
        
        assert result.allowed is False
        assert "filing_service" in result.violations
    
    def test_mygov_access_prohibited(self):
        """Test that myGov access requests are blocked."""
        guardrails = ContentGuardrails()
        content = "Can you login to my myGov account?"
        result = guardrails.check_and_filter(content, context="user")
        
        assert result.allowed is False
        assert "account_access" in result.violations
    
    def test_financial_transaction_prohibited(self):
        """Test that financial transaction requests are blocked."""
        guardrails = ContentGuardrails()
        content = "Can you transfer money to ATO for me?"
        result = guardrails.check_and_filter(content, context="user")
        
        assert result.allowed is False
        assert "financial_transaction" in result.violations
    
    def test_specific_investment_advice_prohibited(self):
        """Test that specific investment advice is blocked."""
        guardrails = ContentGuardrails()
        content = "Should I invest in Bitcoin?"
        result = guardrails.check_and_filter(content, context="user")
        
        assert result.allowed is False
        assert "specific_advice" in result.violations


class TestDisclaimers:
    """Tests for disclaimer addition."""
    
    def test_disclaimer_added(self):
        """Test that disclaimer is added to responses."""
        guardrails = ContentGuardrails()
        response = "Here's some tax information."
        result = guardrails.add_disclaimer(response)
        
        assert "IMPORTANT DISCLAIMER" in result
        assert "general taxation information" in result
    
    def test_disclaimer_not_duplicated(self):
        """Test that disclaimer isn't added twice."""
        guardrails = ContentGuardrails()
        response = "Info\n\n**IMPORTANT DISCLAIMER**: Already here."
        result = guardrails.add_disclaimer(response)
        
        assert result.count("IMPORTANT DISCLAIMER") == 1
