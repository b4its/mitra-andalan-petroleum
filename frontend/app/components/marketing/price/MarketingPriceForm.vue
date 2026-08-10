<script setup lang="ts">
import { h } from 'vue'
import * as z from 'zod'
import type { TableColumn, FormSubmitEvent } from '@nuxt/ui'

definePageMeta({ layout: 'marketing' })

const props = defineProps<{
  category: 'fuel' | 'shipping'
  title: string
  description: string
  unitLabel: string
  unitPlaceholder: string
}>()

const toast = useToast()
const { get, post, put, del } = useApi()

export interface Price {
  id: string
  category: string
  name: string
  price: number
  unit: string
  notes: string | null
  effective_date: string | null
}

const {
  data: prices,
  pending,
  refresh
} = await useAsyncData<Price[]>(
  `prices-${props.category}`,
  () => get<Price[]>(`/prices?category=${props.category}`),
  { default: () => [], lazy: true }
)

const search = ref('')
const filtered = computed(() => {
  const q = search.value.trim().toLowerCase()
  const list = prices.value ?? []
  if (!q) return list
  return list.filter(p =>
    p.name.toLowerCase().includes(q)
    || (p.notes ?? '').toLowerCase().includes(q)
  )
})

const columns: TableColumn<Price>[] = [
  { accessorKey: 'name', header: 'Nama' },
  {
    accessorKey: 'price',
    header: 'Harga',
    cell: ({ row }) =>
      h('span', { class: 'font-semibold' }, `Rp ${Number(row.getValue('price')).toLocaleString('id-ID')}${row.getValue('unit') ? ` / ${row.getValue('unit')}` : ''}`)
  },
  {
    accessorKey: 'effective_date',
    header: 'Berlaku Mulai',
    cell: ({ row }) => (row.getValue('effective_date') as string) || '-'
  },
  {
    accessorKey: 'notes',
    header: 'Catatan',
    cell: ({ row }) => {
      const n = row.getValue('notes') as string
      return n ? h('span', { class: 'block max-w-xs truncate' }, n) : '-'
    }
  },
  { id: 'actions', header: 'Aksi' }
]

const schema = z.object({
  name: z.string().min(2, 'Minimal 2 karakter'),
  price: z.coerce.number().min(0, 'Harga tidak boleh negatif'),
  unit: z.string().optional(),
  effective_date: z.string().optional(),
  notes: z.string().optional()
})

type Schema = z.output<typeof schema>

const modalOpen = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const selectedPrice = ref<Price | null>(null)

const formState = reactive({
  name: 'Bio Diesel / Solar',
  price: 17950,
  unit: 'LITER',
  effective_date: '2026-08-11',
  notes: 'Harga per liter termasuk ongkos angkut'
})

const saving = ref(false)

function openAdd() {
  modalMode.value = 'add'
  selectedPrice.value = null
  formState.name = 'Bio Diesel / Solar'
  formState.price = 17950
  formState.unit = props.unitPlaceholder
  formState.effective_date = '2026-08-11'
  formState.notes = 'Harga per liter termasuk ongkos angkut'
  modalOpen.value = true
}

function openEdit(price: Price) {
  modalMode.value = 'edit'
  selectedPrice.value = price
  formState.name = price.name
  formState.price = price.price
  formState.unit = price.unit ?? ''
  formState.effective_date = price.effective_date ?? ''
  formState.notes = price.notes ?? ''
  modalOpen.value = true
}

async function onSubmit(event: FormSubmitEvent<Schema>) {
  if (saving.value) return
  saving.value = true
  try {
    const payload = {
      category: props.category,
      name: event.data.name,
      price: event.data.price,
      unit: event.data.unit || '',
      effective_date: event.data.effective_date || null,
      notes: event.data.notes || null
    }
    if (modalMode.value === 'add') {
      await post<Price, typeof payload>('/prices', payload)
      toast.add({ title: 'Berhasil', description: 'Harga baru berhasil disimpan.', color: 'success' })
    } else if (selectedPrice.value) {
      await put<Price, typeof payload>(`/prices/${selectedPrice.value.id}`, payload)
      toast.add({ title: 'Berhasil', description: 'Harga berhasil diperbarui.', color: 'success' })
    }
    modalOpen.value = false
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal menyimpan harga.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}

async function onDelete(price: Price) {
  try {
    await del(`/prices/${price.id}`)
    toast.add({ title: 'Berhasil', description: 'Harga berhasil dihapus.', color: 'success' })
    refresh()
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal menghapus harga.',
      color: 'error'
    })
  }
}
</script>

<template>
  <UPageCard
    :title="title"
    :description="description"
    variant="naked"
    class="mb-4"
  >
    <div class="flex flex-wrap items-center justify-between gap-3">
      <UInput
        v-model="search"
        placeholder="Cari harga..."
        class="w-full sm:w-64"
      >
        <template #leading>
          <UIcon name="i-lucide-search" class="size-4 shrink-0 text-muted" />
        </template>
      </UInput>
      <UButton
        label="Tambah Harga"
        icon="i-lucide-plus"
        color="primary"
        @click="openAdd"
      />
    </div>
  </UPageCard>

  <UPageCard variant="subtle">
    <UTable
      :columns="columns"
      :data="filtered"
      :loading="pending"
      :empty-state="{
        icon: 'i-lucide-circle-off',
        label: 'Belum ada data harga',
        description: `Belum ada harga ${props.category === 'fuel' ? 'solar' : 'pengiriman'} yang tersimpan.`
      }"
    >
      <template #actions-header>
        <span class="text-right">Aksi</span>
      </template>

      <template #actions-cell="{ row }">
        <div class="flex justify-end gap-1">
          <UTooltip text="Ubah">
            <UButton
              icon="i-lucide-pencil"
              size="sm"
              color="neutral"
              variant="outline"
              @click="openEdit(row.original)"
            />
          </UTooltip>
          <UTooltip text="Hapus">
            <UButton
              icon="i-lucide-trash"
              size="sm"
              color="error"
              variant="outline"
              @click="onDelete(row.original)"
            />
          </UTooltip>
        </div>
      </template>
    </UTable>
  </UPageCard>

  <UModal v-model:open="modalOpen">
    <UCard :title="modalMode === 'add' ? 'Tambah Harga' : 'Ubah Harga'">
      <UForm
        id="price-form"
        :schema="schema"
        :state="formState"
        class="space-y-4"
        @submit="onSubmit"
      >
        <UFormField name="name" label="Nama" required>
          <UInput
            v-model="formState.name"
            :placeholder="props.category === 'fuel' ? 'Bio Diesel / Solar' : 'Ongkir per km'"
          />
        </UFormField>
        <UFormField name="price" label="Harga" required>
          <UInput
            v-model="formState.price"
            type="number"
            min="0"
            step="any"
            :placeholder="props.category === 'fuel' ? '17950' : '1500'"
          />
        </UFormField>
        <UFormField name="unit" :label="unitLabel">
          <UInput v-model="formState.unit" :placeholder="unitPlaceholder" />
        </UFormField>
        <UFormField name="effective_date" label="Berlaku Mulai">
          <UInput v-model="formState.effective_date" type="date" />
        </UFormField>
        <UFormField name="notes" label="Catatan">
          <UTextarea v-model="formState.notes" :rows="3" />
        </UFormField>
      </UForm>

      <template #footer>
        <div class="flex justify-end gap-2">
          <UButton
            label="Batal"
            color="neutral"
            variant="outline"
            @click="modalOpen = false"
          />
          <UButton
            form="price-form"
            type="submit"
            label="Simpan"
            color="primary"
            :loading="saving"
          />
        </div>
      </template>
    </UCard>
  </UModal>
</template>
