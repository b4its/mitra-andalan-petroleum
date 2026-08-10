import { describe, it, expect } from 'vitest'
import {
  formatCurrency,
  formatDate,
  formatDateDoc,
  formatPercent,
  formatNumber
} from '~/utils/index'

describe('formatCurrency', () => {
  it('formats IDR currency', () => {
    const result = formatCurrency(50000000)
    expect(result).toContain('50')
    expect(result).toContain('000')
  })

  it('handles zero', () => {
    expect(formatCurrency(0)).toContain('0')
  })

  it('handles decimals', () => {
    const result = formatCurrency(1500.5)
    expect(result).toContain('1.501')
  })
})

describe('formatDate', () => {
  it('formats ISO date string', () => {
    const result = formatDate('2025-06-01')
    expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
  })

  it('formats Date object', () => {
    const result = formatDate(new Date(2025, 5, 1))
    expect(result).toMatch(/\d{1,2}\/\d{1,2}\/\d{4}/)
  })
})

describe('formatDateDoc', () => {
  it('formats with long month name', () => {
    const result = formatDateDoc('2025-06-01')
    expect(result).toContain('Juni')
    expect(result).toContain('2025')
  })
})

describe('formatPercent', () => {
  it('formats decimal as percentage', () => {
    const result = formatPercent(0.125)
    expect(result).toContain('13')
  })

  it('handles zero', () => {
    expect(formatPercent(0)).toContain('0')
  })
})

describe('formatNumber', () => {
  it('formats number with ID locale', () => {
    const result = formatNumber(1000000)
    expect(result).toContain('1')
    expect(result).toContain('000')
  })
})
