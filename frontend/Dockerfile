FROM node:22-alpine AS builder
RUN corepack enable
WORKDIR /app
COPY pnpm-lock.yaml package.json pnpm-workspace.yaml ./
RUN pnpm install --frozen-lockfile --ignore-scripts
COPY . .
ENV NODE_OPTIONS="--max-old-space-size=4096"

RUN pnpm build

# Guard: build harus memuat aplikasi (bukan fallback welcome page Nuxt).
# Sering terjadi image lama/template tanpa app/ yang diam-diam menampilkan
# halaman "Get started"/NuxtWelcome lalu disalahkan sebagai bug runtime.
RUN if ! grep -q "Mitra Andalan" .output/server/chunks/build/server.mjs; then \
      echo "FATAL: aplikasi tidak ditemukan di hasil build (cek app/ dan nuxt.config.ts)"; \
      echo "Tindakan: jangan gunakan image ini, cari image lama di ^docker images^"; \
      exit 1; \
    fi

FROM node:22-alpine
RUN corepack enable
WORKDIR /app
COPY --from=builder /app/.output ./.output
EXPOSE 3000
CMD ["node", ".output/server/index.mjs"]
