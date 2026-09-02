<script setup lang="ts">
import { format, parseISO } from "date-fns";
import {
  VisXYContainer,
  VisLine,
  VisAxis,
  VisArea,
  VisCrosshair,
  VisTooltip,
} from "@unovis/vue";
import type { Period, RangeDate } from "~/types";

const cardRef = useTemplateRef<HTMLElement | null>("cardRef");

const props = defineProps<{
  period: Period;
  range: RangeDate;
}>();

type DataRecord = {
  date: Date;
  amount: number;
};

interface RevenuePoint {
  date: string;
  label: string;
  amount: number;
}

const { width } = useElementSize(cardRef);
const { get } = useApi();

const data = ref<DataRecord[]>([]);

async function loadRevenue() {
  const params = new URLSearchParams({
    period: props.period,
    date_from: props.range.start.toISOString(),
    date_to: props.range.end.toISOString(),
  });
  try {
    const res = await get<{ points: RevenuePoint[] }>(
      `/stats/revenue?${params.toString()}`,
    );
    data.value = (res?.points ?? []).map((p) => ({
      date: parseISO(p.date),
      amount: p.amount,
    }));
  } catch {
    data.value = [];
  }
}

watch([() => props.period, () => props.range], loadRevenue, {
  immediate: true,
});

const x = (_: DataRecord, i: number) => i;
const y = (d: DataRecord) => d.amount;

const total = computed(() =>
  data.value.reduce((acc: number, { amount }) => acc + amount, 0),
);

const formatNumber = (value: number) => formatCurrency(value);

const formatDate = (date: Date): string => {
  return {
    daily: format(date, "d MMM"),
    weekly: format(date, "d MMM"),
    monthly: format(date, "MMM yyy"),
  }[props.period];
};

const xTicks = (i: number) => {
  if (i === 0 || i === data.value.length - 1 || !data.value[i]) {
    return "";
  }

  return formatDate(data.value[i].date);
};

const template = (d: DataRecord) =>
  `${formatDate(d.date)}: ${formatNumber(d.amount)}`;
</script>

<template>
  <UCard
    ref="cardRef"
    :ui="{ root: 'overflow-visible', body: 'px-0! pt-0! pb-3!' }"
  >
    <template #header>
      <div>
        <p class="text-xs text-muted uppercase mb-1.5">Revenue</p>
        <p class="text-3xl text-highlighted font-semibold">
          {{ formatNumber(total) }}
        </p>
      </div>
    </template>

    <VisXYContainer
      :data="data"
      :padding="{ top: 40 }"
      class="h-96"
      :width="width"
    >
      <VisLine :x="x" :y="y" color="var(--ui-primary)" />
      <VisArea :x="x" :y="y" color="var(--ui-primary)" :opacity="0.1" />

      <VisAxis type="x" :x="x" :tick-format="xTicks" />

      <VisCrosshair color="var(--ui-primary)" :template="template" />

      <VisTooltip />
    </VisXYContainer>
  </UCard>
</template>

<style scoped>
.unovis-xy-container {
  --vis-crosshair-line-stroke-color: var(--ui-primary);
  --vis-crosshair-circle-stroke-color: var(--ui-bg);

  --vis-axis-grid-color: var(--ui-border);
  --vis-axis-tick-color: var(--ui-border);
  --vis-axis-tick-label-color: var(--ui-text-dimmed);

  --vis-tooltip-background-color: var(--ui-bg);
  --vis-tooltip-border-color: var(--ui-border);
  --vis-tooltip-text-color: var(--ui-text-highlighted);
}
</style>
