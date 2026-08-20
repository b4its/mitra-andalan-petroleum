<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import type { InvoiceDetails, InvoiceDetailsData } from "~/types/finance";

const route = useRoute();
const invoiceId = route.params.id;
const { get } = useApi();

const { data: invoiceDetails, pending } = await useAsyncData(
  "invoice-details",
  async () => {
    const res = await get<InvoiceDetails>(`/invoices/${invoiceId}`);
    return res;
  },
);
const details = computed<InvoiceDetailsData | null>(
  () => invoiceDetails.value?.details ?? null,
);

const links = [
  [
    {
      label: "Detail Invoice Customer",
      icon: "i-lucide-receipt",
      to: `/finance/detail/invoice-${invoiceId}`,
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "finance" });
</script>

<template>
  <UDashboardPanel id="detail-invoice" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar
        :title="`Invoice (${details?.invoiceInformation.invoiceNumber}) ${details?.billToInformation ? `| ${details.billToInformation}` : ''}`"
      >
        <template #leading>
          <UDashboardSidebarCollapse />
        </template>
      </UDashboardNavbar>

      <UDashboardToolbar>
        <!-- NOTE: The `-mx-1` class is used to align with the `DashboardSidebarCollapse` button here. -->
        <UNavigationMenu :items="links" highlight class="-mx-1 flex-1" />
      </UDashboardToolbar>
    </template>

    <template #body>
      <div class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full px-4 lg:px-6">
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
