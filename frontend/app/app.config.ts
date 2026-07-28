export default defineAppConfig({
  ui: {
    colors: {
      primary: 'blue',
      neutral: 'neutral'
    },
    input: {
      slots: {
        root: 'relative inline-flex items-center w-full'
      }
    },
    formField: {
      slots: {
        root: 'w-full'
      }
    }
  }
})
