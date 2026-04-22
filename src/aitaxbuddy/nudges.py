"""Tax nudge system to proactively warn users about ATO audit risks."""

from typing import NamedTuple
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class NudgePriority(str, Enum):
    """Priority level for tax nudges."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class TaxNudge(NamedTuple):
    """A proactive tax guidance nudge."""
    
    title: str
    message: str
    priority: NudgePriority
    ato_reference: str


class TaxNudgeEngine:
    """Engine to detect situations requiring proactive tax guidance."""
    
    # Keyword triggers mapped to nudges
    NUDGE_RULES = {
        "home_office_double_dip": {
            "keywords": [
                "67c",
                "fixed rate",
                "working from home",
                "internet bill",
                "phone bill",
                "electricity",
            ],
            "required_count": 2,
            "nudge": TaxNudge(
                title="⚠️ WARNING: Home Office Double-Dipping",
                message="""CRITICAL AUDIT RISK DETECTED:

You mentioned both the 67c fixed rate method AND separate bills (internet/phone/electricity).

This is "DOUBLE-DIPPING" and is the #1 audit target for 2025.

You MUST choose ONE method:
• Fixed Rate (67c/hour): Covers electricity, gas, internet, phone, stationery
• Actual Cost Method: Claim actual portion of each expense

You CANNOT claim both. The ATO will reject your return and may apply penalties.

Which method would you like to use? I can help you understand both options.""",
                priority=NudgePriority.CRITICAL,
                ato_reference="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/working-from-home-expenses",
            ),
        },
        "commuting_claim": {
            "keywords": ["home to work", "work to home", "commute", "commuting", "travel to work"],
            "required_count": 1,
            "nudge": TaxNudge(
                title="🚫 Non-Deductible: Commuting Expenses",
                message="""IMPORTANT: Travel between home and work (commuting) is NOT tax deductible.

This applies even if you:
• Carry work equipment or tools
• Work irregular hours or overtime
• Live far from work
• Use your car for work purposes during the day

Deductible travel is travel IN THE COURSE of employment (e.g., between job sites), not TO employment.

This is a major ATO audit focus area. Claiming commuting expenses will likely trigger a review.""",
                priority=NudgePriority.CRITICAL,
                ato_reference="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/transport-and-travel-expenses",
            ),
        },
        "crypto_unreported": {
            "keywords": ["crypto", "bitcoin", "ethereum", "cryptocurrency", "sold crypto", "traded"],
            "required_count": 1,
            "nudge": TaxNudge(
                title="📊 Reminder: Crypto Tax Obligations",
                message="""Important reminder about cryptocurrency:

The ATO receives transaction data from Australian crypto exchanges (CoinSpot, Swyftx, etc.).

You MUST declare:
• Selling crypto for AUD
• Trading one crypto for another
• Using crypto to buy goods/services

Each transaction may trigger Capital Gains Tax.

Required records:
• Date and AUD value of each transaction
• What the transaction was for
• The other party (if known)

Crypto is a 2025 audit priority. The ATO WILL know if you traded. Failing to declare is serious.""",
                priority=NudgePriority.WARNING,
                ato_reference="https://www.ato.gov.au/individuals-and-families/investments-and-assets/crypto-asset-investments",
            ),
        },
        "conventional_clothing": {
            "keywords": ["suit", "business attire", "work clothes", "shirt", "dress shoes", "clothes for work"],
            "required_count": 1,
            "nudge": TaxNudge(
                title="👔 Non-Deductible: Conventional Clothing",
                message="""CAUTION: Conventional clothing is NOT tax deductible.

This includes:
• Suits and business attire
• Shirts, pants, skirts, dresses
• Business shoes
• Accessories (watches, jewelry)

Even if your employer requires business attire, conventional clothing is not deductible.

ONLY deductible clothing:
• Occupation-specific (chef whites, nurse scrubs)
• Protective gear (hi-vis, safety boots, hard hats)
• Registered compulsory uniforms with employer logo

Claiming conventional clothing is a common audit trigger.""",
                priority=NudgePriority.WARNING,
                ato_reference="https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/clothing-laundry-and-dry-cleaning-expenses",
            ),
        },
        "side_hustle_unreported": {
            "keywords": ["uber", "doordash", "menulog", "airbnb", "ebay", "facebook marketplace", "side hustle"],
            "required_count": 1,
            "nudge": TaxNudge(
                title="💼 Reminder: Side Hustle Income",
                message="""Important: All side hustle income must be declared.

This includes:
• Rideshare (Uber, Ola, Didi)
• Food delivery (DoorDash, Menulog, Uber Eats)
• Airbnb or short-term rentals
• Online selling (if regular/business-like)
• Freelance or contract work

The ATO receives data from these platforms. They will know what you earned.

Good news: You can claim business expenses against this income (car, phone, supplies).

Need GST registration? Required if you earn over $75,000/year from these activities.

This is a 2025 audit priority area.""",
                priority=NudgePriority.WARNING,
                ato_reference="https://www.ato.gov.au/businesses-and-organisations/starting-your-business/gig-economy",
            ),
        },
        "rental_property_warning": {
            "keywords": ["rental property", "investment property", "negative gearing", "rental deductions"],
            "required_count": 1,
            "nudge": TaxNudge(
                title="🏠 Info: Rental Property Deductions",
                message="""Rental property deduction reminders:

CAN claim:
• Interest on loans (not principal)
• Property management fees
• Council rates, water, insurance
• Repairs and maintenance
• Depreciation (building and assets)

CANNOT claim:
• Principal loan repayments
• Initial repairs (before first tenant)
• Improvements (must depreciate)
• Personal use portion (if holiday home)

Common mistakes:
• Over-claiming interest
• Claiming capital improvements as repairs
• Not keeping proper records

Rental properties are an ATO focus area. Ensure you have receipts for everything.""",
                priority=NudgePriority.INFO,
                ato_reference="https://www.ato.gov.au/individuals-and-families/investments-and-assets/renting-leasing-and-hiring/residential-rental-properties",
            ),
        },
    }
    
    def analyze_query(self, query: str) -> list[TaxNudge]:
        """
        Analyze a user query and return applicable tax nudges.
        
        Args:
            query: The user's query
        
        Returns:
            List of applicable TaxNudge objects
        """
        query_lower = query.lower()
        triggered_nudges = []
        
        for rule_name, rule_config in self.NUDGE_RULES.items():
            keywords = rule_config["keywords"]
            required_count = rule_config["required_count"]
            
            # Count how many keywords appear in the query
            keyword_matches = sum(1 for keyword in keywords if keyword in query_lower)
            
            if keyword_matches >= required_count:
                nudge = rule_config["nudge"]
                triggered_nudges.append(nudge)
                logger.info(f"Triggered nudge: {rule_name} (matched {keyword_matches} keywords)")
        
        # Sort by priority (critical first)
        priority_order = {
            NudgePriority.CRITICAL: 0,
            NudgePriority.WARNING: 1,
            NudgePriority.INFO: 2,
        }
        triggered_nudges.sort(key=lambda n: priority_order[n.priority])
        
        return triggered_nudges
    
    def format_nudge(self, nudge: TaxNudge) -> str:
        """
        Format a nudge for display.
        
        Args:
            nudge: The nudge to format
        
        Returns:
            Formatted nudge string
        """
        return f"""
{nudge.title}

{nudge.message}

📚 ATO Reference: {nudge.ato_reference}
"""


# Global nudge engine instance
nudge_engine = TaxNudgeEngine()
