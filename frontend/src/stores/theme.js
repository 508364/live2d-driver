import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: localStorage.getItem('app-theme') || 'dark',
    customTheme: JSON.parse(localStorage.getItem('custom-theme')) || {
      primary: '#42b983',
      background: '#1e1e1e',
      sidebar: '#252525',
      text: '#ffffff',
      cardBg: '#2d2d2d'
    }
  }),
  actions: {
    setTheme(theme) {
      this.currentTheme = theme
      localStorage.setItem('app-theme', theme)
      this.applyTheme()
    },
    
    setCustomTheme(theme) {
      this.customTheme = theme
      localStorage.setItem('custom-theme', JSON.stringify(theme))
      this.applyTheme()
    },
    
    applyTheme() {
      const root = document.documentElement
      
      if (this.currentTheme === 'custom') {
        // 应用自定义主题
        Object.entries(this.customTheme).forEach(([key, value]) => {
          root.style.setProperty(`--${key}`, value)
        })
      } else {
        // 应用预设主题
        const themes = {
          dark: {
            primary: '#42b983',
            background: '#1e1e1e',
            sidebar: '#252525',
            text: '#ffffff',
            cardBg: '#2d2d2d'
          },
          light: {
            primary: '#42b983',
            background: '#ffffff',
            sidebar: '#f5f5f5',
            text: '#333333',
            cardBg: '#f9f9f9'
          },
          blue: {
            primary: '#2196f3',
            background: '#0d47a1',
            sidebar: '#1a237e',
            text: '#ffffff',
            cardBg: '#283593'
          }
        }
        
        const theme = themes[this.currentTheme] || themes.dark
        Object.entries(theme).forEach(([key, value]) => {
          root.style.setProperty(`--${key}`, value)
        })
      }
    }
  }
})