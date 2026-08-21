<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'
import type { Role } from '~/types'

const props = withDefaults(
  defineProps<{
    showToastTitle?: boolean
    toastTitle?: string
    successDescription?: string
  }>(),
  {
    showToastTitle: true,
    toastTitle: 'Berhasil',
    successDescription: 'Data Akun Anda berhasil diupdate'
  }
)

const show = ref(false)
const auth = useAuth()
const { get, put, postFile } = useApi()

const profileSchema = z.object({
  name: z.string().min(2, 'Too short'),
  email: z.email('Email tidak valid'),
  password: z.string().optional(),
  signature: z.instanceof(File).optional(),
  signature_caption: z.string().optional()
})

type ProfileSchema = z.output<typeof profileSchema>

const profile = reactive<Partial<ProfileSchema>>({
  name: '',
  email: '',
  password: '',
  signature: undefined,
  signature_caption: ''
})

const { data: userSignature, refresh: refreshSignatureData } = await useAsyncData(
  `profile-signature-${auth.user.value?.id ?? 'anon'}`,
  async () => {
    if (!auth.user.value?.id) return ''
    const res = await get<{ url: string }[]>(
      `/uploads?document_type=profile&document_id=${auth.user.value.id}`
    )
    return res[0]?.url || ''
  },
  { default: () => '', server: false }
)

// Preview foto baru (file yang baru dipilih) — pakai object URL
const newSignaturePreview = ref<string>('')
const signatureImageError = ref(false)

watch(
  () => profile.signature,
  (file) => {
    if (newSignaturePreview.value) {
      URL.revokeObjectURL(newSignaturePreview.value)
    }
    if (file instanceof File) {
      newSignaturePreview.value = URL.createObjectURL(file)
    } else {
      newSignaturePreview.value = ''
    }
    signatureImageError.value = false
  }
)

// Caption tanda tangan user saat ini (penanda siapa yang menandatangani)
const { data: userProfile } = await useAsyncData(
  `profile-detail-${auth.user.value?.id ?? 'anon'}`,
  async () => {
    if (!auth.user.value?.id) return null
    return get<{ signature_caption?: string | null }>(
      `/profiles/${auth.user.value.id}`
    )
  },
  { default: () => null, server: false }
)

watch(
  () => auth.user.value,
  (currentUser) => {
    profile.name = currentUser?.name ?? ''
    profile.email = currentUser?.email ?? ''
    profile.password = ''
    profile.signature = undefined
    profile.signature_caption = userProfile.value?.signature_caption ?? ''
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

    // Upload tanda tangan user (otomatis menjadi barcode di dokumen marketing)
    if (event.data.signature) {
      const resUpload = await postFile<{ url: string }[]>('/upload', {
        files: [event.data.signature],
        folder: 'profiles',
        document_type: 'profile',
        document_id: userId
      })
      if (resUpload[0]?.url) {
        body.signature = resUpload[0].url
      }
    }
    if (event.data.signature_caption) {
      body.signature_caption = event.data.signature_caption
    }

    const updated = await put<Record<string, string>, typeof body>(`/profiles/${userId}`, body)

    auth.setUser({
      id: userId,
      name: updated.name || event.data.name,
      email: updated.email || event.data.email,
      password: event.data.password || auth.user.value?.password || '',
      role: (auth.user.value?.role || 'admin') as Role,
      token: auth.user.value?.token || '',
      loggedInAt: auth.user.value?.loggedInAt || ''
    })

    // Setelah simpan: preview baru menjadi "terpasang", muat ulang dari server
    if (event.data.signature) {
      await refreshSignatureData()
    }

    toast.add({
      ...(props.showToastTitle ? { title: props.toastTitle } : {}),
      description: props.successDescription,
      icon: 'i-lucide-check',
      color: 'success'
    })
  } catch (err: unknown) {
    toast.add({
      title: 'Gagal',
      description: (err as Error).message || 'Gagal memperbarui profil',
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
        :title="`Profil Pengguna ${auth.user.value?.name ?? 'Pengguna'} | ${auth.user.value?.role ?? 'Bawaan'}`"
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
          <UFormField name="name" label="Nama" required>
            <UInput v-model="profile.name" autocomplete="off" />
          </UFormField>

          <UFormField name="email" label="Email" required>
            <UInput v-model="profile.email" type="email" autocomplete="off" />
          </UFormField>

          <UFormField name="password" label="Kata Sandi">
            <UInput
              v-model="profile.password"
              placeholder="Kata Sandi"
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
                  :aria-label="show ? 'Sembunyikan kata sandi' : 'Tampilkan kata sandi'"
                  :aria-pressed="show"
                  aria-controls="password"
                  @click="toggleShow"
                />
              </template>
            </UInput>
          </UFormField>

          <USeparator />

          <UFormField name="signature" label="Tanda Tangan">
            <UFileUpload
              v-model="profile.signature"
              label="Upload File Tanda Tangan"
              description="Format gambar (.png, .jpg) — otomatis dijadikan barcode di dokumen marketing"
              accept="image/png,image/jpeg,image/jpg"
            />
            <!-- Live preview: file baru yang dipilih atau tanda tangan terpasang -->
            <div
              v-if="newSignaturePreview"
              class="mt-2 flex items-center gap-2 rounded-lg bg-elevated/50 border border-dashed border-primary/40 p-2"
            >
              <img
                :src="newSignaturePreview"
                alt="Tanda tangan baru"
                class="h-10 w-auto max-w-40 object-contain"
              >
              <span class="text-xs text-muted">
                Tanda tangan baru (belum disimpan)
              </span>
            </div>

            <div
              v-else-if="userSignature && !signatureImageError"
              class="mt-2 flex items-center gap-2 rounded-lg bg-elevated/50 p-2"
            >
              <img
                :src="userSignature"
                alt="Tanda tangan saat ini"
                class="h-10 w-auto max-w-40 object-contain"
                @error="signatureImageError = true"
              >
              <span class="text-xs text-muted">
                Tanda tangan terpasang saat ini
              </span>
            </div>

            <div
              v-else
              class="mt-2 flex items-center gap-2 rounded-lg bg-warning/10 border border-dashed border-warning/40 p-2"
            >
              <UIcon name="i-lucide-alert-triangle" class="size-4 text-warning" />
              <span class="text-xs text-warning">
                {{
                  signatureImageError
                    ? 'Gambar tanda tangan tidak ditemukan'
                    : 'Belum ada tanda tangan'
                }}
              </span>
            </div>
          </UFormField>

          <UFormField
            name="signature_caption"
            label="Caption Tanda Tangan"
            description="Penanda siapa yang ada di tanda tangan ini (contoh: Nico - Marketing)"
          >
            <UInput
              v-model="profile.signature_caption"
              placeholder="Contoh: Nico - Marketing"
              autocomplete="off"
            />
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
