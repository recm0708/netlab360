# NETLAB360 — Auditoría visual IaC S01 / OpenTofu y Ansible

**Prueba ejecutada realmente en Ubuntu, 13/10/2026 22:27–22:30 (Panamá).** Inspeccionados 9 PNG del operador, equivalentes a **7 bloques de evidencia** (el plan se divide en tres capturas consecutivas), cotejados con las salidas originales de terminal completas de los pasos 156–168. **No se ha subido ninguno de esos nueve PNG a GitHub:** se esperan cuatro capturas de sustitución/recuperación antes de generar un lote auditado definitivo.

## Dictamen de ejecución (independiente de la calidad de capturas)

- IPAM v0.1 `VALIDACIÓN B1: OK`, 3 sedes, 9 VLAN, 2 WAN, `RESULTADO_IPAM=0`; ens33 `192.168.47.40/24`, GW `192.168.47.2`, tres servicios activos; Docker y namespaces vacíos.
- OpenTofu v1.13.1 `init=0`, `validate=0`, `plan=0`; plan **5 add / 0 change / 0 destroy** (management guard, HQ, S1, WAN-P, WAN-B). `apply=0`, 5 created, 0 changed, 0 destroyed (recurso built-in `terraform_data`: **NO redes/routers desplegados**).
- Manifiesto JSON exportado y validado: `HQ,S1`, S2 `reserved`, 2 WAN, `ens33` y gateway preservados, SHA256 del SoT vinculado.
- Ansible core 2.20.1, primera ejecución rc0, dos candidatos FRRouting R-HQ/R-S1 renderizados modo 0600, recap `ok=3 changed=2 failed=0`. `validar-iac-frr.py`: dos `COMPLIANT` y rc0.
- Segunda ejecución Ansible rc0, recap `ok=3 changed=0 failed=0`; `tofu plan -detailed-exitcode`: `No changes` y rc0. Tests locales de compliance/drift: 2/2 correctos.
- Postcheck a las 22:30:22: Docker/netns vacíos, red de gestión intacta, servicios activos, Git limpio. State y JSON fuera del repositorio.
- Aviso Ansible de descubrimiento Python 3.14 no inhibió pruebas ni fue cambio en configuración.

**Valoración de gestión interna:** IaC 1/10 → **4/10** (+3) por consumo real SoT→OpenTofu→JSON→Ansible, render validado e idempotencia. S01 estimado **65→68/100**. Quedan otros seis puntos en IaC por integración sobre nodos vivos, ownership, drift/auto-reconciliación controlados en equipos y regresión global. Esta PoC es metadata/archivos, NO despliegue productivo. El drift simple probado por unittest no equivale a reconciliación de un router real.

## Calidad de evidencias

| Imagen original | SHA-256 | Dictamen |
|---|---|---|
| `IAC_S01_01_Precheck_IPAM_Herramientas.png` | `06f1ed81b10299358a6c100d08dfb9f285d9690852d0be8e2c1e8b06c46e5d2b` | Sustituir resumen sin prompt fallido de sudo |
| `IAC_S01_02_Tofu_Plan-1.png` | `359101c469167015bc4d9efefd9bc972e8c111b7d70e7c9f1919f8c5b194435b` | Válida, parte 1/3 |
| `IAC_S01_02_Tofu_Plan-2.png` | `aba0dd626f832c399085baab27b7609edd1129c71af375684dc8c6c69e415458` | Válida, parte 2/3 |
| `IAC_S01_02_Tofu_Plan-3.png` | `1ed4233abd608aaa38e48d92563a917012f5d13b231f760f4893009eccecb4ce` | Válida, parte 3/3, plan 5 to add |
| `IAC_S01_03_Tofu_Apply_Manifest.png` | `ea43d798d6322ff0943cb3a6140b66bcd091a8a00f38bbcc6ec2cdcf6c70683a` | Incompleta: sólo listado de manifiesto |
| `IAC_S01_04_Ansible_Render_Candidato_FRR.png` | `d2280b110172c53e27533297fdd57ac52600eef433db54ca9aadc4dfd65d905d` | Incompleta: sólo listado de 2 archivos |
| `IAC_S01_05_Compliance_FRR.png` | `9e77ba55d38b89cd0054f3cf2abd86680ffbb6ff6061f5cbdb0467b4d4dcb9` | Válida con observación menor: falta comando |
| `IAC_S01_06_Idempotencia.png` | `d42111fd71336d79fd63cc87252acc9b50afb17d96b4669f14e00c59100bf45a` | Incompleta: no aparece Ansible changed=0 |
| `IAC_S01_07_Postcheck_Final.png` | `3007463c9005af7c13a7db9a1f62d16add56c397edc1173038b4e4487a7495de` | Válida, postcheck |

**Clasificación por 7 bloques:** listos para informe 02 y 07 (02 = 3 PNG), 05 aceptable con observación menor, **reemplazar 01, 03, 04 y 06** por resúmenes fundamentados en logs (no repetir `tofu apply`). Es decir, 3 bloques aceptables/7, 4 bloques por mejorar. Ninguna imagen está adulterada o técnicamente inválida; la insuficiencia es de encuadre/documentación. La imagen original 01 muestra fallo de primer intento sudo (sin contraseña visible), se excluye del lote final para informe.

## Evidencia de reemplazo no destructiva

`scripts/evidencias/resumir-iac-s01.py` produce marcadores precisos de inicio/fin de pantalla para 01, 03, 04, 05 opcional y 06, leyendo:
- `~/netlab360-bootstrap/iac/s01/02-tofu-apply.log` (registro de apply exitoso, 5 recursos).
- `~/netlab360-bootstrap/iac/s01/03-ansible-primera.log` y `04-ansible-idempotencia.log` (recaps reales).
- `~/netlab360-bootstrap/iac/s01/05-tofu-idempotencia.log` (No changes).
- `manifest.json` y configuraciones candidatas (validación de integridad y compliance).

**No reejecuta apply ni crea recursos.** Se conservarán 3 PNG de plan y 1 de postcheck, se aceptará 05 o su versión mejorada, y se pedirán 4 reemplazos, con sufijos `-1` etc. solo si el contenido supera una pantalla. El nuevo ejercicio de drift/reconciliación local es otra evidencia distinta, creada sobre **copias externas** y nunca sobre FRR vivo.

**Estado de publicación:** pendientede recepción/validación de los 4 nuevos screenshots; NO crear todavía ZIP/publicar evidencia IaC incompleta.
