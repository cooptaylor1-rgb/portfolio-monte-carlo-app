"""
Manual test for goals API endpoint.
Validates that the API correctly processes goal analysis requests.
"""

import requests
import json

BASE_URL = "http://localhost:8000/api"

def test_goal_analysis():
    """Test goal analysis endpoint with sample goals"""
    
    payload = {
        "current_year": 2024,
        "n_scenarios": 1000,
        "equity_return_annual": 0.07,
        "fi_return_annual": 0.02,
        "cash_return_annual": 0.00,
        "equity_volatility": 0.18,
        "fi_volatility": 0.06,
        "cash_volatility": 0.01,
        "goals": [
            {
                "name": "Retirement Income Portfolio",
                "target_amount": 3000000,
                "target_year": 2045,
                "priority": "critical",
                "current_funding": 1500000,
                "annual_contribution": 50000,
                "equity_pct": 0.70,
                "fi_pct": 0.25,
                "cash_pct": 0.05,
                "use_glide_path": True,
                "years_before_goal_to_derisk": 5,
                "target_equity_at_goal": 0.20,
                "success_threshold": 0.85,
                "acceptable_shortfall_pct": 0.10,
                "notes": "Primary retirement income needs"
            },
            {
                "name": "College Fund - Child 1",
                "target_amount": 300000,
                "target_year": 2030,
                "priority": "high",
                "current_funding": 120000,
                "annual_contribution": 20000,
                "equity_pct": 0.60,
                "fi_pct": 0.35,
                "cash_pct": 0.05,
                "use_glide_path": True,
                "years_before_goal_to_derisk": 3,
                "target_equity_at_goal": 0.20,
                "notes": "Four-year private university"
            },
            {
                "name": "Vacation Home Purchase",
                "target_amount": 500000,
                "target_year": 2035,
                "priority": "medium",
                "current_funding": 50000,
                "annual_contribution": 15000,
                "equity_pct": 0.50,
                "fi_pct": 0.45,
                "cash_pct": 0.05,
                "use_glide_path": False,
                "notes": "Lake house or mountain property"
            }
        ]
    }
    
    print("="*70)
    print("TESTING GOAL ANALYSIS API")
    print("="*70)
    print(f"\nSending request to: {BASE_URL}/goals/analyze")
    print(f"Goals: {len(payload['goals'])}")
    print(f"Scenarios: {payload['n_scenarios']}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/goals/analyze",
            json=payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"\nResponse Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            
            print("\n" + "="*70)
            print("GOAL ANALYSIS RESULTS")
            print("="*70)
            
            # Overall summary
            print(f"\n{data['overall_summary']}")
            print(f"\nGoals on track: {data['on_track_count']}/{len(data['goals'])}")
            print(f"Goals at risk: {data['at_risk_count']}")
            print(f"Critical priority goals: {data['critical_goals_count']}")
            print(f"Total additional funding needed: ${data['total_annual_funding_needed']:,.0f}/year")
            
            # Individual goals
            print("\n" + "-"*70)
            print("INDIVIDUAL GOAL RESULTS")
            print("-"*70)
            
            for goal in data['goals']:
                print(f"\n{goal['goal_name']}")
                print(f"  Priority: {goal['priority'].upper()}")
                print(f"  Status: {goal['status'].upper()}")
                print(f"  Target: ${goal['target_amount']:,.0f} by {goal['target_year']} ({goal['years_remaining']} years)")
                print(f"  Success Probability: {goal['probability_of_success']:.1%}")
                print(f"  Current Funding: {goal['current_funding_pct']:.1%}")
                print(f"  Median Outcome: ${goal['median_value_at_target']:,.0f}")
                print(f"  Range: ${goal['percentile_10']:,.0f} - ${goal['percentile_90']:,.0f}")
                
                if goal['additional_funding_needed'] > 0:
                    print(f"  Additional Funding Needed: ${goal['additional_funding_needed']:,.0f}/year")
                
                print(f"  Recommendation: {goal['recommendation']}")
            
            # Conflicts
            if data['conflicts']:
                print("\n" + "-"*70)
                print("DETECTED CONFLICTS")
                print("-"*70)
                
                for conflict in data['conflicts']:
                    print(f"\n{conflict['conflict_type'].upper()}")
                    print(f"  {conflict['description']}")
                    print(f"  Affected goals: {', '.join(conflict['goals_affected'])}")
                    if conflict.get('total_funding_gap'):
                        print(f"  Total funding gap: ${conflict['total_funding_gap']:,.0f}/year")
                    print(f"  Recommendation: {conflict['recommendation']}")
            
            print("\n" + "="*70)
            print("TEST SUCCESSFUL ✓")
            print("="*70)
            return True
            
        else:
            print(f"\nERROR: {response.status_code}")
            print(response.text)
            return False
            
    except requests.exceptions.ConnectionError:
        print("\nERROR: Cannot connect to API. Is the server running?")
        print("Start the server with: python main.py")
        return False
    except Exception as e:
        print(f"\nERROR: {str(e)}")
        return False


if __name__ == "__main__":
    test_goal_analysis()
