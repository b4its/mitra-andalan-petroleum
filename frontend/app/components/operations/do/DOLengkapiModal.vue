<script setup lang="ts">
import * as z from 'zod'
import type { FormSubmitEvent } from '@nuxt/ui'

const props = defineProps<{
  open: boolean
  doId: string | null
  doNumber?: string
  customerName?: string
  poNumber?: string
  companyInformation?: {
    name: string
    nameSub?: string
    address: string
    phoneNumber: string
  }
}>()

const emit = defineEmits<{ 'update:open': [boolean], 'updated': [] }>()

const toast = useToast()
const { put } = useApi()
const saving = ref(false)
const { user } = useAuth()

const schema = z.object({
  do_number: z.string().min(1, 'Wajib diisi'),
  transport_name: z.string().min(1, 'Wajib diisi'),
  product_name: z.string().min(1, 'Wajib diisi'),
  fuel_qty: z.number().min(1, 'Wajib diisi'),
  do_date: z.string().min(1, 'Wajib diisi'),
  transport_number: z.string().optional(),
  driver_name: z.string().optional(),
  company_coordinator: z.string().optional(),
  distribution_admin: z.string().optional()
})

type Schema = z.output<typeof schema>

const form = reactive<Partial<Schema>>({
  do_number: '005/DO/MAP/VIII/26',
  transport_name: 'PT. Trans Borneo',
  product_name: 'Bio Solar',
  fuel_qty: 10000,
  do_date: new Date().toISOString().split('T')[0],
  transport_number: 'KT 1234 AB',
  driver_name: 'Jaya',
  company_coordinator: 'Andi Wijaya',
  distribution_admin: user.value?.name || 'Rina Kartika'
})

// Isi default dari props saat modal dibuka
watch(
  () => props.open,
  (open) => {
    if (open) {
      form.do_number = props.doNumber || ''
      form.distribution_admin = user.value?.name || ''
    }
  }
)

async function onSubmit(event: FormSubmitEvent<Schema>) {
  if (saving.value || !props.doId) return
  saving.value = true
  try {
    const details = {
      companyInformation: {
        name: props.companyInformation?.name || '',
        nameSub: props.companyInformation?.nameSub || '',
        address: props.companyInformation?.address || '',
        phoneNumber: props.companyInformation?.phoneNumber || ''
      },
      doInformation: {
        doNumber: event.data.do_number,
        doDateCreated: event.data.do_date,
        poCustomerNumber: { purchaseOrderNumber: props.poNumber || '' },
        soNumber: ''
      },
      customerName: props.customerName || '',
      customerId: '',
      customerAddress: '',
      receiverInformation: { name: '', phoneNumber: '' },
      receiverDateReceived: event.data.do_date,
      transportName: event.data.transport_name,
      transportId: '',
      transportAddress: '',
      driverInformation: {
        name: event.data.driver_name || '',
        phoneNumber: ''
      },
      transportDateReceived: event.data.do_date,
      helperName: '',
      dueDate: event.data.do_date,
      total: event.data.fuel_qty,
      productInformation: {
        name: event.data.product_name,
        qty: event.data.fuel_qty,
        topSeal: '',
        bottomSeal: '',
        temperature: 0
      },
      transportInformation: {
        startKm: '',
        endKm: '',
        sgMeter: '',
        timeInformation: {
          departureTime: '',
          arrivalTime: '',
          depotArrivalTime: '',
          unloadingTime: ''
        },
        transportNumber: event.data.transport_number || '',
        transportType: ''
      },
      notes: [
        {
          note: 'Sebelum BBM diserahterimakan, mohon periksa terlebih dahulu surat tera, jarum tera, segel, kualitas, SGMeter, kuantitas, kadar air, flow meter yang digunakan'
        },
        {
          note: 'Setelah pembongkaran, BBM industri yang sudah diterima dengan baik dan ditanda tangani kedua belah pihak, tidak dapat dikembalikan dan BBM tersebut sudah tidak menjadi tanggung jawab kami'
        },
        { note: 'Lainnya :' }
      ],
      fuelReceived: event.data.fuel_qty,
      companyCoordinator: event.data.company_coordinator || '',
      distributionAdmin: event.data.distribution_admin || '',
      receiver: '',
      driver: event.data.driver_name || ''
    }

    await put(`/delivery-orders/${props.doId}`, {
      do_number: event.data.do_number,
      transport_name: event.data.transport_name,
      fuel_total: event.data.fuel_qty,
      details
    })

    toast.add({
      title: 'Berhasil',
      description: 'Data DO berhasil dilengkapi. Surat siap dirender.',
      color: 'success'
    })
    emit('update:open', false)
    emit('updated')
  } catch (err: any) {
    toast.add({
      title: 'Error',
      description: err.message || 'Gagal menyimpan data.',
      color: 'error'
    })
  } finally {
    saving.value = false
  }
}
</script>

<template>
  <UModal
    :open="open"
    :ui="{ content: 'max-w-xl' }"
    @update:open="emit('update:open', $event)"
  >
    <template #title>
      <div class="flex items-center gap-2">
        <UIcon name="i-lucide-clipboard-pen" class="size-4 text-primary" />
        Lengkapi Data Delivery Order
      </div>
    </template>

    <template #body>
      <div
        class="mb-4 rounded-lg bg-warning/10 border border-warning/30 px-4 py-3 text-sm text-warning"
      >
        <p class="font-medium">
          Data DO belum lengkap untuk dicetak.
        </p>
        <p class="text-xs mt-1 text-muted">
          Isi data berikut agar surat DO dapat dirender.
        </p>
      </div>

      <UForm
        :schema="schema"
        :state="form"
        class="space-y-4"
        @submit="onSubmit"
      >
        <div class="grid grid-cols-2 gap-4">
          <UFormField name="do_number" label="Nomor DO" required>
            <UInput
              v-model="form.do_number"
              placeholder="0000/DO/MAP/I/0000"
              class="w-full"
            />
          </UFormField>
          <UFormField name="do_date" label="Tanggal DO" required>
            <UInput v-model="form.do_date" type="date" class="w-full" />
          </UFormField>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <UFormField name="transport_name" label="Nama Transportir" required>
            <UInput
              v-model="form.transport_name"
              placeholder="PT. Transport Logistik"
              class="w-full"
            />
          </UFormField>
          <UFormField name="transport_number" label="Nomor Kendaraan">
            <UInput
              v-model="form.transport_number"
              placeholder="KT 1234 AB"
              class="w-full"
            />
          </UFormField>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <UFormField name="product_name" label="Nama Produk" required>
            <UInput
              v-model="form.product_name"
              placeholder="Nama Produk"
              class="w-full"
            />
          </UFormField>
          <UFormField name="fuel_qty" label="Volume (Liter)" required>
            <UInput
              v-model.number="form.fuel_qty"
              type="number"
              placeholder="5000"
              class="w-full"
            />
          </UFormField>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <UFormField name="driver_name" label="Nama Driver">
            <UInput
              v-model="form.driver_name"
              placeholder="Nama driver"
              class="w-full"
            />
          </UFormField>
          <UFormField name="distribution_admin" label="Admin Distribusi">
            <UInput v-model="form.distribution_admin" class="w-full" />
          </UFormField>
        </div>

        <UFormField name="company_coordinator" label="Koordinator MAP">
          <UInput v-model="form.company_coordinator" class="w-full" />
        </UFormField>

        <div class="flex justify-end gap-2 pt-2">
          <UButton
            type="submit"
            color="primary"
            :loading="saving"
            icon="i-lucide-save"
          >
            Simpan & Aktifkan Surat
          </UButton>

          <UButton
            color="neutral"
            variant="ghost"
            @click="emit('update:open', false)"
          >
            Batal
          </UButton>
        </div>
      </UForm>
    </template>
  </UModal>
</template>
