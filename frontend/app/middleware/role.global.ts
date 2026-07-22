const PROTECTED_ROLES = ["admin", "operations", "marketing", "finance"];

export default defineNuxtRouteMiddleware((to) => {
  if (import.meta.server) return;

  const firstSegment = to.path.split("/")[1];

  if (!PROTECTED_ROLES.includes(firstSegment || "")) return;

  const raw = localStorage.getItem("auth");
  const user = raw ? JSON.parse(raw) : null;

  if (!user) {
    return navigateTo("/login");
  }

  if (user.role !== firstSegment) {
    return navigateTo(`/${user.role}`);
  }
});
