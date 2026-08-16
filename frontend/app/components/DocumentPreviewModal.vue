<script setup lang="ts">
import * as pdfjsLib from 'pdfjs-dist'

const props = defineProps<{
  open: boolean
  title?: string
  buildPdf?: () => Promise<string>
}>()

const emit = defineEmits<{
  close: []
}>()

const pdfUrl = ref<string | null>(null)
const loadingPdf = ref(false)
const pdfError = ref('')
const pages = ref<Array<{ dataUrl: string, width: number, height: number }>>([])

// Konfigurasi worker pdfjs (tanpa unduhan eksternal)
// @ts-expect-error — di Nuxt client bundle path worker tersedia di node_modules
pdfjsLib.GlobalWorkerOptions.workerSrc = new URL(
  'pdfjs-dist/build/pdf.worker.min.mjs',
  import.meta.url
).toString()

async function renderPdfToCanvas(dataUrl: string) {
  const doc = await pdfjsLib.getDocument({ data: atob(dataUrl.split(',')[1]!) }).promise
  const rendered: Array<{ dataUrl: string, width: number, height: number }> = []
  for (let i = 1; i <= doc.numPages; i++) {
    const page = await doc.getPage(i)
    const baseViewport = page.getViewport({ scale: 1 })
    const scale = Math.min(2.2, 1400 / baseViewport.width)
    const viewport = page.getViewport({ scale })
    const canvas = document.createElement('canvas')
    canvas.width = Math.floor(viewport.width)
    canvas.height = Math.floor(viewport.height)
    const ctx = canvas.getContext('2d')
    if (!ctx) continue
    await page.render({ canvasContext: ctx, viewport }).promise
    rendered.push({
      dataUrl: canvas.toDataURL('image/png'),
      width: canvas.width,
      height: canvas.height
    })
  }
  return rendered
}

async function build() {
  if (!props.buildPdf) return
  loadingPdf.value = true
  pdfError.value = ''
  pages.value = []
  try {
    const dataUrl = await props.buildPdf()
    pdfUrl.value = dataUrl
    pages.value = await renderPdfToCanvas(dataUrl)
  } catch (err) {
    pdfError.value = err instanceof Error ? err.message : 'Gagal membuat preview'
  } finally {
    loadingPdf.value = false
  }
}

watch(
  () => props.open,
  (open) => {
    if (open) {
      pdfUrl.value = null
      pages.value = []
      build()
    }
  }
)

function onClose() {
  emit('close')
}
</script>

<template>
  <UModal
    :open="open"
    :ui="{ content: 'max-w-4xl h-[85vh] flex flex-col' }"
    @update:open="(v: boolean) => { if (!v) onClose() }"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-file-text" class="size-5 text-primary" />
        <span>{{ title || 'Preview Dokumen' }}</span>
      </div>
    </template>

    <template #body>
      <div class="flex-1 min-h-0 flex flex-col">
        <div v-if="loadingPdf" class="flex flex-col items-center justify-center py-20 gap-3">
          <UIcon name="i-lucide-loader-circle" class="size-8 animate-spin text-primary" />
          <p class="text-sm text-muted">
            Menyiapkan preview dokumen...
          </p>
        </div>

        <div v-else-if="pdfError" class="flex flex-col items-center justify-center py-20 gap-3">
          <UIcon name="i-lucide-alert-triangle" class="size-8 text-error" />
          <p class="text-sm text-error">
            {{ pdfError }}
          </p>
          <UButton
            size="sm"
            color="neutral"
            variant="soft"
            @click="build"
          >
            Coba Lagi
          </UButton>
        </div>

        <!-- Preview hanya visual (tanpa toolbar print/download) -->
        <div
          v-else-if="pages.length"
          class="flex-1 min-h-0 overflow-auto rounded-lg border border-default bg-neutral-100 dark:bg-neutral-900 p-4"
        >
          <div class="flex flex-col items-center gap-4">
            <div
              v-for="(page, index) in pages"
              :key="index"
              class="shadow-lg rounded-md bg-white overflow-hidden"
            >
              <img
                :src="page.dataUrl"
                :style="{
                  width: '100%',
                  maxWidth: '720px',
                  display: 'block',
                  height: 'auto'
                }"
                :alt="`Halaman ${index + 1}`"
              >
            </div>
          </div>
        </div>

        <div v-else class="flex flex-col items-center justify-center py-20 gap-3">
          <UIcon name="i-lucide-file-question" class="size-8 text-muted" />
          <p class="text-sm text-muted">
            Tidak ada dokumen untuk dipreview.
          </p>
        </div>
      </div>
    </template>

    <template #footer>
      <div class="flex justify-end gap-2">
        <UButton
          icon="i-lucide-refresh-cw"
          color="neutral"
          variant="soft"
          :loading="loadingPdf"
          @click="build"
        >
          Muat Ulang
        </UButton>
        <UButton color="neutral" variant="ghost" @click="onClose">
          Tutup
        </UButton>
      </div>
    </template>
  </UModal>
</template>
