<script setup lang="ts">
withDefaults(
  defineProps<{ height?: string }>(),
  { height: 'h-72 rounded-xl' }
)
</script>

<template>
  <div class="grid gap-6">
    <USkeleton class="w-full" :class="height" />
    <USkeleton class="w-full" :class="height" />
  </div>
</template>
