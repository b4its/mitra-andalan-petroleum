<script setup lang="ts">
import type { TableColumn } from '@nuxt/ui'

const props = defineProps<{ open: boolean }>()
const emit = defineEmits<{ 'update:open': [value: boolean] }>()

const page = ref(1)
const pageSize = 15
const { get, put } = useApi()

const { data, pending, error, refresh } = await useAsyncData(
  () => `admin-notifications-${page.value}`,
  () => get<any[]>('/notifications', { page: page.value, page_size: pageSize }),
  { watch: [page], default: () => [] }
)

const notifications = computed<any[]>(() => Array.isArray(data.value) ? data.value : [])
const total = computed(() => notifications.value.length)

watch(() => props.open, (isOpen) => {
  if (isOpen) {
    page.value = 1
    refresh()
  }
})

async function markAsRead(id: string) {
  try {
    await put(`/notifications/${id}`, { is_read: true })
    refresh()
  } catch {
    // silently ignore
  }
}

const typeColor: Record<string, string> = {
  info: 'info',
  success: 'success',
  warning: 'warning',
  error: 'error'
}

const columns: TableColumn<any>[] = [

  { accessorKey: 'title', header: 'Judul' },
  { accessorKey: 'message', header: 'Pesan' },
  {
    accessorKey: 'is_read',
    header: 'Status',
    cell: ({ row }) => {
      const read = row.getValue('is_read') as boolean
      return h(resolveComponent('UBadge'), {
        variant: 'subtle',
        color: read ? 'success' : 'warning'
      }, () => read ? 'Dibaca' : 'Belum')
    }
  },
{
  accessorKey: 'created_at',
  header: 'Waktu',
  cell: ({ row }) => {
    const rawDate = row.getValue('created_at');
    if (!rawDate) return '-';

    const date = new Date(rawDate);
    
    // Ambil YYYY-MM-DD
    const yyyy = date.getFullYear();
    const mm = String(date.getMonth() + 1).padStart(2, '0');
    const dd = String(date.getDate()).padStart(2, '0');
    
    // Ambil Jam dan Menit
    const hours = String(date.getHours()).padStart(2, '0');
    const minutes = String(date.getMinutes()).padStart(2, '0');

    // Gabungkan sesuai format yang diinginkan
    return `${dd}-${mm}-${yyyy}, ${hours}:${minutes}`;
  }
},
  {
    id: 'action',
    header: '',
    cell: ({ row }) => {
      if (row.original.is_read) return null
      return h(resolveComponent('UButton'), {
        size: 'xs',
        variant: 'soft',
        color: 'primary',
        label: 'Tandai dibaca',
        onClick: () => markAsRead(row.original.id)
      })
    }
  }
]
</script>

<template>
  <UModal
    :open="open"
    title="Notifikasi Sistem"
    :ui="{ content: 'max-w-4xl' }"
    @update:open="emit('update:open', $event)"
  >
    <template #body>
      <UAlert
        v-if="error"
        color="error"
        title="Gagal memuat notifikasi"
        :description="error.message"
      />
      <div v-else-if="pending" class="space-y-3">
        <USkeleton v-for="i in 5" :key="i" class="h-12 w-full" />
      </div>
      <template v-else>
        <div class="flex items-center justify-between mb-3">
          <p class="text-sm text-muted">
            Total {{ total }} notifikasi
          </p>
          <UButton
            size="xs"
            variant="soft"
            icon="i-lucide-refresh-cw"
            @click="() => refresh()"
          />
        </div>
        <UTable :data="notifications" :columns="columns" />
        <UEmpty
          v-if="!notifications.length"
          icon="i-lucide-bell-off"
          title="Tidak ada notifikasi"
          description="Belum ada notifikasi pada sistem."
        />
        <div v-if="total > pageSize" class="flex justify-end mt-4">
          <UPagination v-model:page="page" :total="total" :items-per-page="pageSize" />
        </div>
      </template>
    </template>
  </UModal>
</template>
