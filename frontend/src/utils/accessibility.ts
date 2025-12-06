/**
 * Accessibility Utilities
 * Helper functions for keyboard navigation, focus management, and ARIA support
 */

/**
 * Trap focus within a container (for modals, dropdowns)
 * @param container - The container element to trap focus within
 * @returns Cleanup function to remove event listeners
 */
export const trapFocus = (container: HTMLElement): (() => void) => {
  const focusableElements = container.querySelectorAll<HTMLElement>(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
  
  const firstElement = focusableElements[0];
  const lastElement = focusableElements[focusableElements.length - 1];

  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key !== 'Tab') return;

    if (e.shiftKey) {
      // Shift + Tab
      if (document.activeElement === firstElement) {
        e.preventDefault();
        lastElement?.focus();
      }
    } else {
      // Tab
      if (document.activeElement === lastElement) {
        e.preventDefault();
        firstElement?.focus();
      }
    }
  };

  container.addEventListener('keydown', handleKeyDown);

  // Focus first element on mount
  firstElement?.focus();

  // Return cleanup function
  return () => {
    container.removeEventListener('keydown', handleKeyDown);
  };
};

/**
 * Handle escape key to close modals/dropdowns
 * @param onEscape - Callback function to execute on escape
 * @returns Cleanup function
 */
export const handleEscapeKey = (onEscape: () => void): (() => void) => {
  const handleKeyDown = (e: KeyboardEvent) => {
    if (e.key === 'Escape') {
      onEscape();
    }
  };

  document.addEventListener('keydown', handleKeyDown);

  return () => {
    document.removeEventListener('keydown', handleKeyDown);
  };
};

/**
 * Generate unique ID for ARIA attributes
 * @param prefix - Prefix for the ID
 * @returns Unique ID string
 */
export const generateAriaId = (prefix: string): string => {
  return `${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Announce message to screen readers
 * @param message - Message to announce
 * @param priority - 'polite' or 'assertive'
 */
export const announceToScreenReader = (
  message: string,
  priority: 'polite' | 'assertive' = 'polite'
): void => {
  const announcement = document.createElement('div');
  announcement.setAttribute('role', 'status');
  announcement.setAttribute('aria-live', priority);
  announcement.setAttribute('aria-atomic', 'true');
  announcement.className = 'sr-only';
  announcement.textContent = message;

  document.body.appendChild(announcement);

  // Remove after announcement
  setTimeout(() => {
    document.body.removeChild(announcement);
  }, 1000);
};

/**
 * Check if element is keyboard focusable
 * @param element - Element to check
 * @returns Boolean indicating if element is focusable
 */
export const isFocusable = (element: HTMLElement): boolean => {
  if (element.tabIndex < 0) return false;
  if (element.hasAttribute('disabled')) return false;
  if (element.getAttribute('aria-hidden') === 'true') return false;

  return element.matches(
    'button, [href], input, select, textarea, [tabindex]:not([tabindex="-1"])'
  );
};

/**
 * Get all focusable elements within a container
 * @param container - Container element
 * @returns Array of focusable elements
 */
export const getFocusableElements = (
  container: HTMLElement
): HTMLElement[] => {
  const elements = Array.from(
    container.querySelectorAll<HTMLElement>(
      'button:not([disabled]), [href], input:not([disabled]), select:not([disabled]), textarea:not([disabled]), [tabindex]:not([tabindex="-1"])'
    )
  );

  return elements.filter((el) => {
    return (
      el.offsetWidth > 0 &&
      el.offsetHeight > 0 &&
      window.getComputedStyle(el).visibility !== 'hidden'
    );
  });
};

/**
 * Restore focus to previously focused element
 * @param previousElement - Element to restore focus to
 */
export const restoreFocus = (previousElement: HTMLElement | null): void => {
  if (previousElement && document.body.contains(previousElement)) {
    previousElement.focus();
  }
};

/**
 * Format number for screen readers (e.g., currency, percentages)
 * @param value - Number to format
 * @param type - Type of formatting
 * @returns Formatted string for screen readers
 */
export const formatForScreenReader = (
  value: number,
  type: 'currency' | 'percentage' | 'number' = 'number'
): string => {
  switch (type) {
    case 'currency':
      return `${value.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}`;
    case 'percentage':
      return `${value.toFixed(1)} percent`;
    default:
      return value.toLocaleString('en-US');
  }
};

/**
 * Create skip link for keyboard navigation
 * @param targetId - ID of target element to skip to
 * @param label - Label for skip link
 * @returns Skip link element
 */
export const createSkipLink = (
  targetId: string,
  label: string = 'Skip to main content'
): HTMLAnchorElement => {
  const skipLink = document.createElement('a');
  skipLink.href = `#${targetId}`;
  skipLink.textContent = label;
  skipLink.className =
    'sr-only focus:not-sr-only focus:absolute focus:top-4 focus:left-4 focus:z-50 focus:px-4 focus:py-2 focus:bg-accent-gold focus:text-background-base focus:rounded-sm';

  return skipLink;
};

/**
 * Set up roving tabindex for a group of elements (e.g., radio group, toolbar)
 * @param container - Container element
 * @param selector - Selector for focusable items
 * @returns Cleanup function
 */
export const setupRovingTabindex = (
  container: HTMLElement,
  selector: string
): (() => void) => {
  const items = Array.from(container.querySelectorAll<HTMLElement>(selector));
  let currentIndex = 0;

  // Set initial tabindex
  items.forEach((item, index) => {
    item.tabIndex = index === 0 ? 0 : -1;
  });

  const handleKeyDown = (e: KeyboardEvent) => {
    if (!['ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown', 'Home', 'End'].includes(e.key)) {
      return;
    }

    e.preventDefault();

    // Update tabindex
    items[currentIndex].tabIndex = -1;

    switch (e.key) {
      case 'ArrowLeft':
      case 'ArrowUp':
        currentIndex = currentIndex === 0 ? items.length - 1 : currentIndex - 1;
        break;
      case 'ArrowRight':
      case 'ArrowDown':
        currentIndex = currentIndex === items.length - 1 ? 0 : currentIndex + 1;
        break;
      case 'Home':
        currentIndex = 0;
        break;
      case 'End':
        currentIndex = items.length - 1;
        break;
    }

    items[currentIndex].tabIndex = 0;
    items[currentIndex].focus();
  };

  container.addEventListener('keydown', handleKeyDown);

  return () => {
    container.removeEventListener('keydown', handleKeyDown);
  };
};
