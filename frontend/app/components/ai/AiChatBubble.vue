<script setup lang="ts">
import type { AiMessage } from '~/composables/useAiAssistant'

const props = defineProps<{
  message: AiMessage
}>()

const isUser = computed(() => props.message.role === 'user')
const isStreaming = computed(() => props.message.streaming)
const content = computed(
  () => props.message.content || (isStreaming.value ? '…' : '')
)
</script>

<template>
  <div
    class="flex w-full gap-2"
    :class="isUser ? 'justify-end' : 'justify-start'"
  >
    <div
      v-if="!isUser"
      class="mt-0.5 flex size-7 shrink-0 items-center justify-center rounded-full bg-primary/10 text-primary"
    >
      <UIcon name="i-lucide-sparkles" class="size-4" />
    </div>

    <div
      class="max-w-[80%] whitespace-pre-wrap break-words rounded-2xl px-3.5 py-2.5 text-sm leading-relaxed"
      :class="
        isUser
          ? 'rounded-br-md bg-primary text-inverted'
          : 'rounded-bl-md bg-elevated text-default'
      "
    >
      {{ content }}
      <span
        v-if="isStreaming"
        class="ml-0.5 inline-block size-1.5 animate-pulse rounded-full bg-current align-middle"
      />
    </div>
  </div>
</template>
