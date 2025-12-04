/**
 * Tooltip - Accessible tooltip component
 * Provides contextual help information on hover/focus
 * 
 * Features:
 * - Auto-positioning (top, bottom, left, right)
 * - Keyboard accessible (shows on focus)
 * - ARIA labels for screen readers
 * - Delay on hover
 * - Dark theme styled
 * - Animated entrance
 */

import React, { useState, useRef, useEffect } from 'react';
import { colors } from '../../theme';

export interface TooltipProps {
  content: React.ReactNode;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
  delay?: number;
  className?: string;
  disabled?: boolean;
}

export const Tooltip: React.FC<TooltipProps> = ({
  content,
  children,
  position = 'top',
  delay = 200,
  className = '',
  disabled = false,
}) => {
  const [isVisible, setIsVisible] = useState(false);
  const [actualPosition, setActualPosition] = useState(position);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);
  const triggerRef = useRef<HTMLDivElement>(null);
  const tooltipRef = useRef<HTMLDivElement>(null);

  const showTooltip = () => {
    if (disabled) return;
    
    timeoutRef.current = setTimeout(() => {
      setIsVisible(true);
      // Calculate optimal position
      if (triggerRef.current && tooltipRef.current) {
        const triggerRect = triggerRef.current.getBoundingClientRect();
        const tooltipRect = tooltipRef.current.getBoundingClientRect();
        
        // Check if tooltip would go off screen and adjust position
        if (position === 'top' && triggerRect.top - tooltipRect.height < 0) {
          setActualPosition('bottom');
        } else if (position === 'bottom' && triggerRect.bottom + tooltipRect.height > window.innerHeight) {
          setActualPosition('top');
        } else if (position === 'left' && triggerRect.left - tooltipRect.width < 0) {
          setActualPosition('right');
        } else if (position === 'right' && triggerRect.right + tooltipRect.width > window.innerWidth) {
          setActualPosition('left');
        } else {
          setActualPosition(position);
        }
      }
    }, delay);
  };

  const hideTooltip = () => {
    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }
    setIsVisible(false);
  };

  useEffect(() => {
    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, []);

  const getPositionClasses = () => {
    const base = 'absolute z-50 px-md py-sm text-sm rounded-md shadow-lg transition-all duration-fast';
    
    switch (actualPosition) {
      case 'top':
        return `${base} bottom-full left-1/2 -translate-x-1/2 mb-2`;
      case 'bottom':
        return `${base} top-full left-1/2 -translate-x-1/2 mt-2`;
      case 'left':
        return `${base} right-full top-1/2 -translate-y-1/2 mr-2`;
      case 'right':
        return `${base} left-full top-1/2 -translate-y-1/2 ml-2`;
      default:
        return base;
    }
  };

  const getArrowClasses = () => {
    const base = 'absolute w-0 h-0 border-solid';
    
    switch (actualPosition) {
      case 'top':
        return `${base} border-t-8 border-x-8 border-b-0 border-x-transparent top-full left-1/2 -translate-x-1/2`;
      case 'bottom':
        return `${base} border-b-8 border-x-8 border-t-0 border-x-transparent bottom-full left-1/2 -translate-x-1/2`;
      case 'left':
        return `${base} border-l-8 border-y-8 border-r-0 border-y-transparent left-full top-1/2 -translate-y-1/2`;
      case 'right':
        return `${base} border-r-8 border-y-8 border-l-0 border-y-transparent right-full top-1/2 -translate-y-1/2`;
      default:
        return base;
    }
  };

  return (
    <div 
      className={`relative inline-block ${className}`}
      ref={triggerRef}
    >
      <div
        onMouseEnter={showTooltip}
        onMouseLeave={hideTooltip}
        onFocus={showTooltip}
        onBlur={hideTooltip}
        aria-describedby={isVisible ? 'tooltip' : undefined}
      >
        {children}
      </div>
      
      {isVisible && (
        <div
          id="tooltip"
          ref={tooltipRef}
          role="tooltip"
          className={`${getPositionClasses()} ${isVisible ? 'opacity-100 scale-100' : 'opacity-0 scale-95'}`}
          style={{
            backgroundColor: colors.background.base,
            color: colors.text.primary,
            border: `1px solid ${colors.background.border}`,
          }}
        >
          {content}
          <div 
            className={getArrowClasses()}
            style={{ borderTopColor: colors.background.base }}
          />
        </div>
      )}
    </div>
  );
};

// Simple text tooltip helper
export const TextTooltip: React.FC<{
  text: string;
  children: React.ReactNode;
  position?: 'top' | 'bottom' | 'left' | 'right';
}> = ({ text, children, position }) => (
  <Tooltip content={<span className="whitespace-nowrap">{text}</span>} position={position}>
    {children}
  </Tooltip>
);

export default Tooltip;
