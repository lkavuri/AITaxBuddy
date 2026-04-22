"""ATO knowledge retrieval tool for general tax guidance."""

from typing import Annotated
from pydantic import BaseModel, Field
import logging

logger = logging.getLogger(__name__)


class ATOGuideline(BaseModel):
    """Structured ATO guideline information."""
    
    topic: str
    guideline_text: str
    source_url: str
    last_updated: str
    confidence: float


# Mock ATO knowledge base - In production, this would query GraphRAG/Neo4j
ATO_KNOWLEDGE_BASE = {
    "work_related_expenses": {
        "guideline": """Work-related expenses must meet three golden rules:
        1. You must have spent the money yourself and not been reimbursed
        2. The expense must directly relate to earning your income
        3. You must have a record to prove it (receipt, invoice, etc.)
        
        Common work-related expenses include:
        - Vehicle and travel expenses (with logbook for car claims)
        - Clothing expenses (only occupation-specific, protective, or compulsory uniforms)
        - Home office expenses (using fixed rate method or actual cost method)
        - Self-education expenses (must have connection to current employment)
        
        WARNING: The ATO is targeting overclaiming in 2025. Do NOT claim:
        - Private or domestic travel
        - Normal clothing (suits, business wear)
        - Travel between home and work (commuting)
        """,
        "url": "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/work-related-expenses",
    },
    "home_office": {
        "guideline": """Home office deduction methods (2024-25):
        
        1. FIXED RATE METHOD (67c per hour):
           - Covers electricity, gas, internet, phone, stationery
           - Cannot claim separate deductions for these items
           - Must keep timesheet or diary
        
        2. ACTUAL COST METHOD:
           - Claim actual portion of running expenses
           - Requires detailed records and receipts
           - Can include depreciation of furniture/equipment
        
        CRITICAL WARNING: You CANNOT claim both 67c rate AND separate internet/phone bills.
        This is "double-dipping" and is an ATO audit trigger for 2025.
        """,
        "url": "https://www.ato.gov.au/individuals-and-families/income-deductions-offsets-and-records/deductions-you-can-claim/working-from-home-expenses",
    },
    "crypto": {
        "guideline": """Cryptocurrency tax rules (Australia):
        
        CGT applies to crypto transactions including:
        - Selling crypto for fiat currency
        - Trading one crypto for another
        - Using crypto to purchase goods/services
        - Gifting crypto (except to spouse)
        
        Records required for EVERY transaction:
        - Date of transaction
        - Value in AUD at time of transaction
        - What the transaction was for
        - Who the other party was
        
        ATO DATA MATCHING: The ATO receives data from Australian crypto exchanges.
        They WILL know if you traded crypto. Failing to declare is a serious offense.
        
        2025 FOCUS AREA: The ATO is heavily auditing crypto traders who:
        - Failed to declare any crypto income
        - Claimed crypto losses without proper records
        - Used offshore exchanges to hide transactions
        """,
        "url": "https://www.ato.gov.au/individuals-and-families/investments-and-assets/crypto-asset-investments",
    },
    "side_hustle": {
        "guideline": """Side hustle and gig economy income:
        
        ALL income must be declared, including:
        - Uber/DoorDash/Menulog driving
        - Airbnb rental income
        - Online selling (eBay, Facebook Marketplace if regular)
        - Freelance work (ABN or not)
        - Sharing economy platforms
        
        When to get an ABN:
        - If your side hustle earns over $75,000/year, you MUST register for GST
        - Below $75k, ABN is optional but recommended
        
        Deductions available:
        - Portion of vehicle expenses (need logbook)
        - Phone and internet (work-related portion)
        - Equipment and supplies
        - Marketing and advertising
        
        2025 AUDIT TARGET: ATO is matching data from platforms.
        They know what you earned. Declare it all.
        """,
        "url": "https://www.ato.gov.au/businesses-and-organisations/starting-your-business/gig-economy",
    },
    "rental_property": {
        "guideline": """Rental property deductions:
        
        Can claim:
        - Interest on loans (not principal repayments)
        - Property management fees
        - Council rates, water charges, insurance
        - Repairs and maintenance (immediate deduction)
        - Depreciation (capital works and assets)
        
        Cannot claim:
        - Initial repairs (before property is rented)
        - Improvements (must depreciate over time)
        - Travel expenses to inspect property (limited)
        
        NEGATIVE GEARING: If expenses exceed rental income, loss can offset other income.
        
        WARNING: Over-claiming rental deductions is a major ATO focus area.
        """,
        "url": "https://www.ato.gov.au/individuals-and-families/investments-and-assets/renting-leasing-and-hiring/residential-rental-properties",
    },
}


def query_ato_guidelines(
    topic: Annotated[
        str,
        Field(
            description="Tax topic to query: work_related_expenses, home_office, crypto, side_hustle, or rental_property"
        ),
    ]
) -> ATOGuideline:
    """
    Query the ATO knowledge base for general tax guidelines.
    
    This tool provides GENERAL ADVICE only based on publicly available ATO guidance.
    It does NOT provide specific financial advice tailored to individual circumstances.
    
    Args:
        topic: The tax topic to query
    
    Returns:
        ATOGuideline with general information
    """
    topic_key = topic.lower().replace(" ", "_")
    
    if topic_key not in ATO_KNOWLEDGE_BASE:
        logger.warning(f"Unknown topic requested: {topic}")
        return ATOGuideline(
            topic=topic,
            guideline_text="I don't have specific information on that topic. Please refer to ato.gov.au or consult a registered tax agent.",
            source_url="https://www.ato.gov.au",
            last_updated="2024-07-01",
            confidence=0.0,
        )
    
    knowledge = ATO_KNOWLEDGE_BASE[topic_key]
    
    return ATOGuideline(
        topic=topic,
        guideline_text=knowledge["guideline"],
        source_url=knowledge["url"],
        last_updated="2024-07-01",
        confidence=0.95,
    )
