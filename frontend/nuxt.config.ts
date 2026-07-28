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

  compatibilityDate: '2026-06-30',

  nitro: {
    devProxy: {
      '/api/v1': {
        target: process.env.NUXT_API_PROXY_TARGET || ['http://', '[redacted]:8000/api/v1'].join(''),
        changeOrigin: true
      }
    }
  },

  vite: {
    optimizeDeps: {
      include: [
        'date-fns',
        'maska/vue',
        'chart.js',
        'pdfmake/build/pdfmake', // CJS
        'pdfmake/build/vfs_fonts', // CJS
        'zod',
        'vue-chartjs'
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
