<script setup lang="ts">
import type { FormSubmitEvent } from '@nuxt/ui'
import {
  financeInvoiceProductsSchema,
  type FinanceInvoiceProductsState
} from '~/types/schemas'
import angkaTerbilang from '@develoka/angka-terbilang-js'
import { useChangeCase } from '@vueuse/integrations/useChangeCase'

defineProps<{
  hasPrevious: boolean | undefined
}>()

const emit = defineEmits<{
  submit: []
  previous: []
}>()

const state = defineModel<FinanceInvoiceProductsState>({ required: true })

function emptyProduct() {
  return { name: '', qty: 1, unit: '', price: 0, totalPrice: 0 }
}

const products = computed(() => state.value.products)

watch(
  () => [
    state.value.priceSummary.subTotal,
    state.value.priceSummary.discount,
    state.value.priceSummary.prePaid
  ],
  ([subTotal, discount, prePaid]) => {
    const ppn = Math.round((subTotal || 0) * 0.11)
    const grandTotal = (subTotal || 0) + ppn - (discount || 0) - (prePaid || 0)

    state.value.priceSummary.ppn = ppn
    state.value.priceSummary.grandTotal = grandTotal

    const spellNumber = angkaTerbilang(Math.max(0, Math.round(grandTotal)))

    state.value.priceSummary.spellNumber = useChangeCase(
      spellNumber,
      'capitalCase'
    ).value
  },
  { immediate: true }
)

function addItem() {
  if (!state.value.products) {
    state.value.products = []
  }
  state.value.products.push(emptyProduct())
}

function removeItem(index: number) {
  state.value.products.splice(index, 1)
}

// Keep row totalPrice, grand total, and spell number in sync
watch(
  () => state.value.products,
  (products) => {
    products?.forEach((p) => {
      p.totalPrice = (p.qty || 0) * (p.price || 0)
    })
    state.value.priceSummary.subTotal = (products || []).reduce(
      (sum, p) => sum + (p.totalPrice || 0),
      0
    )
  },
  { deep: true, immediate: true }
)

function previous() {
  emit('previous')
}

function onSubmit(_event: FormSubmitEvent<FinanceInvoiceProductsState>) {
  emit('submit')
}
</script>

<template>
  <UForm
    id="invoice-products"
    :schema="financeInvoiceProductsSchema"
    :state="state"
    :ui="{ base: 'lg:w-full lg:max-w-4xl lg:mx-auto mt-8' }"
    @submit="onSubmit"
  >
    <UPageCard variant="soft">
      <p>Daftar Produk</p>

      <div class="space-y-3">
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

          <UFormField
            :name="`products.${index}.qty`"
            label="Qty"
            class="w-full"
            required
          >
            <UInputNumber v-model="product.qty" :min="1" />
          </UFormField>

          <UFormField
            :name="`products.${index}.unit`"
            label="Unit"
            class="w-full"
            required
          >
            <UInput v-model="product.unit" placeholder="pcs" />
          </UFormField>

          <UFormField
            :name="`products.${index}.price`"
            label="Harga Unit"
            class="w-full"
            required
          >
            <UInputNumber
              v-model="product.price"
              locale="id-ID"
              :format-options="{
                style: 'currency',
                currency: 'IDR',
                currencyDisplay: 'narrowSymbol'
              }"
              :step="1000"
              :min="0"
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
      </div>

      <USeparator />

      <p>Price Summary</p>

      <div class="flex w-full gap-4">
        <UFormField
          name="priceSubtotal"
          label="Sub Total"
          class="w-full"
          required
        >
          <UInputNumber
            v-model="state.priceSummary.subTotal"
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
      </div>

      <div class="flex w-full gap-4">
        <UFormField
          name="pricePrePaid"
          label="Pre Paid"
          class="w-full"
          required
        >
          <UInputNumber
            v-model="state.priceSummary.prePaid"
            class="w-full"
            locale="id-ID"
            :format-options="{
              style: 'currency',
              currency: 'IDR',
              currencyDisplay: 'narrowSymbol'
            }"
            :decrement="false"
            :increment="false"
          />
        </UFormField>

        <UFormField
          name="priceDiscount"
          label="Discount"
          class="w-full"
          required
        >
          <UInputNumber
            v-model="state.priceSummary.discount"
            class="w-full"
            locale="id-ID"
            :format-options="{
              style: 'currency',
              currency: 'IDR',
              currencyDisplay: 'narrowSymbol'
            }"
            :decrement="false"
            :increment="false"
          />
        </UFormField>
      </div>

      <div class="flex w-full gap-4">
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

        <UFormField
          name="priceSpellNumber"
          label="Jumlah Terbilang"
          class="w-full"
          required
        >
          <UInput
            v-model="state.priceSummary.spellNumber"
            class="w-full"
            type="text"
            disabled
          />
        </UFormField>
      </div>

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
