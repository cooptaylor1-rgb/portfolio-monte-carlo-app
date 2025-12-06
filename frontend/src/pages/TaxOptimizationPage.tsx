/**
 * Tax Optimization Page
 * Roth conversion planning and IRMAA threshold management
 */
import React, { useState } from 'react';
import apiClient from '../lib/api';
import { SectionHeader, Button, Card, Badge, Input, Select, Switch } from '../components/ui';
import { DollarSign, AlertCircle } from 'lucide-react';

const TaxOptimizationPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [optimizationResult, setOptimizationResult] = useState<any>(null);

  const [taxInputs, setTaxInputs] = useState({
    age: 65,
    current_ira_balance: 800000,
    current_roth_balance: 200000,
    current_taxable_balance: 500000,
    annual_spending: 80000,
    social_security_benefit: 30000,
    pension_income: 0,
    other_income: 0,
    filing_status: 'married_joint',
    state: 'CA',
    years_to_optimize: 10,
    avoid_irmaa: true,
    target_tax_bracket: 0.22,
    ira_return_rate: 0.07,
    roth_return_rate: 0.07,
    taxable_return_rate: 0.06,
    inflation_rate: 0.03,
  });

  const runOptimization = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.axiosClient.post('/tax/optimize-roth-conversions', taxInputs);
      setOptimizationResult(response.data);
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Tax Optimization"
        description="Roth conversion planning with IRMAA threshold management"
        icon={<DollarSign size={24} />}
      />

      {/* Input Form */}
      <Card>
        <h3 className="text-lg font-semibold mb-6">Optimization Parameters</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          <Input
            label="Current Age"
            type="number"
            value={taxInputs.age}
            onChange={(e) => setTaxInputs({...taxInputs, age: parseInt(e.target.value)})}
          />
          
          <Input
            label="IRA Balance"
            type="number"
            value={taxInputs.current_ira_balance}
            onChange={(e) => setTaxInputs({...taxInputs, current_ira_balance: parseFloat(e.target.value)})}
            helperText="Traditional IRA/401k"
          />
          
          <Input
            label="Roth IRA Balance"
            type="number"
            value={taxInputs.current_roth_balance}
            onChange={(e) => setTaxInputs({...taxInputs, current_roth_balance: parseFloat(e.target.value)})}
            helperText="Current Roth balance"
          />
          
          <Input
            label="Annual Spending"
            type="number"
            value={taxInputs.annual_spending}
            onChange={(e) => setTaxInputs({...taxInputs, annual_spending: parseFloat(e.target.value)})}
            helperText="Retirement expenses"
          />
          
          <Input
            label="Social Security"
            type="number"
            value={taxInputs.social_security_benefit}
            onChange={(e) => setTaxInputs({...taxInputs, social_security_benefit: parseFloat(e.target.value)})}
            helperText="Annual SS benefit"
          />
          
          <Select
            label="Filing Status"
            value={taxInputs.filing_status}
            onChange={(e) => setTaxInputs({...taxInputs, filing_status: e.target.value})}
            options={[
              { value: 'single', label: 'Single' },
              { value: 'married_joint', label: 'Married Filing Jointly' },
              { value: 'married_separate', label: 'Married Filing Separately' },
              { value: 'head_of_household', label: 'Head of Household' },
            ]}
          />
          
          <Input
            label="Years to Optimize"
            type="number"
            value={taxInputs.years_to_optimize}
            onChange={(e) => setTaxInputs({...taxInputs, years_to_optimize: parseInt(e.target.value)})}
            helperText="1-30 years"
          />
          
          <Select
            label="Target Tax Bracket"
            value={taxInputs.target_tax_bracket}
            onChange={(e) => setTaxInputs({...taxInputs, target_tax_bracket: parseFloat(e.target.value)})}
            options={[
              { value: 0.10, label: '10%' },
              { value: 0.12, label: '12%' },
              { value: 0.22, label: '22%' },
              { value: 0.24, label: '24%' },
              { value: 0.32, label: '32%' },
            ]}
            helperText="Stay below this rate"
          />
          
          <div className="flex items-start">
            <Switch
              label="Avoid IRMAA Thresholds"
              checked={taxInputs.avoid_irmaa}
              onChange={(e) => setTaxInputs({...taxInputs, avoid_irmaa: e.target.checked})}
              helperText="Minimize Medicare surcharges"
            />
          </div>
        </div>
        <div className="mt-6">
          <Button onClick={runOptimization} disabled={isLoading} loading={isLoading}>
            Optimize Conversions
          </Button>
        </div>
      </Card>

      {/* Results */}
      {optimizationResult && (
        <>
          {/* Summary */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Optimization Summary</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">Total Conversions</p>
                <p className="text-2xl font-bold">${optimizationResult.total_conversions?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Lifetime Tax Savings</p>
                <p className="text-2xl font-bold text-green-600">${optimizationResult.lifetime_tax_savings?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Final Roth Balance</p>
                <p className="text-2xl font-bold">${optimizationResult.final_roth_balance?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Final IRA Balance</p>
                <p className="text-2xl font-bold">${optimizationResult.final_ira_balance?.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          {/* Conversion Schedule */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Annual Conversion Schedule</h3>
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left">Year</th>
                    <th className="px-4 py-2 text-right">Age</th>
                    <th className="px-4 py-2 text-right">Conversion Amount</th>
                    <th className="px-4 py-2 text-right">Tax Owed</th>
                    <th className="px-4 py-2 text-right">Effective Rate</th>
                    <th className="px-4 py-2 text-right">IRMAA Impact</th>
                    <th className="px-4 py-2 text-left">Notes</th>
                  </tr>
                </thead>
                <tbody>
                  {optimizationResult.conversion_schedule?.map((year: any, idx: number) => (
                    <tr key={idx} className={idx % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                      <td className="px-4 py-2">{year.year}</td>
                      <td className="px-4 py-2 text-right">{year.age}</td>
                      <td className="px-4 py-2 text-right font-semibold">
                        ${year.conversion_amount?.toLocaleString()}
                      </td>
                      <td className="px-4 py-2 text-right text-red-600">
                        ${year.tax_owed?.toLocaleString()}
                      </td>
                      <td className="px-4 py-2 text-right">
                        {(year.effective_tax_rate * 100).toFixed(1)}%
                      </td>
                      <td className="px-4 py-2 text-right">
                        {year.irmaa_triggered ? (
                          <Badge variant="warning">+${year.irmaa_cost}</Badge>
                        ) : (
                          <Badge variant="success">None</Badge>
                        )}
                      </td>
                      <td className="px-4 py-2 text-sm text-gray-600">{year.notes}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </Card>

          {/* Tax Projection Chart */}
          {optimizationResult.tax_comparison && (
            <Card>
              <h3 className="text-lg font-semibold mb-4">Tax Comparison: With vs Without Conversions</h3>
              <div className="grid grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">With Conversions</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Conversion Taxes:</span>
                      <span className="font-semibold">${optimizationResult.tax_comparison.with_conversions.conversion_taxes?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between">
                      <span>RMD Taxes:</span>
                      <span className="font-semibold">${optimizationResult.tax_comparison.with_conversions.rmd_taxes?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="font-bold">Total Lifetime Taxes:</span>
                      <span className="font-bold">${optimizationResult.tax_comparison.with_conversions.total_lifetime_taxes?.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Without Conversions</h4>
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span>Conversion Taxes:</span>
                      <span className="font-semibold">$0</span>
                    </div>
                    <div className="flex justify-between">
                      <span>RMD Taxes:</span>
                      <span className="font-semibold">${optimizationResult.tax_comparison.without_conversions.rmd_taxes?.toLocaleString()}</span>
                    </div>
                    <div className="flex justify-between border-t pt-2">
                      <span className="font-bold">Total Lifetime Taxes:</span>
                      <span className="font-bold">${optimizationResult.tax_comparison.without_conversions.total_lifetime_taxes?.toLocaleString()}</span>
                    </div>
                  </div>
                </div>
              </div>
              <div className="mt-4 p-4 bg-green-50 border border-green-200 rounded">
                <p className="text-lg font-bold text-green-800">
                  Net Savings: ${optimizationResult.tax_comparison.net_savings?.toLocaleString()}
                </p>
              </div>
            </Card>
          )}

          {/* Recommendations */}
          {optimizationResult.recommendations && optimizationResult.recommendations.length > 0 && (
            <Card>
              <h3 className="text-lg font-semibold mb-4">Strategic Recommendations</h3>
              <div className="space-y-3">
                {optimizationResult.recommendations.map((rec: string, idx: number) => (
                  <div key={idx} className="flex items-start gap-3 p-3 bg-blue-50 border border-blue-200 rounded">
                    <AlertCircle className="text-blue-600 mt-0.5" size={16} />
                    <p className="text-sm text-blue-900">{rec}</p>
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

export default TaxOptimizationPage;
