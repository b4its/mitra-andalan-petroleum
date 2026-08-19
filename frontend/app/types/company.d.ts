export interface Company {
  id: string
  name: string
  abbreviation: string
  company_image: string | null
}

export const CompanySchema = z.object({
  id: z.string().uuid(),
  name: z.string().min(1),
  abbreviation: z.string().min(1).max(20),
  company_image: z.string().nullable()
})

export type CompanyData = z.infer<typeof CompanySchema>
