# Selección preliminar de evidencias — fase 5

El catálogo técnico completo reúne **71 PNG originales**, mientras que el informe académico necesita una selección de figuras sin redundancias. Proponemos organizar las ilustraciones por resultado, sin fijar números de figura hasta revisar la última versión Word.

| Resultado | Archivo principal o grupo |
|---|---|
| Arquitectura multisede | `S05_10_Topologia_General_Tres_Sedes.png` |
| Adyacencias OSPF | `S05_18_OSPF_Adyacencias_FULL_Multisede-1.png`, `-2.png`, `-3.png` |
| Rutas principales por FIB | `S05_19_FIB_Rutas_Principales_HQ_S1_S2.png` |
| Recuperación WAN | `S05_24_Failover_WAN_S1_y_Restauracion.png`, `S05_25_Failover_WAN_S2_y_Restauracion.png` |
| Alta disponibilidad HTTP | `S05_38_Conmutacion_HTTP_Principal_Respaldo_Retorno.png` |
| LACP en las tres sedes | `S05_52_LACP_Tres_Sedes_8023ad_Operativas.png`, `S05_57_LACP_Tres_Sedes_Conmutacion_y_Restauracion_Validada.png` |
| Controlador SDN | `S05_58_SDN_Faucet_OpenFlow_Conectado-1.png` |
| Segmentación SDN | `S05_59_SDN_VLAN410_Comunicacion_Permitida.png`, `S05_60_SDN_VLAN420_Aislamiento_Verificado.png` |
| Visión central de NOC | `S05_63_NOC_LACP_Multisede_y_Faucet_Operativos.png` |
| Prueba de HA de instancia | `S05_64_HA_Instancia_HQ_Respaldo_S1_y_Retorno.png` |

Los registros JSONL y TXT del último caso documentan 17 muestras y la secuencia HQ→S1→HQ; recomendamos utilizarlos como evidencia primaria junto con la captura y no presentarlos como prueba de redundancia del servidor físico.

El recorte OSPF `S05_18_OSPF_Adyacencias_FULL_Multisede-3.png` mide 510×93 píxeles y está íntegro. Puede incorporarse como subfigura cuando el conjunto resulte más legible que un montaje. Ninguna figura debe publicarse con nombres de usuario, rutas o IP internas que contradigan la política de privacidad establecida para la entrega.

[Inventario de capturas](../../evidencias/capturas/README.md) · [Guion del informe](../academico/s05-guion-de-actualizacion-del-informe.md).
