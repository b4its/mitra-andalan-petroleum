<script setup lang="ts">
import { sub } from "date-fns";
import type { Period, Range } from "~/types";

const range = shallowRef<Range>({
  start: sub(new Date(), { days: 14 }),
  end: new Date(),
});
const period = ref<Period>("daily");

definePageMeta({ layout: "finance" });
</script>

<template>
  <FinanceInvoiceData />
</template>
