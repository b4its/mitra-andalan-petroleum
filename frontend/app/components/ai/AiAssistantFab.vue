<script setup lang="ts">
const { isOpen, toggle, messages } = useAiAssistant()

const unread = computed(() => messages.value.length)
</script>

<template>
  <UButton
    :icon="isOpen ? 'i-lucide-x' : 'i-lucide-sparkles'"
    color="primary"
    size="xl"
    rounded="full"
    class="fixed bottom-5 right-5 z-40 shadow-lg transition-transform hover:scale-105"
    :aria-label="isOpen ? 'Tutup AI Assistant' : 'Buka AI Assistant'"
    @click="toggle"
  >
    <template v-if="!isOpen && unread" #trailing>
      <span
        class="absolute -right-1 -top-1 flex size-5 items-center justify-center rounded-full bg-error text-[10px] font-bold text-white"
      >
        {{ unread > 9 ? '9+' : unread }}
      </span>
    </template>
  </UButton>
</template>
