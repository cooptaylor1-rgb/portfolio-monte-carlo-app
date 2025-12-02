# Phase 4 Advanced Analytics - User Guide

## 🎯 Quick Access

All Phase 4 features are located in the **Scenarios** tab under the **"🔬 Advanced Analytics"** section.

After running your base simulation in the Portfolio Analysis tab, navigate to Scenarios to access these powerful analytical tools.

---

## 📊 Feature 1: Asset Correlation Analysis

**Location**: Scenarios → Advanced Analytics → "📊 Asset Correlation Analysis" expander

### What It Does
Visualizes how different asset classes move together and helps you understand diversification benefits.

### How to Use
1. Open the expander
2. Adjust the correlation sliders:
   - **Equity-Fixed Income**: Default 0.0 (independent)
   - **Fixed Income-Cash**: Default 0.3 (slightly positive)
3. View the interactive correlation matrix

### Interpreting Results
- **Positive correlation (0 to 1)**: Assets move together
- **Negative correlation (-1 to 0)**: Assets move opposite
- **Zero**: Assets move independently

**Color Scale**:
- 🟢 Green: Positive correlation (move together)
- 🟡 Yellow: Low correlation (mostly independent)
- 🔴 Red: Negative correlation (move opposite)

### Example Use Cases
- Understanding why your portfolio dropped less than the market in 2008
- Evaluating if adding more bonds will reduce volatility
- Checking if your "diversified" portfolio is actually correlated

---

## 📉 Feature 2: Historical Stress Scenarios

**Location**: Scenarios → Advanced Analytics → "📉 Historical Stress Scenarios" expander

### What It Does
Tests your portfolio against major historical market crises to see how it would have performed.

### Available Scenarios

#### 2008 Financial Crisis
- Equity return: -15%
- Volatility: 35% (high fear)
- Best for: Understanding severe bear markets

#### COVID-19 Crash (2020)
- Equity return: 0%
- Volatility: 45% (extreme uncertainty)
- Best for: Sharp but short-lived crashes

#### Dot-com Bubble (2000-2002)
- Equity return: -10%
- Volatility: 30%
- Best for: Tech-heavy portfolios

#### 1970s Stagflation
- Equity return: 2%
- Inflation: 8%
- Best for: High inflation environments

### How to Use
1. Open the expander
2. Select a scenario with the radio buttons
3. Click **"Run Historical Scenario"**
4. Review the comparison with your base case

### Interpreting Results
The comparison table shows:
- **Median Ending**: Expected final value
- **P10 Ending**: Worst-case (pessimistic)
- **P90 Ending**: Best-case (optimistic)

**What to Look For**:
- Can your portfolio survive the crisis?
- How much lower are ending values?
- Does your success probability drop significantly?

---

## 🔄 Feature 3: Dynamic Rebalancing Analysis

**Location**: Scenarios → Advanced Analytics → "🔄 Dynamic Rebalancing Analysis" expander

### What It Does
Compares different rebalancing strategies to find the optimal balance between performance and trading costs.

### Available Strategies

#### Annual Rebalancing
- Rebalances once per year
- Low trading costs
- Moderate drift control

#### Quarterly Rebalancing
- Rebalances every 3 months
- Higher trading costs
- Better drift control

#### 5% Threshold
- Rebalances when allocation drifts >5%
- Adaptive to market conditions
- Most common approach

#### 10% Threshold
- Rebalances when allocation drifts >10%
- Very low trading costs
- More portfolio drift

#### No Rebalancing
- Buy and hold
- Zero trading costs
- Maximum drift (allocation changes over time)

### How to Use
1. Open the expander
2. Select 2-3 strategies using the multi-select
3. Click **"Analyze Rebalancing Strategies"**
4. Review performance comparison and individual charts

### Interpreting Results

**Performance Table**:
- **Median/P10/P90 Ending**: Portfolio values under each strategy
- **Avg Rebalances**: How often rebalancing occurred

**What to Consider**:
- Higher frequency ≠ always better
- Each rebalance has costs (commissions, spreads, taxes)
- Threshold strategies adapt to volatility
- Your specific costs matter (low-cost ETFs vs. high-commission stocks)

### Example Insights
- Annual rebalancing often provides 90% of the benefit
- 5% threshold is ideal for most investors
- No rebalancing can lead to unintended risk exposure

---

## 💰 Feature 4: Tax-Efficient Withdrawal Strategies

**Location**: Scenarios → Advanced Analytics → "💰 Tax-Efficient Withdrawal Strategies" expander

### What It Does
Optimizes the order you withdraw from different account types to minimize lifetime taxes.

### Strategies Compared

#### Naive Proportional
- Withdraws proportionally from all accounts
- Simple but tax-inefficient
- Baseline for comparison

#### Tax-Efficient Sequencing
1. **First**: Taxable accounts (15% capital gains)
2. **Second**: Traditional IRA (22% ordinary income)
3. **Last**: Roth IRA (tax-free)

#### RMD-Aware Strategy
- Tax-efficient sequencing
- **Plus**: Ensures Required Minimum Distributions are taken
- Starts at age 72 (IRS requirement)
- Avoids 50% penalty on missed RMDs

### Assumptions
- **Taxable**: 35% of portfolio (15% long-term cap gains tax)
- **Traditional IRA**: 50% of portfolio (22% ordinary income tax)
- **Roth IRA**: 15% of portfolio (tax-free withdrawals)

### How to Use
1. Open the expander
2. Click **"Analyze Tax Strategies"**
3. Review comparison table and details

### Interpreting Results

**Comparison Table**:
- **Total Tax**: Lifetime taxes paid
- **Effective Tax Rate**: Average tax rate
- **Tax Savings**: Dollars saved vs. naive approach
- **Savings %**: Percentage reduction in taxes

**Typical Savings**: 10-20% reduction in lifetime taxes ($50,000-$100,000+)

### Key Insights
- Order matters: Can save $50K-$100K+ over retirement
- RMDs are mandatory after age 72
- Roth conversions in low-income years can help
- Consider state taxes (not modeled here)

### Example Scenario
**Naive Strategy**: $450,000 in taxes  
**Tax-Efficient**: $380,000 in taxes  
**Savings**: $70,000 (15.6%)

---

## 🚀 Workflow Recommendations

### For New Plans
1. **Start**: Run base simulation in Portfolio Analysis
2. **Test**: Run 2008 Crisis scenario (worst-case stress test)
3. **Optimize**: Compare rebalancing strategies
4. **Plan**: Review tax-efficient withdrawal strategy

### For Existing Clients
1. **Update**: Refresh base simulation with current values
2. **Compare**: Check multiple historical scenarios
3. **Decide**: Pick optimal rebalancing frequency
4. **Document**: Export results for client meeting

### For Risk Assessment
1. **Stress**: Run all 4 historical scenarios
2. **Correlate**: Adjust correlations to match client holdings
3. **Rebalance**: Test if more frequent rebalancing reduces risk
4. **Report**: Show client range of outcomes

---

## 💡 Tips & Best Practices

### Correlation Analysis
- Start with defaults (0.0 and 0.3)
- Increase correlations during market stress
- Negative correlations are rare (use cautiously)

### Historical Scenarios
- Test at least 2-3 scenarios
- Focus on 2008 for conservative planning
- COVID shows quick-recovery scenarios

### Rebalancing
- 5% threshold works for most portfolios
- Consider your specific trading costs
- Taxable accounts may prefer less frequent rebalancing

### Tax Strategies
- Results assume federal tax rates only
- State taxes can significantly impact strategy
- Consider current and future tax brackets
- Roth conversions not modeled (future enhancement)

---

## 📊 Expected Outcomes

### Good Portfolio
- Survives 2008 scenario with >60% success
- 5-10% improvement with optimal rebalancing
- 10-20% tax savings with efficient withdrawals

### Red Flags
- <40% success in any historical scenario
- Large performance gaps between rebalancing strategies
- Very high effective tax rate (>25%)

---

## 🎓 Learning More

### Correlation
- Modern Portfolio Theory (Markowitz)
- Diversification benefits
- Risk reduction through low correlation

### Historical Analysis
- Sequence of returns risk
- Market cycle patterns
- Crisis behavior modeling

### Rebalancing
- Academic research: 5% threshold optimal for most
- Behavioral benefits (enforces buy low, sell high)
- Tax implications in taxable accounts

### Tax Efficiency
- Withdrawal sequencing strategies
- RMD requirements (IRS rules)
- Roth conversion opportunities

---

## ❓ FAQs

### Q: How long do these analyses take?
A: 10-30 seconds each (historical scenarios are slowest)

### Q: Can I run multiple scenarios at once?
A: Yes! Rebalancing analysis runs all selected strategies simultaneously

### Q: Are results saved?
A: Yes, in session state until you refresh the page

### Q: Can I export these results?
A: Partial support via Excel export. Enhanced export in future phase.

### Q: How accurate are the tax calculations?
A: Simplified federal rates. Consult tax professional for specific situations.

---

## 🔮 Coming Soon (Phase 5)

- Factor analysis (market, size, value factors)
- Sequence of returns risk visualization
- Healthcare cost projections
- Social Security optimization
- Enhanced PDF reports with all advanced analytics

---

**Ready to explore?** Head to the **Scenarios** tab and open the **Advanced Analytics** section!

*Last Updated: December 2, 2025*
