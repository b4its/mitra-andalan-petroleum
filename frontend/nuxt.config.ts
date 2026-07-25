// https://nuxt.com/docs/api/configuration/nuxt-config
export default defineNuxtConfig({
  modules: ["@nuxt/eslint", "@nuxt/ui", "@vueuse/nuxt", "nuxt-pdfmake"],

  devtools: {
    enabled: true,
  },

  css: ["~/assets/css/main.css"],

  routeRules: {
    "/api/**": {
      cors: true,
    },
  },

  nitro: {
    devProxy: {
      "/api/v1": {
        target: "http://localhost:8000/api/v1",
        changeOrigin: true,
      },
    },
  },

  compatibilityDate: "2026-06-30",

  eslint: {
    config: {
      stylistic: {
        commaDangle: "never",
        braceStyle: "1tbs",
      },
    },
  },

  vite: {
    optimizeDeps: {
      include: [
        "date-fns",
        "maska/vue",
        "pdfmake/build/pdfmake", // CJS
        "pdfmake/build/vfs_fonts", // CJS
        "zod",
      ],
    },
  },
});
