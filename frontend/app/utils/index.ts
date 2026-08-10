export function randomInt(min: number, max: number): number {
  return Math.floor(Math.random() * (max - min + 1)) + min;
}

export function randomFrom<T>(array: T[]): T {
  return array[Math.floor(Math.random() * array.length)]!;
}

export function formatCurrency(value: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "currency",
    currency: "IDR",
    currencyDisplay: "narrowSymbol",
  }).format(value);
}

export function formatDate(date: string | Date) {
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "numeric",
    day: "numeric",
  };

  return new Intl.DateTimeFormat("id-ID", options).format(new Date(date));
}

export function formatDateDoc(date: string | Date) {
  const options: Intl.DateTimeFormatOptions = {
    year: "numeric",
    month: "long",
    day: "numeric",
  };

  return new Intl.DateTimeFormat("id-ID", options).format(new Date(date));
}

export function toBase64(url: string): Promise<string> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    img.setAttribute("crossOrigin", "anonymous");
    img.onload = () => {
      const canvas = document.createElement("canvas");
      canvas.width = img.width;
      canvas.height = img.height;
      canvas.getContext("2d")?.drawImage(img, 0, 0);
      resolve(canvas.toDataURL("image/jpeg"));
    };
    img.onerror = reject;
    img.src = url;
  });
}

export function formatPercent(value: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "percent",
  }).format(value);
}

export function formatNumber(value: number) {
  return new Intl.NumberFormat("id-ID").format(value);
}

export function formatToKm(value: number) {
  return new Intl.NumberFormat("id-ID", {
    style: "unit",
    unitDisplay: "short",
    unit: "kilometer",
  }).format(value);
}

export function calculateDynamicStatus(
  dateCreated: string | Date,
  termsDay: number,
  currentInvoiceStatus: string,
): {
  invoiceStatus: "unpaid" | "paid" | "overdue";
  deadlineStatus: "on_time" | "overdue" | "due_soon";
} {
  // If it's already marked as paid in the database, keep it paid.
  if (currentInvoiceStatus === "paid") {
    return {
      invoiceStatus: "paid",
      deadlineStatus: "on_time",
    };
  }

  const createdDate = new Date(dateCreated);
  const deadline = new Date(createdDate);
  deadline.setDate(deadline.getDate() + termsDay);

  // Use UTC to avoid timezone Daylight Saving Time issues
  const today = new Date();
  const todayUTC = Date.UTC(
    today.getFullYear(),
    today.getMonth(),
    today.getDate(),
  );
  const deadlineUTC = Date.UTC(
    deadline.getFullYear(),
    deadline.getMonth(),
    deadline.getDate(),
  );

  const msPerDay = 1000 * 60 * 60 * 24;
  const daysRemaining = Math.floor((deadlineUTC - todayUTC) / msPerDay);

  let invoiceStatus: "unpaid" | "paid" | "overdue" = "unpaid";
  let deadlineStatus: "on_time" | "overdue" | "due_soon" = "on_time";

  if (daysRemaining < 0) {
    invoiceStatus = "overdue";
    deadlineStatus = "overdue";
  } else if (daysRemaining <= 7) {
    deadlineStatus = "due_soon";
  }

  return { invoiceStatus, deadlineStatus };
}
