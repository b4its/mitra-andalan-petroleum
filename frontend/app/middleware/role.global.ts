const PROTECTED_ROLES = ['admin', 'operations', 'marketing', 'finance', 'accounting']

export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return

  const raw = localStorage.getItem('auth')
  const user = raw ? JSON.parse(raw) : null

  if (to.path === '/') {
    if (user) {
      return navigateTo(`/${user.role}`)
    }
    return navigateTo('/login')
  }

  const firstSegment = to.path.split('/')[1]

  if (!PROTECTED_ROLES.includes(firstSegment || '')) return

  if (!user) {
    return navigateTo('/login')
  }

  // Admin dapat mengakses halaman role mana pun
  if (user.role === 'admin') return

  if (user.role !== firstSegment) {
    return navigateTo(`/${user.role}`)
  }
})
