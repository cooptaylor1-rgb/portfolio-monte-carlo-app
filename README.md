# Portfolio Monte Carlo + Stress Test App

This application runs a full portfolio Monte Carlo simulation with:
- Shaded fan chart (P10/P25/Median/P75/P90)
- Adjustable assumptions and spending rules
- One-time cash flows
- Stress tests based on deterministic shocks to:
  - Expected returns
  - Spending level
  - Inflation
- Comparison of stress-test paths vs the median Monte Carlo result
- Streamlit UI with formatted dollar and percent inputs

---

## 🚀 Running the App in GitHub Codespaces

1. Open the repository in a **Codespace**
2. Open a terminal inside the Codespace
3. Install dependencies:

   ```bash
   pip install -r requirements.txt
