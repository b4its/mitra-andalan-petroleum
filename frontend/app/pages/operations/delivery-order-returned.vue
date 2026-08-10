<script setup lang="ts">
import type { StepperItem, NavigationMenuItem } from '@nuxt/ui'
import type { ResUploads } from '~/types'
import type { OperationsDOState } from '~/types/schemas'

const { postFile } = useApi()
const toast = useToast()
const uploading = ref(false)

const items: StepperItem[] = [
  {
    title: 'Upload Surat DO',
    slot: 'doReturned',
    icon: 'i-lucide-receipt-text'
  }
]

const doReturned = reactive<OperationsDOState>({
  deliveryOrderNumber: '',
  doDocument: undefined
})

async function onDoSubmit() {
  if (uploading.value) return
  const file = Array.isArray(doReturned.doDocument)
    ? doReturned.doDocument[0]
    : doReturned.doDocument

  if (!doReturned.deliveryOrderNumber || !file) {
    toast.add({ title: 'Validasi', description: 'Pilih nomor DO dan file yang akan diupload.', color: 'warning' })
    return
  }

  uploading.value = true
  try {
    await postFile<ResUploads[]>('/upload', {
      files: [file],
      folder: 'do',
      document_type: 'do',
      document_id: doReturned.deliveryOrderNumber
    })
    toast.add({ title: 'Sukses', description: 'File Delivery Order berhasil diupload.', color: 'success' })
    doReturned.deliveryOrderNumber = ''
    doReturned.doDocument = undefined
  } catch (error: any) {
    toast.add({ title: 'Error', description: error.message || 'Gagal upload file Delivery Order.', color: 'error' })
  } finally {
    uploading.value = false
  }
}

const links = [
  [
    {
      label: 'Buat Delivery Order',
      icon: 'i-lucide-truck',
      to: '/operations/delivery-order'
    },
    {
      label: 'Upload Delivery Order (Yang sudah dikembalikan)',
      icon: 'i-lucide-file-output',
      to: '/operations/delivery-order-returned'
    }
  ]
] satisfies NavigationMenuItem[][]

definePageMeta({ layout: 'operations' })
</script>

<template>
  <UDashboardPanel id="do" :ui="{ body: 'w-full' }">
    <template #header>
      <UDashboardNavbar
        title="Form Pembuatan Delivery Order"
        :ui="{ right: 'gap-3' }"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <template #left>
          <!-- NOTE: The `-ms-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
          <UNavigationMenu :items="links" highlight class="-mx-1 flex-1" />
        </template>
      </UDashboardToolbar>
    </template>

    <template #body>
      <UStepper ref="stepper" disabled :items>
        <template #doReturned>
          <!-- <MarketingPOCustomerForm v-model="doReturned" @submit="onDoSubmit" /> -->
          <OperationsDOReturnedForm v-model="doReturned" @submit="onDoSubmit" />
        </template>
      </UStepper>
    </template>
  </UDashboardPanel>
</template>
