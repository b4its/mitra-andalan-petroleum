<script setup lang="ts">
import { h } from "vue"
import type { TableColumn } from "@nuxt/ui"

definePageMeta({ layout: "admin" })

const UBadge = resolveComponent("UBadge")

const { data, pending } = useAsyncData("admin-finance", async () => {
  const { get } = useApi()
  const [stats, invList] = await Promise.all([
    get<any>("/stats/admin"),
    get<{ items: any[] }>("/invoices", { page: 1, page_size: 10 }),
  ])
  return { stats, invList: invList.items || [] }
}, { default: () => ({ stats: null, invList: [] }), lazy: true })

const invStats = computed(() => {
  if (!data.value?.stats?.stats) return []
  return data.value.stats.stats.filter((s: any) =>
    ["Invoice", "Total Revenue"].includes(s.title)
  )
})

const invTrendMonths = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.month.split(" ")[0]) || []
)

const invTrendData = computed(() =>
  data.value?.stats?.monthly_trends?.map((m: any) => m.invoices) || []
)

const invDistLabels = computed(() =>
  data.value?.stats?.invoice_status_distribution?.map((d: any) => d.label) || []
)

const invDistValues = computed(() =>
  data.value?.stats?.invoice_status_distribution?.map((d: any) => d.value) || []
)

const columns: TableColumn<any>[] = [
  { accessorKey: "invoice_number", header: "Nomor Invoice" },
  {
    accessorKey: "grand_total",
    header: "Total",
    cell: ({ row }: any) =>
      new Intl.NumberFormat("id-ID", { style: "currency", currency: "IDR", maximumFractionDigits: 0 }).format(row.getValue("grand_total")),
  },
  {
    accessorKey: "invoice_status",
    header: "Status",
    cell: ({ row }: any) => {
      const color: Record<string, string> = { unpaid: "warning", paid: "success", overdue: "error" }
      return h(UBadge, { class: "capitalize", variant: "subtle", color: color[row.getValue("invoice_status") as string] || "neutral" }, () => row.getValue("invoice_status"))
    },
  },
  {
    accessorKey: "deadline_status",
    header: "Tenggat",
    cell: ({ row }: any) => {
      const color: Record<string, string> = { on_time: "success", due_soon: "warning", overdue: "error" }
      return h(UBadge, { class: "capitalize", variant: "subtle", color: color[row.getValue("deadline_status") as string] || "neutral" }, () => row.getValue("deadline_status"))
    },
  },
]
</script>

<template>
  <div class="space-y-6 p-6">
    <h1 class="text-3xl font-bold">Finance — Rekap</h1>

    <div v-if="pending" class="flex items-center justify-center py-20">
      <UIcon name="i-lucide-loader" class="size-8 animate-spin text-muted" />
    </div>

    <template v-else>
      <div v-if="invStats.length" class="grid grid-cols-2 gap-4 sm:grid-cols-3">
        <UCard v-for="s in invStats" :key="s.title" variant="subtle">
          <template #title><p class="truncate text-xs text-muted">{{ s.title }}</p></template>
          <span class="text-2xl font-semibold">{{ s.value }}</span>
        </UCard>
      </div>

      <div class="grid grid-cols-1 gap-6 lg:grid-cols-2">
        <UCard>
          <template #header><p class="text-sm font-medium">Tren Invoice</p></template>
          <AdminBarChart
            v-if="invTrendMonths.length"
            :labels="invTrendMonths"
            :datasets="[
              { label: 'Invoice', data: invTrendData, backgroundColor: 'rgba(239,68,68,0.7)' },
            ]"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">Belum ada data</div>
        </UCard>

        <UCard>
          <template #header><p class="text-sm font-medium">Status Invoice</p></template>
          <AdminPieChart
            v-if="invDistLabels.length"
            :labels="invDistLabels"
            :data="invDistValues"
          />
          <div v-else class="flex h-64 items-center justify-center text-sm text-muted">Belum ada data</div>
        </UCard>
      </div>

      <UCard>
        <template #header><p class="text-sm font-medium">Invoice Terbaru</p></template>
        <UTable :data="invList" :columns="columns" class="shrink-0" />
      </UCard>
    </template>
  </div>
</template>
