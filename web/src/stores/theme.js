// src/stores/theme.js
import { defineStore } from 'pinia'

export const useThemeStore = defineStore('theme', {
  state: () => ({
    currentTheme: 'dark'
  }),
  actions: {
    setTheme(theme) {
      this.currentTheme = theme
    }
  }
})