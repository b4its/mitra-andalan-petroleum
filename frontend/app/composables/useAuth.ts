export type Role = "admin" | "operations" | "marketing" | "finance";

export interface AuthUser {
  name: string;
  email: string;
  role: Role;
  token: string;
  loggedInAt: string;
}

export function useAuth() {
  const user = ref<AuthUser | null>(null);

  function loadUser() {
    if (import.meta.server) return;
    const raw = localStorage.getItem("auth");
    user.value = raw ? JSON.parse(raw) : null;
  }

  function setUser(newUser: AuthUser) {
    localStorage.setItem("auth", JSON.stringify(newUser));
    user.value = newUser;
  }

  function logout() {
    localStorage.removeItem("auth");
    user.value = null;
  }

  const isLoggedIn = computed(() => !!user.value);

  onMounted(loadUser);

  return { user, isLoggedIn, loadUser, setUser, logout };
}
