"""
Annuity Engine - Single Premium Immediate Annuities (SPIA), Deferred Income Annuities (DIA), and QLACs
======================================================================================================

This module implements actuarially-sound annuity pricing and payout calculations for:
1. SPIA (Single Premium Immediate Annuity) - Payments start immediately
2. DIA (Deferred Income Annuity) - Payments start at future date
3. QLAC (Qualified Longevity Annuity Contract) - Special IRA-funded DIA

PRICING METHODOLOGY:
-------------------
Annuity pricing uses:
- Mortality tables (SOA 2012 Individual Annuity Mortality - simplified)
- Discount rate (insurance company's return assumption)
- Longevity credit (benefit from pooling mortality risk)
- Load factors (insurance company profit margin and expenses)

ACTUARIAL PRINCIPLES:
--------------------
Present Value of Life Annuity:
PV = Σ [PMT * p(t) * v^t]

where:
- PMT = annual payment
- p(t) = probability of survival to time t
- v = discount factor = 1/(1+r)
- r = discount rate

Longevity Credit:
The "insurance value" comes from pooling:
- Those who die early subsidize those who live long
- Credit = difference between individual life expectancy and pool average
- Higher longevity credit for older purchasers

PRICING SPREAD:
--------------
Market Price = Actuarial Value * (1 + Load Factor)

Typical loads:
- SPIA: 5-10% markup
- DIA: 8-12% markup (higher due to longer duration risk)
- QLAC: 6-10% markup
"""

import numpy as np
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from enum import Enum
import logging

from core.longevity_engine import (
    LongevityEngine,
    LongevityParameters,
    Gender,
    HealthStatus
)

logger = logging.getLogger(__name__)


class AnnuityType(Enum):
    """Types of annuity products"""
    SPIA = "spia"  # Single Premium Immediate Annuity
    DIA = "dia"    # Deferred Income Annuity
    QLAC = "qlac"  # Qualified Longevity Annuity Contract


class PayoutFrequency(Enum):
    """Payment frequency options"""
    MONTHLY = 12
    QUARTERLY = 4
    SEMI_ANNUAL = 2
    ANNUAL = 1


class LifeOption(Enum):
    """Life coverage options"""
    LIFE_ONLY = "life_only"              # Payments for life, nothing at death
    LIFE_WITH_10_CERTAIN = "10_certain"  # Minimum 10 years of payments
    LIFE_WITH_20_CERTAIN = "20_certain"  # Minimum 20 years of payments
    JOINT_LIFE = "joint_life"            # Payments until both spouses die
    JOINT_SURVIVOR_100 = "joint_100"     # 100% to survivor
    JOINT_SURVIVOR_50 = "joint_50"       # 50% to survivor


@dataclass
class AnnuityQuote:
    """
    Annuity pricing quote with all details.
    """
    annuity_type: AnnuityType
    premium: float                       # Lump sum payment
    annual_payout: float                 # Annual income amount
    monthly_payout: float                # Monthly income amount
    payout_rate: float                   # Annual payout / premium
    
    # Actuarial metrics
    expected_total_payments: float       # Expected lifetime payments
    expected_years_of_payments: float    # Expected duration
    longevity_credit: float              # Value of mortality pooling
    breakeven_years: float               # Years to recover premium
    
    # Present value analysis
    actuarial_present_value: float       # Fair value
    load_factor: float                   # Markup percentage
    insurance_company_margin: float      # Dollar amount of profit
    
    # Demographics
    purchase_age: int
    start_age: int                       # When payments begin
    deferral_years: int                  # Years until payments start
    life_expectancy: float
    
    # Product features
    life_option: LifeOption
    cola_pct: float                      # Annual inflation adjustment
    has_refund: bool                     # Return of premium at death
    
    # Tax considerations
    exclusion_ratio: float               # % of payment tax-free
    taxable_portion_pct: float           # % subject to ordinary income


@dataclass
class QLACSpecialRules:
    """
    QLAC-specific IRS rules and limitations.
    """
    max_premium_pct: float = 0.25        # 25% of IRA balance
    max_premium_dollar: float = 200_000  # 2024 limit (indexed)
    max_start_age: int = 85              # Must start by 85
    rmd_exclusion: bool = True           # Excluded from RMD calculations
    must_be_ira_funded: bool = True      # Can't use taxable money


class AnnuityEngine:
    """
    Actuarially-sound annuity pricing and analysis engine.
    
    Uses proper mortality tables, discount rates, and insurance company
    pricing conventions to generate realistic annuity quotes.
    """
    
    def __init__(self, seed: Optional[int] = None):
        """
        Initialize annuity pricing engine.
        
        Args:
            seed: Random seed for Monte Carlo simulations
        """
        self.seed = seed
        self.longevity_engine = LongevityEngine(seed=seed)
        
        # Insurance company pricing assumptions
        self.discount_rate = 0.045  # 4.5% return assumption
        self.load_factor_spia = 0.07  # 7% markup for SPIA
        self.load_factor_dia = 0.10  # 10% markup for DIA (longer duration)
        self.load_factor_qlac = 0.08  # 8% markup for QLAC
        
        logger.info("✓ Annuity engine initialized")
    
    def quote_spia(
        self,
        premium: float,
        age: int,
        gender: Gender = Gender.MALE,
        health_status: HealthStatus = HealthStatus.AVERAGE,
        life_option: LifeOption = LifeOption.LIFE_ONLY,
        cola_pct: float = 0.0,
        frequency: PayoutFrequency = PayoutFrequency.MONTHLY,
        smoker: bool = False
    ) -> AnnuityQuote:
        """
        Price a Single Premium Immediate Annuity (SPIA).
        
        SPIA characteristics:
        - Payments start immediately (within 1 year)
        - Irrevocable - cannot get premium back
        - Provides longevity insurance
        - Taxed partially (exclusion ratio)
        
        Args:
            premium: Lump sum investment
            age: Purchase age
            gender: Male or female (affects mortality)
            health_status: Health condition (affects mortality)
            life_option: Payment structure (life only, period certain, joint)
            cola_pct: Annual cost-of-living adjustment (0 = level payments)
            frequency: Payment frequency
            smoker: Smoking status
            
        Returns:
            AnnuityQuote with pricing and actuarial analysis
        """
        logger.info(f"Pricing SPIA: ${premium:,.0f} premium, age {age}, {gender.value}, {life_option.value}")
        
        # Build mortality parameters
        params = LongevityParameters(
            current_age=age,
            gender=gender,
            health_status=health_status,
            smoker=smoker
        )
        
        # Calculate life expectancy
        death_ages = self.longevity_engine.simulate_lifetime(params, n_scenarios=10000)
        life_expectancy = np.mean(death_ages)
        expected_years = life_expectancy - age
        
        # Calculate actuarial present value
        apv = self._calculate_annuity_present_value(
            age=age,
            params=params,
            life_option=life_option,
            cola_pct=cola_pct,
            n_years=int(expected_years * 2)  # Project to tail
        )
        
        # Add load factor for market price
        market_pv = apv * (1 + self.load_factor_spia)
        
        # Calculate annual payout
        # Premium = PV of payments, so Payment = Premium / PV_factor
        annual_payout = premium / market_pv
        monthly_payout = annual_payout / 12.0
        
        # Payout rate (quoted as % of premium)
        payout_rate = annual_payout / premium
        
        # Expected total payments (not discounted)
        expected_total = annual_payout * expected_years
        
        # Longevity credit calculation
        # This is the value of mortality pooling
        # Those who die early subsidize those who live long
        certain_annuity_pv = self._calculate_certain_annuity_pv(
            annual_payment=annual_payout,
            n_years=expected_years,
            discount_rate=self.discount_rate
        )
        longevity_credit = market_pv - certain_annuity_pv
        
        # Breakeven analysis
        breakeven_years = premium / annual_payout
        
        # Tax treatment (exclusion ratio)
        # Portion of each payment considered return of principal (tax-free)
        total_expected_payments = annual_payout * expected_years
        exclusion_ratio = min(1.0, premium / total_expected_payments)
        taxable_portion = 1.0 - exclusion_ratio
        
        # Build quote
        quote = AnnuityQuote(
            annuity_type=AnnuityType.SPIA,
            premium=premium,
            annual_payout=annual_payout,
            monthly_payout=monthly_payout,
            payout_rate=payout_rate,
            expected_total_payments=expected_total,
            expected_years_of_payments=expected_years,
            longevity_credit=longevity_credit,
            breakeven_years=breakeven_years,
            actuarial_present_value=apv,
            load_factor=self.load_factor_spia,
            insurance_company_margin=premium - (premium / (1 + self.load_factor_spia)),
            purchase_age=age,
            start_age=age,
            deferral_years=0,
            life_expectancy=life_expectancy,
            life_option=life_option,
            cola_pct=cola_pct,
            has_refund=False,
            exclusion_ratio=exclusion_ratio,
            taxable_portion_pct=taxable_portion
        )
        
        logger.info(f"✓ SPIA quote: ${annual_payout:,.0f}/year ({payout_rate:.2%} rate)")
        logger.info(f"  Longevity credit: ${longevity_credit:,.0f}")
        logger.info(f"  Breakeven: {breakeven_years:.1f} years")
        
        return quote
    
    def quote_dia(
        self,
        premium: float,
        purchase_age: int,
        start_age: int,
        gender: Gender = Gender.MALE,
        health_status: HealthStatus = HealthStatus.AVERAGE,
        life_option: LifeOption = LifeOption.LIFE_ONLY,
        cola_pct: float = 0.0,
        smoker: bool = False
    ) -> AnnuityQuote:
        """
        Price a Deferred Income Annuity (DIA).
        
        DIA characteristics:
        - Payments start at future date (typically 5-20 years later)
        - Much higher payout rate than SPIA (time value of money)
        - Good for "longevity insurance" - insure against living too long
        - Premium locked in today, payments start later
        
        Typical use case:
        - Age 65: Pay $100,000 premium
        - Age 80: Start receiving $20,000/year for life
        - Insures against running out of money in late life
        
        Args:
            premium: Lump sum today
            purchase_age: Age when buying DIA
            start_age: Age when payments begin
            gender: Male or female
            health_status: Health condition
            life_option: Payment structure
            cola_pct: Annual adjustment
            smoker: Smoking status
            
        Returns:
            AnnuityQuote for deferred annuity
        """
        deferral_years = start_age - purchase_age
        
        if deferral_years < 1:
            raise ValueError(f"DIA must have deferral period (start_age {start_age} > purchase_age {purchase_age})")
        
        logger.info(f"Pricing DIA: ${premium:,.0f} at age {purchase_age}, start at {start_age} ({deferral_years}y deferral)")
        
        # Mortality at START age (not purchase age)
        params = LongevityParameters(
            current_age=start_age,
            gender=gender,
            health_status=health_status,
            smoker=smoker
        )
        
        death_ages = self.longevity_engine.simulate_lifetime(params, n_scenarios=10000)
        life_expectancy_at_start = np.mean(death_ages)
        expected_years_of_payments = life_expectancy_at_start - start_age
        
        # Calculate present value AT START DATE
        apv_at_start = self._calculate_annuity_present_value(
            age=start_age,
            params=params,
            life_option=life_option,
            cola_pct=cola_pct,
            n_years=int(expected_years_of_payments * 2)
        )
        
        # Discount back to PURCHASE DATE
        # PV_today = PV_future / (1+r)^years
        discount_factor = (1 + self.discount_rate) ** deferral_years
        apv_today = apv_at_start / discount_factor
        
        # Add DIA load factor (higher than SPIA due to duration risk)
        market_pv_today = apv_today * (1 + self.load_factor_dia)
        
        # Calculate annual payout AT START
        annual_payout = premium / market_pv_today
        monthly_payout = annual_payout / 12.0
        
        # Payout rate
        payout_rate = annual_payout / premium
        
        # Expected total (not discounted)
        expected_total = annual_payout * expected_years_of_payments
        
        # Longevity credit
        certain_pv_at_start = self._calculate_certain_annuity_pv(
            annual_payment=annual_payout,
            n_years=expected_years_of_payments,
            discount_rate=self.discount_rate
        )
        certain_pv_today = certain_pv_at_start / discount_factor
        longevity_credit = market_pv_today - certain_pv_today
        
        # Breakeven
        breakeven_years = premium / annual_payout
        
        # Tax treatment
        total_expected_payments = annual_payout * expected_years_of_payments
        exclusion_ratio = min(1.0, premium / total_expected_payments)
        
        quote = AnnuityQuote(
            annuity_type=AnnuityType.DIA,
            premium=premium,
            annual_payout=annual_payout,
            monthly_payout=monthly_payout,
            payout_rate=payout_rate,
            expected_total_payments=expected_total,
            expected_years_of_payments=expected_years_of_payments,
            longevity_credit=longevity_credit,
            breakeven_years=breakeven_years,
            actuarial_present_value=apv_today,
            load_factor=self.load_factor_dia,
            insurance_company_margin=premium - (premium / (1 + self.load_factor_dia)),
            purchase_age=purchase_age,
            start_age=start_age,
            deferral_years=deferral_years,
            life_expectancy=life_expectancy_at_start,
            life_option=life_option,
            cola_pct=cola_pct,
            has_refund=False,
            exclusion_ratio=exclusion_ratio,
            taxable_portion_pct=1.0 - exclusion_ratio
        )
        
        logger.info(f"✓ DIA quote: ${annual_payout:,.0f}/year starting age {start_age} ({payout_rate:.2%} rate)")
        logger.info(f"  {deferral_years} year deferral increases payout by {payout_rate/0.05:.1f}x vs immediate")
        
        return quote
    
    def quote_qlac(
        self,
        premium: float,
        purchase_age: int,
        start_age: int,
        ira_balance: float,
        gender: Gender = Gender.MALE,
        health_status: HealthStatus = HealthStatus.AVERAGE,
        life_option: LifeOption = LifeOption.LIFE_ONLY,
        smoker: bool = False
    ) -> Tuple[AnnuityQuote, QLACSpecialRules]:
        """
        Price a Qualified Longevity Annuity Contract (QLAC).
        
        QLAC is a special type of DIA with unique tax benefits:
        - Funded from IRA/401(k) (pre-tax money)
        - Excluded from RMD calculations
        - Must start by age 85
        - Limited to lesser of $200k or 25% of IRA balance
        
        Key Benefit:
        - Reducing RMDs by moving money to QLAC
        - This can reduce lifetime taxes and Medicare premiums
        
        Example:
        - $1M IRA at age 70
        - Move $200k to QLAC (max allowed)
        - RMDs now based on $800k instead of $1M
        - Save ~$5k/year in RMDs for 15 years = $75k savings
        
        Args:
            premium: Amount from IRA
            purchase_age: Age when buying
            start_age: When payments begin (max 85)
            ira_balance: Total IRA balance (for limit calc)
            gender: Male or female
            health_status: Health status
            life_option: Payment structure
            smoker: Smoking status
            
        Returns:
            Tuple of (AnnuityQuote, QLACSpecialRules with validation)
        """
        # QLAC compliance checks
        rules = QLACSpecialRules()
        
        # Check premium limits
        max_premium_25_pct = ira_balance * rules.max_premium_pct
        max_premium = min(max_premium_25_pct, rules.max_premium_dollar)
        
        if premium > max_premium:
            logger.warning(f"QLAC premium ${premium:,.0f} exceeds limit ${max_premium:,.0f}")
            raise ValueError(f"QLAC premium cannot exceed lesser of $200k or 25% of IRA (${max_premium:,.0f})")
        
        # Check start age
        if start_age > rules.max_start_age:
            raise ValueError(f"QLAC must start by age {rules.max_start_age}, requested {start_age}")
        
        logger.info(f"Pricing QLAC: ${premium:,.0f} from ${ira_balance:,.0f} IRA")
        logger.info(f"  Start age {start_age} (within limit {rules.max_start_age})")
        
        # Price as DIA (same actuarial structure)
        base_quote = self.quote_dia(
            premium=premium,
            purchase_age=purchase_age,
            start_age=start_age,
            gender=gender,
            health_status=health_status,
            life_option=life_option,
            cola_pct=0.0,  # QLACs typically don't have COLA
            smoker=smoker
        )
        
        # Modify for QLAC specifics
        base_quote.annuity_type = AnnuityType.QLAC
        base_quote.load_factor = self.load_factor_qlac
        
        # Tax treatment different for QLAC
        # ALL payments from QLAC are ordinary income (pre-tax money)
        base_quote.exclusion_ratio = 0.0
        base_quote.taxable_portion_pct = 1.0
        
        logger.info(f"✓ QLAC quote: ${base_quote.annual_payout:,.0f}/year starting age {start_age}")
        logger.info(f"  RMD exclusion saves on ${premium:,.0f} for {start_age - purchase_age} years")
        
        return base_quote, rules
    
    def _calculate_annuity_present_value(
        self,
        age: int,
        params: LongevityParameters,
        life_option: LifeOption,
        cola_pct: float,
        n_years: int = 50
    ) -> float:
        """
        Calculate actuarial present value of $1/year annuity.
        
        Uses proper mortality tables and discount factors.
        
        Formula:
        APV = Σ [PMT * p(t) * v^t]
        where:
        - PMT = payment in year t (adjusted for COLA)
        - p(t) = survival probability to year t
        - v = 1/(1+discount_rate)
        
        Args:
            age: Starting age
            params: Mortality parameters
            life_option: Life only, period certain, joint, etc.
            cola_pct: Annual inflation adjustment
            n_years: Maximum years to project
            
        Returns:
            Present value per dollar of annual payment
        """
        # Calculate survival probabilities
        survival_probs = self._calculate_survival_probabilities(age, params, n_years)
        
        # Discount factors
        discount_factors = np.array([(1 / (1 + self.discount_rate)) ** t for t in range(n_years)])
        
        # Payment amounts (adjust for COLA)
        if cola_pct > 0:
            payment_factors = np.array([(1 + cola_pct) ** t for t in range(n_years)])
        else:
            payment_factors = np.ones(n_years)
        
        # Handle period certain options
        if life_option == LifeOption.LIFE_WITH_10_CERTAIN:
            # Guarantee 10 years of payments regardless of survival
            survival_probs[:10] = 1.0
        elif life_option == LifeOption.LIFE_WITH_20_CERTAIN:
            survival_probs[:20] = 1.0
        
        # Present value calculation
        pv = np.sum(payment_factors * survival_probs * discount_factors)
        
        return pv
    
    def _calculate_survival_probabilities(
        self,
        age: int,
        params: LongevityParameters,
        n_years: int
    ) -> np.ndarray:
        """
        Calculate probability of surviving to each future year.
        
        Uses Gompertz-Makeham mortality model.
        
        Args:
            age: Starting age
            params: Mortality parameters
            n_years: Years to project
            
        Returns:
            Array of survival probabilities [p(1), p(2), ..., p(n)]
        """
        # Simulate many lifetimes
        death_ages = self.longevity_engine.simulate_lifetime(params, n_scenarios=10000)
        
        # Calculate survival to each year
        survival_probs = np.zeros(n_years)
        for t in range(n_years):
            target_age = age + t
            survival_probs[t] = np.mean(death_ages >= target_age)
        
        return survival_probs
    
    def _calculate_certain_annuity_pv(
        self,
        annual_payment: float,
        n_years: float,
        discount_rate: float
    ) -> float:
        """
        Present value of certain annuity (no mortality risk).
        
        This is the PV if you were GUARANTEED to live exactly n_years.
        The difference between this and the life annuity PV is the
        "longevity credit" from mortality pooling.
        
        Formula:
        PV = PMT * [(1 - (1+r)^-n) / r]
        
        Args:
            annual_payment: Annual payment amount
            n_years: Number of years
            discount_rate: Discount rate
            
        Returns:
            Present value
        """
        if discount_rate == 0:
            return annual_payment * n_years
        
        pv_factor = (1 - (1 + discount_rate) ** (-n_years)) / discount_rate
        return annual_payment * pv_factor
    
    def compare_annuity_vs_portfolio(
        self,
        premium: float,
        age: int,
        annual_spending: float,
        portfolio_return: float = 0.05,
        portfolio_vol: float = 0.10,
        gender: Gender = Gender.MALE,
        health_status: HealthStatus = HealthStatus.AVERAGE,
        smoker: bool = False,
        n_scenarios: int = 1000
    ) -> Dict[str, Any]:
        """
        Compare purchasing annuity vs. keeping money in portfolio.
        
        This analysis shows the trade-off:
        - Annuity: Guaranteed income for life, but lose flexibility
        - Portfolio: Maintain control, but risk running out
        
        Args:
            premium: Amount to annuitize
            age: Current age
            annual_spending: Desired annual income
            portfolio_return: Expected portfolio return
            portfolio_vol: Portfolio volatility
            gender: Gender
            health_status: Health status
            smoker: Smoking status
            n_scenarios: Monte Carlo scenarios
            
        Returns:
            Dictionary with comparison metrics
        """
        logger.info(f"Comparing annuity vs portfolio: ${premium:,.0f} premium")
        
        # Get annuity quote
        annuity_quote = self.quote_spia(
            premium=premium,
            age=age,
            gender=gender,
            health_status=health_status,
            smoker=smoker
        )
        
        # Monte Carlo portfolio depletion
        rng = np.random.default_rng(self.seed)
        
        # Simulate portfolio with withdrawals
        n_years = 50
        portfolio_paths = np.zeros((n_scenarios, n_years + 1))
        portfolio_paths[:, 0] = premium
        
        for scenario in range(n_scenarios):
            for year in range(1, n_years + 1):
                if portfolio_paths[scenario, year-1] <= 0:
                    portfolio_paths[scenario, year] = 0
                    continue
                
                # Apply return (lognormal)
                ret = np.exp(
                    (portfolio_return - 0.5 * portfolio_vol**2) +
                    portfolio_vol * rng.standard_normal()
                )
                
                # Grow portfolio
                portfolio_paths[scenario, year] = portfolio_paths[scenario, year-1] * ret
                
                # Subtract spending (match annuity payout for fair comparison)
                portfolio_paths[scenario, year] -= annuity_quote.annual_payout
                
                # Floor at zero
                portfolio_paths[scenario, year] = max(0, portfolio_paths[scenario, year])
        
        # Calculate metrics
        # Depletion: portfolio hits zero
        depletion_scenarios = np.sum(portfolio_paths[:, -1] <= 0)
        depletion_probability = depletion_scenarios / n_scenarios
        
        # Years until depletion (for failed scenarios)
        years_to_depletion = []
        for scenario in range(n_scenarios):
            for year in range(n_years + 1):
                if portfolio_paths[scenario, year] <= 0:
                    years_to_depletion.append(year)
                    break
        
        median_years_to_depletion = np.median(years_to_depletion) if years_to_depletion else None
        
        # Ending values (successful scenarios)
        ending_values = portfolio_paths[:, -1]
        median_ending = np.median(ending_values)
        
        comparison = {
            "annuity": {
                "annual_income": annuity_quote.annual_payout,
                "monthly_income": annuity_quote.monthly_payout,
                "payout_rate": annuity_quote.payout_rate,
                "guaranteed_for_life": True,
                "longevity_credit": annuity_quote.longevity_credit,
                "flexibility": "None (irrevocable)",
                "death_benefit": 0.0  # Life only
            },
            "portfolio": {
                "annual_income": annuity_quote.annual_payout,  # Same for comparison
                "starting_balance": premium,
                "depletion_probability": depletion_probability,
                "median_years_to_depletion": median_years_to_depletion,
                "median_ending_value": median_ending,
                "flexibility": "Full (can adjust spending, bequest)",
                "death_benefit": "Remaining balance"
            },
            "recommendation": self._generate_annuity_recommendation(
                annuity_quote=annuity_quote,
                depletion_prob=depletion_probability,
                median_ending=median_ending
            )
        }
        
        logger.info(f"✓ Comparison complete")
        logger.info(f"  Annuity: ${annuity_quote.annual_payout:,.0f}/year guaranteed")
        logger.info(f"  Portfolio: {depletion_probability:.1%} depletion risk")
        
        return comparison
    
    def _generate_annuity_recommendation(
        self,
        annuity_quote: AnnuityQuote,
        depletion_prob: float,
        median_ending: float
    ) -> str:
        """Generate recommendation based on comparison"""
        
        if depletion_prob > 0.30:
            return (
                f"HIGH depletion risk ({depletion_prob:.0%}). Consider annuitizing "
                f"${annuity_quote.premium:,.0f} to secure ${annuity_quote.annual_payout:,.0f}/year "
                f"floor income. This provides longevity insurance worth ${annuity_quote.longevity_credit:,.0f}."
            )
        elif depletion_prob > 0.15:
            return (
                f"MODERATE depletion risk ({depletion_prob:.0%}). Consider partial annuitization "
                f"(e.g., 50% = ${annuity_quote.premium/2:,.0f}) to create income floor while "
                f"maintaining portfolio flexibility."
            )
        else:
            return (
                f"LOW depletion risk ({depletion_prob:.0%}). Portfolio approach viable with "
                f"${median_ending:,.0f} median ending. Annuity may not be necessary, but "
                f"provides peace of mind and simplifies planning."
            )
