# NETLAB360 — Figuras representativas del informe académico (S01)

**Catálogo oficial al 27/10/2026: 83 PNG S01.** Selección técnica por relevancia y legibilidad; el informe mantiene capítulos 1–8 y referencias, sin apartado de anexos.

| Ensayo | Evidencia técnica recomendada | Interpretación |
|---|---|---|
| VLAN/ACL HTTP | `S01_B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` | Puerto 8080 permitido, 8081 restringido en la prueba |
| HTTP dual WAN | `S01_B2_L3_02_HTTP_WAN_Respaldo.png` | Servicio accesible en ruta alternativa estabilizada |
| Enlace agregado LACP | `S01_B2_LACP_01_Agregacion_Dos_Enlaces-1.png`, `S01_B2_LACP_02_Falla_Un_Enlace-1.png` | Bond lógico IEEE 802.3ad; no ancho de banda físico medido |
| Bonding activo/respaldo | `S01_B2_DUALNIC_02_Conmutacion_Respaldo.png` | Failover lógico del enlace virtual |
| Integración inicial IaC→FRR | `S01_IAC_B2_03_OSPF_y_Rutas_IAC.png` | Configuraciones generadas y probadas en FRR |
| Alertas S01 | `S01_B3_12_Alerta_Prometheus_WAN_Down.png` | Evaluación de reglas Prometheus, no entrega externa |
| Diagnóstico determinista | `S01_B4_08_Diagnostico_Reglas_Reales.png` | Reglas sobre 76 muestras, no un modelo ML |

Cada imagen requiere texto introductorio, número, título y nota cuando proceda. La numeración corresponde al Word único; al corte del borrador 4.4 se han incorporado figuras 1–20 y tablas 1–13. El paquete TAR con evidencias técnicas se preparará por separado en S08.
