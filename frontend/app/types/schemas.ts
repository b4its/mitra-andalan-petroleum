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
  offeringLetterNumber: z.string(),
});

export type MarketingPOCustomerState = z.infer<
  typeof marketingPOCustomerSchema
>;

export const marketingOLHeaderSchema = z.object({
  location: z.string().min(2),
  date: z.string(),
  offeringLetterNumber: z.string(),
  regarding: z.string(),
  receiver: z.string().min(2),
});

export type MarketingOLHeaderState = z.infer<typeof marketingOLHeaderSchema>;

export const marketingOLDetailsSchema = z.object({
  supplyPoint: z.string(),
  qualityAssurance: z.string(),
  custodyTransfer: z.string(),
  unloadingProcedure: z.string(),
  volumeUnit: z.string(),
  volumeTolerance: z.number().min(0),
  paymentTerm: z.number().min(1),
  latePenalty: z.number().min(0.01),
  servicePattern: z.string(),
  personInCharge: z.object({
    name: z.string(),
    phoneNumber: z.string().length(11, "Phone Number"),
  }),
  paymentAddress: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  fuelPrices: z.object({
    logisticInformation: z.string(),
    productName: z.string(),
    sellingPrice: z.object({
      ppkb: z.number(),
      oat: z.number().nullable(),
    }),
    ppn: z.number(),
  }),
});

export type MarketingOLDetailsState = z.infer<typeof marketingOLDetailsSchema>;

export const marketingOLFooterSchema = z.object({
  purchaseOrderDeadline: z.number(),
  offeror: z.object({
    name: z.string(),
    signature: z.string(),
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
  associateInformation: z.object({
    name: z.string(),
    address: z.string(),
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
    date: z.string().min(1, "Wajib diisi"),
    number: z.string().min(1, "Wajib diisi"),
  }),
  vat: z.number(),
  paymentAddress: z.object({
    bankName: z.string(),
    accountNumber: z.string(),
    accountName: z.string(),
  }),
  products: z
    .array(
      z.object({
        name: z.string().min(1, "Wajib diisi"),
        qty: z.number().min(1, "Min 1"),
        unit: z.string().min(1, "Wajib diisi"),
        price: z.number().min(0, "Min 0"),
        totalPrice: z.number(),
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
    loadingDate: z.string().optional(),
    picOperationMap: z.string().optional(),
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
