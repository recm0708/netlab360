# NETLAB360 — Auditoría visual del lote 04: LACP IEEE 802.3ad

**Corte:** 13 de octubre de 2026, posterior a 21:20 (Panamá).  
**Material recibido:** 13 archivos PNG auténticos, sin edición, de 4 bloques de evidencia: 4 fragmentos B2_LACP_01, 4 de B2_LACP_02, 4 de B2_LACP_03 y 1 de B2_LACP_04. **Auditoría: 13/13 válidos como secuencias complementarias**, no 13 pruebas independientes. El texto de terminal está cotejado con el log original 20:43 y el postcheck 20:51; cada fragmento aporta una parte de una salida larga.

**Estado de publicación binaria:** los 13 PNG **RECIBIDOS y AUDITADOS, NO SUBIDOS A GITHUB**. El manifiesto y ZIP se proporcionaron al usuario para que los importe desde Ubuntu con un commit propio y un push verificable. No cerrar issue de evidencias hasta ese paso.

## Dictamen por bloque

| Bloque | PNG | Lectura correlacionada con log |
|---|---:|---|
| B2_LACP_01 | 4 | Negociación activa/fast IEEE802.3ad de ambos bonds, agregador 2 puertos en A/B y HTTP `NETLAB360_LACP_HTTP_OK` |
| B2_LACP_02 | 4 | Miembro a1/b1 down, contador de fallas 1, agregador 1 puerto en A/B y HTTP por a2/b2 OK |
| B2_LACP_03 | 4 | Puertos a1/b1 restaurados, agregador otra vez 2 puertos por lado y HTTP OK |
| B2_LACP_04 | 1 | Postcheck 20:51 Docker/netns sin residuos, gestión ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios activos, Git limpio en ese instante |

Ninguna captura evidencia hardware NIC físico/VMware dual NIC ni otro switch. Tasa veth 10 Gbps es dato de interfaz virtual, **no** throughput real; HTTP comprobado en estados estabilizados, **no** disponibilidad sin microcortes.

## Manifiesto SHA-256 individual

| Archivo PNG | SHA-256 |
|---|---|
| `B2_LACP_01_Agregacion_Dos_Enlaces-1.png` | `b9b27914aafed87b989617376a45d20d7ccf10a07df19f6189ba682d4c1a6dba` |
| `B2_LACP_01_Agregacion_Dos_Enlaces-2.png` | `a5d8283029ec9da4fdfb90264c99583f0773bd3599e0800f8798dce927b9b334` |
| `B2_LACP_01_Agregacion_Dos_Enlaces-3.png` | `92866280a8633f65d552bd3507e08323fc728fe533feacb0ec19ac2e18c75548` |
| `B2_LACP_01_Agregacion_Dos_Enlaces-4.png` | `9a6bbb529c5a2cb62da770b942a6ef080827c35e0be41b16af5fa787beb335a3` |
| `B2_LACP_02_Falla_Un_Enlace-1.png` | `326014333b0b0e662371df6911b12addb52390230e61c5c3780b462e6904a984` |
| `B2_LACP_02_Falla_Un_Enlace-2.png` | `978a24e436cad1ff5276533dfb2a17ce496d9e6fbc1ce429a5480257b0c737c2` |
| `B2_LACP_02_Falla_Un_Enlace-3.png` | `a194183a8e042fc5a38f475f76a618db04f74b9300c90775ef249a9dbf7a180d` |
| `B2_LACP_02_Falla_Un_Enlace-4.png` | `f5f3c22298ce169f1f326f787296677f6c4fc2e7a88987b3b5676f0f85b24af6` |
| `B2_LACP_03_Restauracion_Dos_Enlaces-1.png` | `eea78861a59c54b8deb000ee725eefb99f833c352999668f4d03c4469ba79481` |
| `B2_LACP_03_Restauracion_Dos_Enlaces-2.png` | `321771e0096f5169bde27952321f0aa84f8a4aec299bfe86b893660dc34e63cf` |
| `B2_LACP_03_Restauracion_Dos_Enlaces-3.png` | `66837c63b141b1c79f4fbd546be4ea1b59ccf0df8c49cff14e2ad6fd1400c65a` |
| `B2_LACP_03_Restauracion_Dos_Enlaces-4.png` | `deee6d3a66f327bd47bbe8d6dd2a85e320984fc8216c070fc458a81277dac197` |
| `B2_LACP_04_Postcheck_Final.png` | `7e938f6db40b113f09158e76bf02d764ccab75169cf06bedb62dea5d1e371fb9` |

## Paquete preparado

- `NETLAB360_LOTE04_LACP_13PNG_AUDITADOS_2026-10-13.zip`: **726693 bytes**, SHA-256 `085cfb84dd6926a01a0d8185be46ed09ae619c5e719175e161c73324bb2695c7`.
- CSV interior `MANIFIESTO_SHA256_NETLAB360_LOTE04_LACP_13PNG.csv`: SHA-256 `e3a70d1688676b08b869e41038cb4e4469a4d7443dae08d98be0d431c344d46a`.
- Contenido ZIP: `capturas/` 13 PNG, CSV manifiesto e instrucciones TXT. Archivo ZIP comprobado sin miembros corruptos.
- Ruta destino reservada: `evidencias/capturas/B2_LACP_lote04/` (13 PNG + CSV). **No reemplazar ni duplicar lotes 01/02/03**.
- Mantener convenciones `-1`.. `-4` porque son segmentos originales de la misma evidencia.

## Estado posterior del proyecto

Los 20 PNG del lote03 (más CSV) **sí fueron publicados** en GitHub por el usuario, commit `0d749dff5a27c4c108aea7cdec8ddb5723394bb1` con verificación `PUBLICACION_GITHUB=OK` y HEAD local=remoto. El ensayo dualNIC active-backup arrancó a las 21:20 pero abortó antes del HTTP por bug Bash `n_ACTIVA: variable sin asignar` en `bond_info`; limpieza reportó `RED_GESTION_INTACTA=SI`, `RESULTADO_B2_DUALNIC=1`. Se corrigieron las dos expansiones Bash en `scripts/laboratorio/b2-dualnic-activebackup-http.sh`. **DualNIC aún NO acreditado; puntuación S01 permanece 63/100.**
