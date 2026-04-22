"""Tool to validate common tax deduction scenarios and identify audit risks."""

from typing import Annotated
from pydantic import BaseModel, Field
from enum import Enum


class RiskLevel(str, Enum):
    """Risk level for audit attention."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class DeductionValidation(BaseModel):
    """Result of deduction validation."""
    
    deduction_type: str
    is_likely_valid: bool
    risk_level: RiskLevel
    reasoning: str
    warnings: list[str]
    required_evidence: list[str]


def validate_deduction(
    deduction_type: Annotated[
        str,
        Field(description="Type of deduction: car, home_office, clothing, travel, self_education, etc."),
    ],
    description: Annotated[
        str, Field(description="Description of the expense and how it relates to work")
    ],
    amount: Annotated[float, Field(description="Claimed amount in AUD", gt=0)] | None = None,
) -> DeductionValidation:
    """
    Validate a proposed tax deduction against ATO rules and flag audit risks.
    
    This provides GENERAL guidance on whether a deduction type typically qualifies.
    It does NOT constitute specific financial advice.
    
    Args:
        deduction_type: Category of deduction
        description: Details about the expense
        amount: Claimed amount (optional, for risk assessment)
    
    Returns:
        DeductionValidation with risk assessment
    """
    deduction_type = deduction_type.lower()
    description_lower = description.lower()
    
    # Car expenses validation
    if "car" in deduction_type or "vehicle" in deduction_type:
        warnings = []
        risk_level = RiskLevel.LOW
        
        if "home" in description_lower and "work" in description_lower:
            return DeductionValidation(
                deduction_type="car_travel",
                is_likely_valid=False,
                risk_level=RiskLevel.CRITICAL,
                reasoning="Travel between home and work (commuting) is NOT deductible under ATO rules, even if you carry work equipment or work long hours.",
                warnings=[
                    "Commuting is explicitly non-deductible",
                    "This is a common audit trigger",
                    "Claiming this could result in penalties",
                ],
                required_evidence=[],
            )
        
        if amount and amount > 5000:
            warnings.append("Claims over $5,000 require logbook method")
            risk_level = RiskLevel.MEDIUM
        
        return DeductionValidation(
            deduction_type="car_travel",
            is_likely_valid=True,
            risk_level=risk_level,
            reasoning="Car travel for work purposes (excluding commuting) is generally deductible. Must be travel IN THE COURSE of employment, not TO employment.",
            warnings=warnings,
            required_evidence=[
                "Logbook if claiming over $5,000",
                "Record of work-related kilometers",
                "Documentation of business purpose for trips",
            ],
        )
    
    # Home office validation
    elif "home" in deduction_type and "office" in deduction_type:
        warnings = []
        risk_level = RiskLevel.LOW
        
        # Check for double-dipping
        if any(
            term in description_lower
            for term in ["internet", "phone", "electricity", "67c", "fixed rate"]
        ):
            if "separate" in description_lower or "also" in description_lower:
                return DeductionValidation(
                    deduction_type="home_office",
                    is_likely_valid=False,
                    risk_level=RiskLevel.CRITICAL,
                    reasoning="DOUBLE-DIPPING DETECTED: You cannot claim the 67c fixed rate AND separate internet/phone/electricity bills. This is the #1 audit trigger for 2025.",
                    warnings=[
                        "Choose either fixed rate (67c) OR actual costs",
                        "Cannot claim both methods simultaneously",
                        "ATO has flagged this as a priority audit area",
                    ],
                    required_evidence=[],
                )
        
        return DeductionValidation(
            deduction_type="home_office",
            is_likely_valid=True,
            risk_level=risk_level,
            reasoning="Home office expenses are deductible if you work from home for employment. Choose fixed rate (67c/hr) or actual cost method, not both.",
            warnings=warnings,
            required_evidence=[
                "Timesheet or diary of hours worked from home",
                "If using actual cost: receipts for all expenses",
                "Floor plan showing dedicated workspace (for actual cost)",
            ],
        )
    
    # Clothing validation
    elif "clothing" in deduction_type or "uniform" in deduction_type:
        occupation_specific = any(
            word in description_lower
            for word in ["chef", "nurse", "tradesperson", "protective", "safety", "hi-vis", "logo"]
        )
        
        conventional = any(
            word in description_lower for word in ["suit", "business", "shirt", "dress", "shoes"]
        )
        
        if conventional and not occupation_specific:
            return DeductionValidation(
                deduction_type="clothing",
                is_likely_valid=False,
                risk_level=RiskLevel.HIGH,
                reasoning="Conventional clothing (suits, business attire) is NOT deductible even if required for work. Only occupation-specific, protective, or compulsory uniforms qualify.",
                warnings=[
                    "Conventional clothing is explicitly non-deductible",
                    "High audit risk if claimed",
                ],
                required_evidence=[],
            )
        
        return DeductionValidation(
            deduction_type="clothing",
            is_likely_valid=occupation_specific,
            risk_level=RiskLevel.MEDIUM if occupation_specific else RiskLevel.HIGH,
            reasoning="Only occupation-specific clothing, protective gear, or registered compulsory uniforms are deductible.",
            warnings=["Must be unique to your occupation or compulsory"],
            required_evidence=[
                "Receipts for purchases",
                "Evidence uniform is compulsory or occupation-specific",
            ],
        )
    
    # Self-education validation
    elif "education" in deduction_type or "course" in deduction_type:
        is_work_related = any(
            word in description_lower for word in ["current", "job", "employment", "role"]
        )
        
        is_new_career = any(
            word in description_lower for word in ["new", "career change", "different", "unrelated"]
        )
        
        if is_new_career:
            return DeductionValidation(
                deduction_type="self_education",
                is_likely_valid=False,
                risk_level=RiskLevel.HIGH,
                reasoning="Self-education for a NEW career or unrelated to CURRENT employment is NOT deductible.",
                warnings=["Must relate to current employment, not future career"],
                required_evidence=[],
            )
        
        return DeductionValidation(
            deduction_type="self_education",
            is_likely_valid=is_work_related,
            risk_level=RiskLevel.LOW if is_work_related else RiskLevel.MEDIUM,
            reasoning="Self-education is deductible if it maintains or improves skills for CURRENT employment.",
            warnings=["Must have sufficient connection to current role"],
            required_evidence=[
                "Course receipts",
                "Evidence of connection to current employment",
                "Employer confirmation if required by employer",
            ],
        )
    
    # Generic validation
    else:
        return DeductionValidation(
            deduction_type=deduction_type,
            is_likely_valid=True,
            risk_level=RiskLevel.MEDIUM,
            reasoning="This deduction may be valid if it meets the three golden rules: you spent the money, it relates to earning income, and you have records.",
            warnings=["Ensure you meet all three golden rules"],
            required_evidence=[
                "Receipt or invoice",
                "Evidence of work-related purpose",
                "Record of payment",
            ],
        )
