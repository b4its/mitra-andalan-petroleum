import { describe, it, expect } from "vitest";
import {
  addCustomerSchema,
  profileSchema,
  passwordSchema,
  marketingOLHeaderSchema,
} from "~/types/schemas";

describe("addCustomerSchema", () => {
  it("accepts valid data", () => {
    const result = addCustomerSchema.safeParse({
      name: "PT ABC",
      email: "abc@email.com",
    });
    expect(result.success).toBe(true);
  });

  it("rejects short name", () => {
    const result = addCustomerSchema.safeParse({
      name: "A",
      email: "a@b.com",
    });
    expect(result.success).toBe(false);
  });

  it("rejects invalid email", () => {
    const result = addCustomerSchema.safeParse({
      name: "Test",
      email: "not-an-email",
    });
    expect(result.success).toBe(false);
  });
});

describe("profileSchema", () => {
  it("accepts valid profile", () => {
    const result = profileSchema.safeParse({
      name: "John Doe",
      email: "john@email.com",
      username: "johndoe",
    });
    expect(result.success).toBe(true);
  });

  it("accepts with optional avatar and bio", () => {
    const result = profileSchema.safeParse({
      name: "John",
      email: "john@email.com",
      username: "john",
      avatar: "https://example.com/avatar.jpg",
      bio: "Hello world",
    });
    expect(result.success).toBe(true);
  });

  it("rejects missing email", () => {
    const result = profileSchema.safeParse({
      name: "John",
      username: "john",
    });
    expect(result.success).toBe(false);
  });
});

describe("passwordSchema", () => {
  it("accepts valid passwords", () => {
    const result = passwordSchema.safeParse({
      current: "12345678",
      new: "abcdefgh",
    });
    expect(result.success).toBe(true);
  });

  it("rejects short current password", () => {
    const result = passwordSchema.safeParse({
      current: "123",
      new: "abcdefgh",
    });
    expect(result.success).toBe(false);
  });

  it("rejects short new password", () => {
    const result = passwordSchema.safeParse({
      current: "12345678",
      new: "abc",
    });
    expect(result.success).toBe(false);
  });
});

describe("marketingOLHeaderSchema", () => {
  it("accepts valid OL header", () => {
    const result = marketingOLHeaderSchema.safeParse({
      location: "Jakarta",
      date: "2025-06-01",
      offeringLetterNumber: "001/OL/VI/2025",
      regarding: "Penawaran BBM Solar",
      receiver: "PT Bina Karya",
    });
    expect(result.success).toBe(true);
  });

  it("rejects short location", () => {
    const result = marketingOLHeaderSchema.safeParse({
      location: "J",
      date: "2025-06-01",
      offeringLetterNumber: "001",
      regarding: "Test",
      receiver: "Test",
    });
    expect(result.success).toBe(false);
  });

  it("rejects invalid date", () => {
    const result = marketingOLHeaderSchema.safeParse({
      location: "Jakarta",
      date: "not-a-date",
      offeringLetterNumber: "001",
      regarding: "Test",
      receiver: "Test",
    });
    expect(result.success).toBe(false);
  });
});
