<script setup lang="ts">
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

async function build() {
  if (!props.buildPdf) return
  loadingPdf.value = true
  pdfError.value = ''
  try {
    pdfUrl.value = await props.buildPdf()
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

        <iframe
          v-else-if="pdfUrl"
          :src="pdfUrl"
          class="w-full h-full min-h-[60vh] rounded-lg border border-default"
          title="Preview Dokumen"
        />

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
