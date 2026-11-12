// Flujo completo de la persona usuaria con revisión de accesibilidad WCAG 2.1 AA en cada pantalla.
// Usa el caso sintético que crea backend/pruebas_carga/sembrar.py (sin contenido clínico).
import AxeBuilder from "@axe-core/playwright";
import { expect, Page, test } from "@playwright/test";

async function revisarAccesibilidad(page: Page, pantalla: string) {
  const r = await new AxeBuilder({ page }).withTags(["wcag2a", "wcag2aa", "wcag21a", "wcag21aa"]).analyze();
  const resumen = r.violations.map((v) => `${v.impact}: ${v.id} (${v.nodes.length})`);
  await test.info().attach(`axe-${pantalla}`, { body: JSON.stringify(resumen, null, 1), contentType: "application/json" });
  // Criterio del Plan de Calidad (C-04, RNF-008): cero errores críticos de accesibilidad.
  expect(r.violations.filter((v) => v.impact === "critical"), `Errores críticos en ${pantalla}: ${resumen.join("; ")}`).toEqual([]);
}

test("registro, simulación completa, progreso y privacidad", async ({ page }) => {
  const correo = `e2e_${Date.now()}_${Math.random().toString(36).slice(2, 7)}@ejemplo.com`;

  // Pantalla 02 · Registro (RF-001 1.1)
  await page.goto("/");
  await revisarAccesibilidad(page, "01-ingreso");
  await page.getByRole("button", { name: "Crear una cuenta" }).click();
  await page.getByLabel("Nombre").fill("Persona de prueba E2E");
  await page.getByLabel("Correo").fill(correo);
  await page.getByLabel(/^Contraseña/).fill("Segura123");
  await page.getByLabel(/política de tratamiento/).check();
  await revisarAccesibilidad(page, "02-registro");
  await page.getByRole("button", { name: "Registrarme" }).click();

  // Pantalla 01 · Inicio de sesión (RF-001 1.2)
  await expect(page.getByRole("heading", { name: "Iniciar sesión" })).toBeVisible();
  await page.getByLabel("Correo").fill(correo);
  await page.getByLabel("Contraseña").fill("Segura123");
  await page.getByRole("button", { name: "Ingresar" }).click();

  // Pantalla 03 · Catálogo (RF-002 2.6)
  await expect(page.getByRole("heading", { name: "Biblioteca de casos" })).toBeVisible();
  const tarjeta = page.locator("article", { hasText: "Caso sintético de carga" }).first();
  await expect(tarjeta).toBeVisible();
  await revisarAccesibilidad(page, "03-catalogo");
  await tarjeta.getByRole("button").click();

  // Pantalla 04 · Aviso de alcance (RF-003 3.1)
  await expect(page.getByRole("heading", { name: "Antes de empezar" })).toBeVisible();
  await revisarAccesibilidad(page, "04-aviso");
  await page.getByRole("button", { name: "Entiendo y quiero continuar" }).click();

  // Pantallas 05 a 07 · Etapas, retroalimentación y resumen (RF-003, RF-004, RF-005)
  for (let etapa = 1; etapa <= 2; etapa++) {
    await expect(page.getByText(`Etapa ${etapa} de 2`)).toBeVisible();
    await expect(page.getByText(/Resultado experimental de apoyo a la detección e interpretación/)).toBeVisible();
    if (etapa === 1) await revisarAccesibilidad(page, "05-etapa");
    await page.getByRole("button", { name: "¿Por qué sugiere esto?" }).click();
    await expect(page.locator(".chat .ia").first()).toBeVisible();
    await page.getByLabel("Opción A").check();
    await page.getByRole("button", { name: /^3/ }).click();
    await page.getByRole("button", { name: "Confirmar decisión" }).click();
    await expect(page.getByText(/puntos/)).toBeVisible();
    if (etapa === 1) await revisarAccesibilidad(page, "06-retroalimentacion");
    await page.getByRole("button", { name: etapa === 2 ? "Ver resumen" : "Siguiente etapa" }).click();
  }
  await expect(page.getByRole("heading", { name: /Resumen/ })).toBeVisible();
  await expect(page.getByText("2 de 2")).toBeVisible();
  await revisarAccesibilidad(page, "07-resumen");

  // Pantalla 08 · Progreso (RF-008)
  await page.getByRole("button", { name: "Mi progreso" }).click();
  await expect(page.getByRole("heading", { name: "Mi progreso" })).toBeVisible();
  await expect(page.getByText("Caso sintético de carga").first()).toBeVisible();
  await revisarAccesibilidad(page, "08-progreso");

  // Pantalla 09 y datos personales (RF-010, RF-009)
  await page.getByRole("button", { name: "Mis estudios" }).click();
  await expect(page.getByRole("heading", { name: "Mis estudios" })).toBeVisible();
  await revisarAccesibilidad(page, "09-estudios");
  await page.getByRole("button", { name: "Mis datos" }).click();
  await expect(page.getByRole("heading", { name: "Mis datos y privacidad" })).toBeVisible();
  await revisarAccesibilidad(page, "privacidad");

  // RF-001 1.2b: cerrar sesión
  await page.getByRole("button", { name: "Cerrar sesión" }).click();
  await expect(page.getByRole("heading", { name: "Iniciar sesión" })).toBeVisible();
});
