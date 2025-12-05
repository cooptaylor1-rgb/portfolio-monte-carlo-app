/**
 * Cash Flow Projection Table
 * Detailed year-by-year cash flow breakdown
 */
import React, { useState } from 'react';
import type { CashFlowProjection } from '../../types/reports';
import { AnalysisTable, type Column } from '../ui/AnalysisTable';
import { Button } from '../ui';

interface CashFlowTableProps {
  data: CashFlowProjection[];
}

const formatCurrency = (value: number): string => {
  const absValue = Math.abs(value);
  const sign = value < 0 ? '-' : '';
  if (absValue >= 1e6) {
    return `${sign}$${(absValue / 1e6).toFixed(2)}M`;
  } else if (absValue >= 1e3) {
    return `${sign}$${(absValue / 1e3).toFixed(0)}K`;
  }
  return `${sign}$${absValue.toLocaleString(undefined, { maximumFractionDigits: 0 })}`;
};

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
        <span style={{ fontFamily: 'var(--salem-font-mono)' }}>
          {formatCurrency(value)}
        </span>
      ),
    },
    {
      key: 'income_sources_total',
      label: 'Income',
      align: 'right',
      format: (value: number) => (
        <span style={{ color: 'var(--salem-success)', fontFamily: 'var(--salem-font-mono)' }}>
          {formatCurrency(value)}
        </span>
      ),
    },
    {
      key: 'withdrawals',
      label: 'Withdrawals',
      align: 'right',
      format: (value: number) => (
        <span style={{ color: 'var(--salem-danger)', fontFamily: 'var(--salem-font-mono)' }}>
          {formatCurrency(value)}
        </span>
      ),
    },
    {
      key: 'taxes',
      label: 'Taxes',
      align: 'right',
      format: (value: number) => (
        <span style={{ color: 'var(--salem-danger)', fontFamily: 'var(--salem-font-mono)' }}>
          {formatCurrency(value)}
        </span>
      ),
    },
    {
      key: 'investment_return',
      label: 'Investment Return',
      align: 'right',
      format: (value: number) => (
        <span
          style={{
            color: value >= 0 ? 'var(--salem-success)' : 'var(--salem-danger)',
            fontFamily: 'var(--salem-font-mono)',
          }}
        >
          {formatCurrency(value)}
        </span>
      ),
    },
    {
      key: 'ending_balance',
      label: 'Ending Balance',
      align: 'right',
      cellClassName: 'font-semibold',
      format: (value: number) => (
        <span style={{ fontFamily: 'var(--salem-font-mono)' }}>
          {formatCurrency(value)}
        </span>
      ),
    },
  ];

  return (
    <div className="salem-card">
      <h3 style={{ fontSize: 'var(--salem-text-xl)', marginBottom: 'var(--salem-spacing-md)' }}>
        Cash Flow Projection Details
      </h3>
      <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
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
        <div style={{ textAlign: 'center', marginTop: 'var(--salem-spacing-md)' }}>
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
