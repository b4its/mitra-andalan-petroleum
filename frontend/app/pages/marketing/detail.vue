<script setup lang="ts">
import type { NavigationMenuItem } from "@nuxt/ui";
import type { Customer, OfferingLetterPost } from "~/types/marketing";

const route = useRoute();
const idOfferingLetter = route.params.id;
const { get } = useApi();

const { data: offeringLetterDetails, pending: pendingOL } = await useAsyncData(
  "offering-letter-detail",
  async () => {
    const res = await get<OfferingLetterPost>(
      `/offering-letters/${idOfferingLetter}`,
    );
    return res;
  },
);

const { data: customerDetail, pending: pendingCustomer } = await useAsyncData(
  "customer-detail-offering",
  async () => {
    const res = await get<Customer>(
      `/customers/${offeringLetterDetails.value?.details?.receiver}`,
    );
    return res;
  },
);

const links = [
  [
    {
      label: "Revisi Surat Penawaran Customer",
      icon: "i-lucide-file-user",
      to: `/marketing/detail/revisi-surat-penawaran-${idOfferingLetter}`,
    },
    {
      label: "Detail Surat Penawaran Customer",
      icon: "i-lucide-receipt-text",
      to: `/marketing/detail/surat-penawaran-${idOfferingLetter}`,
    },
  ],
] satisfies NavigationMenuItem[][];

definePageMeta({ layout: "marketing" });
</script>

<template>
  <UDashboardPanel id="offering-letter" :ui="{ body: 'lg:py-12' }">
    <template #header>
      <UDashboardNavbar
        :title="
          pendingOL || pendingCustomer
            ? `Surat Penawaran Customer (…)`
            : `Surat Penawaran Customer (${offeringLetterDetails?.details?.offeringLetterNumber}) ${customerDetail?.name ? `| ${customerDetail?.name}` : ''}`
        "
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
      <div
        v-if="pendingOL || pendingCustomer"
        class="flex flex-col gap-4 w-full px-4 lg:px-6"
      >
        <div class="space-y-3">
          <USkeleton v-for="i in 6" :key="i" class="h-12 rounded-lg" />
        </div>
      </div>
      <div
        v-else
        class="flex flex-col gap-4 sm:gap-6 lg:gap-12 w-full px-4 lg:px-6"
      >
        <NuxtPage />
      </div>
    </template>
  </UDashboardPanel>
</template>
