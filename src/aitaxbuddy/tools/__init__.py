"""Tool definitions for the AI Tax Buddy agent."""

from aitaxbuddy.tools.tax_calculator import calculate_tax_bracket, calculate_medicare_levy
from aitaxbuddy.tools.ato_knowledge import query_ato_guidelines
from aitaxbuddy.tools.deduction_validator import validate_deduction

__all__ = [
    "calculate_tax_bracket",
    "calculate_medicare_levy",
    "query_ato_guidelines",
    "validate_deduction",
]
