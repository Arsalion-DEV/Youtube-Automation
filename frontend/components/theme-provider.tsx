"use client"

import * as React from "react"
import { ThemeProvider as NextThemesProvider } from "next-themes"
import { type ThemeProviderProps } from "next-themes/dist/types"

interface ExtendedThemeProviderProps extends ThemeProviderProps {
  accentColor?: string
  fontSize?: 'sm' | 'md' | 'lg'
  borderRadius?: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  highContrast?: boolean
}

interface ThemeContextValue {
  accentColor: string
  fontSize: 'sm' | 'md' | 'lg'
  borderRadius: 'none' | 'sm' | 'md' | 'lg' | 'xl'
  highContrast: boolean
  setAccentColor: (color: string) => void
  setFontSize: (size: 'sm' | 'md' | 'lg') => void
  setBorderRadius: (radius: 'none' | 'sm' | 'md' | 'lg' | 'xl') => void
  setHighContrast: (enabled: boolean) => void
}

const ThemeContext = React.createContext<ThemeContextValue | undefined>(undefined)

export function ThemeProvider({ 
  children, 
  accentColor = '#3b82f6',
  fontSize = 'md',
  borderRadius = 'md',
  highContrast = false,
  ...props 
}: ExtendedThemeProviderProps) {
  const [currentAccentColor, setCurrentAccentColor] = React.useState(accentColor)
  const [currentFontSize, setCurrentFontSize] = React.useState(fontSize)
  const [currentBorderRadius, setCurrentBorderRadius] = React.useState(borderRadius)
  const [currentHighContrast, setCurrentHighContrast] = React.useState(highContrast)

  React.useEffect(() => {
    const root = document.documentElement
    
    // Set CSS custom properties for theme customization
    root.style.setProperty('--accent-color', currentAccentColor)
    root.style.setProperty('--font-size-scale', currentFontSize === 'sm' ? '0.875' : currentFontSize === 'lg' ? '1.125' : '1')
    root.style.setProperty('--border-radius-scale', 
      currentBorderRadius === 'none' ? '0' :
      currentBorderRadius === 'sm' ? '0.125rem' :
      currentBorderRadius === 'lg' ? '0.75rem' :
      currentBorderRadius === 'xl' ? '1rem' :
      '0.5rem'
    )
    
    if (currentHighContrast) {
      root.classList.add('high-contrast')
    } else {
      root.classList.remove('high-contrast')
    }
  }, [currentAccentColor, currentFontSize, currentBorderRadius, currentHighContrast])

  const contextValue: ThemeContextValue = {
    accentColor: currentAccentColor,
    fontSize: currentFontSize,
    borderRadius: currentBorderRadius,
    highContrast: currentHighContrast,
    setAccentColor: setCurrentAccentColor,
    setFontSize: setCurrentFontSize,
    setBorderRadius: setCurrentBorderRadius,
    setHighContrast: setCurrentHighContrast,
  }

  return (
    <ThemeContext.Provider value={contextValue}>
      <NextThemesProvider {...props}>
        {children}
      </NextThemesProvider>
    </ThemeContext.Provider>
  )
}

export const useTheme = () => {
  const context = React.useContext(ThemeContext)
  if (context === undefined) {
    throw new Error("useTheme must be used within a ThemeProvider")
  }
  return context
}

export { ThemeProvider as default }