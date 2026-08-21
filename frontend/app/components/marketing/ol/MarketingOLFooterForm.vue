<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import {
  marketingOLFooterSchema,
  type MarketingOLFooterState
} from '~/types/schemas'

const emit = defineEmits<{
  submit: []
  previous: []
  preview: []
}>()

const state = defineModel<MarketingOLFooterState>({ required: true })
const location = defineModel<string>('location', { default: '' })

const auth = useAuth()
const { get, put, postFile } = useApi()
const toast = useToast()

// ── Tanda tangan dari profil user ─────────────────────────────
interface ProfileSignature {
  signature?: string | null
  signature_caption?: string | null
}

const signatureUrl = ref('')
const signatureCaption = ref('')
const signatureLoading = ref(false)
const signatureUploading = ref(false)
const signatureFile = ref<File | null>(null)

async function loadSignature() {
  const userId = auth.user.value?.id
  if (!userId) return
  signatureLoading.value = true
  try {
    const sig = await get<ProfileSignature>(`/profiles/${userId}`)
    signatureUrl.value = sig?.signature || ''
    signatureCaption.value = sig?.signature_caption || ''
  } catch {
    // abaikan — form tetap bisa dipakai, validasi dilakukan saat submit
  } finally {
    signatureLoading.value = false
  }
}

onMounted(loadSignature)

watch(signatureFile, (file) => {
  if (file) {
    uploadSignature(file)
  }
})

async function uploadSignature(file: File) {
  const userId = auth.user.value?.id
  if (!userId) return
  signatureUploading.value = true
  try {
    const res = await postFile<ResUploads[]>('/upload', {
      files: [file],
      folder: 'profiles',
      document_type: 'profile',
      document_id: userId
    })
    const url = res[0]?.url
    if (!url) {
      throw new Error('Gambar tanda tangan gagal diunggah')
    }
    await put<unknown, { signature: string }>(`/profiles/${userId}`, {
      signature: url
    })
    signatureUrl.value = url
    signatureFile.value = null
    toast.add({
      title: 'Sukses',
      description: 'Tanda tangan profil berhasil diperbarui',
      color: 'success'
    })
  } catch (e) {
    console.error(e)
    toast.add({
      title: 'Gagal',
      description: e instanceof Error ? e.message : 'Gagal memperbarui tanda tangan',
      color: 'error'
    })
  } finally {
    signatureUploading.value = false
  }
}

function onPreview() {
  emit('preview')
}

const deadlineOptions = [
  { label: '1 - 14', value: '1 - 14' },
  { label: '15 - 28', value: '15 - 28' },
  { label: '15 - 29', value: '15 - 29' },
  { label: '15 - 30', value: '15 - 30' },
  { label: '15 - 31', value: '15 - 31' },
  { label: 'Custom...', value: '__custom__' }
]

const deadlineCustom = ref(
  state.value.purchaseOrderDeadline
  && !deadlineOptions.some(o => o.value === state.value.purchaseOrderDeadline)
    ? state.value.purchaseOrderDeadline
    : ''
)

watch(
  () => state.value.purchaseOrderDeadline,
  (value) => {
    if (value === '__custom__') {
      deadlineCustom.value = ''
      state.value.purchaseOrderDeadline = ''
    } else if (!deadlineOptions.some(o => o.value === value)) {
      deadlineCustom.value = value || ''
    }
  }
)

const regionProvince = ref('')
const regionCity = ref('')
const baseStreet = ref('')

watch(
  () => state.value.companyInformation.address,
  (value) => {
    const suffix = [regionCity.value, regionProvince.value]
      .filter(Boolean)
      .join(', ')
    if (suffix && value && value.endsWith(suffix)) {
      baseStreet.value = value
        .slice(0, value.length - suffix.length)
        .replace(/[, ]+$/, '')
    } else {
      baseStreet.value = value
    }
  }
)

watch([regionProvince, regionCity], () => {
  location.value = regionCity.value
  if (regionCity.value) {
    state.value.companyInformation.address = [
      baseStreet.value,
      regionCity.value,
      regionProvince.value
    ]
      .filter(Boolean)
      .join(', ')
  }
})

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<MarketingOLFooterState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="letter-footer"
    :schema="marketingOLFooterSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <UFormField
        name="purchaseOrderDeadline"
        label="Tenggat Purchase Order"
        description="Pilih periode atau gunakan Custom untuk range bebas"
        required
      >
        <USelect
          v-model="state.purchaseOrderDeadline"
          :items="deadlineOptions"
          value-key="value"
          placeholder="Pilih periode tenggat"
        />
      </UFormField>

      <UFormField
        v-if="state.purchaseOrderDeadline === '__custom__'"
        name="purchaseOrderDeadlineCustom"
        label="Range Custom (hari)"
        required
      >
        <UInput
          v-model="deadlineCustom"
          type="text"
          placeholder="Contoh: 5 - 20 atau 30"
          @update:model-value="(v: string) => (state.purchaseOrderDeadline = v)"
        />
      </UFormField>

      <USeparator />

      <UFormField name="offerorName" label="Hormat Kami" required>
        <UInput v-model="state.offeror.name" type="text" autocomplete="off" />
      </UFormField>

      <USeparator />

      <!-- Tanda tangan dari profil user: tampilkan preview + bisa diganti -->
      <div class="flex flex-col gap-3">
        <div>
          <p class="text-sm font-medium text-muted mb-1.5">
            Tanda Tangan (dari Profil)
          </p>
          <p class="text-xs text-muted mb-2">
            Tanda tangan diambil dari profil user. Jika belum ada, upload di
            sini agar bisa membuat surat penawaran.
          </p>

          <div
            v-if="signatureLoading"
            class="flex items-center gap-2 text-xs text-muted h-14"
          >
            <UIcon name="i-lucide-loader-circle" class="size-4 animate-spin" />
            Memeriksa tanda tangan profil...
          </div>

          <div
            v-else-if="signatureUrl"
            class="flex items-center gap-4 rounded-lg bg-elevated/50 border border-default p-3"
          >
            <img
              :src="signatureUrl"
              alt="Tanda tangan profil"
              class="h-14 w-auto object-contain"
            >
            <div class="flex flex-col gap-0.5">
              <p class="text-xs font-semibold text-success">
                Tanda tangan sudah diunggah
              </p>
              <p v-if="signatureCaption" class="text-xs text-muted">
                Caption: {{ signatureCaption }}
              </p>
            </div>
          </div>

          <div
            v-else
            class="flex items-center gap-3 rounded-lg bg-elevated/50 border border-dashed border-warning/40 p-3"
          >
            <UIcon
              name="i-lucide-alert-triangle"
              class="size-5 text-warning"
            />
            <div class="flex flex-col gap-0.5">
              <p class="text-xs font-semibold text-warning">
                Belum ada tanda tangan di profil
              </p>
              <p class="text-xs text-muted">
                Upload tanda tangan di bawah untuk dapat menyelesaikan surat
                penawaran.
              </p>
            </div>
          </div>
        </div>

        <UFormField name="offerorSignature" label="Ganti Tanda Tangan">
          <UFileUpload
            v-model="signatureFile"
            label="Upload / Ganti Foto Tanda Tangan"
            description="Format gambar (.png, .jpg) — langsung tersimpan ke profil"
            accept="image/png,image/jpeg,image/jpg"
            :multiple="false"
          />
          <p
            v-if="signatureUploading"
            class="mt-2 flex items-center gap-2 text-xs text-muted"
          >
            <UIcon name="i-lucide-loader-circle" class="size-4 animate-spin" />
            Mengunggah tanda tangan baru...
          </p>
        </UFormField>
      </div>

      <USeparator />

      <p>Informasi Perusahaan</p>

      <UFormField name="address" label="Alamat" required>
        <UTextarea
          v-model="state.companyInformation.address"
          autocomplete="off"
          :rows="3"
          class="w-full"
        />
      </UFormField>

      <div class="w-full">
        <p class="text-sm font-medium text-muted mb-1.5">
          Lokasi <span class="text-red-500">*</span>
        </p>
        <WilayahLocationPicker
          v-model:province="regionProvince"
          v-model:city="regionCity"
        />
      </div>

      <div class="flex w-full gap-4">
        <UFormField name="phoneNumber" label="Nomor Telepon" required>
          <UInput
            v-model="state.companyInformation.phoneNumber"
            v-maska="'0541-#######'"
            type="text"
            autocomplete="off"
          />
        </UFormField>

        <UFormField name="email" label="Alamat Email" required>
          <UInput
            v-model="state.companyInformation.email"
            type="email"
            autocomplete="off"
          />
        </UFormField>
      </div>

      <div class="flex justify-between pt-4">
        <UButton
          type="button"
          variant="ghost"
          color="neutral"
          leading-icon="i-lucide-arrow-left"
          @click="previous"
        >
          Sebelumnya
        </UButton>

        <div class="flex gap-2">
          <UButton
            type="button"
            color="info"
            variant="soft"
            leading-icon="i-lucide-eye"
            @click="onPreview"
          >
            Preview Dokumen
          </UButton>

          <UButton type="submit" trailing-icon="i-lucide-arrow-right">
            Selesai
          </UButton>
        </div>
      </div>
    </UPageCard>
  </UForm>
</template>
