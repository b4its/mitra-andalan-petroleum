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
        'zod',
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
