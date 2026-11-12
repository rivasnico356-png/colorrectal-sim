"""Escenario de Locust para RNF-001: personas que entran, revisan el catálogo y resuelven un caso.

Carga:  locust -f pruebas_carga/locustfile.py --headless -u 30 -r 5 -t 10m --host http://localhost:8000
Estrés: agrega --class-picker o usa la forma escalonada con ESTRES=1 (de 30 a 150 usuarios en escalones de 30).
"""
import os
import random
import uuid

from locust import HttpUser, LoadTestShape, between, task

API = "/api/v1"


class PersonaUsuaria(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        correo = f"carga_{uuid.uuid4().hex}@carga.ejemplo.com"
        self.client.post(f"{API}/auth/registro", name="registro", json={
            "nombre": "Persona de carga", "correo": correo, "contrasena": "Carga12345", "rango_edad": "50-59", "acepta_politica": True})
        r = self.client.post(f"{API}/auth/login", name="login", json={"correo": correo, "contrasena": "Carga12345"})
        self.client.headers["Authorization"] = f"Bearer {r.json().get('access_token', '')}"

    @task(3)
    def catalogo(self):
        self.client.get(f"{API}/casos", name="catálogo")

    @task(1)
    def progreso(self):
        self.client.get(f"{API}/progreso", name="progreso")

    @task(2)
    def resolver_caso(self):
        casos = self.client.get(f"{API}/casos", name="catálogo").json()
        if not casos:
            return
        r = self.client.post(f"{API}/intentos", name="iniciar intento", json={"id_caso": casos[0]["id_caso"], "acepto_aviso": True})
        id_intento = r.json().get("id_intento")
        for _ in range(5):
            estado = self.client.get(f"{API}/intentos/{id_intento}", name="ver etapa").json()
            etapa = estado.get("etapa")
            if not etapa:
                break
            self.client.post(f"{API}/intentos/{id_intento}/etapas/{etapa['id_etapa']}/tutor", name="tutor", json={})
            self.client.post(f"{API}/intentos/{id_intento}/decisiones", name="decidir", json={
                "id_etapa": etapa["id_etapa"], "id_opcion": random.choice(etapa["opciones"])["id_opcion"], "confianza": 3, "tiempo_ms": 3000})


if os.getenv("ESTRES") == "1":
    class Escalones(LoadTestShape):
        """Estrés: 30, 60, 90, 120 y 150 usuarios, 60 s cada escalón, y luego 60 s de recuperación con 30."""
        escalones = [30, 60, 90, 120, 150, 30]

        def tick(self):
            i = int(self.get_run_time() // 60)
            return (self.escalones[i], 10) if i < len(self.escalones) else None
