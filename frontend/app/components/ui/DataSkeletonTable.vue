<script setup lang="ts">
withDefaults(
  defineProps<{ rows?: number }>(),
  { rows: 5 }
)
</script>

<template>
  <UCard>
    <div class="space-y-3">
      <USkeleton
        v-for="i in rows"
        :key="i"
        class="h-12 rounded-lg"
        :class="i % 2 === 0 && 'w-4/5'"
      />
    </div>
  </UCard>
</template>
