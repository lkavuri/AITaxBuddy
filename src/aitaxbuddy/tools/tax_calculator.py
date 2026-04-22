"""Deterministic tax calculation tools for Australian tax system."""

from typing import Annotated
from pydantic import BaseModel, Field


class TaxBracketResult(BaseModel):
    """Result from tax bracket calculation."""
    
    taxable_income: float
    tax_payable: float
    effective_rate: float
    marginal_rate: float
    bracket_description: str


class MedicareLevyResult(BaseModel):
    """Result from Medicare levy calculation."""
    
    income: float
    levy_amount: float
    levy_rate: float
    threshold_info: str


def calculate_tax_bracket(
    taxable_income: Annotated[float, Field(description="Annual taxable income in AUD", gt=0)]
) -> TaxBracketResult:
    """
    Calculate Australian tax bracket and tax payable for FY 2024-25.
    
    This is a deterministic calculation based on ATO tax rates.
    Does NOT provide personalized advice.
    
    Tax Brackets (2024-25):
    - $0 - $18,200: 0%
    - $18,201 - $45,000: 19%
    - $45,001 - $120,000: 32.5%
    - $120,001 - $180,000: 37%
    - $180,001+: 45%
    
    Args:
        taxable_income: Annual taxable income in AUD
    
    Returns:
        TaxBracketResult with tax calculation details
    """
    income = float(taxable_income)
    tax = 0.0
    marginal_rate = 0.0
    bracket_desc = ""
    
    if income <= 18200:
        tax = 0
        marginal_rate = 0.0
        bracket_desc = "Tax-free threshold"
    elif income <= 45000:
        tax = (income - 18200) * 0.19
        marginal_rate = 0.19
        bracket_desc = "$18,201 - $45,000 (19%)"
    elif income <= 120000:
        tax = 5092 + (income - 45000) * 0.325
        marginal_rate = 0.325
        bracket_desc = "$45,001 - $120,000 (32.5%)"
    elif income <= 180000:
        tax = 29467 + (income - 120000) * 0.37
        marginal_rate = 0.37
        bracket_desc = "$120,001 - $180,000 (37%)"
    else:
        tax = 51667 + (income - 180000) * 0.45
        marginal_rate = 0.45
        bracket_desc = "$180,001+ (45%)"
    
    effective_rate = (tax / income) if income > 0 else 0.0
    
    return TaxBracketResult(
        taxable_income=income,
        tax_payable=round(tax, 2),
        effective_rate=round(effective_rate, 4),
        marginal_rate=marginal_rate,
        bracket_description=bracket_desc,
    )


def calculate_medicare_levy(
    income: Annotated[float, Field(description="Annual income in AUD", gt=0)],
    is_single: Annotated[bool, Field(description="Is taxpayer single (vs family)")] = True,
    num_dependents: Annotated[int, Field(description="Number of dependent children", ge=0)] = 0,
) -> MedicareLevyResult:
    """
    Calculate Medicare Levy for FY 2024-25.
    
    Standard rate is 2% of taxable income, with low-income thresholds.
    
    Thresholds (2024-25):
    - Single: $26,000
    - Family: $43,846 + $4,027 per dependent child
    
    Args:
        income: Annual income in AUD
        is_single: Whether taxpayer is single
        num_dependents: Number of dependent children
    
    Returns:
        MedicareLevyResult with levy calculation
    """
    base_rate = 0.02
    
    if is_single:
        threshold = 26000
        shade_in_threshold = 32500
    else:
        threshold = 43846 + (4027 * num_dependents)
        shade_in_threshold = threshold * 1.25
    
    if income <= threshold:
        levy = 0.0
        threshold_info = f"Below threshold (${threshold:,.0f})"
    elif income <= shade_in_threshold:
        levy = (income - threshold) * 0.1
        threshold_info = f"Shade-in range (${threshold:,.0f} - ${shade_in_threshold:,.0f})"
    else:
        levy = income * base_rate
        threshold_info = f"Standard rate applies"
    
    return MedicareLevyResult(
        income=income,
        levy_amount=round(levy, 2),
        levy_rate=base_rate if income > shade_in_threshold else round(levy / income, 4),
        threshold_info=threshold_info,
    )
