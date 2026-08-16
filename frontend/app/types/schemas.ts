import * as z from "zod";

export const addCustomerSchema = z.object({
  name: z.string().min(2, "Too short"),
  email: z.email("Invalid email"),
});

export type AddCustomerState = z.infer<typeof addCustomerSchema>;

export const profileSchema = z.object({
  name: z.string().min(2, "Too short"),
  email: z.email("Invalid email"),
  username: z.string().min(2, "Too short"),
  avatar: z.string().optional(),
  bio: z.string().optional(),
});

export type ProfileState = z.infer<typeof profileSchema>;

export const passwordSchema = z.object({
  current: z.string().min(8, "Must be at least 8 characters"),
  new: z.string().min(8, "Must be at least 8 characters"),
});

export type PasswordState = z.infer<typeof passwordSchema>;

export const marketingPOCustomerSchema = z.object({
  selectedOfferingLetter: z.object(),
  poDocument: z.file().optional(),
  purchaseOrderNumber: z.string().min(1),
  total: z.number().min(1),
  poReceivedDate: z.string(),
});

export type MarketingPOCustomerState = z.infer<
  typeof marketingPOCustomerSchema
>;

export const operationsDOSchema = z.object({
  deliveryOrderNumber: z.string(),
  doDocument: z.file().optional(),
});

export type OperationsDOState = z.infer<typeof operationsDOSchema>;

export const marketingOLHeaderSchema = z.object({
  location: z.string().min(2).or(z.literal("")),
  date: z.iso.date(),
  offeringLetterNumber: z.string(),
  regarding: z.string(),
  receiver: z.string(),
});

export type MarketingOLHeaderState = z.infer<typeof marketingOLHeaderSchema>;

export const marketingOLDetailsSchema = z.object({
  supplyPoint: z.string(),
  qualityAssurance: z.string(),
  custodyTransfer: z.string(),
  unloadingProcedure: z.string(),
  volumeUnit: z.string(),
  volumeTolerance: z.number().min(0),
  paymentMethod: z.enum(["cash", "kredit"]),
  cashMethod: z
    .enum(["cash_before_delivery", "cash_after_delivery"])
    .optional(),
  paymentTerm: z.string().min(1, "Wajib diisi"),
  latePenalty: z.number().min(0.01),
  servicePattern: z.string(),
  personInCharge: z.object({
    name: z.string(),
    phoneNumber: z.string().min(1, "Nomor telepon wajib diisi"),
  }),
  paymentAddress: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  fuelPrices: z.object({
    logisticInformation: z.string(),
    productName: z.string(),
    hppPrice: z.number(),
    basePrice: z.number(),
    totalPrice: z.number(),
    sellingPrice: z.object({
      ppkb: z.number(),
      oat: z.number().nullable(),
      ppn: z.number(),
      pph: z.number().nullable().optional(),
    }),
    percentageNum: z.object({
      ppkb: z.number(),
      oat: z.number(),
      ppn: z.number(),
      pph: z.number().optional(),
    }),
  }),
  informasiTambahan: z.array(z.string()).optional(),
});

export type MarketingOLDetailsState = z.infer<typeof marketingOLDetailsSchema>;

export const marketingOLFooterSchema = z.object({
  purchaseOrderDeadline: z.string().min(1, "Wajib diisi"),
  offeror: z.object({
    name: z.string(),
    signature: z.file().optional(),
  }),
  companyInformation: z.object({
    address: z.string(),
    phoneNumber: z.string(),
    email: z.email(),
  }),
});

export type MarketingOLFooterState = z.infer<typeof marketingOLFooterSchema>;

export const marketingPOCompanySchema = z.object({
  companyInformation: z.object({
    name: z.string(),
    address: z.string(),
    npwp: z.string(),
    contactPerson: z.string(),
    email: z.email(),
  }),
});

export type MarketingPOCompanyState = z.infer<typeof marketingPOCompanySchema>;

export const marketingPOAssociateSchema = z.object({
  receiver: z.object({
    id: z.string(),
    name: z.string(),
    address: z.string().optional(),
    npwp: z.string().optional(),
    contactPerson: z.string().optional(),
    email: z.email().optional(),
  }),
});

export type MarketingPOAssociateState = z.infer<
  typeof marketingPOAssociateSchema
>;

export const marketingPODetailsSchema = z.object({
  po: z.object({
    date: z.iso.date(),
    number: z.string().min(1, "Wajib diisi"),
  }),
  vat: z.number(),
  paymentAddress: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  selectedOfferingLetter: z.object(),
  products: z
    .array(
      z.object({
        name: z.string().min(1, "Wajib diisi"),
        qty: z.number().min(1, "Min 1"),
        unit: z.string().min(1, "Wajib diisi"),
        price: z.number().min(0, "Min 0"),
        totalPrice: z.number(),
        ppkb: z.number().optional(),
        pph: z.number().optional(),
        ppn: z.number().optional(),
      }),
    )
    .min(1, "Tambahkan minimal 1 produk"),
  totalProductsPrice: z.number(),
});

export type MarketingPODetailsState = z.infer<typeof marketingPODetailsSchema>;

export const marketingPOAdditionalSchema = z.object({
  termAndCondition: z.string(),
  delivery: z.object({
    loadingTerminal: z.string().optional(),
    loadingDate: z.iso.date().optional(),
    picOperationMap: z.string().optional(),
    distance: z.number(),
  }),
  details: z.string().optional(),
  forwarder: z.object({
    trucking: z.string(),
  }),
  signed: z.object({
    createdBy: z.string(),
    approvedBy: z.string(),
  }),
});

export type MarketingPOAdditionalState = z.infer<
  typeof marketingPOAdditionalSchema
>;

// Operations Delivery Order
export const operationsDOHeaderSchema = z.object({
  companyInformation: z.object({
    name: z.string(),
    nameSub: z.string().optional(),
    address: z.string(),
    phoneNumber: z.string(),
  }),
  doInformation: z.object({
    doNumber: z.string(),
    doDateCreated: z.iso.date(),
    poCustomerNumber: z.object(),
    soNumber: z.string().optional(),
  }),
});
export const operationsDOReceiverSchema = z.object({
  customerName: z.string(),
  customerId: z.string(),
  customerAddress: z.string(),
  receiverInformation: z.object({
    name: z.string().optional(),
    phoneNumber: z.string().optional(),
  }),
  receiverDateReceived: z.iso.date(),
});
export const operationsDOTransportSchema = z.object({
  transportName: z.string(),
  transportId: z.string().optional(),
  transportAddress: z.string(),
  driverInformation: z.object({
    name: z.string().optional(),
    phoneNumber: z.string().optional(),
  }),
  helperName: z.string().optional(),
  transportDateReceived: z.iso.date(),
});
export const operationsDODetailsTransportSchema = z.object({
  dueDate: z.iso.date().optional(),
  productInformation: z.object({
    name: z.string().optional(),
    qty: z.coerce.number().optional(),
    temperature: z.coerce.number().optional(),
    topSeal: z.string().optional(),
    bottomSeal: z.string().optional(),
  }),
  transportInformation: z.object({
    transportType: z.string().optional(),
    transportNumber: z.string().optional(),
    startKm: z.coerce.number().optional(),
    endKm: z.coerce.number().optional(),
    sgMeter: z.coerce.number().optional(),
    // isWaterFree: z.boolean().optional(), // need to discuss
    timeInformation: z.object({
      departureTime: z.string().optional(),
      arrivalTime: z.string().optional(),
      unloadingTime: z.string().optional(),
      depotArrivalTime: z.string().optional(),
    }),
  }),
  total: z.coerce.number(),
});
export const operationsDOAdditionalSchema = z.object({
  notes: z.array(
    z.object({
      note: z.string().optional(),
    }),
  ),
  t2Depot: z.coerce.number().optional(),
  t2Unloading: z.coerce.number().optional(),
  indexSensitivity: z.coerce.number().optional(),
  fuelReceived: z.coerce.number().optional(),
});
export const operationsDOFooterSchema = z.object({
  companyCoordinator: z.string(),
  distributionAdmin: z.string(),
  receiver: z.string().optional(),
  driver: z.string().optional(),
});

export type OperationsDOHeaderState = z.infer<typeof operationsDOHeaderSchema>;
export type OperationsDOReceiverState = z.infer<
  typeof operationsDOReceiverSchema
>;
export type OperationsDOTransportState = z.infer<
  typeof operationsDOTransportSchema
>;
export type OperationsDODetailsTransportState = z.infer<
  typeof operationsDODetailsTransportSchema
>;
export type OperationsDOAdditionalState = z.infer<
  typeof operationsDOAdditionalSchema
>;
export type OperationsDOFooterState = z.infer<typeof operationsDOFooterSchema>;

// Finance Invoice
export const financeInvoiceHeaderSchema = z.object({
  companyInformation: z.object({
    name: z.string(),
    nameSub: z.string().optional(),
    address: z.string(),
    phoneNumber: z.string(),
    email: z.email(),
  }),
  billToInformation: z.string(),
  deliveryPointInformation: z.string(),
});

export const financeInvoiceDetailsSchema = z.object({
  invoiceInformation: z.object({
    invoiceNumber: z.string(),
    invoiceDate: z.iso.date(),
    terms: z.number(),
    invoiceDueDate: z.iso.date(),
  }),
  customerPurchaseInformation: z.object({
    deliveryOrderNumberData: z.array(z.string()),
    customerPurchaseOrderNumber: z.object(),
    taxInvoiceNumber: z.string(),
  }),
});
export const financeInvoiceProductsSchema = z.object({
  products: z
    .array(
      z.object({
        qty: z.number().min(1, "Min 1"),
        unit: z.string().min(1, "Wajib diisi"),
        name: z.string().min(1, "Wajib diisi"),
        price: z.number().min(0, "Min 0"),
        totalPrice: z.number(),
      }),
    )
    .min(1, "Tambahkan minimal 1 produk"),
  priceSummary: z.object({
    subTotal: z.number(),
    prePaid: z.number().optional(),
    discount: z.number().optional(),
    ppn: z.number(),
    grandTotal: z.number(),
    spellNumber: z.string(),
  }),
});
export const financeInvoiceFooterSchema = z.object({
  termsAndCondition: z.array(
    z.object({
      term: z.string(),
    }),
  ),
  paymentInformation: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  signature: z.object({
    companyName: z.string(),
    createdBy: z.string(),
  }),
});

export type FinanceInvoiceHeaderState = z.infer<
  typeof financeInvoiceHeaderSchema
>;
export type FinanceInvoiceDetailsState = z.infer<
  typeof financeInvoiceDetailsSchema
>;
export type FinanceInvoiceProductsState = z.infer<
  typeof financeInvoiceProductsSchema
>;
export type FinanceInvoiceFooterState = z.infer<
  typeof financeInvoiceFooterSchema
>;

export const operationsPOTransportHeaderSchema = z.object({
  date: z.iso.date(),
  poTransportNumber: z.string(),
  regarding: z.string(),
  receiver: z.string(),
  picPerson: z.string(),
});
export const operationsPOTransportDetailsSchema = z.object({
  products: z
    .array(
      z.object({
        name: z.string().min(1, "Wajib diisi"),
        qty: z.number().min(1, "Min 1"),
        ratePrice: z.number().min(0, "Min 0"),
        totalPrice: z.number(),
        loadingDate: z.iso.date().optional(),
        unloadingDate: z.iso.date().optional(),
      }),
    )
    .min(1, "Tambahkan minimal 1 produk"),
  priceSummary: z.object({
    subTotal: z.number(),
    ppn: z.number(),
    grandTotal: z.number(),
  }),
  percentageNum: z.object({
    ppn: z.number(),
  }),
});
export const operationsPOTransportFooterSchema = z.object({
  loadingInformation: z.string(),
  discharge: z.string(),
  termsOfPayment: z.string(),
  shrinkageTolerance: z.string(),
  contactPerson: z.object({
    companyName: z.string(),
    customerName: z.string(),
    companyContactPerson: z
      .array(
        z.object({
          name: z.string(),
          phoneNumber: z.string(),
        }),
      )
      .optional(),
    customerContactPerson: z
      .array(
        z.object({
          name: z.string(),
          phoneNumber: z.string(),
        }),
      )
      .optional(),
  }),
  offeror: z.object({
    name: z.string(),
    signature: z.file().optional(),
  }),
});

export type OperationsPOTransportHeaderState = z.infer<
  typeof operationsPOTransportHeaderSchema
>;
export type OperationsPOTransportDetailsState = z.infer<
  typeof operationsPOTransportDetailsSchema
>;
export type OperationsPOTransportFooterState = z.infer<
  typeof operationsPOTransportFooterSchema
>;
