<script setup lang="ts">
import type { AuthFormField, FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";

const toast = useToast();
const router = useRouter();
const { setUser } = useAuth();
const { post } = useApi();

const schema = z.object({
  email: z.email("Invalid email"),
  password: z.string().min(6, "Must be at least 6 characters"),
});

type Schema = z.output<typeof schema>;

const fields: AuthFormField[] = [
  {
    name: "email",
    type: "email",
    label: "Email",
    placeholder: "Enter your email",
    required: true,
  },
  {
    name: "password",
    type: "password",
    label: "Password",
    placeholder: "Enter your password",
    required: true,
  },
];

const loading = ref(false);

async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true;

  try {
    const result = await post<{
      name: string;
      email: string;
      role: string;
      token: string;
      logged_in_at: string;
    }>("/auth/login", {
      email: event.data.email,
      password: event.data.password,
    });

    // setUser({
    //   email: result.email,
    //   name: result.name,
    //   password: result.password,
    //   role: result.role as any,
    //   token: result.token,
    //   loggedInAt: result.logged_in_at,
    // });

    toast.add({
      title: "Logged in",
      description: `Welcome, ${result.name}! (${result.role})`,
      color: "success",
    });

    router.push(`/${result.role}`);
  } catch (err: any) {
    toast.add({
      title: "Login failed",
      description: err.message || "Invalid email or password.",
      color: "error",
    });
  } finally {
    loading.value = false;
  }
}
</script>

<template>
  <UPageCard class="max-w-md mx-auto mt-48">
    <UAuthForm
      title="Sign In MAP"
      description="Login dengan akun Anda"
      icon="i-lucide-log-in"
      :schema="schema"
      :fields="fields"
      :loading="loading"
      :submit="{ label: 'Sign in' }"
      @submit="onSubmit"
    />

    <template #footer>
      <div class="text-xs text-muted space-y-1">
        <p class="font-medium">Akun tersedia:</p>
        <p v-for="acc in dummyAccounts" :key="acc.email">
          {{ acc.role }}: {{ acc.email }} / {{ acc.password }}
        </p>
      </div>
    </template>
  </UPageCard>
</template>
