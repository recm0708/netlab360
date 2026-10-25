# NETLAB360 — Figuras/tablas para el informe único oficial (16/10)

**Documento de selección histórica para el informe académico único; preservar títulos reales de capturas.** El único informe académico técnico exige **7 Implementación, 8 Pruebas y validación, 9 Análisis**, y se prepara presentación después. S01 cuenta con **86 PNG originales y 7 CSV hash** en GitHub; seleccionar solo figuras legibles que apoyen resultados, no publicar indiscriminadamente.

| Tema técnico/ubicación de informe | Evidencia representativa en `evidencias/capturas/fase1/` | Interpretación o límite |
|---|---|---|
| Arquitectura/diseño, sección 6 | Figura lógica de HQ↔S1 doble WAN, S2 reservada, creada para el documento | Es diseño conceptual, NO topología final integrada |
| VLAN/ACL, 7–8 | `S01_B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` | Restricción 8081 vs 8080, dentro de HQ |
| HTTP dual WAN, 8 | `S01_B2_L3_01_HTTP_WAN_Principal.png`, `S01_B2_L3_02_HTTP_WAN_Respaldo.png`, `S01_B2_L3_03_HTTP_WAN_Restaurada.png` | Estados estabilizados, no cero downtime demostrado |
| LACP, 8 | Imágenes originales `S01_B2_LACP_01*`, `S01_B2_LACP_02*`, `S01_B2_LACP_03*` | Negociación IEEE 802.3ad veth 2→1→2; no capacidad medida |
| Bonding activo-respaldo, 8 | `S01_B2_DUALNIC_02_Conmutacion_Respaldo.png` | Redundancia de miembros virtuales, no NIC del hipervisor |
| IaC→FRR, 7–8 | `S01_IAC_B2_03_OSPF_y_Rutas_IAC.png`; `S01_IAC_09_Reconciliacion.png` | Ansible alimentó FRR real; drift corregido en COPIAS de config |
| Observabilidad, 8 | `S01_B3_12_Alerta_Prometheus_WAN_Down.png`, `S01_B3_13_Alerta_Prometheus_Resuelta.png` | firing/resolución en Prometheus, no receptor Alertmanager |
| Diagnóstico B4, 8–9 | `S01_B4_08_Diagnostico_Reglas_Reales.png` y perfil estadístico | Diagnóstico reglas, no modelo ML evaluado |
| Estado final S01 | Captura postcheck validada ya publicada o logs seguros | Host limpio y red de gestión intacta, según ejecución |

## Inserción APA 7 / formato institucional
- Introducir cada figura/tabla **mediante un párrafo y cita cruzada a su número**; número en negrita, título en cursiva, y `Nota.` cuando fuente, abreviaturas, procedencia, criterio o restricción lo requiera.
- Numerar desde Figura 1/Tabla 1 a lo largo del ÚNICO Word. **No asumir numeración final actual**: el documento antiguo tenía seis figuras y seis tablas; al migrar a doce apartados puede cambiar el orden, por lo que se debe actualizar el índice automático de Word.
- Priorizar legibilidad impresa y recortar/agrandar sin alterar contenido. Si una imagen de terminal es extensa, seleccionar el fragmento que acredita la prueba y remitir a registro técnico del paquete TAR externo, siempre íntegro.
- Las capturas adicionales pueden usarse en PPT final solo después de cerrar informe.
- No publicar contraseñas, claves, tokens ni datos privados en el informe o TAR externo.

[Plan de migración](../academico/01-migracion-borrador-a-formato-docente.md) · [Guía oficial](../academico/00-criterios-docentes-y-hitos.md).


## Nota de migración (25/10/2026)

**Estas son referencias de imágenes históricas seleccionadas**, no una nueva numeración de Figuras 1–11 del Word. Los 86 PNG están ahora bajo `evidencias/capturas/fase1/`, con prefijo S01 y su bloque original conservado. Para cualquier ruta previa, consultar [mapa de renombrado](../../evidencias/manifiestos/MAPA_RENOMBRADO_FASE1_2026-10-25.csv). Figuras/títulos formales del borrador 3 se controlan exclusivamente en Word. El paquete docente es `.tar` externo, **sin capítulo de anexos**.
