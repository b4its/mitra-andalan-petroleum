<script setup lang="ts">
/**
 * Modal pertama — ditampilkan saat bar / segment chart diklik.
 * Menampilkan ringkasan konteks klik. Tombol "Lihat Record" menutup
 * modal ini dan membuka AdminDrilldownModal (modal kedua).
 */

export interface ChartClickPayload {
  // dari bar chart
  label?: string; // label sumbu x / periode
  datasetLabel?: string; // nama dataset (OL, PO, DO, Invoice)
  value?: number;
  // dari pie chart
  segmentLabel?: string; // label status / distribusi
  segmentValue?: number;
  // konteks: metric key yang relevan untuk drilldown
  metricKey?: string;
  chartType: "bar" | "pie";
}

const props = defineProps<{
  open: boolean;
  payload: ChartClickPayload | null;
  dateFrom: string;
  dateTo: string;
}>();

const emit = defineEmits<{
  "update:open": [value: boolean];
  viewRecords: [
    metric: {
      key: string;
      title: string;
      value: number;
      unit: string;
      description: string;
    },
  ];
}>();

// Mapping dataset label → metric key + unit
const datasetToMetric: Record<string, { key: string; unit: string }> = {
  OL: { key: "offering_letters", unit: "count" },
  PO: { key: "customer_purchase_orders", unit: "count" },
  DO: { key: "delivery_orders", unit: "count" },
  Invoice: { key: "invoice_value", unit: "currency" },
};

// Mapping status distribusi → metric key
const statusToMetric: Record<string, { key: string; unit: string }> = {
  unpaid: { key: "outstanding_value", unit: "currency" },
  paid: { key: "paid_value", unit: "currency" },
  overdue: { key: "overdue_value", unit: "currency" },
  created: { key: "offering_letters", unit: "count" },
  under_revision: { key: "offering_letters", unit: "count" },
  po_received: { key: "offering_letters", unit: "count" },
  document_returned: { key: "delivery_orders", unit: "count" },
  customer: { key: "customer_purchase_orders", unit: "count" },
  supplier: { key: "supplier_purchase_orders", unit: "count" },
};

const title = computed(() => {
  if (!props.payload) return "";
  if (props.payload.chartType === "bar") {
    return `${props.payload.datasetLabel} — Periode ${props.payload.label}`;
  }
  return `Distribusi: ${props.payload.segmentLabel}`;
});

const summary = computed(() => {
  if (!props.payload) return null;
  if (props.payload.chartType === "bar") {
    return {
      label: props.payload.label ?? "",
      dataset: props.payload.datasetLabel ?? "",
      value: props.payload.value ?? 0,
      description: `Jumlah dokumen ${props.payload.datasetLabel} pada periode ${props.payload.label}`,
    };
  }
  return {
    label: props.payload.segmentLabel ?? "",
    dataset: "Status",
    value: props.payload.segmentValue ?? 0,
    description: `Jumlah record dengan status "${props.payload.segmentLabel}"`,
  };
});

function handleViewRecords() {
  if (!props.payload) return;
  let metricInfo: { key: string; unit: string } | undefined;

  if (props.payload.chartType === "bar") {
    metricInfo = props.payload.datasetLabel
      ? datasetToMetric[props.payload.datasetLabel]
      : undefined;
  } else {
    const seg = props.payload.segmentLabel?.toLowerCase() ?? "";
    metricInfo = statusToMetric[seg];
  }

  if (!metricInfo) return;

  const value =
    props.payload.chartType === "bar"
      ? (props.payload.value ?? 0)
      : (props.payload.segmentValue ?? 0);

  emit("update:open", false);
  emit("viewRecords", {
    key: metricInfo.key,
    title: summary.value?.description ?? metricInfo.key,
    value,
    unit: metricInfo.unit,
    description: summary.value?.description ?? "",
  });
}
</script>

<template>
  <UModal
    :open="open"
    :ui="{ content: 'max-w-lg' }"
    @update:open="emit('update:open', $event)"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon
          :name="
            payload?.chartType === 'bar'
              ? 'i-lucide-chart-bar'
              : 'i-lucide-chart-pie'
          "
          class="size-4 text-primary"
        />
        {{ title }}
      </div>
    </template>

    <template #body>
      <div v-if="summary" class="space-y-4">
        <!-- Ringkasan klik -->
        <div class="rounded-lg bg-muted/50 p-4 space-y-2">
          <div class="flex items-center justify-between">
            <div>
              <p class="text-xs text-muted uppercase tracking-wide">
                {{ payload?.chartType === "bar" ? "Dataset" : "Status" }}
              </p>
              <p class="text-sm font-semibold text-highlighted">
                {{ summary.dataset }}
              </p>
            </div>
            <div class="text-right">
              <p class="text-xs text-muted uppercase tracking-wide">Jumlah</p>
              <p class="text-2xl font-bold tabular-nums text-primary">
                {{ formatNumber(summary.value) }}
              </p>
            </div>
          </div>
          <p class="text-xs text-muted border-t border-default pt-2">
            {{ summary.description }}
          </p>
          <p class="text-xs text-dimmed">
            Filter aktif: {{ formatDate(dateFrom) }} — {{ formatDate(dateTo) }}
          </p>
        </div>

        <!-- Info chart type -->
        <div
          v-if="payload?.chartType === 'bar'"
          class="rounded-lg border border-default p-3 text-sm text-muted space-y-1"
        >
          <p>
            <span class="font-medium text-highlighted">Periode:</span>
            {{ payload?.label }}
          </p>
          <p>
            <span class="font-medium text-highlighted">Dokumen:</span>
            {{ payload?.datasetLabel }}
          </p>
          <p>
            <span class="font-medium text-highlighted">Total:</span>
            {{ formatNumber(payload?.value ?? 0) }} record
          </p>
        </div>

        <div
          v-else
          class="rounded-lg border border-default p-3 text-sm text-muted space-y-1"
        >
          <p>
            <span class="font-medium text-highlighted">Status:</span>
            {{ payload?.segmentLabel }}
          </p>
          <p>
            <span class="font-medium text-highlighted">Jumlah:</span>
            {{ formatNumber(payload?.segmentValue ?? 0) }} record
          </p>
        </div>
      </div>
    </template>

    <template #footer>
      <UButton
        color="primary"
        icon="i-lucide-table-2"
        @click="handleViewRecords"
      >
        Lihat Record
      </UButton>

      <div class="flex items-center justify-end gap-2">
        <UButton
          color="neutral"
          variant="ghost"
          @click="emit('update:open', false)"
        >
          Tutup
        </UButton>
      </div>
    </template>
  </UModal>
</template>
