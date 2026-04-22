"""Tests for tax calculation and validation tools."""

import pytest
from src.tools.tax_calculator import calculate_tax_bracket, calculate_medicare_levy
from src.tools.deduction_validator import validate_deduction, RiskLevel


class TestTaxCalculator:
    """Tests for tax calculation tools."""
    
    def test_tax_free_threshold(self):
        """Test income below tax-free threshold."""
        result = calculate_tax_bracket(15000)
        assert result.tax_payable == 0
        assert result.marginal_rate == 0.0
        assert "Tax-free threshold" in result.bracket_description
    
    def test_first_bracket(self):
        """Test income in first tax bracket."""
        result = calculate_tax_bracket(30000)
        expected_tax = (30000 - 18200) * 0.19
        assert result.tax_payable == pytest.approx(expected_tax, abs=0.01)
        assert result.marginal_rate == 0.19
    
    def test_second_bracket(self):
        """Test income in second tax bracket."""
        result = calculate_tax_bracket(80000)
        expected_tax = 5092 + (80000 - 45000) * 0.325
        assert result.tax_payable == pytest.approx(expected_tax, abs=0.01)
        assert result.marginal_rate == 0.325
    
    def test_top_bracket(self):
        """Test income in top tax bracket."""
        result = calculate_tax_bracket(200000)
        expected_tax = 51667 + (200000 - 180000) * 0.45
        assert result.tax_payable == pytest.approx(expected_tax, abs=0.01)
        assert result.marginal_rate == 0.45
    
    def test_effective_rate(self):
        """Test effective tax rate calculation."""
        result = calculate_tax_bracket(80000)
        expected_effective = result.tax_payable / 80000
        assert result.effective_rate == pytest.approx(expected_effective, abs=0.0001)


class TestMedicareLevy:
    """Tests for Medicare levy calculations."""
    
    def test_below_threshold_single(self):
        """Test levy below threshold for single taxpayer."""
        result = calculate_medicare_levy(25000, is_single=True)
        assert result.levy_amount == 0
        assert "Below threshold" in result.threshold_info
    
    def test_shade_in_range(self):
        """Test levy in shade-in range."""
        result = calculate_medicare_levy(30000, is_single=True)
        expected_levy = (30000 - 26000) * 0.1
        assert result.levy_amount == pytest.approx(expected_levy, abs=0.01)
    
    def test_full_rate_single(self):
        """Test full levy rate for single taxpayer."""
        result = calculate_medicare_levy(100000, is_single=True)
        expected_levy = 100000 * 0.02
        assert result.levy_amount == pytest.approx(expected_levy, abs=0.01)
        assert result.levy_rate == 0.02
    
    def test_family_threshold(self):
        """Test levy for family with dependents."""
        result = calculate_medicare_levy(40000, is_single=False, num_dependents=2)
        expected_threshold = 43846 + (4027 * 2)
        assert result.levy_amount == 0
        assert f"${expected_threshold:,.0f}" in result.threshold_info


class TestDeductionValidator:
    """Tests for deduction validation."""
    
    def test_commuting_not_deductible(self):
        """Test that commuting is flagged as non-deductible."""
        result = validate_deduction(
            "car_travel", "Travel from home to work every day", 3000
        )
        assert result.is_likely_valid is False
        assert result.risk_level == RiskLevel.CRITICAL
        assert "commuting" in result.reasoning.lower()
    
    def test_work_related_car_travel_valid(self):
        """Test that legitimate work travel is valid."""
        result = validate_deduction(
            "car_travel", "Travel between client sites during work", 2000
        )
        assert result.is_likely_valid is True
    
    def test_home_office_double_dip(self):
        """Test detection of home office double-dipping."""
        result = validate_deduction(
            "home_office",
            "I claim 67c fixed rate and also claim separate internet bills",
        )
        assert result.is_likely_valid is False
        assert result.risk_level == RiskLevel.CRITICAL
        assert "double-dip" in result.reasoning.lower()
    
    def test_conventional_clothing_invalid(self):
        """Test that conventional clothing is flagged as invalid."""
        result = validate_deduction("clothing", "Business suits for office work")
        assert result.is_likely_valid is False
        assert result.risk_level == RiskLevel.HIGH
        assert "conventional" in result.reasoning.lower()
    
    def test_occupation_specific_clothing_valid(self):
        """Test that occupation-specific clothing is valid."""
        result = validate_deduction("clothing", "Chef whites and safety shoes")
        assert result.is_likely_valid is True
        assert "occupation-specific" in result.reasoning.lower()
    
    def test_self_education_current_job(self):
        """Test self-education related to current job."""
        result = validate_deduction(
            "self_education", "Course to improve skills for current role"
        )
        assert result.is_likely_valid is True
    
    def test_self_education_new_career(self):
        """Test self-education for new career is invalid."""
        result = validate_deduction(
            "self_education", "Course for new career change"
        )
        assert result.is_likely_valid is False
        assert result.risk_level == RiskLevel.HIGH
