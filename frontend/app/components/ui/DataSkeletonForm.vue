<script setup lang="ts">
withDefaults(
  defineProps<{ rows?: number }>(),
  { rows: 3 }
)
</script>

<template>
  <div class="space-y-4">
    <div v-for="i in rows" :key="i" class="space-y-2">
      <USkeleton class="h-4 w-24 rounded" />
      <USkeleton class="h-10 w-full rounded-lg" />
    </div>
    <USkeleton class="h-10 w-32 rounded-lg" />
  </div>
</template>
