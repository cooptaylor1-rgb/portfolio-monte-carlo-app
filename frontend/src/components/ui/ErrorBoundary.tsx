/**
 * ErrorBoundary - Catch and display errors gracefully
 * Phase 6: Better error handling across the application
 */
import React, { Component, ErrorInfo, ReactNode } from 'react';
import { AlertCircle, RefreshCw, Home } from 'lucide-react';
import { colors } from '../../theme';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
  errorInfo: ErrorInfo | null;
}

export class ErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
    };
  }

  static getDerivedStateFromError(error: Error): State {
    return {
      hasError: true,
      error,
      errorInfo: null,
    };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
    });
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // Use custom fallback if provided
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // Default error UI
      return (
        <div className="min-h-screen bg-background-base flex items-center justify-center p-4">
          <div className="max-w-2xl w-full">
            <div
              className="bg-background-elevated border border-status-error-base rounded-lg p-8"
              role="alert"
              aria-live="assertive"
            >
              {/* Error Icon */}
              <div className="flex justify-center mb-6">
                <div className="w-16 h-16 rounded-full bg-status-error-base bg-opacity-10 flex items-center justify-center">
                  <AlertCircle size={32} style={{ color: colors.status.error.base }} />
                </div>
              </div>

              {/* Error Message */}
              <h1 className="text-h2 font-display text-text-primary text-center mb-3">
                Something went wrong
              </h1>
              <p className="text-body text-text-secondary text-center mb-6">
                We encountered an unexpected error. Please try refreshing the page or
                returning to the home screen.
              </p>

              {/* Error Details (in development) */}
              {import.meta.env.DEV && this.state.error && (
                <details className="mb-6 p-4 bg-background-base rounded border border-background-border">
                  <summary className="text-small font-semibold text-text-primary cursor-pointer mb-2">
                    Error Details (Development Only)
                  </summary>
                  <div className="text-micro text-text-tertiary space-y-2">
                    <div>
                      <strong>Error:</strong>{' '}
                      <code className="text-status-error-light">{this.state.error.message}</code>
                    </div>
                    {this.state.errorInfo && (
                      <div>
                        <strong>Stack:</strong>
                        <pre className="mt-2 p-2 bg-background-elevated rounded overflow-auto text-micro">
                          {this.state.errorInfo.componentStack}
                        </pre>
                      </div>
                    )}
                  </div>
                </details>
              )}

              {/* Action Buttons */}
              <div className="flex flex-wrap gap-3 justify-center">
                <button
                  onClick={this.handleReset}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-accent-gold text-background-base rounded-md font-semibold hover:bg-opacity-90 transition-colors"
                >
                  <RefreshCw size={16} />
                  Try Again
                </button>
                <button
                  onClick={this.handleGoHome}
                  className="inline-flex items-center gap-2 px-6 py-3 bg-background-hover text-text-primary border border-background-border rounded-md font-semibold hover:bg-background-border transition-colors"
                >
                  <Home size={16} />
                  Go to Home
                </button>
              </div>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}
