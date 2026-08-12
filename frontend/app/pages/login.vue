<script setup lang="ts">
import type { AuthFormField, FormSubmitEvent } from '@nuxt/ui'
import { z } from 'zod'
import type { Role } from '~/types'

const toast = useToast()
const router = useRouter()
const { setUser } = useAuth()
const { post, get } = useApi()

interface Account {
  id: string
  name: string
  email: string
  role: string
  password: string
}

const { data: accounts } = await useAsyncData<Account[]>(
  'login-accounts',
  () => get<Account[]>('/profiles/demo'),
  { default: () => [], lazy: true }
)

const schema = z.object({
  email: z.email('Email tidak valid'),
  password: z.string().min(6, 'Minimal 6 karakter')
})

type Schema = z.output<typeof schema>

const fields: AuthFormField[] = [
  {
    name: 'email',
    type: 'email',
    label: 'Email',
    placeholder: 'Masukkan email',
    required: true
  },
  {
    name: 'password',
    type: 'password',
    label: 'Kata Sandi',
    placeholder: 'Masukkan kata sandi',
    required: true
  }
]

const loading = ref(false)

const authFormRef = useTemplateRef('authFormRef')

function fillEmail(email: string) {
  const formRef = authFormRef.value
  if (formRef) {
    formRef.state.email = email
  }
}

async function onSubmit(event: FormSubmitEvent<Schema>) {
  loading.value = true

  try {
    const result = await post<
      {
        id: string
        name: string
        email: string
        role: string
        token: string
        logged_in_at: string
      },
      {
        email: string
        password: string
      }
    >('/auth/login', {
      email: event.data.email,
      password: event.data.password
    })

    setUser({
      id: result.id,
      email: result.email,
      name: result.name,
      password: event.data.password,
      role: result.role as Role,
      token: result.token,
      loggedInAt: result.logged_in_at
    })

    toast.add({
      title: 'Berhasil Masuk',
      icon: 'i-lucide-check-circle',
      description: `Selamat datang, ${result.name}! (${result.role})`,
      color: 'success'
    })

    router.push(`/${result.role}`)
  } catch (err: any) {
    toast.add({
      title: 'Login Gagal',
      description: err.message || 'Email atau kata sandi salah.',
      color: 'error'
    })
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <UPageCard class="max-w-md mx-auto mt-48">
    <UAuthForm
      ref="authFormRef"
      title="Masuk MAP"
      description="Login dengan akun Anda"
      icon="i-lucide-log-in"
      :schema="schema"
      :fields="fields"
      :loading="loading"
      :submit="{ label: 'Masuk' }"
      @submit="onSubmit"
    />

    <template #footer>
      <div class="text-xs text-muted space-y-1">
        <p class="font-medium">
          Akun terdaftar di sistem:
        </p>
        <p v-for="acc in accounts" :key="acc.id">
          {{ acc.role }}:
          <button type="button" class="underline hover:text-primary" @click="fillEmail(acc.email)">
            {{ acc.email }} || {{ acc.password }}
          </button>
        </p>
      </div>
    </template>
  </UPageCard>
</template>
