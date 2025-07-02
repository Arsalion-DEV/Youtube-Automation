"use client"

// Import fixed components using default imports
import EnterpriseApp from './enterprise/EnterpriseApp'
import EnterpriseNavigation from './enterprise/EnterpriseNavigation'
import EnterpriseMainDashboard from './enterprise/EnterpriseMainDashboard'

// Re-export as both default and named exports for maximum compatibility
export default EnterpriseApp
export { EnterpriseApp, EnterpriseNavigation, EnterpriseMainDashboard }

// Additional enterprise components and utilities
export const EnterpriseComponents = {
  EnterpriseApp,
  EnterpriseNavigation,
  EnterpriseMainDashboard,
}

// Enterprise configuration
export const enterpriseConfig = {
  version: '2.0.0',
  features: {
    analytics: true,
    monetization: true,
    abTesting: true,
    whiteLabel: true,
    teamManagement: true,
  },
  apiEndpoints: {
    health: '/api/v1/enterprise/health',
    analytics: '/api/v1/enterprise/analytics',
    monetization: '/api/v1/enterprise/monetization',
    abTesting: '/api/v1/enterprise/ab-testing',
  },
}

// Utility functions for enterprise features
export const enterpriseUtils = {
  checkFeatureAvailability: (feature: keyof typeof enterpriseConfig.features) => {
    return enterpriseConfig.features[feature]
  },
  
  formatCurrency: (amount: number, currency = 'USD') => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency,
    }).format(amount)
  },
  
  formatNumber: (num: number) => {
    return new Intl.NumberFormat('en-US').format(num)
  },
  
  formatPercentage: (num: number, decimals = 1) => {
    return `${num.toFixed(decimals)}%`
  },
}

// Enterprise theme configuration
export const enterpriseTheme = {
  colors: {
    primary: {
      50: '#eff6ff',
      100: '#dbeafe',
      500: '#3b82f6',
      600: '#2563eb',
      900: '#1e3a8a',
    },
    enterprise: {
      50: '#fef3c7',
      100: '#fde68a',
      500: '#f59e0b',
      600: '#d97706',
      900: '#78350f',
    },
  },
  gradients: {
    primary: 'from-blue-500 to-purple-600',
    enterprise: 'from-orange-500 to-red-600',
    success: 'from-green-500 to-emerald-600',
  },
}