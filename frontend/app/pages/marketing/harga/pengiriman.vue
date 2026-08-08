<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import { profileSchema, type ProfileState } from '~/types/schemas'

const fileRef = ref<HTMLInputElement>()
const selectedFile = ref<File>()
const { postFile } = useApi()

const profile = reactive<ProfileState>({
  name: 'Benjamin Canac',
  email: 'ben@nuxtlabs.com',
  username: 'benjamincanac'
})
const toast = useToast()
async function onSubmit(event: FormSubmitEvent<ProfileState>) {
  try {
    if (selectedFile.value) {
      await postFile<ResUploads[]>('/upload', {
        files: [selectedFile.value],
        folder: 'marketing-harga'
      })
    }
    toast.add({
      title: 'Sukses',
      description: 'Data harga pengiriman berhasil disimpan.',
      icon: 'i-lucide-check',
      color: 'success'
    })
  } catch (error: any) {
    toast.add({ title: 'Error', description: error.message || 'Gagal menyimpan file.', color: 'error' })
  }
}

function onFileChange(e: Event) {
  const input = e.target as HTMLInputElement

  if (!input.files?.length) {
    return
  }

  selectedFile.value = input.files[0]!
  profile.avatar = URL.createObjectURL(selectedFile.value)
}

function onFileClick() {
  fileRef.value?.click()
}

definePageMeta({ layout: 'marketing' })
</script>

<template>
  <UForm
    id="settings"
    :schema="profileSchema"
    :state="profile"
    @submit="onSubmit"
  >
    <UPageCard
      title="Form Harga Pengiriman"
      description="Form input untuk harga pengiriman solar"
      variant="naked"
      orientation="horizontal"
      class="mb-4"
    >
      <UButton
        form="settings"
        label="Save changes"
        color="neutral"
        type="submit"
        class="w-fit lg:ms-auto"
      />
    </UPageCard>

    <UPageCard variant="subtle">
      <UFormField
        name="name"
        label="Name"
        description="Will appear on receipts, invoices, and other communication."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput v-model="profile.name" autocomplete="off" />
      </UFormField>
      <USeparator />
      <UFormField
        name="email"
        label="Email"
        description="Used to sign in, for email receipts and product updates."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput v-model="profile.email" type="email" autocomplete="off" />
      </UFormField>
      <USeparator />
      <UFormField
        name="username"
        label="Username"
        description="Your unique username for logging in and your profile URL."
        required
        class="flex max-sm:flex-col justify-between items-start gap-4"
      >
        <UInput v-model="profile.username" type="username" autocomplete="off" />
      </UFormField>
      <USeparator />
      <UFormField
        name="avatar"
        label="Avatar"
        description="JPG, GIF or PNG. 1MB Max."
        class="flex max-sm:flex-col justify-between sm:items-center gap-4"
      >
        <div class="flex flex-wrap items-center gap-3">
          <UAvatar :src="profile.avatar" :alt="profile.name" size="lg" />
          <UButton label="Choose" color="neutral" @click="onFileClick" />
          <input
            ref="fileRef"
            type="file"
            class="hidden"
            accept=".jpg, .jpeg, .png, .gif"
            @change="onFileChange"
          >
        </div>
      </UFormField>
      <USeparator />
      <UFormField
        name="bio"
        label="Bio"
        description="Brief description for your profile. URLs are hyperlinked."
        class="flex max-sm:flex-col justify-between items-start gap-4"
        :ui="{ container: 'w-full' }"
      >
        <UTextarea
          v-model="profile.bio"
          :rows="5"
          autoresize
          class="w-full"
        />
      </UFormField>
    </UPageCard>
  </UForm>
</template>
