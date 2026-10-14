# NETLAB360 — Selección preliminar de figuras y tablas S01 para los tres maestros

**Control 14/10/2026:** lista de archivos comprobados contra el árbol Git con **86 PNG** publicados. No importar indiscriminadamente las 86 capturas a Word. **Esta tabla es un inventario editorial preliminar, no un segundo índice de figuras en los documentos.** La numeración final Figura 1, 2, ... se asigna separadamente y de forma continua en cada uno de los tres documentos.

## Documento 01 — Investigación
| Tema explicado y figura o tabla sugerida | Evidencia seleccionada | Uso editorial |
|---|---|---|
| Arquitectura e IPAM previsto HQ/S1/S2 | diagrama de topología propio derivado de inventario, aún por preparar | diseño, rotulado como previsto vs desplegado |
| WAN doble y selección de rutas | IAC_B2_03_OSPF_y_Rutas_IAC.png | apoyar resultados, no reemplazar gráfico de arquitectura |
| Prometheus y alerta de caída real | B3_12_Alerta_Prometheus_WAN_Down.png | resultados observabilidad |
| Resultados B4, sin ML entrenado | B4_05_Perfil_Estadistico_Real.png | análisis con limitaciones de sesion única |
| Tabla de comparación de capacidades probadas/pendientes | crear desde matriz S01 | tabla explicada, nunca captura de texto como sustituto |

## Documento 02 — Informe técnico/laboratorio
| Subprueba | Evidencia seleccionada (ruta relativa desde raíz del repositorio) |
|---|---|
| VLAN y trunk 802.1Q | evidencias/capturas/B2_L2_02_Trunk_8021Q_VLAN110_120.png |
| ACL HTTP permitido y denegado | evidencias/capturas/B2_L2_06_ACL_HTTP_Permitido_Bloqueado.png |
| HTTP WAN principal | evidencias/capturas/B2_L3_01_HTTP_WAN_Principal.png |
| HTTP WAN respaldo | evidencias/capturas/B2_L3_02_HTTP_WAN_Respaldo.png |
| HTTP WAN restaurada | evidencias/capturas/B2_L3_03_HTTP_WAN_Restaurada.png |
| LACP dos enlaces, salida larga **en cuatro fragmentos originales** | evidencias/capturas/B2_LACP_01_Agregacion_Dos_Enlaces-1.png a -4.png |
| LACP un enlace, **cuatro fragmentos originales** | evidencias/capturas/B2_LACP_02_Falla_Un_Enlace-1.png a -4.png |
| Redundancia virtual active-backup | evidencias/capturas/B2_DUALNIC_02_Conmutacion_Respaldo.png |
| IaC aplicada a FRR y OSPF | evidencias/capturas/IAC_B2_03_OSPF_y_Rutas_IAC.png |
| Drift detectado/reconciliado sobre copia | evidencias/capturas/IAC_S01_08_Drift_Detectado.png y IAC_S01_09_Reconciliacion.png |
| NOC real | evidencias/capturas/B3_08_Dashboard_NOC_En_Vivo.png |
| Alertas firing y resolución | evidencias/capturas/B3_12_Alerta_Prometheus_WAN_Down.png y B3_13_Alerta_Prometheus_Resuelta.png |
| Perfil y diagnóstico por reglas | evidencias/capturas/B4_05_Perfil_Estadistico_Real.png y B4_08_Diagnostico_Reglas_Reales.png |
| Sensibilidad exploratoria | evidencias/capturas/B4_10_Sensibilidad_Umbral_RTT.png |

## Documento 03 — Manual
| Procedimiento / vista | Evidencia seleccionada |
|---|---|
| Vista inicial del NOC, **sólo capacidad disponible** | evidencias/capturas/B3_08_Dashboard_NOC_En_Vivo.png |
| Identificar alarma WAN | evidencias/capturas/B3_12_Alerta_Prometheus_WAN_Down.png |
| Verificar recuperación | evidencias/capturas/B3_13_Alerta_Prometheus_Resuelta.png |
| Ver rutas OSPF | evidencias/capturas/IAC_B2_03_OSPF_y_Rutas_IAC.png |
| Diagnóstico de histórico | evidencias/capturas/B4_08_Diagnostico_Reglas_Reales.png |
| Apagado/limpieza | aún no publicado el PNG LOTE06_Postcheck_Publicacion.png recibido en chat; no marcarlo presente en Git |

## Política de incorporación APA 7

**Ejemplo de preámbulo:** “Para comprobar la selección del enlace de respaldo, se consultó la tabla de enrutamiento del router HQ durante la indisponibilidad administrada del enlace principal. La Figura N presenta la interfaz activa observada y permite verificar el cambio a WAN-B”.

**Ejemplo de pie en Word:** número en negrita “Figura N” en línea propia, título descriptivo en cursiva debajo, imagen y nota si aplica. **Nota.** Captura del laboratorio NETLAB360, [fecha], [archivo de evidencia], elaborada por el equipo. La nota también deberá distinguir si es referencia interna, captura original o adaptación. Ajustar al formato institucional cuando el usuario lo proporcione.

Las tablas también llevan número y título APA 7 sobre la tabla, notas debajo cuando haga falta y párrafo explicativo previo. **No repetir un índice para cada fase**. Referir cada figura/tabla en el texto, y elegir los fragmentos LACP necesarios en lugar de pegar los doce.
