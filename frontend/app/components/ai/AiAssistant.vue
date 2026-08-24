<script setup lang="ts">
/**
 * AiAssistant — wrapper yang merangkum FAB + Slideover chat.
 * Cukup pasang <AiAssistant /> di layout mana pun agar AI Assistant
 * aktif di seluruh halaman yang menggunakan layout tersebut.
 */
</script>

<template>
  <ClientOnly>
    <AiAssistantFab />
    <AiAssistantSlideover />
    <template #fallback>
      <span />
    </template>
  </ClientOnly>
</template>
