/**
 * Estate Planning Analysis Page
 * Estate taxes, inherited IRA, basis step-up, and Roth conversion planning
 */
import React, { useState } from 'react';
import apiClient from '../lib/api';
import { SectionHeader, Button, Card, Badge, Input, Select } from '../components/ui';
import { Home, Shield, AlertCircle } from 'lucide-react';

const EstatePlanningPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<any>(null);

  const [estateInputs, setEstateInputs] = useState({
    total_estate_value: 5000000,
    taxable_account: 1500000,
    ira_balance: 2000000,
    roth_balance: 500000,
    other_assets: 1000000,
    taxable_cost_basis: 1000000,
    federal_exemption: 13610000,
    state_estate_tax: 'NONE',
    heir_age: 30,
    heir_tax_bracket: 0.24,
    heir_state_tax_rate: 0.05,
    heir_filing_status: 'single',
    years_to_model: 30,
    discount_rate: 0.06,
    ira_growth_rate: 0.07,
    consider_roth_conversion: true,
  });

  const runAnalysis = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.axiosClient.post('/estate/analyze', estateInputs);
      setAnalysisResult(response.data.result);
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Estate Planning Analysis"
        description="Comprehensive estate tax, inherited IRA, and legacy planning"
        icon={<Home size={24} />}
      />

      {/* Input Form */}
      <Card>
        <h3 className="text-lg font-semibold mb-6">Estate Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Input
            label="Total Estate Value"
            type="number"
            value={estateInputs.total_estate_value}
            onChange={(e) => setEstateInputs({...estateInputs, total_estate_value: parseFloat(e.target.value)})}
            helperText="Total assets at death"
          />
          
          <Input
            label="Taxable Account"
            type="number"
            value={estateInputs.taxable_account}
            onChange={(e) => setEstateInputs({...estateInputs, taxable_account: parseFloat(e.target.value)})}
            helperText="Non-qualified investments"
          />
          
          <Input
            label="IRA Balance"
            type="number"
            value={estateInputs.ira_balance}
            onChange={(e) => setEstateInputs({...estateInputs, ira_balance: parseFloat(e.target.value)})}
            helperText="Traditional IRA/401k"
          />
          
          <Input
            label="Roth IRA Balance"
            type="number"
            value={estateInputs.roth_balance}
            onChange={(e) => setEstateInputs({...estateInputs, roth_balance: parseFloat(e.target.value)})}
            helperText="Tax-free accounts"
          />
          
          <Input
            label="Heir Age"
            type="number"
            value={estateInputs.heir_age}
            onChange={(e) => setEstateInputs({...estateInputs, heir_age: parseInt(e.target.value)})}
            helperText="Beneficiary age"
          />
          
          <Select
            label="Heir Tax Bracket"
            value={estateInputs.heir_tax_bracket}
            onChange={(e) => setEstateInputs({...estateInputs, heir_tax_bracket: parseFloat(e.target.value)})}
            options={[
              { value: 0.10, label: '10%' },
              { value: 0.12, label: '12%' },
              { value: 0.22, label: '22%' },
              { value: 0.24, label: '24%' },
              { value: 0.32, label: '32%' },
              { value: 0.35, label: '35%' },
              { value: 0.37, label: '37%' },
            ]}
            helperText="Heir's marginal rate"
          />
        </div>
        <div className="mt-6">
          <Button onClick={runAnalysis} disabled={isLoading} loading={isLoading}>
            Analyze Estate Plan
          </Button>
        </div>
      </Card>

      {/* Results */}
      {analysisResult && (
        <>
          {/* Estate Tax Summary */}
          <Card>
            <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Shield size={20} />
              Estate Tax Summary
            </h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Taxable Estate</p>
                <p className="text-2xl font-bold">${analysisResult.estate_tax?.taxable_estate?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Federal Tax</p>
                <p className="text-2xl font-bold text-red-600">${analysisResult.estate_tax?.federal_tax?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">State Tax</p>
                <p className="text-2xl font-bold text-red-600">${analysisResult.estate_tax?.state_tax?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Tax</p>
                <p className="text-2xl font-bold text-red-600">${analysisResult.estate_tax?.total_estate_tax?.toLocaleString()}</p>
              </div>
            </div>
            {analysisResult.estate_tax?.total_estate_tax > 0 && (
              <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded">
                <p className="text-sm text-yellow-800 flex items-center gap-2">
                  <AlertCircle size={16} />
                  Effective tax rate: {(analysisResult.estate_tax?.effective_rate * 100).toFixed(2)}%
                </p>
              </div>
            )}
          </Card>

          {/* Inherited IRA Analysis */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Inherited IRA Analysis (SECURE Act 2.0)</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
              <div>
                <p className="text-sm text-gray-600">Initial IRA Value</p>
                <p className="text-xl font-bold">${analysisResult.inherited_ira?.initial_ira_value?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Required Distributions</p>
                <p className="text-xl font-bold">${analysisResult.inherited_ira?.total_required_distributions?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Tax Owed</p>
                <p className="text-xl font-bold text-red-600">${analysisResult.inherited_ira?.total_tax_owed?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">After-Tax Value</p>
                <p className="text-xl font-bold text-green-600">${analysisResult.inherited_ira?.after_tax_value?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Tax Drag</p>
                <p className="text-xl font-bold">{(analysisResult.inherited_ira?.tax_drag * 100).toFixed(1)}%</p>
              </div>
            </div>
          </Card>

          {/* Basis Step-Up */}
          {analysisResult.basis_step_up && (
            <Card>
              <h3 className="text-lg font-semibold mb-4">Basis Step-Up Benefit</h3>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div>
                  <p className="text-sm text-gray-600">Original Basis</p>
                  <p className="text-xl font-bold">${analysisResult.basis_step_up.original_basis?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Stepped-Up Basis</p>
                  <p className="text-xl font-bold">${analysisResult.basis_step_up.stepped_up_basis?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Capital Gains Avoided</p>
                  <p className="text-xl font-bold text-green-600">${analysisResult.basis_step_up.capital_gains_avoided?.toLocaleString()}</p>
                </div>
                <div>
                  <p className="text-sm text-gray-600">Tax Savings</p>
                  <p className="text-xl font-bold text-green-600">${analysisResult.basis_step_up.tax_savings?.toLocaleString()}</p>
                </div>
              </div>
            </Card>
          )}

          {/* Recommendations */}
          {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
            <Card>
              <h3 className="text-lg font-semibold mb-4">Planning Recommendations</h3>
              <div className="space-y-3">
                {analysisResult.recommendations.map((rec: any, idx: number) => (
                  <div key={idx} className="p-4 bg-blue-50 border border-blue-200 rounded">
                    <div className="flex items-start gap-3">
                      <Badge variant={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'default'}>
                        {rec.priority}
                      </Badge>
                      <div className="flex-1">
                        <p className="font-semibold text-blue-900">{rec.recommendation}</p>
                        <p className="text-sm text-blue-700 mt-1">{rec.rationale}</p>
                        {rec.estimated_benefit > 0 && (
                          <p className="text-sm text-green-700 mt-1">
                            Potential savings: ${rec.estimated_benefit.toLocaleString()}
                          </p>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}
        </>
      )}
    </div>
  );
};

export default EstatePlanningPage;
