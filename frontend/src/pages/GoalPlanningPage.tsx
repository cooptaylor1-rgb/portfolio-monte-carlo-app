/**
 * Goal-Based Planning Page
 * Financial goal tracking and success probability analysis
 */
import React, { useState } from 'react';
import apiClient from '../lib/api';
import { SectionHeader, Button, Card, Badge, Input, Switch } from '../components/ui';
import { Target, Plus, Trash2 } from 'lucide-react';

interface Goal {
  goal_id?: string;
  name: string;
  target_amount: number;
  target_year: number;
  priority: number;
  is_essential: boolean;
  inflation_adjusted: boolean;
}

const GoalPlanningPage: React.FC = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [goals, setGoals] = useState<Goal[]>([]);
  const [analysisResult, setAnalysisResult] = useState<any>(null);
  const [showAddGoal, setShowAddGoal] = useState(false);

  const [newGoal, setNewGoal] = useState<Goal>({
    name: '',
    target_amount: 50000,
    target_year: new Date().getFullYear() + 5,
    priority: 1,
    is_essential: false,
    inflation_adjusted: true,
  });

  const addGoal = () => {
    if (newGoal.name && newGoal.target_amount > 0) {
      setGoals([...goals, { ...newGoal, goal_id: `goal_${Date.now()}` }]);
      setNewGoal({
        name: '',
        target_amount: 50000,
        target_year: new Date().getFullYear() + 5,
        priority: 1,
        is_essential: false,
        inflation_adjusted: true,
      });
      setShowAddGoal(false);
    }
  };

  const removeGoal = (goalId: string) => {
    setGoals(goals.filter(g => g.goal_id !== goalId));
  };

  const runAnalysis = async () => {
    if (goals.length === 0) {
      alert('Please add at least one goal');
      return;
    }

    setIsLoading(true);
    try {
      const requestData = {
        current_age: 65,
        retirement_age: 65,
        portfolio_value: 1000000,
        annual_income: 0,
        annual_spending: 80000,
        return_rate: 0.07,
        volatility: 0.18,
        inflation_rate: 0.03,
        goals: goals.map(g => ({
          name: g.name,
          target_amount: g.target_amount,
          target_year: g.target_year,
          priority: g.priority,
          is_essential: g.is_essential,
          inflation_adjusted: g.inflation_adjusted,
        })),
        monte_carlo_runs: 1000,
      };

      const response = await apiClient.axiosClient.post('/goals/analyze', requestData);
      setAnalysisResult(response.data);
    } catch (error: any) {
      alert(`Error: ${error.response?.data?.detail || error.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      <SectionHeader
        title="Goal-Based Planning"
        description="Track financial goals and analyze success probabilities"
        icon={<Target size={24} />}
      />

      {/* Goals List */}
      <Card>
        <div className="flex justify-between items-center mb-4">
          <h3 className="text-lg font-semibold">Your Financial Goals</h3>
          <Button onClick={() => setShowAddGoal(!showAddGoal)} size="sm">
            <Plus size={16} className="mr-1" />
            Add Goal
          </Button>
        </div>

        {/* Add Goal Form */}
        {showAddGoal && (
          <div className="p-6 bg-background-hover rounded-lg mb-4">
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              <Input
                label="Goal Name"
                type="text"
                value={newGoal.name}
                onChange={(e) => setNewGoal({...newGoal, name: e.target.value})}
                placeholder="e.g., New Car, Vacation Home"
              />
              
              <Input
                label="Target Amount"
                type="number"
                value={newGoal.target_amount}
                onChange={(e) => setNewGoal({...newGoal, target_amount: parseFloat(e.target.value)})}
              />
              
              <Input
                label="Target Year"
                type="number"
                value={newGoal.target_year}
                onChange={(e) => setNewGoal({...newGoal, target_year: parseInt(e.target.value)})}
              />
              
              <Input
                label="Priority (1-10)"
                type="number"
                value={newGoal.priority}
                onChange={(e) => setNewGoal({...newGoal, priority: parseInt(e.target.value)})}
                helperText="1 = highest priority"
              />
              
              <div className="flex items-start">
                <Switch
                  label="Essential Goal"
                  checked={newGoal.is_essential}
                  onChange={(e) => setNewGoal({...newGoal, is_essential: e.target.checked})}
                  helperText="Must-have vs nice-to-have"
                />
              </div>
              
              <div className="flex items-start">
                <Switch
                  label="Adjust for Inflation"
                  checked={newGoal.inflation_adjusted}
                  onChange={(e) => setNewGoal({...newGoal, inflation_adjusted: e.target.checked})}
                  helperText="Account for rising costs"
                />
              </div>
            </div>
            <div className="flex gap-3 mt-6">
              <Button onClick={addGoal} size="sm">Save Goal</Button>
              <Button onClick={() => setShowAddGoal(false)} variant="secondary" size="sm">Cancel</Button>
            </div>
          </div>
        )}

        {/* Goals Table */}
        {goals.length > 0 ? (
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-4 py-2 text-left">Goal Name</th>
                  <th className="px-4 py-2 text-right">Amount</th>
                  <th className="px-4 py-2 text-right">Year</th>
                  <th className="px-4 py-2 text-center">Priority</th>
                  <th className="px-4 py-2 text-center">Type</th>
                  <th className="px-4 py-2 text-center">Actions</th>
                </tr>
              </thead>
              <tbody>
                {goals.map((goal) => (
                  <tr key={goal.goal_id} className="border-t">
                    <td className="px-4 py-2 font-medium">{goal.name}</td>
                    <td className="px-4 py-2 text-right">${goal.target_amount.toLocaleString()}</td>
                    <td className="px-4 py-2 text-right">{goal.target_year}</td>
                    <td className="px-4 py-2 text-center">
                      <Badge variant={goal.priority <= 3 ? 'error' : goal.priority <= 7 ? 'warning' : 'default'}>
                        {goal.priority}
                      </Badge>
                    </td>
                    <td className="px-4 py-2 text-center">
                      <Badge variant={goal.is_essential ? 'error' : 'default'}>
                        {goal.is_essential ? 'Essential' : 'Optional'}
                      </Badge>
                    </td>
                    <td className="px-4 py-2 text-center">
                      <button
                        onClick={() => removeGoal(goal.goal_id!)}
                        className="text-red-600 hover:text-red-800"
                      >
                        <Trash2 size={16} />
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        ) : (
          <p className="text-gray-500 text-center py-8">No goals added yet. Click "Add Goal" to get started.</p>
        )}

        {goals.length > 0 && (
          <div className="mt-4">
            <Button onClick={runAnalysis} disabled={isLoading}>
              Analyze Goals
            </Button>
          </div>
        )}
      </Card>

      {/* Analysis Results */}
      {analysisResult && (
        <>
          {/* Overall Summary */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Overall Goal Success</h3>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div>
                <p className="text-sm text-gray-600">All Goals Success</p>
                <p className="text-2xl font-bold">{(analysisResult.overall_success_probability * 100).toFixed(1)}%</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Essential Goals</p>
                <p className="text-2xl font-bold text-green-600">
                  {(analysisResult.essential_goals_success_probability * 100).toFixed(1)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Total Goal Value</p>
                <p className="text-2xl font-bold">${analysisResult.total_goal_value?.toLocaleString()}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Projected Portfolio</p>
                <p className="text-2xl font-bold">${analysisResult.projected_portfolio_value?.toLocaleString()}</p>
              </div>
            </div>
          </Card>

          {/* Individual Goal Results */}
          <Card>
            <h3 className="text-lg font-semibold mb-4">Goal-by-Goal Analysis</h3>
            <div className="space-y-4">
              {analysisResult.goal_results?.map((result: any, idx: number) => (
                <div key={idx} className="p-4 border rounded-lg">
                  <div className="flex justify-between items-start mb-3">
                    <div>
                      <h4 className="font-semibold text-lg">{result.goal_name}</h4>
                      <p className="text-sm text-gray-600">
                        Target: ${result.target_amount?.toLocaleString()} by {result.target_year}
                      </p>
                    </div>
                    <Badge 
                      variant={
                        result.success_probability >= 0.9 ? 'success' : 
                        result.success_probability >= 0.7 ? 'warning' : 
                        'error'
                      }
                    >
                      {(result.success_probability * 100).toFixed(1)}% Success
                    </Badge>
                  </div>
                  <div className="grid grid-cols-3 gap-4">
                    <div>
                      <p className="text-xs text-gray-500">Years Until Goal</p>
                      <p className="font-semibold">{result.years_until_goal} years</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Expected Shortfall</p>
                      <p className="font-semibold text-red-600">${result.expected_shortfall?.toLocaleString()}</p>
                    </div>
                    <div>
                      <p className="text-xs text-gray-500">Confidence Level</p>
                      <p className="font-semibold">
                        {result.success_probability >= 0.9 ? 'High' : 
                         result.success_probability >= 0.7 ? 'Medium' : 'Low'}
                      </p>
                    </div>
                  </div>
                  {result.recommendation && (
                    <div className="mt-3 p-3 bg-blue-50 rounded text-sm text-blue-900">
                      <strong>Recommendation:</strong> {result.recommendation}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </Card>

          {/* Recommendations */}
          {analysisResult.recommendations && analysisResult.recommendations.length > 0 && (
            <Card>
              <h3 className="text-lg font-semibold mb-4">Planning Recommendations</h3>
              <div className="space-y-3">
                {analysisResult.recommendations.map((rec: string, idx: number) => (
                  <div key={idx} className="p-3 bg-yellow-50 border border-yellow-200 rounded">
                    <p className="text-sm text-yellow-900">{rec}</p>
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

export default GoalPlanningPage;
