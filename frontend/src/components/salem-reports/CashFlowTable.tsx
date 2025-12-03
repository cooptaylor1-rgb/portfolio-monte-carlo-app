/**
 * Cash Flow Projection Table
 * Detailed year-by-year cash flow breakdown
 */
import React, { useState } from 'react';
import type { CashFlowProjection } from '../../types/reports';

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

  return (
    <div className="salem-card">
      <h3 style={{ fontSize: 'var(--salem-text-xl)', marginBottom: 'var(--salem-spacing-md)' }}>
        Cash Flow Projection Details
      </h3>
      <p style={{ fontSize: 'var(--salem-text-sm)', color: 'var(--salem-gray-600)', marginBottom: 'var(--salem-spacing-md)' }}>
        Year-by-year breakdown of portfolio cash flows (median scenario)
      </p>

      <div style={{ overflowX: 'auto', maxHeight: showAll ? '600px' : 'auto', overflowY: showAll ? 'auto' : 'visible' }}>
        <table className="salem-table">
          <thead style={{ position: 'sticky', top: 0, backgroundColor: 'var(--salem-navy-primary)', zIndex: 1 }}>
            <tr>
              <th>Year</th>
              <th style={{ textAlign: 'right' }}>Age</th>
              <th style={{ textAlign: 'right' }}>Beginning Balance</th>
              <th style={{ textAlign: 'right' }}>Income</th>
              <th style={{ textAlign: 'right' }}>Withdrawals</th>
              <th style={{ textAlign: 'right' }}>Taxes</th>
              <th style={{ textAlign: 'right' }}>Investment Return</th>
              <th style={{ textAlign: 'right' }}>Ending Balance</th>
            </tr>
          </thead>
          <tbody>
            {displayData.map((row) => (
              <tr key={row.year}>
                <td style={{ fontWeight: 600 }}>{row.year}</td>
                <td style={{ textAlign: 'right' }}>{row.age}</td>
                <td style={{ textAlign: 'right', fontFamily: 'var(--salem-font-mono)' }}>
                  {formatCurrency(row.beginning_balance)}
                </td>
                <td style={{ textAlign: 'right', color: 'var(--salem-success)', fontFamily: 'var(--salem-font-mono)' }}>
                  {formatCurrency(row.income_sources_total)}
                </td>
                <td style={{ textAlign: 'right', color: 'var(--salem-danger)', fontFamily: 'var(--salem-font-mono)' }}>
                  {formatCurrency(row.withdrawals)}
                </td>
                <td style={{ textAlign: 'right', color: 'var(--salem-danger)', fontFamily: 'var(--salem-font-mono)' }}>
                  {formatCurrency(row.taxes)}
                </td>
                <td style={{ textAlign: 'right', color: row.investment_return >= 0 ? 'var(--salem-success)' : 'var(--salem-danger)', fontFamily: 'var(--salem-font-mono)' }}>
                  {formatCurrency(row.investment_return)}
                </td>
                <td style={{ textAlign: 'right', fontWeight: 600, fontFamily: 'var(--salem-font-mono)' }}>
                  {formatCurrency(row.ending_balance)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {data.length > 10 && (
        <div style={{ textAlign: 'center', marginTop: 'var(--salem-spacing-md)' }}>
          <button
            onClick={() => setShowAll(!showAll)}
            style={{
              padding: '8px 16px',
              backgroundColor: 'var(--salem-navy-primary)',
              color: 'white',
              border: 'none',
              borderRadius: 'var(--salem-border-radius)',
              cursor: 'pointer',
              fontSize: 'var(--salem-text-sm)',
              fontWeight: 500,
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--salem-navy-dark)';
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = 'var(--salem-navy-primary)';
            }}
          >
            {showAll ? 'Show Less' : `Show All ${data.length} Years`}
          </button>
        </div>
      )}
    </div>
  );
};
