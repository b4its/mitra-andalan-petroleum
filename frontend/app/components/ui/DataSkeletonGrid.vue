<script setup lang="ts">
withDefaults(
  defineProps<{
    count?: number
    rows?: number
    cols?: string
    height?: string
  }>(),
  {
    count: 4,
    rows: 5,
    cols: 'grid-cols-1 xs:grid-cols-2 lg:grid-cols-4',
    height: 'h-28 rounded-xl'
  }
)
</script>

<template>
  <div class="grid gap-4" :class="cols">
    <USkeleton
      v-for="i in count"
      :key="i"
      class="w-full"
      :class="height"
    />
  </div>
</template>
