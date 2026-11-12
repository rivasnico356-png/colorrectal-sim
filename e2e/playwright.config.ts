// Pruebas de sistema de punta a punta (Plan de Pruebas: sistema y compatibilidad, RNF-005 y RNF-008).
import { defineConfig, devices } from "@playwright/test";

export default defineConfig({
  testDir: "./pruebas",
  timeout: 90_000,
  retries: 1,
  reporter: [["list"], ["html", { open: "never", outputFolder: "reporte" }], ["json", { outputFile: "resultados.json" }]],
  use: { baseURL: process.env.URL_APP ?? "http://localhost:4173", trace: "retain-on-failure", screenshot: "only-on-failure" },
  projects: [
    { name: "Chrome", use: { ...devices["Desktop Chrome"] } },
    { name: "Firefox", use: { ...devices["Desktop Firefox"] } },
    { name: "Safari (WebKit)", use: { ...devices["Desktop Safari"] } },
    { name: "Chrome Android", use: { ...devices["Pixel 5"] } },
    { name: "Safari iPhone", use: { ...devices["iPhone 12"] } },
  ],
});
