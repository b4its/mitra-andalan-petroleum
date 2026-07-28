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

const emit = defineEmits<{
  submitted: [
    {
      name: string
      email: string
      password?: string
    }
  ]
}>()

const show = ref(false)
const user = useAuth()

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
  () => user.user.value,
  (currentUser) => {
    profile.name = currentUser?.name ?? ''
    profile.email = currentUser?.email ?? ''
    profile.password = currentUser?.password ?? ''
  },
  { immediate: true }
)

const toast = useToast()

async function onSubmit(event: FormSubmitEvent<ProfileSchema>) {
  toast.add({
    ...(props.showToastTitle ? { title: props.toastTitle } : {}),
    description: props.successDescription,
    icon: 'i-lucide-check',
    color: 'success'
  })

  emit('submitted', event.data)
  console.log(event.data)
}

function toggleShow() {
  show.value = !show.value
}
</script>

<template>
  <UDashboardPanel id="profile">
    <template #header>
      <UDashboardNavbar
        :title="`Profil User ${user.user.value?.name === undefined ? 'User' : user.user.value?.name} | ${user.user.value?.role === undefined ? 'Default' : user.user.value?.role}`"
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
