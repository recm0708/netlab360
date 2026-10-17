# NETLAB360 — Figuras/tablas para el informe único oficial (16/10)

**Reemplaza guía anterior «dos documentos»**. El único informe académico técnico exige **7 Implementación, 8 Pruebas y validación, 9 Análisis**, y se prepara presentación después. S01 cuenta con **86 PNG originales y 7 CSV hash** en GitHub; seleccionar solo figuras legibles que apoyen resultados, no publicar indiscriminadamente.

| Tema técnico/ubicación de informe | Evidencia representativa en `evidencias/capturas/` | Interpretación o límite |
|---|---|---|
| Arquitectura/diseño, sección 6 | Figura lógica de HQ↔S1 doble WAN, S2 reservada, creada para el documento | Es diseño conceptual, NO topología final integrada |
| VLAN/ACL, 7–8 | `B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png` | Restricción 8081 vs 8080, dentro de HQ |
| HTTP dual WAN, 8 | `B2_L3_01_HTTP_WAN_Principal.png`, `B2_L3_02_HTTP_WAN_Respaldo.png`, `B2_L3_03_HTTP_WAN_Restaurada.png` | Estados estabilizados, no cero downtime demostrado |
| LACP, 8 | Imágenes originales `B2_LACP_01*`, `B2_LACP_02*`, `B2_LACP_03*` | Negociación IEEE 802.3ad veth 2→1→2; no capacidad medida |
| Bonding activo-respaldo, 8 | `B2_DUALNIC_02_Conmutacion_Respaldo.png` | Redundancia de miembros virtuales, no NIC del hipervisor |
| IaC→FRR, 7–8 | `IAC_B2_03_OSPF_y_Rutas_IAC.png`; `IAC_S01_09_Reconciliacion.png` | Ansible alimentó FRR real; drift corregido en COPIAS de config |
| Observabilidad, 8 | `B3_12_Alerta_Prometheus_WAN_Down.png`, `B3_13_Alerta_Prometheus_Resuelta.png` | firing/resolución en Prometheus, no receptor Alertmanager |
| Diagnóstico B4, 8–9 | `B4_08_Diagnostico_Reglas_Reales.png` y perfil estadístico | Diagnóstico reglas, no modelo ML evaluado |
| Estado final S01 | Captura postcheck validada ya publicada o logs seguros | Host limpio y red de gestión intacta, según ejecución |

## Inserción APA 7 / formato institucional
- Introducir cada figura/tabla **mediante un párrafo y cita cruzada a su número**; número en negrita, título en cursiva, y `Nota.` cuando fuente, abreviaturas, procedencia, criterio o restricción lo requiera.
- Numerar desde Figura 1/Tabla 1 a lo largo del ÚNICO Word. **No asumir numeración final actual**: el documento antiguo tenía seis figuras y seis tablas; al migrar a doce apartados puede cambiar el orden, por lo que se debe actualizar el índice automático de Word.
- Priorizar legibilidad impresa y recortar/agrandar sin alterar contenido. Si una imagen de terminal es extensa, seleccionar el fragmento que acredita la prueba y remitir a log anexo, siempre íntegro.
- Las capturas adicionales pueden usarse en PPT final solo después de cerrar informe.
- No publicar contraseñas, claves, tokens ni datos privados en el informe o ZIP.

[Plan de migración](../academico/01-migracion-borrador-a-formato-docente.md) · [Guía oficial](../academico/00-criterios-docentes-y-hitos.md).
