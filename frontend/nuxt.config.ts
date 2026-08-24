// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ['@nuxt/eslint', '@nuxt/ui', '@vueuse/nuxt', 'nuxt-pdfmake'],

  devtools: {
    enabled: true
  },

  css: ['~/assets/css/main.css'],

  routeRules: {
    '/api/**': {
      cors: true
    }
  },

  devServer: {
    port: 3012
  },

  // ── AI Assistant runtime config ──────────────────────────────
  // Default ke endpoint lokal yang diberikan. Bisa di-override lewat env.
  runtimeConfig: {
    ai: {
      baseURL: process.env.NUXT_AI_BASE_URL || 'http://localhost:20128/v1',
      apiKey: process.env.NUXT_AI_API_KEY || 'sk-dede08aea594e222-upk4p8-5bfa2c54',
      model: process.env.NUXT_AI_MODEL || 'qd/dmodel'
    }
  },

  compatibilityDate: '2026-06-30',

  vite: {
    optimizeDeps: {
      include: [
        '@internationalized/date',
        'chart.js',
        'date-fns',
        'maska/vue',
        'pdfmake/build/pdfmake', // CJS
        'pdfmake/build/vfs_fonts', // CJS
        'vue-chartjs',
        'zod'
      ]
    }
  },

  eslint: {
    config: {
      stylistic: {
        commaDangle: 'never',
        braceStyle: '1tbs'
      }
    }
  }
})
