"""
Basic API tests using pytest
"""
import pytest
from fastapi.testclient import TestClient
from backend.main import app
from backend.models.schemas import ModelInputsModel, ClientInfoModel, SimulationRequest

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "version" in data


def test_list_presets():
    """Test getting assumption presets"""
    response = client.get("/api/presets/")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "name" in data[0]


def test_get_specific_preset():
    """Test getting a specific preset"""
    response = client.get("/api/presets/Conservative")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Conservative"
    assert "equity_return" in data


def test_validate_inputs_valid():
    """Test input validation with valid inputs"""
    inputs = ModelInputsModel(
        starting_portfolio=1000000,
        years_to_model=30,
        current_age=50,
        horizon_age=80,
        monthly_spending=-5000,
        equity_pct=0.6,
        fi_pct=0.3,
        cash_pct=0.1
    )
    
    response = client.post("/api/simulation/validate", json=inputs.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is True


def test_validate_inputs_invalid_allocation():
    """Test input validation with invalid allocation"""
    inputs = ModelInputsModel(
        starting_portfolio=1000000,
        years_to_model=30,
        current_age=50,
        horizon_age=80,
        equity_pct=0.5,
        fi_pct=0.3,
        cash_pct=0.1  # Sums to 0.9, not 1.0
    )
    
    response = client.post("/api/simulation/validate", json=inputs.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["is_valid"] is False
    assert len(data["errors"]) > 0


def test_run_simulation_basic():
    """Test running a basic Monte Carlo simulation"""
    request = SimulationRequest(
        client_info=ClientInfoModel(
            client_name="Test Client",
            advisor_name="Test Advisor"
        ),
        inputs=ModelInputsModel(
            starting_portfolio=1000000,
            years_to_model=10,
            current_age=50,
            horizon_age=60,
            monthly_spending=-3000,
            equity_pct=0.6,
            fi_pct=0.3,
            cash_pct=0.1,
            n_scenarios=100  # Smaller for faster testing
        ),
        seed=42  # For reproducibility
    )
    
    response = client.post("/api/simulation/run", json=request.model_dump())
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "metrics" in data
    assert "stats" in data
    
    # Validate metrics structure
    metrics = data["metrics"]
    assert 0 <= metrics["success_probability"] <= 1
    assert metrics["ending_median"] >= 0


def test_run_simulation_invalid_allocation():
    """Test simulation with invalid inputs returns error"""
    request = {
        "client_info": {"client_name": "Test"},
        "inputs": {
            "starting_portfolio": 1000000,
            "years_to_model": 10,
            "current_age": 50,
            "horizon_age": 60,
            "equity_pct": 0.5,
            "fi_pct": 0.3,
            "cash_pct": 0.1,  # Invalid total
            "n_scenarios": 100
        }
    }
    
    response = client.post("/api/simulation/run", json=request)
    assert response.status_code == 400


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
