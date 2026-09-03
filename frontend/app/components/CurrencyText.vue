<script setup lang="ts">
import { formatCurrency } from '~/utils'

const props = withDefaults(
  defineProps<{
    value: number | string
    size?: 'sm' | 'md' | 'lg'
  }>(),
  { size: 'md' }
)

const formatted = computed(() => {
  if (typeof props.value === 'string') {
    const n = Number(props.value)
    return Number.isFinite(n) ? formatCurrency(n) : props.value
  }
  return formatCurrency(props.value)
})

const length = computed(() => formatted.value.length)

const sizes = {
  sm: { clamp: '0.7rem, 0.55vw + 0.4rem, 0.875rem', threshold: 22 },
  md: { clamp: '0.875rem, 0.9vw + 0.5rem, 1.25rem', threshold: 18 },
  lg: { clamp: '1rem, 1.4vw + 0.6rem, 1.75rem', threshold: 14 }
} as const

const fontSize = computed(() => {
  const { clamp, threshold } = sizes[props.size]
  const scale = `clamp(0.5, ${threshold} / ${Math.max(length.value, 1)}, 1)`
  return `calc(clamp(${clamp}) * ${scale})`
})
</script>

<template>
  <span
    class="inline-block max-w-full truncate align-baseline leading-tight tabular-nums"
    :style="{ fontSize, lineHeight: 1.2 }"
  >
    {{ formatted }}
  </span>
</template>
