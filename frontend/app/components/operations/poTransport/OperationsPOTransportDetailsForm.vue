<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  operationsPOTransportDetailsSchema,
  type OperationsPOTransportDetailsState
} from '~/types/schemas'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<OperationsPOTransportDetailsState>({
  required: true
})

function emptyProduct() {
  return {
    name: '',
    qty: 1,
    ratePrice: 0,
    totalPrice: 0,
    loadingDate: new Date().toISOString().split('T')[0],
    unloadingDate: new Date().toISOString().split('T')[0]
  }
}

const products = computed(() => state.value.products)

function addItem() {
  if (!state.value.products) {
    state.value.products = []
  }
  state.value.products.push(emptyProduct())
}

function removeItem(index: number) {
  state.value.products.splice(index, 1)
}

const calculatePpnPercent = computed(() => {
  return state.value.priceSummary.subTotal * state.value.percentageNum.ppn
})

watch(
  () => state.value.products,
  (products) => {
    products?.forEach((p) => {
      p.totalPrice = (p.qty || 0) * (p.ratePrice || 0)
    })
    state.value.priceSummary.subTotal = (products || []).reduce(
      (sum, p) => sum + (p.totalPrice || 0),
      0
    )
  },
  { deep: true, immediate: true }
)

watch(
  calculatePpnPercent,
  (ppn) => {
    state.value.priceSummary.ppn = ppn
  },
  { immediate: true }
)

watch(
  () => [state.value.priceSummary.subTotal, state.value.priceSummary.ppn],
  ([subTotal, ppn]) => {
    const grandTotal = (subTotal || 0) + (ppn || 0)

    state.value.priceSummary.ppn = ppn || 0
    state.value.priceSummary.grandTotal = grandTotal
  },
  { immediate: true }
)

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<OperationsPOTransportDetailsState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="po-transport-details"
    :schema="operationsPOTransportDetailsSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-5xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Informasi PO Transportir</p>

      <div class="space-y-3">
        <p class="font-medium">
          Daftar Produk
        </p>

        <div
          v-for="(product, index) in products"
          :key="`product-${index}`"
          class="flex items-end gap-2"
        >
          <UFormField
            :name="`products.${index}.name`"
            label="Produk"
            class="w-full"
            required
          >
            <UInput v-model="product.name" placeholder="Nama produk" />
          </UFormField>

          <UFormField name="loadingDate" label="Tanggal Loading" required>
            <UInput
              v-model="product.loadingDate"
              type="date"
              autocomplete="off"
            />
          </UFormField>

          <UFormField name="unloadingDate" label="Tanggal Bongkar" required>
            <UInput
              v-model="product.unloadingDate"
              type="date"
              autocomplete="off"
            />
          </UFormField>

          <UFormField
            :name="`products.${index}.qty`"
            label="Volume (Liter)"
            class="w-full"
            required
          >
            <UInputNumber v-model="product.qty" :min="1" />
          </UFormField>

          <UFormField
            :name="`products.${index}.ratePrice`"
            label="Rate/Liter (RP.)"
            class="w-full"
            required
          >
            <UInputNumber
              v-model="product.ratePrice"
              locale="id-ID"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol'
              }"
              :step="1"
              :min="0"
              :increment="false"
              :decrement="false"
            />
          </UFormField>

          <UFormField
            :name="`products.${index}.totalPrice`"
            label="Total"
            class="w-full"
            required
          >
            <UInputNumber
              v-model="product.totalPrice"
              locale="id-ID"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol'
              }"
              :decrement="false"
              :increment="false"
              disabled
            />
          </UFormField>

          <UButton
            icon="i-lucide-trash-2"
            color="error"
            variant="ghost"
            :disabled="state.products.length === 1"
            @click="removeItem(index)"
          />
        </div>

        <UButton
          icon="i-lucide-plus"
          color="neutral"
          variant="subtle"
          size="sm"
          label="Tambah produk"
          @click="addItem"
        />

        <div class="flex justify-end pt-2 font-semibold">
          SubTotal: {{ formatCurrency(state.priceSummary.subTotal) }}
        </div>
      </div>

      <div class="flex gap-2">
        <UFormField name="percentagePpn" label="Persentase PPN" required>
          <UInputNumber
            v-model="state.percentageNum.ppn"
            :ui="{
              root: 'w-full'
            }"
            orientation="vertical"
            :step="0.001"
            :format-options="{
              style: 'percent',
              minimumFractionDigits: 1
            }"
          />
        </UFormField>
        <UFormField
          name="pricePpn"
          label="PPn"
          class="w-full"
          required
        >
          <UInputNumber
            v-model="state.priceSummary.ppn"
            class="w-full"
            locale="id-ID"
            :format-options="{
              style: 'currency',
              currency: 'IDR',
              currencyDisplay: 'narrowSymbol'
            }"
            :decrement="false"
            :increment="false"
            disabled
          />
        </UFormField>

        <UFormField
          name="priceGrandTotal"
          label="Grand Total"
          class="w-full"
          required
        >
          <UInputNumber
            v-model="state.priceSummary.grandTotal"
            class="w-full"
            locale="id-ID"
            :format-options="{
              style: 'currency',
              currency: 'IDR',
              currencyDisplay: 'narrowSymbol'
            }"
            :decrement="false"
            :increment="false"
            disabled
          />
        </UFormField>
      </div>

      <USeparator />

      <div class="flex justify-between pt-4">
        <UButton
          variant="ghost"
          color="neutral"
          leading-icon="i-lucide-arrow-left"
          :disabled="!hasPrevious"
          @click="previous"
        >
          Sebelumnya
        </UButton>

        <UButton type="submit" trailing-icon="i-lucide-arrow-right">
          Selanjutnya
        </UButton>
      </div>
    </UPageCard>
  </UForm>
</template>
