import { describe, it, expect } from 'vitest'
import { dummyAccounts } from '~/utils/dummyAccounts'

describe('dummyAccounts', () => {
  it('has 5 accounts', () => {
    expect(dummyAccounts).toHaveLength(5)
  })

  it('each account has required fields', () => {
    for (const acc of dummyAccounts) {
      expect(acc).toHaveProperty('email')
      expect(acc).toHaveProperty('password')
      expect(acc).toHaveProperty('role')
      expect(acc).toHaveProperty('name')
    }
  })

  it('has all required roles', () => {
    const roles = dummyAccounts.map(a => a.role)
    expect(roles).toContain('admin')
    expect(roles).toContain('operations')
    expect(roles).toContain('marketing')
    expect(roles).toContain('finance')
    expect(roles).toContain('accounting')
  })

  it('has all required emails', () => {
    const emails = dummyAccounts.map(a => a.email)
    expect(emails).toContain('admin@email.com')
    expect(emails).toContain('ops@email.com')
    expect(emails).toContain('marketing@email.com')
    expect(emails).toContain('finance@email.com')
    expect(emails).toContain('accounting@email.com')
  })

  it('passwords are non-empty', () => {
    for (const acc of dummyAccounts) {
      expect(acc.password.length).toBeGreaterThan(0)
    }
  })

  it('names are non-empty', () => {
    for (const acc of dummyAccounts) {
      expect(acc.name.length).toBeGreaterThan(0)
    }
  })
})
