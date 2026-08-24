<script setup lang="ts">
import { sub } from "date-fns";
import type { Period, RangeDate, Stat } from "~/types";

const range = shallowRef<RangeDate>({
  start: sub(new Date(), { days: 14 }),
  end: new Date(),
});
const period = ref<Period>("daily");

definePageMeta({ layout: "operations" });

// ── AI Assistant: konteks analisa halaman ──────────────────────
const { get } = useApi();
const { data: aiStats } = await useAsyncData<Stat[]>(
  "operations-ai-stats",
  async () => {
    const res = await get<{ stats: Stat[] }>("/stats/operations");
    return res.stats || [];
  },
  { watch: [() => period.value, () => range.value], default: () => [] }
);

const { setContext: setAiContext, clearContext: clearAiContext, open: openAi } =
  useAiAssistant();

const aiContext = computed(() => {
  const stats = (aiStats.value || []).map((s) => ({
    judul: s.title,
    nilai: s.value,
    perubahan: s.variation,
  }));
  return JSON.stringify(
    {
      halaman: "Dashboard Operations",
      rentang: {
        dari: range.value.start.toISOString().split("T")[0],
        sampai: range.value.end.toISOString().split("T")[0],
        periode: period.value,
      },
      ringkasanStatistik: stats,
    },
    null,
    2
  );
});

watch(aiContext, (val) => setAiContext(val, "Dashboard Operations"), {
  immediate: true,
});
onBeforeUnmount(() => clearAiContext());

function openAiAssistant() {
  openAi();
}
</script>

<template>
  <UDashboardPanel id="home">
    <template #header>
      <UDashboardNavbar title="Beranda" :ui="{ right: 'gap-3' }">
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
        <template #right>
          <UButton
            icon="i-lucide-sparkles"
            color="primary"
            variant="soft"
            label="Analisa AI"
            @click="openAiAssistant"
          />
        </template>
      </UDashboardNavbar>
    </template>

    <template #body>
      <h1 class="text-3xl font-bold dark:text-neutral-50 text-neutral-900">
        Rekap Data Operations
      </h1>
      <OperationsStats :period="period" :range="range" />
    </template>
  </UDashboardPanel>
</template>
