/**
 * ExportCard Component
 * Professional export option card with format details, preview, and actions
 */
import React from 'react';
import { Card } from './Card';
import { Button } from './Button';
import { Badge } from './Badge';
import { LucideIcon } from 'lucide-react';

export interface ExportFormat {
  id: string;
  name: string;
  description: string;
  icon: LucideIcon;
  fileType: string;
  includes: string[];
  recommended?: boolean;
  size?: string;
}

export interface ExportCardProps {
  format: ExportFormat;
  onExport: (formatId: string) => void;
  isExporting?: boolean;
  disabled?: boolean;
}

export const ExportCard: React.FC<ExportCardProps> = ({
  format,
  onExport,
  isExporting = false,
  disabled = false,
}) => {
  const Icon = format.icon;

  return (
    <Card className="hover:border-accent-gold transition-all duration-200 hover:shadow-md">
      <div className="flex flex-col h-full">
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div className="flex items-center gap-3">
            <div className="w-12 h-12 rounded-lg bg-accent-gold/10 flex items-center justify-center flex-shrink-0">
              <Icon size={24} className="text-accent-gold" />
            </div>
            <div>
              <h3 className="text-h4 font-semibold text-text-primary mb-1">
                {format.name}
              </h3>
              {format.recommended && (
                <Badge variant="success" size="sm">
                  Recommended
                </Badge>
              )}
            </div>
          </div>
        </div>

        {/* Description */}
        <p className="text-small text-text-secondary mb-4 flex-grow">
          {format.description}
        </p>

        {/* File Details */}
        <div className="flex items-center gap-4 mb-4 text-micro text-text-tertiary">
          <div>
            <span className="font-semibold">Format:</span> {format.fileType}
          </div>
          {format.size && (
            <div>
              <span className="font-semibold">Size:</span> ~{format.size}
            </div>
          )}
        </div>

        {/* Includes List */}
        <div className="mb-6">
          <p className="text-micro font-semibold text-text-tertiary uppercase mb-2">
            Includes:
          </p>
          <ul className="space-y-1">
            {format.includes.map((item, index) => (
              <li key={index} className="text-small text-text-secondary flex items-start gap-2">
                <span className="text-accent-gold mt-0.5">•</span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </div>

        {/* Export Button */}
        <Button
          variant={format.recommended ? 'primary' : 'secondary'}
          size="md"
          onClick={() => onExport(format.id)}
          loading={isExporting}
          disabled={disabled || isExporting}
          className="w-full"
        >
          {isExporting ? 'Exporting...' : `Export ${format.fileType}`}
        </Button>
      </div>
    </Card>
  );
};

/**
 * ExportProgress Component
 * Shows export progress with status updates
 */
export interface ExportProgressProps {
  format: string;
  status: 'preparing' | 'generating' | 'complete' | 'error';
  message?: string;
  onClose?: () => void;
}

export const ExportProgress: React.FC<ExportProgressProps> = ({
  format,
  status,
  message,
  onClose,
}) => {
  const getStatusColor = () => {
    switch (status) {
      case 'complete':
        return 'text-status-success-base';
      case 'error':
        return 'text-status-error-base';
      default:
        return 'text-accent-gold';
    }
  };

  const getStatusIcon = () => {
    switch (status) {
      case 'complete':
        return '✓';
      case 'error':
        return '✕';
      default:
        return '○';
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50 w-96 animate-slide-in-right">
      <Card className="border-2 border-accent-gold shadow-xl">
        <div className="flex items-start justify-between mb-3">
          <div className="flex items-center gap-3">
            <div
              className={`w-10 h-10 rounded-full flex items-center justify-center font-bold text-xl ${
                status === 'preparing' || status === 'generating'
                  ? 'bg-accent-gold/20 text-accent-gold animate-pulse'
                  : status === 'complete'
                  ? 'bg-status-success-light text-status-success-base'
                  : 'bg-status-error-light text-status-error-base'
              }`}
            >
              {getStatusIcon()}
            </div>
            <div>
              <h4 className="text-body font-semibold text-text-primary">
                Exporting {format}
              </h4>
              <p className={`text-small ${getStatusColor()}`}>
                {status === 'preparing' && 'Preparing export...'}
                {status === 'generating' && 'Generating file...'}
                {status === 'complete' && 'Export complete!'}
                {status === 'error' && 'Export failed'}
              </p>
            </div>
          </div>
          {onClose && (status === 'complete' || status === 'error') && (
            <button
              onClick={onClose}
              className="text-text-tertiary hover:text-text-primary transition-colors"
            >
              ✕
            </button>
          )}
        </div>

        {message && (
          <p className="text-small text-text-secondary mb-2">{message}</p>
        )}

        {/* Progress bar for active exports */}
        {(status === 'preparing' || status === 'generating') && (
          <div className="w-full h-2 bg-background-border rounded-full overflow-hidden">
            <div className="h-full bg-accent-gold animate-progress-indeterminate" />
          </div>
        )}
      </Card>
    </div>
  );
};
