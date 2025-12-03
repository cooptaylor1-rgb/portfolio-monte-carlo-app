/**
 * ReportHeader Component
 * Professional header for advisor-grade reports with firm branding
 */
import React from 'react';
import type { ClientInfo } from '../../types';
import { formatReportDate, formatGeneratedDate } from '../../utils/reportFormatters';

interface ReportHeaderProps {
  clientInfo: ClientInfo;
  scenarioName?: string;
  firmName?: string;
  firmLogo?: string;
}

export const ReportHeader: React.FC<ReportHeaderProps> = ({
  clientInfo,
  scenarioName = 'Base Case Analysis',
  firmName = 'Salem Investment Counselors',
  firmLogo,
}) => {
  return (
    <div className="report-header border-b-2 border-accent-navy pb-8 mb-8 print:pb-6 print:mb-6">
      <div className="flex items-start justify-between mb-6">
        <div className="flex-1">
          {firmLogo && (
            <img 
              src={firmLogo} 
              alt={firmName}
              className="h-16 mb-4 print:h-12"
            />
          )}
          <h1 className="text-display font-display text-text-primary mb-2 print:text-4xl">
            Portfolio Analysis Report
          </h1>
          <p className="text-h3 text-text-secondary font-light print:text-xl">
            {scenarioName}
          </p>
        </div>
        
        <div className="text-right">
          <div className="text-body text-text-tertiary space-y-1">
            <div>
              <span className="text-text-secondary font-medium">Report Date:</span>{' '}
              {formatReportDate(clientInfo.report_date)}
            </div>
            <div>
              <span className="text-text-secondary font-medium">Generated:</span>{' '}
              {formatGeneratedDate()}
            </div>
            {clientInfo.client_id && (
              <div>
                <span className="text-text-secondary font-medium">Client ID:</span>{' '}
                {clientInfo.client_id}
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-6 border-t border-background-border">
        <div>
          <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-2">
            Client Information
          </p>
          <div className="space-y-1">
            <p className="text-h4 font-display text-text-primary">
              {clientInfo.client_name || 'Not Specified'}
            </p>
            {clientInfo.client_notes && (
              <p className="text-body text-text-tertiary">
                {clientInfo.client_notes}
              </p>
            )}
          </div>
        </div>
        
        <div>
          <p className="text-small font-semibold text-text-secondary uppercase tracking-wider mb-2">
            Prepared By
          </p>
          <div className="space-y-1">
            <p className="text-h4 font-display text-text-primary">
              {clientInfo.advisor_name || firmName}
            </p>
            <p className="text-body text-text-tertiary">
              {firmName}
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};
