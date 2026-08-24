<script setup lang="ts">
const {
  isOpen,
  messages,
  streaming,
  error,
  context,
  contextTitle,
  close,
  send,
  analyze,
  clear
} = useAiAssistant()

const input = ref('')
const scrollEl = useTemplateRef<HTMLDivElement>('scrollEl')

const hasMessages = computed(() => messages.value.length > 0)

function onSubmit() {
  const text = input.value.trim()
  if (!text || streaming.value) return
  input.value = ''
  send(text)
}

function onAnalyze() {
  if (streaming.value) return
  analyze()
}

function onKeydown(e: KeyboardEvent) {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    onSubmit()
  }
}

// Auto-scroll ke bawah saat pesan/streaming berubah
watch(
  () => messages.value.map((m) => m.content).join(''),
  async () => {
    await nextTick()
    const el = scrollEl.value
    if (el) el.scrollTop = el.scrollHeight
  }
)
</script>

<template>
  <USlideover
    v-model:open="isOpen"
    title="AI Assistant"
    :ui="{ content: 'sm:max-w-lg', body: 'p-0' }"
  >
    <template #header>
      <div class="flex items-center gap-2">
        <div
          class="flex size-8 items-center justify-center rounded-lg bg-primary/10 text-primary ring ring-inset ring-primary/25"
        >
          <UIcon name="i-lucide-sparkles" class="size-5" />
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold leading-tight">AI Assistant</p>
          <p class="text-xs text-muted leading-tight">
            Analisa &amp; prediksi data
          </p>
        </div>
      </div>
    </template>

    <template #body>
      <div class="flex h-[calc(100dvh-3.5rem)] flex-col">
        <!-- Indikator konteks halaman -->
        <div
          v-if="context"
          class="flex items-center gap-2 border-b border-default bg-primary/5 px-4 py-2"
        >
          <UIcon
            name="i-lucide-file-chart-column"
            class="size-4 shrink-0 text-primary"
          />
          <p class="truncate text-xs text-muted">
            Konteks: <span class="font-medium text-highlighted">{{ contextTitle || 'halaman ini' }}</span>
          </p>
          <UButton
            size="xs"
            variant="soft"
            color="primary"
            icon="i-lucide-wand-sparkles"
            class="ml-auto shrink-0"
            :loading="streaming"
            @click="onAnalyze"
          >
            Analisa
          </UButton>
        </div>

        <!-- Toolbar -->
        <div class="flex items-center justify-between border-b border-default px-4 py-1.5">
          <p class="text-xs text-muted">Model: qd/dmodel</p>
          <div class="flex items-center gap-1">
            <UButton
              size="xs"
              variant="ghost"
              color="neutral"
              icon="i-lucide-trash-2"
              :disabled="!hasMessages || streaming"
              @click="clear"
            >
              Bersihkan
            </UButton>
            <UButton
              size="xs"
              variant="ghost"
              color="neutral"
              icon="i-lucide-x"
              @click="close"
            />
          </div>
        </div>

        <!-- Daftar pesan -->
        <div ref="scrollEl" class="flex-1 space-y-4 overflow-y-auto p-4">
          <!-- Empty state -->
          <div
            v-if="!hasMessages"
            class="flex h-full flex-col items-center justify-center gap-3 text-center"
          >
            <div
              class="flex size-14 items-center justify-center rounded-2xl bg-primary/10 text-primary ring ring-inset ring-primary/25"
            >
              <UIcon name="i-lucide-bot" class="size-7" />
            </div>
            <div class="space-y-1">
              <p class="text-sm font-medium">Halo! Saya AI Assistant</p>
              <p class="max-w-xs text-xs text-muted">
                Tanyakan apa saja seputar data, prediksi, atau analisa.
                <span v-if="context">
                  Klik <b>Analisa</b> agar saya memproses data halaman ini.
                </span>
              </p>
            </div>
            <div class="flex flex-wrap justify-center gap-2 pt-1">
              <UButton
                v-if="context"
                size="xs"
                variant="soft"
                color="primary"
                icon="i-lucide-wand-sparkles"
                @click="onAnalyze"
              >
                Analisa data halaman
              </UButton>
              <UButton
                size="xs"
                variant="outline"
                color="neutral"
                @click="send('Jelaskan singkat fungsi sistem ini')"
              >
                Apa yang bisa kamu bantu?
              </UButton>
            </div>
          </div>

          <!-- Bubble pesan -->
          <AiChatBubble
            v-for="msg in messages"
            :key="msg.id"
            :message="msg"
          />

          <!-- Error -->
          <UAlert
            v-if="error && !streaming"
            color="error"
            variant="soft"
            icon="i-lucide-alert-triangle"
            :title="error"
          />
        </div>

        <!-- Input -->
        <div class="border-t border-default p-3">
          <div class="flex items-end gap-2">
            <UTextarea
              v-model="input"
              :rows="1"
              autoresize
              :maxrows="5"
              placeholder="Tulis pesan untuk AI…"
              class="flex-1"
              :disabled="streaming"
              @keydown="onKeydown"
            />
            <UButton
              :icon="streaming ? 'i-lucide-square' : 'i-lucide-send'"
              :color="streaming ? 'error' : 'primary'"
              :loading="streaming"
              :disabled="!input.trim() && !streaming"
              @click="streaming ? undefined : onSubmit()"
            />
          </div>
          <p class="mt-1.5 text-center text-[11px] text-dimmed">
            Tekan Enter untuk kirim · Shift+Enter baris baru
          </p>
        </div>
      </div>
    </template>
  </USlideover>
</template>
