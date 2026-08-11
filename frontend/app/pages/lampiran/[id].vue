<script setup lang="ts">
import type { ResUploads } from '~/types'

const route = useRoute()
const router = useRouter()
const { get } = useApi()

const id = route.params.id

const { data: upload, pending, error } = await useAsyncData(
  `lampiran-${id}`,
  () => get<ResUploads>(`/uploads/${id}`)
)

function fileIcon(mimeType: string): string {
  if (mimeType.startsWith('image/')) return 'i-lucide-image'
  if (mimeType === 'application/pdf') return 'i-lucide-file-text'
  if (mimeType.includes('spreadsheet') || mimeType.includes('excel'))
    return 'i-lucide-table'
  if (mimeType.includes('word')) return 'i-lucide-file-type'
  return 'i-lucide-paperclip'
}

function fmtSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

function fileUrl(url: string): string {
  if (url.startsWith('http')) return url
  return url
}

async function downloadFile() {
  if (!upload.value) return
  const a = document.createElement('a')
  a.href = fileUrl(upload.value.url)
  a.download = upload.value.original_filename
  a.target = '_blank'
  a.rel = 'noopener noreferrer'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
}
</script>

<template>
  <div class="min-h-dvh bg-default">
    <header
      class="sticky top-0 z-10 border-b border-default bg-elevated/80 backdrop-blur"
    >
      <div
        class="mx-auto flex w-full max-w-5xl items-center gap-3 px-4 py-3"
      >
        <UButton
          icon="i-lucide-arrow-left"
          color="neutral"
          variant="ghost"
          aria-label="Kembali"
          @click="router.back()"
        />
        <div class="flex min-w-0 flex-1 items-center gap-2.5">
          <UIcon
            :name="fileIcon(upload?.mime_type || '')"
            class="size-5 shrink-0 text-primary"
          />
          <div class="min-w-0">
            <p class="truncate text-sm font-semibold">
              {{ upload?.original_filename || 'Lampiran' }}
            </p>
            <p v-if="upload" class="text-xs text-muted">
              {{ fmtSize(upload.size) }} · {{ upload.mime_type }}
            </p>
          </div>
        </div>
        <UButton
          icon="i-lucide-download"
          color="primary"
          variant="soft"
          :disabled="!upload"
          @click="downloadFile"
        >
          Download
        </UButton>
      </div>
    </header>

    <main class="mx-auto w-full max-w-5xl px-4 py-6">
      <!-- Loading -->
      <div v-if="pending" class="space-y-3">
        <USkeleton v-for="i in 3" :key="i" class="h-64 rounded-lg" />
      </div>

      <!-- Guard: file tidak ditemukan -->
      <UEmpty
        v-else-if="error"
        icon="i-lucide-file-x"
        title="File tidak dapat ditemukan"
        description="Lampiran yang Anda cari tidak tersedia, mungkin telah dihapus atau tidak terdaftar di sistem."
      />

      <template v-else-if="upload">
        <!-- Preview gambar -->
        <img
          v-if="upload.mime_type.startsWith('image/')"
          :src="fileUrl(upload.url)"
          :alt="upload.original_filename"
          class="mx-auto max-h-[75dvh] rounded-lg border border-default bg-elevated object-contain"
        >

        <!-- Preview PDF -->
        <iframe
          v-else-if="upload.mime_type === 'application/pdf'"
          :src="fileUrl(upload.url)"
          class="h-[75dvh] w-full rounded-lg border border-default bg-elevated"
        />

        <!-- Tipe tidak bisa di-preview -->
        <UEmpty
          v-else
          icon="i-lucide-eye-off"
          title="Preview tidak tersedia"
          description="Tipe file ini tidak dapat ditampilkan di browser. Gunakan tombol Download untuk mengunduhnya."
        />
      </template>
    </main>
  </div>
</template>
