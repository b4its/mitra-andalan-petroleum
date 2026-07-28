<script setup lang="ts">
import { h } from "vue"
import type { TableColumn } from "@nuxt/ui"

definePageMeta({ layout: "admin" })

const UBadge = resolveComponent("UBadge")

const { data, pending } = useAsyncData("admin-marketing", async () => {
  const { get } = useApi()
  const [stats, olList] = await Promise.all([
    get<any>("/stats/admin"),
    get<{ items: any[] }>("/offering-letters", { page: 1, page_size: 10 }),
  ])
  return { stats, olList: olList.items || [] }
}, { default: () => ({ stats: null, olList: [] }), lazy: true })

const olStats = computed(() => {
  if (!data.value?.stats?.stats) return []
  const all = data.value.stats.stats
  return all.filter((s: any) =>
    ["Surat Penawaran", "Purchase Order"].includes(s.title)
  )
})

const olTrendMonths = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.month.split(" ")[0]) || []
)

const olTrendData = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.offering_letters) || []
)

const poTrendData = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.purchase_orders) || []
)

const olDistLabels = computed(() =>
  data.value?.stats?.ol_status_distribution?.map((d: any) => d.label) || []
)

const olDistValues = computed(() =>
  data.value?.stats?.ol_status_distribution?.map((d: any) => d.value) || []
)

const columns: TableColumn<any>[] = [
  { accessorKey: "offering_letter_number", header: "Nomor" },
  { accessorKey: "receiver", header: "Penerima" },
  {
    accessorKey: "fuel_total_price",
    header: "Total",
    cell: ({ row }: any) =>
      new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(row.getValue("fuel_total_price")),
  },
  {
    accessorKey: "status",
    header: "Status",
    cell: ({ row }: any) => {
      const color: Record<string, string> = { created: "warning", under_revision: "info", po_received: "success" }
      return h(UBadge, { class: "capitalize", variant: "subtle", color: color[row.getValue("status") as string] || "neutral" }, () => row.getValue("status"))
    },
  },
]
</script>

<template>
  <div class="space-y-6 p-6">
    <h1 class="text-3xl font-bold">Marketing — Rekap</h1>

    <div v-if="pending" class="flex items-center justify-center py-20">
      <UIcon name="i-lucide-loader" class="size-8 animate-spin text-muted" />
    </div>

    <template v-else>
      <div v-if="olStats.length" class="grid grid-cols-2 gap-4 sm:grid-cols-4">
        <UCard v-for="s in olStats" :key="s.title" variant="subtle">
          <template #title><p class="truncate text-xs text-muted">{{ s.title }}</p></template>
          <span class="text-2xl font-semibold">{{ s.value }}</span>
        </UCard>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <UCard>
          <template #header><p class="text-sm font-medium">Tren Surat Penawaran</p></template>
          <AdminBarChart
            v-if="olTrendMonths.length"
            :labels="olTrendMonths"
            :datasets="[
              { label: 'Surat Penawaran', data: olTrendData, backgroundColor: 'rgba(59,130,246,0.7)' },
              { label: 'Purchase Order', data: poTrendData, backgroundColor: 'rgba(16,185,129,0.7)' },
            ]"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">Belum ada data</div>
        </UCard>

        <UCard>
          <template #header><p class="text-sm font-medium">Status Surat Penawaran</p></template>
          <AdminPieChart
            v-if="olDistLabels.length"
            :labels="olDistLabels"
            :data="olDistValues"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">Belum ada data</div>
        </UCard>
      </div>

      <UCard>
        <template #header><p class="text-sm font-medium">Surat Penawaran Terbaru</p></template>
        <UTable :data="olList" :columns="columns" class="shrink-0" />
      </UCard>
    </template>
  </div>
</template>
