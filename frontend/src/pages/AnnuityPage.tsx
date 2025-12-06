/**
 * Annuity Analysis Page
 * SPIA, DIA, and QLAC pricing and comparison
 */
import React, { useState } from 'react';
import { useSimulationStore } from '../store/simulationStore';
import apiClient from '../lib/api';
import { SectionHeader, Button, Card } from '../components/ui';
import { DollarSign } from 'lucide-react';

const AnnuityPage: React.FC = () => {
  const { modelInputs } = useSimulationStore();
  const [isLoading, setIsLoading] = useState(false);
  const [quoteResult, setQuoteResult] = useState<any>(null);
  const [comparisonResult, setComparisonResult] = useState<any>(null);

  const [annuityInputs, setAnnuityInputs] = useState({
    premium: 100000,
    age: modelInputs.current_age || 65,
    gender: 'MALE',
    health_status: 'AVERAGE',
    annuity_type: 'SPIA',
    life_option: 'SINGLE_LIFE',
    years_certain: 0,
    deferral_years: 0,
    inflation_rider: false,
    inflation_rate: 0.025,
  });

  const getAnnuityQuote = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.axiosClient.post('/annuity/quote', annuityInputs);
      setQuoteResult(response.data.result);
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const compareAnnuities = async () => {
    setIsLoading(true);
    try {
      const response = await apiClient.axiosClient.post('/annuity/compare', {
        premium: annuityInputs.premium,
        age: annuityInputs.age,
        gender: annuityInputs.gender,
        health_status: annuityInputs.health_status,
        simulation_years: 30,
      });
      setComparisonResult(response.data.comparison);
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Annuity Analysis"
        description="Institutional-grade SPIA, DIA, and QLAC pricing and comparison"
        icon={<DollarSign size={24} />}
      />

      {/* Input Form */}
      <Card>
        <h3 className="text-lg font-semibold mb-4">Annuity Parameters</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
          <div>
            <label className="block text-sm font-medium mb-1">Premium Amount</label>
            <input
              type="number"
              value={annuityInputs.premium}
              onChange={(e) => setAnnuityInputs({...annuityInputs, premium: parseFloat(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Current Age</label>
            <input
              type="number"
              value={annuityInputs.age}
              onChange={(e) => setAnnuityInputs({...annuityInputs, age: parseInt(e.target.value)})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Annuity Type</label>
            <select
              value={annuityInputs.annuity_type}
              onChange={(e) => setAnnuityInputs({...annuityInputs, annuity_type: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="SPIA">SPIA - Immediate</option>
              <option value="DIA">DIA - Deferred</option>
              <option value="QLAC">QLAC - Qualified Longevity</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Gender</label>
            <select
              value={annuityInputs.gender}
              onChange={(e) => setAnnuityInputs({...annuityInputs, gender: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="MALE">Male</option>
              <option value="FEMALE">Female</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Life Option</label>
            <select
              value={annuityInputs.life_option}
              onChange={(e) => setAnnuityInputs({...annuityInputs, life_option: e.target.value})}
              className="w-full px-3 py-2 border border-gray-300 rounded-md"
            >
              <option value="SINGLE_LIFE">Single Life</option>
              <option value="JOINT_SURVIVOR">Joint & Survivor</option>
              <option value="PERIOD_CERTAIN">Period Certain</option>
              <option value="LIFE_WITH_PERIOD_CERTAIN">Life w/ Period Certain</option>
            </select>
          </div>
          {annuityInputs.annuity_type !== 'SPIA' && (
            <div>
              <label className="block text-sm font-medium mb-1">Deferral Years</label>
              <input
                type="number"
                value={annuityInputs.deferral_years}
                onChange={(e) => setAnnuityInputs({...annuityInputs, deferral_years: parseInt(e.target.value)})}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
              />
            </div>
          )}
        </div>
        <div className="mt-4 flex gap-4">
          <Button onClick={getAnnuityQuote} disabled={isLoading}>
            Get Quote
          </Button>
          <Button onClick={compareAnnuities} disabled={isLoading} variant="secondary">
            Compare All Types
          </Button>
        </div>
      </Card>

      {/* Quote Results */}
      {quoteResult && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Quote Results</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div>
              <p className="text-sm text-gray-600">Monthly Payment</p>
              <p className="text-2xl font-bold">${quoteResult.monthly_payment?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Annual Payment</p>
              <p className="text-2xl font-bold">${quoteResult.annual_payment?.toLocaleString()}</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Payout Rate</p>
              <p className="text-2xl font-bold">{(quoteResult.payout_rate * 100).toFixed(2)}%</p>
            </div>
            <div>
              <p className="text-sm text-gray-600">Breakeven Age</p>
              <p className="text-2xl font-bold">{quoteResult.breakeven_age}</p>
            </div>
          </div>
        </Card>
      )}

      {/* Comparison Results */}
      {comparisonResult && (
        <Card>
          <h3 className="text-lg font-semibold mb-4">Annuity Type Comparison</h3>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead>
                <tr className="border-b">
                  <th className="text-left py-2">Type</th>
                  <th className="text-right py-2">Monthly Payment</th>
                  <th className="text-right py-2">Payout Rate</th>
                  <th className="text-right py-2">Breakeven Age</th>
                  <th className="text-right py-2">Total Lifetime</th>
                </tr>
              </thead>
              <tbody>
                {comparisonResult.scenarios?.map((scenario: any, idx: number) => (
                  <tr key={idx} className="border-b">
                    <td className="py-2">{scenario.annuity_type}</td>
                    <td className="text-right">${scenario.quote.monthly_payment?.toLocaleString()}</td>
                    <td className="text-right">{(scenario.quote.payout_rate * 100).toFixed(2)}%</td>
                    <td className="text-right">{scenario.quote.breakeven_age}</td>
                    <td className="text-right">${scenario.quote.total_lifetime_payments?.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Card>
      )}
    </div>
  );
};

export default AnnuityPage;
