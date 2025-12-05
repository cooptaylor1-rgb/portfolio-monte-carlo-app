/**
 * Cash Flow Projection Table
 * Phase 7: Updated with design system styling
 */
import React, { useState } from 'react';
import type { CashFlowProjection } from '../../types/reports';
import { AnalysisTable, type Column } from '../ui/AnalysisTable';
import { Button } from '../ui';
import { colors, formatChartCurrency } from '../../theme';

interface CashFlowTableProps {
  data: CashFlowProjection[];
}

export const CashFlowTable: React.FC<CashFlowTableProps> = ({ data }) => {
  const [showAll, setShowAll] = useState(false);
  const displayData = showAll ? data : data.slice(0, 10);

  const columns: Column<CashFlowProjection>[] = [
    {
      key: 'year',
      label: 'Year',
      align: 'left',
      cellClassName: 'font-semibold',
    },
    {
      key: 'age',
      label: 'Age',
      align: 'right',
    },
    {
      key: 'beginning_balance',
      label: 'Beginning Balance',
      align: 'right',
      format: (value: number) => (
        <span className="font-mono">
          {formatChartCurrency(value)}
        </span>
      ),
    },
    {
      key: 'income_sources_total',
      label: 'Income',
      align: 'right',
      format: (value: number) => (
        <span className="font-mono" style={{ color: colors.status.success.base }}>
          {formatChartCurrency(value)}
        </span>
      ),
    },
    {
      key: 'withdrawals',
      label: 'Withdrawals',
      align: 'right',
      format: (value: number) => (
        <span className="font-mono" style={{ color: colors.status.error.base }}>
          {formatChartCurrency(value)}
        </span>
      ),
    },
    {
      key: 'taxes',
      label: 'Taxes',
      align: 'right',
      format: (value: number) => (
        <span className="font-mono" style={{ color: colors.status.error.base }}>
          {formatChartCurrency(value)}
        </span>
      ),
    },
    {
      key: 'investment_return',
      label: 'Investment Return',
      align: 'right',
      format: (value: number) => (
        <span
          className="font-mono"
          style={{
            color: value >= 0 ? colors.status.success.base : colors.status.error.base,
          }}
        >
          {formatChartCurrency(value)}
        </span>
      ),
    },
    {
      key: 'ending_balance',
      label: 'Ending Balance',
      align: 'right',
      cellClassName: 'font-semibold',
      format: (value: number) => (
        <span className="font-mono">
          {formatChartCurrency(value)}
        </span>
      ),
    },
  ];

  return (
    <div 
      className="salem-card"
      style={{ 
        backgroundColor: colors.background.elevated,
        borderColor: colors.background.border 
      }}
    >
      <h3 className="text-h3 font-display text-text-primary mb-3">
        Cash Flow Projection Details
      </h3>
      <p className="text-body text-text-secondary mb-4">
        Year-by-year breakdown of portfolio cash flows (median scenario)
      </p>

      <div style={{ maxHeight: showAll ? '600px' : 'auto', overflowY: showAll ? 'auto' : 'visible' }}>
        <AnalysisTable<CashFlowProjection>
          columns={columns}
          data={displayData}
          variant="striped"
          stickyHeader={showAll}
        />
      </div>

      {data.length > 10 && (
        <div className="text-center mt-4">
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowAll(!showAll)}
          >
            {showAll ? 'Show Less' : `Show All ${data.length} Years`}
          </Button>
        </div>
      )}
    </div>
  );
};
