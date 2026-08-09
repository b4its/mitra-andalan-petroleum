<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import { operationsDOSchema, type OperationsDOState } from '~/types/schemas'

const emit = defineEmits<{
  submit: []
}>()

const state = defineModel<OperationsDOState>({ required: true })
const { get } = useApi()

const { data: deliveryOrderList, pending } = await useAsyncData(
  'operations-returned-delivery-orders',
  async () => {
    const res = await get<{ items: any[] }>('/delivery-orders', {
      page: 1,
      page_size: 100
    })
    return res.items || []
  },
  { default: () => [], server: false }
)

const deliveryOrders = computed(() =>
  deliveryOrderList.value.map((deliveryOrder: any) => ({
    label: deliveryOrder.customer_name || deliveryOrder.do_number,
    value: deliveryOrder.id,
    doNumber: deliveryOrder.do_number,
  }))
)

function onSubmit(_event: FormSubmitEvent<OperationsDOState>) {
  emit('submit')
}

</script>

<template>
  <UForm
    id="po-customer"
    :schema="operationsDOSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-2xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <div v-if="pending" class="space-y-4 py-2">
        <div class="space-y-2">
          <USkeleton class="h-4 w-40 rounded" />
          <USkeleton class="h-10 w-full rounded-lg" />
        </div>
        <div class="space-y-2">
          <USkeleton class="h-4 w-40 rounded" />
          <USkeleton class="h-10 w-full rounded-lg" />
        </div>
      </div>
      <template v-else>
        <UFormField name="deliveryOrder" label="Nomor Delivery Order" required>
        <USelect
          v-model="state.deliveryOrderNumber"
          :items="deliveryOrders"
          placeholder="Pilih "
          value-key="value"
          :ui="{ content: 'min-w-fit' }"
          class="w-full"
        >
          <template #item-label="{ item }">
            {{ item.label }}

            <span class="text-muted text-xs"> ({{ item.doNumber }}) </span>
          </template>
        </USelect>
      </UFormField>

      <UFormField
        name="doFile"
        label="File Delivery Order Yang Dikembalikan"
        required
      >
        <UFileUpload
          v-model="state.doDocument"
          label="Upload File Delivery Order"
          description="Format file .pdf dengan max 50MB"
        />
      </UFormField>

      <div class="flex justify-end pt-4">
        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Upload DO
        </UButton>
      </div>
      </template>
    </UPageCard>
  </UForm>
</template>
