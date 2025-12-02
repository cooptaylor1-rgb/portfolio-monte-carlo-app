"""
AI-Powered Stress Test Builder and Audit Trail System

Provides natural language stress test creation and compliance-friendly audit logging.

Key Features:
- Natural language stress scenario parsing
- Parameter override translation
- Audit trail with timestamped records
- Exportable compliance logs
- Scenario comparison tracking
"""

import re
import json
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
import pandas as pd


@dataclass
class StressScenario:
    """Structured stress test scenario"""
    name: str
    description: str
    parameter_overrides: Dict[str, Any]
    rationale: str
    severity: str  # 'mild', 'moderate', 'severe', 'extreme'
    created_at: str
    created_by: str
    
    def to_dict(self):
        return asdict(self)


@dataclass
class AuditRecord:
    """Complete audit record for a simulation run"""
    record_id: str
    timestamp: str
    user_id: str
    client_id: Optional[str]
    scenario_type: str  # 'base', 'stress', 'comparison'
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    ai_analysis: Optional[Dict[str, Any]]
    advisor_notes: str
    compliance_flags: List[str]
    
    def to_dict(self):
        return asdict(self)


class StressTestBuilder:
    """
    Natural language stress test builder.
    
    Translates descriptions like:
    - "stagflation with 2% real yields and flat equities for 5 years"
    - "severe recession with -30% equity returns"
    - "prolonged inflation at 6% with rising rates"
    
    Into structured parameter overrides for Monte Carlo simulation.
    """
    
    def __init__(self):
        self.scenario_templates = self._build_templates()
        self.nlp_patterns = self._build_nlp_patterns()
    
    def _build_templates(self) -> Dict[str, Dict[str, Any]]:
        """Build library of common stress scenarios"""
        return {
            'stagflation': {
                'description': 'High inflation with stagnant growth',
                'overrides': {
                    'equity_return_annual': 0.02,
                    'fi_return_annual': 0.02,
                    'inflation_annual': 0.06,
                    'equity_vol_annual': 0.25
                },
                'severity': 'severe'
            },
            'severe_recession': {
                'description': 'Major economic contraction',
                'overrides': {
                    'equity_return_annual': -0.20,
                    'fi_return_annual': 0.03,
                    'inflation_annual': 0.01,
                    'equity_vol_annual': 0.35
                },
                'severity': 'severe'
            },
            'market_crash': {
                'description': 'Sudden major market decline',
                'overrides': {
                    'equity_return_annual': -0.30,
                    'fi_return_annual': 0.04,
                    'equity_vol_annual': 0.40
                },
                'severity': 'extreme'
            },
            'prolonged_inflation': {
                'description': 'Extended high inflation period',
                'overrides': {
                    'inflation_annual': 0.06,
                    'fi_return_annual': 0.03,
                    'equity_return_annual': 0.05,
                    'equity_vol_annual': 0.22
                },
                'severity': 'moderate'
            },
            'lost_decade': {
                'description': 'Extended period of flat returns',
                'overrides': {
                    'equity_return_annual': 0.0,
                    'fi_return_annual': 0.03,
                    'inflation_annual': 0.025,
                    'equity_vol_annual': 0.20
                },
                'severity': 'moderate'
            },
            'rising_rates': {
                'description': 'Rapid interest rate increases',
                'overrides': {
                    'fi_return_annual': 0.01,
                    'cash_return_annual': 0.04,
                    'equity_vol_annual': 0.22
                },
                'severity': 'moderate'
            },
            'deflation': {
                'description': 'Deflationary environment',
                'overrides': {
                    'inflation_annual': -0.01,
                    'equity_return_annual': 0.01,
                    'fi_return_annual': 0.04
                },
                'severity': 'moderate'
            }
        }
    
    def _build_nlp_patterns(self) -> Dict[str, List[Tuple[str, Any]]]:
        """Build NLP patterns for parameter extraction"""
        return {
            'equity_return': [
                (r'equit(?:y|ies) (?:return|returns?) (?:of )?(-?\d+\.?\d*)%', 'percent'),
                (r'stock(?:s)? (?:return|returns?) (?:of )?(-?\d+\.?\d*)%', 'percent'),
                (r'flat equit(?:y|ies)', 0.0),
                (r'negative equit(?:y|ies)', -0.10),
            ],
            'fi_return': [
                (r'bond(?:s)? (?:return|returns?) (?:of )?(-?\d+\.?\d*)%', 'percent'),
                (r'fixed income (?:return|returns?) (?:of )?(-?\d+\.?\d*)%', 'percent'),
                (r'(?:real )?yield(?:s)? (?:of )?(\d+\.?\d*)%', 'percent'),
            ],
            'inflation': [
                (r'inflation (?:of |at )?(\d+\.?\d*)%', 'percent'),
                (r'(\d+\.?\d*)% inflation', 'percent'),
                (r'high inflation', 0.06),
                (r'low inflation', 0.015),
                (r'stagflation', 0.06),
            ],
            'volatility': [
                (r'volatility (?:of )?(\d+\.?\d*)%', 'percent'),
                (r'high volatility', 0.30),
                (r'low volatility', 0.12),
                (r'extreme volatility', 0.40),
            ],
            'duration': [
                (r'for (\d+) years?', 'years'),
                (r'(\d+)-year', 'years'),
                (r'extended', 10),
                (r'prolonged', 10),
            ]
        }
    
    def parse_stress_description(self, description: str) -> StressScenario:
        """
        Parse natural language description into structured stress scenario.
        
        Args:
            description: Natural language stress scenario description
            
        Returns:
            StressScenario with parameter overrides
            
        Example:
            "stagflation with 6% inflation and flat equities for 5 years"
            → equity_return: 0%, inflation: 6%, duration: 5 years
        """
        desc_lower = description.lower()
        overrides = {}
        
        # Check for template matches first
        for template_name, template in self.scenario_templates.items():
            if template_name.replace('_', ' ') in desc_lower:
                overrides.update(template['overrides'])
                severity = template['severity']
                break
        else:
            severity = 'moderate'
        
        # Extract specific parameters from description
        for param, patterns in self.nlp_patterns.items():
            for pattern, value_type in patterns:
                match = re.search(pattern, desc_lower)
                if match:
                    if value_type == 'percent':
                        value = float(match.group(1)) / 100
                    elif value_type == 'years':
                        # Duration affects how scenario is applied
                        continue  # Handle separately
                    else:
                        value = value_type
                    
                    # Map to actual parameter names
                    if param == 'equity_return':
                        overrides['equity_return_annual'] = value
                    elif param == 'fi_return':
                        overrides['fi_return_annual'] = value
                    elif param == 'inflation':
                        overrides['inflation_annual'] = value
                    elif param == 'volatility':
                        overrides['equity_vol_annual'] = value
                    
                    break
        
        # Determine severity if not from template
        if severity == 'moderate':
            severity = self._assess_severity(overrides)
        
        # Generate scenario name
        name = self._generate_scenario_name(description, overrides)
        
        # Generate rationale
        rationale = self._generate_rationale(overrides, severity)
        
        return StressScenario(
            name=name,
            description=description,
            parameter_overrides=overrides,
            rationale=rationale,
            severity=severity,
            created_at=datetime.now().isoformat(),
            created_by='system'
        )
    
    def _assess_severity(self, overrides: Dict[str, Any]) -> str:
        """Assess scenario severity based on parameter overrides"""
        severity_score = 0
        
        # Equity returns
        if 'equity_return_annual' in overrides:
            ret = overrides['equity_return_annual']
            if ret < -0.20:
                severity_score += 3
            elif ret < -0.10:
                severity_score += 2
            elif ret < 0.03:
                severity_score += 1
        
        # Inflation
        if 'inflation_annual' in overrides:
            inf = overrides['inflation_annual']
            if inf > 0.06:
                severity_score += 2
            elif inf > 0.04:
                severity_score += 1
        
        # Volatility
        if 'equity_vol_annual' in overrides:
            vol = overrides['equity_vol_annual']
            if vol > 0.35:
                severity_score += 2
            elif vol > 0.25:
                severity_score += 1
        
        # Map score to severity
        if severity_score >= 5:
            return 'extreme'
        elif severity_score >= 3:
            return 'severe'
        elif severity_score >= 1:
            return 'moderate'
        else:
            return 'mild'
    
    def _generate_scenario_name(self, description: str, overrides: Dict[str, Any]) -> str:
        """Generate descriptive scenario name"""
        # Extract key terms from description
        keywords = []
        desc_lower = description.lower()
        
        if 'stagflation' in desc_lower:
            keywords.append('Stagflation')
        if 'recession' in desc_lower:
            keywords.append('Recession')
        if 'crash' in desc_lower:
            keywords.append('Market Crash')
        if 'inflation' in desc_lower and 'stagflation' not in desc_lower:
            keywords.append('High Inflation')
        if 'flat' in desc_lower or 'lost decade' in desc_lower:
            keywords.append('Flat Returns')
        
        if keywords:
            return ' + '.join(keywords)
        else:
            return 'Custom Stress Scenario'
    
    def _generate_rationale(self, overrides: Dict[str, Any], severity: str) -> str:
        """Generate rationale for stress scenario"""
        rationale_parts = []
        
        if 'equity_return_annual' in overrides:
            ret = overrides['equity_return_annual']
            if ret < 0:
                rationale_parts.append(f"Equity decline of {ret:.0%}")
            else:
                rationale_parts.append(f"Subdued equity returns at {ret:.1%}")
        
        if 'inflation_annual' in overrides:
            inf = overrides['inflation_annual']
            if inf > 0.04:
                rationale_parts.append(f"Elevated inflation at {inf:.1%}")
            elif inf < 0:
                rationale_parts.append(f"Deflationary pressure at {inf:.1%}")
        
        if 'equity_vol_annual' in overrides:
            vol = overrides['equity_vol_annual']
            if vol > 0.25:
                rationale_parts.append(f"High volatility at {vol:.0%}")
        
        if rationale_parts:
            return f"{severity.title()} scenario: " + ", ".join(rationale_parts)
        else:
            return f"{severity.title()} stress test scenario"
    
    def build_test_suite(self, base_inputs: Dict[str, Any],
                        scenarios: List[str]) -> List[Tuple[str, Dict[str, Any]]]:
        """
        Build complete stress test suite from descriptions.
        
        Args:
            base_inputs: Base case input parameters
            scenarios: List of stress scenario descriptions
            
        Returns:
            List of (scenario_name, modified_inputs) tuples
        """
        test_suite = []
        
        for scenario_desc in scenarios:
            stress = self.parse_stress_description(scenario_desc)
            
            # Apply overrides to base inputs
            modified_inputs = base_inputs.copy()
            modified_inputs.update(stress.parameter_overrides)
            
            test_suite.append((stress.name, modified_inputs))
        
        return test_suite


class AuditTrailSystem:
    """
    Compliance-friendly audit trail system.
    
    Features:
    - Timestamped records of all analyses
    - Input/output tracking
    - AI explanation logging
    - Advisor notes capture
    - Exportable audit logs
    - Data retention policies
    """
    
    def __init__(self, audit_path: str = "./audit_logs"):
        self.audit_path = audit_path
        self._ensure_audit_directory()
        self.retention_days = 2555  # 7 years (common regulatory standard)
    
    def _ensure_audit_directory(self):
        """Create audit directory structure"""
        os.makedirs(self.audit_path, exist_ok=True)
        os.makedirs(os.path.join(self.audit_path, "simulations"), exist_ok=True)
        os.makedirs(os.path.join(self.audit_path, "analyses"), exist_ok=True)
        os.makedirs(os.path.join(self.audit_path, "exports"), exist_ok=True)
    
    def create_record(self,
                     user_id: str,
                     client_id: Optional[str],
                     scenario_type: str,
                     inputs: Dict[str, Any],
                     outputs: Dict[str, Any],
                     ai_analysis: Optional[Dict[str, Any]] = None,
                     advisor_notes: str = "") -> AuditRecord:
        """
        Create audit record for a simulation run.
        
        Args:
            user_id: Advisor/user identifier
            client_id: Client identifier (if applicable)
            scenario_type: Type of scenario ('base', 'stress', 'comparison')
            inputs: Simulation input parameters
            outputs: Simulation results
            ai_analysis: AI-generated analysis (if any)
            advisor_notes: Additional notes from advisor
            
        Returns:
            AuditRecord object
        """
        record_id = self._generate_record_id()
        timestamp = datetime.now().isoformat()
        
        # Check for compliance flags
        compliance_flags = self._check_compliance(inputs, outputs)
        
        record = AuditRecord(
            record_id=record_id,
            timestamp=timestamp,
            user_id=user_id,
            client_id=client_id,
            scenario_type=scenario_type,
            inputs=inputs,
            outputs=outputs,
            ai_analysis=ai_analysis,
            advisor_notes=advisor_notes,
            compliance_flags=compliance_flags
        )
        
        # Save record
        self._save_record(record)
        
        return record
    
    def _generate_record_id(self) -> str:
        """Generate unique record ID"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        import random
        random_suffix = f"{random.randint(1000, 9999)}"
        return f"AUD{timestamp}{random_suffix}"
    
    def _check_compliance(self, inputs: Dict[str, Any], outputs: Dict[str, Any]) -> List[str]:
        """Check for compliance flags"""
        flags = []
        
        # Check withdrawal rate
        withdrawal_rate = (abs(inputs.get('monthly_spending', 0)) * 12 / 
                          inputs.get('starting_portfolio', 1)) * 100
        if withdrawal_rate > 6.0:
            flags.append(f"HIGH_WITHDRAWAL_RATE: {withdrawal_rate:.2f}%")
        
        # Check success probability
        success_prob = outputs.get('success_probability', 1.0)
        if success_prob < 0.5:
            flags.append(f"LOW_SUCCESS_PROBABILITY: {success_prob:.0%}")
        
        # Check aggressive allocation
        equity_pct = inputs.get('equity_pct', 0) * 100
        age = inputs.get('current_age', 50)
        if equity_pct > (120 - age):
            flags.append(f"AGGRESSIVE_ALLOCATION: {equity_pct:.0f}% equity at age {age}")
        
        return flags
    
    def _save_record(self, record: AuditRecord):
        """Save audit record to file"""
        # Save to simulations folder
        filename = f"{record.record_id}.json"
        filepath = os.path.join(self.audit_path, "simulations", filename)
        
        with open(filepath, 'w') as f:
            json.dump(record.to_dict(), f, indent=2, default=str)
    
    def export_audit_log(self, 
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None,
                        client_id: Optional[str] = None) -> pd.DataFrame:
        """
        Export audit log to DataFrame.
        
        Args:
            start_date: Filter records after this date
            end_date: Filter records before this date
            client_id: Filter by specific client
            
        Returns:
            DataFrame with audit records
        """
        records = []
        sim_path = os.path.join(self.audit_path, "simulations")
        
        for filename in os.listdir(sim_path):
            if filename.endswith('.json'):
                filepath = os.path.join(sim_path, filename)
                with open(filepath, 'r') as f:
                    record = json.load(f)
                    
                # Apply filters
                record_date = datetime.fromisoformat(record['timestamp'])
                if start_date and record_date < start_date:
                    continue
                if end_date and record_date > end_date:
                    continue
                if client_id and record.get('client_id') != client_id:
                    continue
                
                # Flatten for DataFrame
                flat_record = {
                    'record_id': record['record_id'],
                    'timestamp': record['timestamp'],
                    'user_id': record['user_id'],
                    'client_id': record.get('client_id'),
                    'scenario_type': record['scenario_type'],
                    'success_probability': record['outputs'].get('success_probability'),
                    'starting_portfolio': record['inputs'].get('starting_portfolio'),
                    'compliance_flags': ', '.join(record.get('compliance_flags', []))
                }
                records.append(flat_record)
        
        return pd.DataFrame(records)
    
    def get_client_history(self, client_id: str) -> List[AuditRecord]:
        """Get all audit records for a specific client"""
        records = []
        sim_path = os.path.join(self.audit_path, "simulations")
        
        for filename in os.listdir(sim_path):
            if filename.endswith('.json'):
                filepath = os.path.join(sim_path, filename)
                with open(filepath, 'r') as f:
                    record_dict = json.load(f)
                    if record_dict.get('client_id') == client_id:
                        # Reconstruct AuditRecord (simplified)
                        records.append(record_dict)
        
        # Sort by timestamp
        records.sort(key=lambda x: x['timestamp'], reverse=True)
        return records
    
    def cleanup_old_records(self, retention_days: Optional[int] = None):
        """Remove records older than retention period"""
        if retention_days is None:
            retention_days = self.retention_days
        
        cutoff_date = datetime.now() - pd.Timedelta(days=retention_days)
        sim_path = os.path.join(self.audit_path, "simulations")
        
        deleted_count = 0
        for filename in os.listdir(sim_path):
            if filename.endswith('.json'):
                filepath = os.path.join(sim_path, filename)
                with open(filepath, 'r') as f:
                    record = json.load(f)
                    record_date = datetime.fromisoformat(record['timestamp'])
                    
                if record_date < cutoff_date:
                    os.remove(filepath)
                    deleted_count += 1
        
        return deleted_count


# Export key classes
__all__ = [
    'StressTestBuilder',
    'AuditTrailSystem',
    'StressScenario',
    'AuditRecord'
]
