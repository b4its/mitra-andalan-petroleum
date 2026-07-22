<script setup lang="ts">
import type { AuthFormField, FormSubmitEvent } from "@nuxt/ui";
import { z } from "zod";

const toast = useToast();
const router = useRouter();
const { setUser } = useAuth();

const schema = z.object({
  email: z.string().email("Invalid email"),
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

  // simulate network delay while waiting for real backend
  await new Promise((resolve) => setTimeout(resolve, 800));

  const account = dummyAccounts.find(
    (acc) =>
      acc.email === event.data.email && acc.password === event.data.password,
  );

  loading.value = false;

  if (!account) {
    toast.add({
      title: "Login failed",
      description: "Invalid email or password.",
      color: "error",
    });
    return;
  }

  setUser({
    email: account.email,
    name: account.name,
    role: account.role,
    token: `dummy-token-${Date.now()}`,
    loggedInAt: new Date().toISOString(),
  });

  toast.add({
    title: "Logged in",
    description: `Welcome, ${account.name}! (${account.role})`,
    color: "success",
  });

  router.push(`/${account.role}`);
}
</script>

<template>
  <UPageCard class="max-w-md mx-auto mt-48">
    <UAuthForm
      title="Sign In MAP"
      description="*Dummy login while backend is in progress."
      icon="i-lucide-log-in"
      :schema="schema"
      :fields="fields"
      :loading="loading"
      :submit="{ label: 'Sign in' }"
      @submit="onSubmit"
    />

    <template #footer>
      <div class="text-xs text-muted space-y-1">
        <p class="font-medium">Dummy accounts:</p>
        <p v-for="acc in dummyAccounts" :key="acc.email">
          {{ acc.role }}: {{ acc.email }} / {{ acc.password }}
        </p>
      </div>
    </template>
  </UPageCard>
</template>
