<script setup lang="ts">
import type { Price } from '~/components/marketing/price/MarketingPriceForm.vue'

const { get } = useApi()

const { data: prices, pending } = await useAsyncData<Price[]>(
  'prices-all',
  () => get<Price[]>('/prices'),
  { default: () => [] }
)

const categoryLabel: Record<string, string> = {
  fuel: 'Solar',
  shipping: 'Pengiriman'
}

const formatted = computed(() =>
  prices.value.map(p => ({
    id: p.id,
    nama: p.name,
    kategori: categoryLabel[p.category] || p.category,
    harga: formatCurrency(p.price),
    unit: p.unit,
    berlaku: p.effective_date ? formatDate(p.effective_date) : '-',
    catatan: p.notes || '-'
  }))
)
</script>

<template>
  <UDashboardPanel id="price-history">
    <template #header>
      <UDashboardNavbar title="Rekap Histori Harga" />
    </template>

    <template #body>
      <UPageCard variant="subtle">
        <UTable
          :columns="[{
            accessorKey: 'nama',
            header: 'Nama Harga'
          }, {
            accessorKey: 'kategori',
            header: 'Kategori'
          }, {
            accessorKey: 'harga',
            header: 'Harga'
          }, {
            accessorKey: 'unit',
            header: 'Satuan'
          }, {
            accessorKey: 'berlaku',
            header: 'Berlaku Mulai'
          }, {
            accessorKey: 'catatan',
            header: 'Catatan'
          }]"
          :data="formatted"
          :loading="pending"
          :empty-state="{
            icon: 'i-lucide-circle-off',
            label: 'Belum ada harga tersimpan.'
          }"
        />
      </UPageCard>
    </template>
  </UDashboardPanel>
</template>
