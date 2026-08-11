<script setup lang="ts">
import type { ResUploads } from '~/types'
import type { WorkBook } from 'xlsx'

const route = useRoute()
const router = useRouter()
const { get } = useApi()

const id = route.params.id

const { data: upload, pending, error } = await useAsyncData(
  `lampiran-${id}`,
  () => get<ResUploads>(`/uploads/${id}`)
)

watch(upload, (value) => {
  if (!import.meta.client || !value) return
  if (fileKind(value) === 'spreadsheet') loadExcel()
  else if (fileKind(value) === 'word') loadWordPdf()
})

const EXT = /\.([a-z0-9]+)$/i

function extOf(name: string): string {
  return (EXT.exec(name) || [])[1]?.toLowerCase() || ''
}

type FileKind = 'image' | 'pdf' | 'spreadsheet' | 'word' | 'other'

function fileKind(u: ResUploads): FileKind {
  const mime = u.mime_type
  const ext = extOf(u.original_filename)
  if (mime.startsWith('image/') || ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg'].includes(ext))
    return 'image'
  if (mime === 'application/pdf' || ext === 'pdf') return 'pdf'
  if (
    mime.includes('spreadsheet') || mime.includes('excel') || mime === 'text/csv'
    || ['xls', 'xlsx', 'csv'].includes(ext)
  )
    return 'spreadsheet'
  if (mime.includes('word') || ['doc', 'docx'].includes(ext)) return 'word'
  return 'other'
}

type XlsxModule = typeof import('xlsx')
const xlsxRef = shallowRef<XlsxModule | null>(null)
const workbookRef = shallowRef<WorkBook | null>(null)

const sheets = shallowRef<string[]>([])
const sheetHtml = shallowRef('')
const activeSheet = ref('')
const sheetPending = ref(false)
const sheetFailed = ref(false)

async function loadExcel() {
  if (!upload.value || fileKind(upload.value) !== 'spreadsheet') return
  sheetPending.value = true
  sheetFailed.value = false
  try {
    const buffer = await $fetch<ArrayBuffer>(upload.value.url, {
      responseType: 'arrayBuffer'
    })
    const xlsx = await import('xlsx')
    xlsxRef.value = xlsx
    const workbook = xlsx.read(buffer, { type: 'array' })
    workbookRef.value = workbook
    sheets.value = workbook.SheetNames
    activeSheet.value = workbook.SheetNames[0] || ''
    if (activeSheet.value)
      sheetHtml.value = xlsx.utils.sheet_to_html(
        workbook.Sheets[activeSheet.value],
        { header: '' }
      )
  } catch {
    sheetFailed.value = true
  } finally {
    sheetPending.value = false
  }
}

function selectSheet(name: string) {
  const xlsx = xlsxRef.value
  const workbook = workbookRef.value
  if (!xlsx || !workbook || !workbook.Sheets[name]) return
  activeSheet.value = name
  sheetHtml.value = xlsx.utils.sheet_to_html(workbook.Sheets[name], {
    header: ''
  })
}

const wordPdfUrl = ref('')
const wordPdfPending = ref(false)

async function loadWordPdf() {
  if (!upload.value || fileKind(upload.value) !== 'word') return
  wordPdfPending.value = true
  try {
    const pdfBlob = await $fetch<Blob>(`/api/v1/uploads/${upload.value.id}/pdf`, {
      responseType: 'blob'
    })
    wordPdfUrl.value = URL.createObjectURL(pdfBlob)
  } catch {
    wordPdfUrl.value = ''
  } finally {
    wordPdfPending.value = false
  }
}

function fileIcon(u: ResUploads | null | undefined): string {
  switch (fileKind(u as ResUploads)) {
    case 'image': return 'i-lucide-image'
    case 'pdf': return 'i-lucide-file-text'
    case 'spreadsheet': return 'i-lucide-table'
    case 'word': return 'i-lucide-file-type'
    default: return 'i-lucide-paperclip'
  }
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
            :name="fileIcon(upload)"
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
          v-if="fileKind(upload) === 'image'"
          :src="fileUrl(upload.url)"
          :alt="upload.original_filename"
          class="mx-auto max-h-[75dvh] rounded-lg border border-default bg-elevated object-contain"
        >

        <!-- Preview PDF -->
        <iframe
          v-else-if="fileKind(upload) === 'pdf'"
          :src="fileUrl(upload.url)"
          class="h-[75dvh] w-full rounded-lg border border-default bg-elevated"
        />

        <!-- Preview Excel / CSV -->
        <template v-else-if="fileKind(upload) === 'spreadsheet'">
          <div
            v-if="sheets.length > 1"
            class="mb-3 flex flex-wrap items-center gap-1.5"
          >
            <UButton
              v-for="name in sheets"
              :key="name"
              :label="name"
              size="xs"
              color="neutral"
              :variant="activeSheet === name ? 'solid' : 'ghost'"
              @click="selectSheet(name)"
            />
          </div>

          <div
            v-if="sheetPending"
            class="flex h-64 items-center justify-center rounded-lg border border-default bg-elevated"
          >
            <UIcon name="i-lucide-loader-circle" class="size-6 animate-spin" />
          </div>

          <UEmpty
            v-else-if="sheetFailed"
            icon="i-lucide-eye-off"
            title="Preview tidak tersedia"
            description="File Excel tidak dapat dibaca. Gunakan tombol Download untuk mengunduhnya."
          />

          <div
            v-else-if="sheetHtml"
            class="max-h-[75dvh] overflow-auto rounded-lg border border-default bg-elevated p-2"
          >
            <!-- eslint-disable vue/no-v-html -- SheetJS escapes cell content, safe -->
            <div
              class="text-xs text-muted"
              v-html="sheetHtml"
            />
            <!-- eslint-enable vue/no-v-html -->
          </div>
        </template>

        <!-- Preview Word (.docx) — dikonversi ke PDF via LibreOffice -->
        <template v-else-if="fileKind(upload) === 'word'">
          <div
            v-if="wordPdfPending"
            class="flex h-64 items-center justify-center rounded-lg border border-default bg-elevated"
          >
            <UIcon name="i-lucide-loader-circle" class="size-6 animate-spin" />
          </div>

          <iframe
            v-else-if="wordPdfUrl"
            :src="wordPdfUrl"
            class="h-[75dvh] w-full rounded-lg border border-default bg-elevated"
          />

          <UEmpty
            v-else
            icon="i-lucide-eye-off"
            title="Preview tidak tersedia"
            description="File dokumen ini tidak dapat ditampilkan di browser. Gunakan tombol Download untuk mengunduhnya."
          />
        </template>

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
