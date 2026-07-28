<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const props = withDefaults(
  defineProps<{
    showToastTitle?: boolean
    toastTitle?: string
    successDescription?: string
  }>(),
  {
    showToastTitle: true,
    toastTitle: 'Success',
    successDescription: 'Data Akun Anda berhasil diupdate'
  }
)

const show = ref(false)
const auth = useAuth()
const { put } = useApi()

const profileSchema = z.object({
  name: z.string().min(2, 'Too short'),
  email: z.email('Invalid email'),
  password: z.string().optional()
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  name: '',
  email: '',
  password: ''
})

watch(
  () => auth.user.value,
  (currentUser) => {
    profile.name = currentUser?.name ?? ''
    profile.email = currentUser?.email ?? ''
    profile.password = ''
  },
  { immediate: true }
)

const toast = useToast()
const saving = ref(false)

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  if (saving.value) return
  saving.value = true

  try {
    const userId = auth.user.value?.id
    if (!userId) {
      throw new Error('User ID not found')
    }

    const body: Record<string, string> = {
      name: event.data.name,
      email: event.data.email
    }
    if (event.data.password) {
      body.password = event.data.password
    }

    const updated = await put<any, typeof body>(`/profiles/${userId}`, body)

    auth.setUser({
      id: userId,
      name: updated.name || event.data.name,
      email: updated.email || event.data.email,
      password: event.data.password || auth.user.value?.password || '',
      role: auth.user.value?.role || 'staff',
      token: auth.user.value?.token || '',
      loggedInAt: auth.user.value?.loggedInAt || ''
    })

    toast.add({
      ...(props.showToastTitle ? { title: props.toastTitle } : {}),
      description: props.successDescription,
      icon: 'i-lucide-check',
      color: 'success'
    })
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal memperbarui profil',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

function toggleShow() {
  show.value = !show.value
}
</script>

<template>
  <UDashboardPanel id="profile">
    <template #header>
      <UDashboardNavbar
        :title="`Profil User ${auth.user.value?.name ?? 'User'} | ${auth.user.value?.role ?? 'Default'}`"
        :ui="{ right: 'gap-3', title: 'capitalize' }"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <UForm
        id="profile"
        :schema="profileSchema"
        :state="profile"
        :ui="{
          base: 'lg:max-w-lg'
        }"
        @submit="onSubmit"
      >
        <UPageCard variant="subtle">
          <UFormField name="name" label="Name" required>
            <UInput v-model="profile.name" autocomplete="off" />
          </UFormField>

          <UFormField name="email" label="Email" required>
            <UInput v-model="profile.email" type="email" autocomplete="off" />
          </UFormField>

          <UFormField name="password" label="Password">
            <UInput
              v-model="profile.password"
              placeholder="Password"
              :type="show ? 'text' : 'password'"
              :ui="{ trailing: 'pe-1' }"
            >
              <template #trailing>
                <UButton
                  type="button"
                  color="neutral"
                  variant="link"
                  size="sm"
                  :icon="show ? 'i-lucide-eye-off' : 'i-lucide-eye'"
                  :aria-label="show ? 'Hide password' : 'Show password'"
                  :aria-pressed="show"
                  aria-controls="password"
                  @click="toggleShow"
                />
              </template>
            </UInput>
          </UFormField>

          <UButton
            label="Simpan Perubahan"
            color="primary"
            type="submit"
            class="w-fit mt-4"
          />
        </UPageCard>
      </UForm>
    </template>
  </UDashboardPanel>
</template>
