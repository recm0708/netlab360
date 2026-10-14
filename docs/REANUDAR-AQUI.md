# NETLAB360 — REANUDAR AQUÍ (checkpoint operativo)

## CORTE MÁS RECIENTE 13/10 23:35 — PRIORIZAR ENTREGABLES S01

- Lote06 **realmente publicado**: commit `b410548f9338233c8dc23816ce78a11d67bb2896`, Git local/remoto igual; 86 PNG y 7 CSV, SHA256 correctos, sin subcarpetas.
- Cuatro resúmenes IaC 01/03/04/06 generados desde logs con códigos 0, fotos de reemplazo aún pendientes de recibir; postcheck `LOTE06_Postcheck_Publicacion.png` recibido y por auditar/publicar posteriormente.
- CI `38511477595` exitosa. VM postcheck 23:35:02 Docker/netns vacíos, ens33 `192.168.47.40/24`, gateway `.2` y tres servicios activos.
- **S01 continúa ABIERTA (72/100 técnico estimado)**. Pausar funciones nuevas B4/AIOps para terminar primero documentación e identificar alcance rubricado de las pruebas imprescindibles.
- Borradores académicos versionados en `docs/entregables/s01/`: informe, bitácora, manual y checklist crítico. Sus archivos Word editables se generaron fuera del repo para revisión y no deben confundirse con DOCX versionados.
- **Próximo objetivo:** confirmar guía/criterios docentes, metadatos de portada y formato; completar figuras; decidir pruebas de integración mínimas y necesidad actual de OVA/reimportación. [Checklist operativo](entregables/s01/00-checklist-cierre-y-entrega.md).

---


## CHECKPOINT ACTUAL — 13/10/2026 23:24 PANAMÁ | B4 REGLAS OPERATIVAS, LOTE06 AUDITADO

**Datos REALES del operador pasos 202–212:** sincronizó a `12a9d2f`, sintaxis0, suite **24/24 tests OK**, CSV 76 ICMP SHA256 verificado, `b4-diagnostico-reglas.py --save` exit0, 0 pérdidas, 0 desviaciones FIB en fases estables, 0 señales RTT; umbral exploratorio 3×P95 normal = 0.147 ms; umbral 5×P95=0.245 ms también 0 señales; **4 transiciones operativas** (sondeos 15/16/32/61) no consideradas incidentes. Reporte externo `~/netlab360-bootstrap/analitica/b4/diagnostico-reglas-real.json` JSON válido y modo0600. **No ML entrenado**, no métricas precision/recall/F1, baseline derivado de **MISMA** sesión histórica, nunca llamar a 0 señales `100% acierto`. Postcheck 23:23:26: Docker/netns vacíos, ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios activos, Git limpio. [Auditoría fotográfica actual](evidencias/08-auditoria-lote06-iac-b4-2026-10-13.md).

**CI Node24 realmente comprobada:** GitHub Actions run `38510552044` job `115677813059` `completed/success`, todos los pasos verdes (fuente: `gh run view --exit-status` y jobs remotos), quedó solo aviso informativo de futuro runner Ubuntu26. Nuevos commits GitHub posteriores a ese run requieren comprobar CI de nuevo si cambian scripts.

**FOTOGRAFÍAS RECIBIDAS Y AUDITADAS:** 19 PNG nuevos (13 B4+6 IaC), 5 PNG IaC buenos de un envío anterior ⇒ **24 seleccionados** (23 sin observación + `IAC_S01_05_Compliance_FRR.png` válida con observación menor porque no enseña comando). Originales SHA256 individuales y nombres correctos en CSV del ZIP ya preparado. **Excluidos** 4 originales IAC incompletos `IAC_S01_01/03/04/06`, pendientes de reemplazo desde logs (NO repetir `tofu apply`). **Lote06 ZIP:** `NETLAB360_LOTE06_IAC_B4_24PNG_AUDITADOS_2026-10-13.zip` SHA256 `803ee03050a2261e938c56ed1c266097639c357f3fc77882a8a18eb5330bc781`, 1,293,367 bytes; CSV SHA `fbf6b9567ad6249a071ab9b53ba89368d0c0ab275b84b5a00d82eb4e85718c7f`, 24 filas. **No se han publicado aún los 24 PNG en GitHub**, aunque la auditoría y scripts sí; 62 PNG previos y seis CSV siguen versionados.

**PRÓXIMO PASO DE UBUNTU:** `git pull --ff-only` limpio; descargar ZIP desde ChatGPT a Windows y enviarlo por SCP a `rc-aa-ec@192.168.47.40:~/` si no está ya; `scripts/mantenimiento/importar-lote06-iac-b4.py --verificar` y después `--importar`, auditar `scripts/validacion/validar-capturas-unificadas.py`; commit/push solo `evidencias/capturas/` y `evidencias/manifiestos/`; comparar SHA Git local/remoto y **86 PNG planos + 7 CSV**, ningún subdirectorio, preservar 62 anteriores. NO publicar ZIP mismo dentro del repo. Después generar fotos de cuatro bloques IAC faltantes mediante `scripts/evidencias/resumir-iac-s01.py` y mandar en próxima tanda. No hacer nuevo laboratorio WAN solo por fotos. **S01=72/100 técnico estimado**, B4 evaluación ML no acreditada; issue #1/#6 abiertas, #43 abierta para fotos pendientes.

---


## CHECKPOINT VIGENTE 13/10/2026 23:12:45 PANAMÁ — B4 PERFIL ESTADÍSTICO VERIFICADO

**Fuente:** transcripción del operador pasos 192–201. Regresión local Python **16/16 OK**, CSV B2 original SHA256 verificado (349643e93c3e5f69cd529508d2349be0ef570a3e0291d144344413fc2b373eb5); perfil real creado `~/netlab360-bootstrap/analitica/b4/perfil-estadistico-real.json`, válido, `0600`, código0. **76/76 ICMP correctos, 0 fallas, 0 desvíos FIB en fases estables**, RTT medias/P95 por cinco fases documentadas en [bitácora B4 perfil](sesiones/2026-10-13-b4-perfil-estadistico-verificado.md). Eventos B3 separados (12 JSONL), no sumar a 76 ni presentarlos como etiquetas independientes. Postcheck 23:12:45 sin Docker/netns, ens33 `192.168.47.40/24`, GW `192.168.47.2`, tres servicios activos, Git limpio.

**CI:** runs GitHub `38509420496` y `38509454510` presentados ✓ en `gh run list`; run previo `38508522760` confirmado con `gh run view --exit-status`. Advertencia Node20 no causó fallo; workflow actualizado a `checkout@v5` / `setup-python@v6` (Node24), nueva ejecución AUN POR COMPROBAR. Comando correcto para seleccionar run sin literal de ejemplo: `RUN_ID=$(gh run list -R recm0708/netlab360 --workflow ci-regresion-s01.yml --limit 1 --json databaseId --jq '.[0].databaseId'); gh run view "$RUN_ID" -R recm0708/netlab360 --exit-status`.

**ESTADO S01=72/100 estimado** (sin nuevos puntos por estadística únicamente); B4 IA/ML aún **NO entrenada ni evaluada**. Capturas nuevas de B4/IaC se enviarán después a voluntad del usuario, no solicitarlas ahora.

**SIGUIENTE BLOQUE preparado en GitHub, NO ejecutado:** `scripts/analitica/b4-diagnostico-reglas.py` (solo lectura, SHA256 vinculados, tres reglas ICMP/FIB/RTT >3×P95 normal, transiciones operativas diferenciadas; referencia basada en misma sesión, NO clasificación ni false-positive rate); `tests/test_b4_diagnostico_reglas.py` ocho tests nuevos (24 tests globales esperados). Reporte futuro externo al repo `~/netlab360-bootstrap/analitica/b4/diagnostico-reglas-real.json`, 0600. Próximo: pull Git limpio, tests, ejecutar --save, auditar reporte vs perfil, sensibilidad factor5 SIN guardar, CI actualizado, postcheck. Ninguna falla WAN, aplicación FRR, cambio VMware ni instalación sklearn en esta tanda. [Bitácora](sesiones/2026-10-13-b4-perfil-estadistico-verificado.md).

---


## CHECKPOINT VIGENTE 13/10/2026 23:00 PANAMÁ — B4 AUDITORÍA EJECUTADA Y CI VERDE

El operador terminó **pasos 181–191** con Git sincronizado (`a6eaa91` al cierre de ensayo), 11/11 pruebas unitarias correctas, auditoría de fuente real B4 exit0, reporte JSON de 2,4 KB permisos 0600, postcheck 23:00 con Docker/netns vacíos, ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios activos y Git limpio. **CI GitHub comprobada** run `38508522760`, job `offline-regression` id `115671442438` completado **success** en todos los pasos. El error del usuario al intentar `gh run view --workflow`/usar literalmente `ID_DE_EJECUCION` es solo sintaxis CLI; comando correcto `gh run view 38508522760 -R recm0708/netlab360 --exit-status`. [Bitácora B4 ejecutada](sesiones/2026-10-13-b4-auditoria-datos-ci-ejecutada.md).

**Datos auditados:** 1 CSV ICMP original `17-b2-convergencia-20261013-115141.csv`, 76 muestras; 1 resumen derivado de **los mismos 76**, NO fuente independiente; 2 JSONL `b3-wan-live-events*.jsonl`, 12 eventos (1 started, 2 stopped, 2 primary down, 2 primary restored, 5 route changed). SHA256 y esquema inspeccionados; fuentes B2 y B3 son sesiones distintas, no alinear filas. **Sin etiquetas independientes de normalidad o incidentes, sin ML entrenado, sin precision/recall/F1**. Disponibilidad Python 3.14.4, numpy existente, pandas/sklearn/matplotlib no instalados; no instalar sin necesidad.

**PROGRESO** S01 **72/100 estimado** (71→72 **+1 por CI offline realmente ejecutada y validada**, documentación/regresión 2→3/5; B4 permanece 0/5 hasta disponer de diagnóstico evaluado). IaC–FRR live 22:48 sigue validada; issue S01 abierta, rúbrica docente no ratificada. Evidencias nuevas B4/IaC: usuario enviará capturas MÁS ADELANTE, **no pedirlas ahora**, ni crear ZIP incompleto. En GitHub aún 62 PNG originales y seis CSV.

**PRÓXIMO BLOQUE PREPARADO, AÚN NO EJECUTADO:** `scripts/analitica/b4-perfil-estadistico-real.py` y `tests/test_b4_perfil_estadistico.py`, para estadísticas por fase de muestras reales ICMP y conteo de ruta FIB usando hash del inventario auditado, sin datos sintéticos ni modelos ML. Se espera pull limpio, regresión 16/16 si los nuevos 5 pasan, corrida `--save` y JSON resultante con permisos 0600 fuera del repo, comprobación de cifras contra 76 filas, CI de nuevo por ver, postcheck de VM. Si hay CSV inválido, no forzar/editar fuente, reportar error. Luego diseñar adquisición de muestras independientes etiquetadas por ensayo.

---


## CHECKPOINT MÁS RECIENTE — 13/10/2026 22:48 PANAMÁ | IaC EN FRR REAL VERIFICADA; B4 PREPARADA

**Fase S01: 71/100 técnico estimado, ABIERTA** (sube 68→71: IaC 4→7/10). Fuente real recibida del operador: los pasos 169–180 fueron exitosos. En copia FRR candidata: R-HQ OSPF WAN-P cost 10→50, detector NON_COMPLIANT (rc1 esperado), Ansible reconcilió changed1, luego changed0, hashes originales intactos, `RESULTADO_DRIFT_RECONCILIACION=0`. Gate IaC–B2 protegió VMnet8 y confirmó SoT: `IAC_B2_PRECHECK=0`, origen `IAC_OPENTOFU_ANSIBLE`, configuración R-HQ/R-S1 desde `~/netlab360-bootstrap/iac/s01/rendered/`.

**Despliegue REAL en contenedores FRRouting:** 22:46 up0, OSPF 2 vecinos Full por router, FIB WAN-P; 22:47 status0, fail0 WAN-P→WAN-B por OSPF, restore0 WAN-B→WAN-P; 22:48 down0 y postcheck limpio (Docker/netns vacíos; ens33 `192.168.47.40/24`, GW `192.168.47.2`, 3 servicios activos y Git limpio). **NO** sostener que OpenTofu creó routers ni que Ansible reconcilió drift de router vivo: el primero registra `terraform_data`, el drift fue sobre **archivos copiados** y el script B2 consumió los candidatos para arrancar FRR. Todavía no se probó modificación/reconciliación en FRR en ejecución, ni conmutación de equipo físico. [Bitácora IaC–B2](sesiones/2026-10-13-iac-b2-frr-live-y-drift-verificado.md).

**EVIDENCIAS:** el usuario indicó que enviará las capturas nuevas y los complementos juntos en un mensaje posterior. **No se han recibido los PNG de esta tanda ni publicado lote nuevo.** Los 62 PNG anteriores y 6 CSV ya permanecen en GitHub con integridad comprobada. No repetir up/fail/restore/down para tomar fotos; el log original respalda el nuevo hito. Posibles capturas a recuperar después desde logs de fail y restore sin ejecutar fallas.

**SIGUIENTE BLOQUE PREPARADO EN GITHUB:** `scripts/analitica/b4-auditar-fuentes-reales.py` y test `tests/test_b4_fuentes_reales.py`, análisis SOLO de lectura sobre CSV ICMP B2 y eventos JSONL reales B3, archivo resumen fuera del repo bajo `~/netlab360-bootstrap/analitica/b4/`, NO entrena ML. [Plan B4](sesiones/2026-10-13-b4-auditoria-fuentes-preparada.md). `.github/workflows/ci-regresion-s01.yml` creado para regresiones offline; **estado CI por comprobar**, no contar como ejecutado sin ver el run. Próximo: pull limpio, tests, captura B4_01 delimitada, auditar dataset y determinar plan de etiquetas/modelo, comprobar CI. Sin instalar librerías ML preventivamente, ni provocar nueva caída WAN, ni tocar ens33/VMnet8/rutas host.

---


## CHECKPOINT VIGENTE — 13/10/2026 22:30 PANAMÁ | IAC APLICADA EN ESTADO LOCAL, COMPLIANCE E IDEMPOTENCIA OK

**Ejecutado y verificado realmente en Ubuntu** por el operador (pasos 156–168): IPAM rc0, OpenTofu 1.13.1 `init=0,validate=0,plan=0,apply=0` con **5 registros `terraform_data`** (guarda ens33/VMnet8, HQ/S1, 2 WAN); estado físico y manifiesto FUERA del repo bajo `~/netlab360-bootstrap/iac/s01/`. `manifest.json` válido (HQ/S1, S2 reservada, dos WAN, gestión protegida); Ansible 2.20.1 generó R-HQ/R-S1 candidatos modo0600, `ok=3 changed=2 failed=0`; comparador FRR `COMPLIANT` ambos; segunda ejecución Ansible `changed=0,failed=0`; `tofu plan -detailed-exitcode` devolvió 0 `No changes`. Postcheck 22:30:22 Docker/netns vacíos, ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios activos, Git limpio. **S01 65→68/100 estimado, IaC 1→4/10.** Esto es **estado de metadatos y archivos candidatos**, no provisioning de red/FRR vivo. [Bitácora de ejecución](sesiones/2026-10-13-iac-s01-ejecutado.md).

**AUDITORÍA VISUAL IAC:** se recibieron **9 PNG** en 7 bloques. Plan `02` (3 PNG) y postcheck `07` se conservan; compliance `05` es aceptable con observación por falta de comando; `01` se reemplazará para no exhibir error de contraseña sudo, y `03/04/06` requieren contexto adicional. **NO REEJECUTAR OPEN TOFU APPLY.** `scripts/evidencias/resumir-iac-s01.py` ya versionado lee **logs auténticos** y emite límites `INICIO/FIN CAPTURA` para 01/03/04/05 opcional/06. No subir aún el lote de evidencias incompleto. [Auditoría visual](evidencias/07-auditoria-visual-iac-s01-2026-10-13.md).

**SIGUIENTE BLOQUE PREPARADO, AÚN NO EJECUTADO:** 1) recuperar esas 4 capturas mediante resúmenes históricos, 2) comprobar archivos de state/manifest están protegidos 0600, 3) ejecutar `scripts/laboratorio/iac-s01-drift-reconciliacion-local.py` una sola vez, sobre COPIAS externas (costo OSPF 10→50→10, `NON_COMPLIANT`→Ansible `changed=1`→`COMPLIANT`, segunda `changed=0`), 4) probar `scripts/validacion/precheck-iac-b2.py` (solo lectura) y `bash -n scripts/laboratorio/b2-dualwan-ospf.sh`, 5) verificar snapshot y ejecutar B2 con variable `NETLAB360_IAC_CONFIG_DIR=$HOME/netlab360-bootstrap/iac/s01/rendered` **solo si todos los prechecks pasan**. El script B2 conserva baseline sin variable, y con variable copia exclusivamente candidatos validados por gate para crear routers FRR aislados, luego down/postcheck. No afirmar fase live terminada hasta recibir logs de esa nueva ejecución. Nunca tocar `ens33`/VMnet8/NetworkManager/firewall ni volver a importar capturas 01–05.

**Estado evidencias antiguas:** 62 PNG/6 CSV ya publicados desde `328591a` y carpeta plana, confirmado SHA remotos y local. Issue #43 abierta para nuevas evidencias IaC. S01 #1, #16, #17, #18 abiertas.

---


## CHECKPOINT MÁS RECIENTE — 13/10/2026 22:16 PANAMÁ | 62 CAPTURAS PUBLICADAS + IAC PREPARADA

**Evidencia binaria / GitHub:** el usuario ejecutó exitosamente la importación corregida del lote05, `RESULTADO_IMPORTACION_LOTE05=0`, `LOTE05_IMPORTADO=SI`, `SHA256_INDIVIDUALES=OK`. El auditor de todos los originales dio `PNG_DIRECTOS=62`, `CSV_VERIFICADOS=6`, `SHA256_ORIGINALES=OK`, `AUDITORIA_CAPTURAS_PLANAS=OK`, exit0. Commit `328591acaed06431457b903dec6c7a2b91c39b25` publicado, SHA local y remoto **idénticos**, `GITHUB_SINCRONIZADO=SI`, rama limpia, **cero subdirectorios** de capturas en Ubuntu y GitHub. Confirmado también por árbol remoto real. **Reorganización COMPLETADA; no repetir ni solicitar lotes 01–05.** [Auditoría lote05](evidencias/06-auditoria-lote05-dualnic-noc-2026-10-13.md) · [capturas](../evidencias/capturas/) · [manifiestos](../evidencias/manifiestos/). Issue #43 sigue abierta para futuras evidencias del semestre, no por lotes 01–05.

**S01 65/100 técnico estimado** (no es calificación). LACP y dual-NIC active-backup veth están validados, **no** duplicidad de hardware. Los 62 PNG son evidencia auditada y publicada, no incremento adicional a puntuación.

**NUEVA VERTICAL IAC PREPARADA EN GITHUB, NO EJECUTADA:** `iac/s01/main.tf` (OpenTofu terraform_data built-in con 1 guarda VMnet8, 2 sitios activos HQ/S1 y 2 WAN; S2 reservada), `ansible/s01/render-frr.yml` con plantilla `templates/frr-router.conf.j2` para configs candidatas R-HQ/R-S1, `scripts/validacion/validar-iac-frr.py` y `tests/test_iac_frr.py`. [Runbook completo](sesiones/2026-10-13-iac-s01-opentofu-ansible-preparado.md). **OpenTofu state y salida Ansible FUERA del clon** en `~/netlab360-bootstrap/iac/s01/`. Ni OpenTofu ni Ansible de esta PoC tocan interfaces de red, Docker, rutas o FRR en ejecución; solo registran estado declarativo y crean archivos candidatos. No sumar puntos sin ejecutar y verificar `plan/apply`, consumo del manifiesto, compliance e idempotencia. Los pasos próximos comienzan con pull `main` limpio, precheck red/SoT/herramientas y unit tests. El recurso built-in **no** supone despliegue de routers; la integración activa B2 vendrá después, con guardas y rollback. Si falla una fase, no reejecutar a ciegas, enviar salida.

---


## CHECKPOINT VIGENTE — 13/10/2026 POSTERIOR A 21:39 | APLANADO PUBLICADO, LOTE05 PENDIENTE

**Fuente: salida real de Ubuntu y árbol GitHub verificado.** El operador corrió `aplanar-capturas.py --plan`: 57 PNG, 4 CSV, 0 colisiones, 61 movimientos. `--aplicar` **sí movió los 61 archivos y generó el mapa SHA256**, pero terminó con código1 porque `git mv` dejó físicamente las cuatro carpetas originales (vacías o por verificar). El usuario **ya hizo commit/push** de esos 61 movimientos + mapa: commit [`570088c`](https://github.com/recm0708/netlab360/commit/570088c5ed3fd7ce3b888facecfe79c39e78005f), `GITHUB_SINCRONIZADO=SI`, SHAs local/remoto iguales. Todos los PNG fueron reportados con similitud Git 100%. En **GitHub** ya NO hay cuatro subcarpetas: **57 PNG directos** en `evidencias/capturas/`, **4 CSV históricos + 1 mapa** en `evidencias/manifiestos/`. El clon Ubuntu aún muestra cuatro carpetas físicas residuales, no versionadas.

**Lote05:** ZIP local `~/NETLAB360_LOTE05_DUALNIC_NOC_5PNG_2026-10-13.zip` con SHA256 verificado `9e57057e402a9a87e1c2e91997ad59dd88cb136d6329f75ba50721181959cdfa`. El importador anterior abortó en guardia de carpetas y **NO añadió 5 PNG ni CSV**; por ello el commit `570088c` usa un mensaje que menciona lote05 prematuramente. **No alterar/revertir ese commit; completar mediante nuevo commit.** Avance técnico S01 sigue 65/100 estimado, no sumar por organización.

**Corrección ya publicada en GitHub después del commit del operador:** `scripts/mantenimiento/aplanar-capturas.py` elimina carpetas viejas solo si están vacías al finalizar movimientos (no repetir `--aplicar`); `scripts/mantenimiento/importar-lote05.py` ahora reconoce **exclusivamente** las cuatro carpetas antiguas si están vacías y las retira de modo seguro **después** de validar ZIP, manifiesto, hashes, nombres y antes de escribir los 5 PNG. Nuevo auditor no destructivo `scripts/validacion/validar-capturas-unificadas.py` verifica mapa de 61 entradas y cinco capturas nuevas. **Próxima tanda:** Git limpio + `git pull --ff-only`, inspeccionar físicamente el contenido de las cuatro carpetas, verificar nuevos scripts, reejecutar SOLO `importar-lote05.py` (no aplanado), auditar 62 PNG + 6 CSV, stage solo `evidencias/capturas` + `evidencias/manifiestos`, commit/push nuevo, comparar SHAs y recuento remoto, postcheck Git limpio. Si queda cualquier archivo oculto o directorio con datos, abortar sin forzar borrado. **No** tocar VMware, VMnet8, ens33, gateway, rutas/firewall, Docker, servicios ni logs fuera del clon. Documentación de auditoría de lotes 01–05 ya tiene rutas actuales y distingue historial.

**Pendientes posteriores:** normalizar referencias de acceso en README/checkpoint, cierre issue #43 según alcance de próximas evidencias y comenzar IaC OpenTofu/Ansible integrado, sin repetir LACP/dualNIC/OSPF ya validados.

---


## CHECKPOINT VIGENTE — 13/10/2026 21:39 PANAMÁ | DUAL-NIC APROBADO, LOTE04 PUBLICADO, APLANADO PREPARADO

**Esta sección prevalece sobre menciones previas de “dualNIC pendiente” y de lote04 no publicado.** El operador publicó lote04 con **13 PNG LACP + CSV** y confirmó `LOTE04_PUBLICADO=OK`; commit `2af7a8054a87bc10db1195f5f54d92b2dbc04c8f`, `main...origin/main` limpio. En total GitHub tiene **57 PNG** en cuatro carpetas, antes del lote05.

**DUAL-NIC REALMENTE EJECUTADO 21:37–21:39:** ensayo `b2-dualnic-activebackup-http.sh` corregido, bonding active-backup en namespaces virtuales, **a1/b1 → a2/b2 → a1/b1 disponibles con a2/b2 aún activo**, HTTP `NETLAB360_DUAL_NIC_HTTP_OK` en los 3 estados estabilizados, `DUALNIC_ACTIVE_BACKUP_TRES_ESTADOS=OK`, `RESULTADO_B2_DUALNIC=0`, `RESULTADO_EJECUCION_DUALNIC=0`, `RED_GESTION_INTACTA=SI`. Postcheck 21:39:13: Docker/netns vacíos, `ens33 192.168.47.40/24`, GW `192.168.47.2`, servicios activos y Git limpio. **4/4 PNG dualNIC recibidos, válidos, NO publicados binariamente aún**. Límite: veth, no VMware dual NIC real ni equipo redundante. **S01 sube 63→65% técnico estimado (+2, redundancia 4→6/10)**, #1 abierta.

**Otros 4 PNG adjuntos:** `B3_04_Postcheck_Servicio_NOC_Final.png` es complemento útil **nuevo**, 8765 libre; `B3_04_Postcheck_Servicio_NOC(1).png` duplicado exacto de captura Git existente; `B3_09_Postcheck_Telemetria_Viva.png` intermedio reemplazado por FINAL; `B2_L3_04_Postcheck_HTTP_WAN.png` primer intento fallido reemplazado por FINAL. **Solo 5 nuevos a publicar**, no los 3 excluidos. [Auditoría lote05](evidencias/06-auditoria-lote05-dualnic-noc-2026-10-13.md).

**CAMBIO ORGANIZATIVO A SOLICITUD DEL USUARIO:** los 57 PNG actualmente en cuatro carpetas por lotes se migrarán por `git mv` directamente a **`evidencias/capturas/`**, manteniendo nombres de PNG y bytes; 4 CSV se trasladarán a `evidencias/manifiestos/`, renombrando los dos `MANIFIESTO_SHA256.csv` colisionantes a `...LOTE01.csv` y `...LOTE02.csv`. Script versionado **`scripts/mantenimiento/aplanar-capturas.py`**, con `--plan` y `--aplicar`, guarda mapa SHA256 de origen-destino. **Migración todavía NO EJECUTADA.** Después añadir ZIP lote05 con cinco PNG directos + CSV de integridad, `commit/push`, comprobar **62 PNG directos y 5 CSV de lote + mapa** en el clon y remoto. Mantener 2–3 capturas históricas excluidas fuera del nuevo lote. No tocar `~/netlab360-bootstrap/evidencias` (logs fuera del clon), VMnet8, ens33, rutas, gateway, Docker ni firewall. Luego avanzar IaC OpenTofu/Ansible y topología integrada; no repetir pruebas completadas.

---


## CHECKPOINT MÁS RECIENTE — 13/10/2026 ~21:20 PANAMÁ | LOTE03 PUBLICADO, LACP FOTOGRÁFICO AUDITADO, DUALNIC ABORTADO Y CORREGIDO

**Prevalece sobre el historial posterior de este documento:** el usuario realizó `git commit` y `git push` del lote03: commit `0d749dff5a27c4c108aea7cdec8ddb5723394bb1`, **20 PNG originales + 1 CSV ya físicamente publicados en GitHub**, `PUBLICACION_GITHUB=OK`, refs local/remoto iguales. El lote 03 deja de estar pendiente de publicación.

**LACP:** recibidos y auditados 13 PNG (4 segmentos del bloque 01, 4 del 02, 4 del 03, 1 del 04), todos válidos como secuencias; manifiesto SHA256 individual, ZIP `NETLAB360_LOTE04_LACP_13PNG_AUDITADOS_2026-10-13.zip` (726693 bytes, SHA256 `085cfb84dd6926a01a0d8185be46ed09ae619c5e719175e161c73324bb2695c7`) generados para transferencia. **NO publicados aún como PNG en GitHub**. [Auditoría lote04](evidencias/05-auditoria-visual-lote04-lacp-2026-10-13.md). No repetir LACP.

**Dual-NIC:** precheck 21:20 correcto (script sintaxis 0; Docker/netns vacíos, ens33 `192.168.47.40/24`, GW `192.168.47.2`, 3 servicios activos, bonding disponible); inicio de ensayo active-backup mostró modo correcto y a1/a2 up, pero falló en `bond_info` por expansión `$n_ACTIVA` en `set -u` (variable `n_ACTIVA` sin asignar), **antes de HTTP o falla controlada**. `RESULTADO_B2_DUALNIC=1`, `RED_GESTION_INTACTA=SI`; postcheck posterior necesario para confirmar namespaces vacíos. Dos líneas corregidas a `${n}_ACTIVA` y `${n}_MIEMBROS` en commit `5a4569f`. **NO aprobado; S01 mantiene 63/100**, issue #1 abierta.

**CONTINUACIÓN:** primero confirmar cleanup e integridad host; `git pull --ff-only origin main` tras comprobar que la rama está limpia; `bash -n` y `grep` de expansiones corregidas; transferir ZIP de 13 imágenes al guest, validar SHA256 e importar a `evidencias/capturas/B2_LACP_lote04`, commit/push y hashes; solo con precheck/snapshot confirmado reejecutar UNA VEZ el script dualNIC corregido. Exigir HTTP por primaria, HTTP por respaldo y HTTP tras restauración, dos miembros en ambos bonds, marcadores 01/02/03, código 0 y cleanup. Si falla, no relanzar; enviar log/postcheck. Después capturas `B2_DUALNIC_01/02/03/04`, cambios documentales e IaC. No modificar VMnet8, ens33, GW, firewall o rutas del host.

---


## CHECKPOINT VIGENTE — 13/10/2026 20:52 PANAMÁ | LACP PROBADO + 20 PNG NUEVOS AUDITADOS

**Este estado prevalece sobre notas anteriores sobre LACP y fotos pendientes.** Usuario aportó salida real de Ubuntu: `b2-lacp-8023ad-dos-enlaces.sh --snapshot-confirmado` comprobó **IEEE802.3ad LACP active/fast, dos puertos en agregador de cada extremo, caída a UN puerto tras apagar a1/b1, recuperación a DOS puertos**, HTTP `NETLAB360_LACP_HTTP_OK` en los tres estados, `LACP_8023AD_TRES_ESTADOS=OK`, `RESULTADO_B2_LACP=0`, `RESULTADO_EJECUCION_LACP=0`, `RED_GESTION_INTACTA=SI`. Postcheck **20:51:35** Docker/netns vacíos, ens33 `192.168.47.40/24`, default `192.168.47.2`, docker/ssh/open-vm-tools activos, Git `main...origin/main` limpio en commit local `a8a9879` **antes de nuevos commits documentales**. Módulo bonding estaba disponible en `modinfo bonding`, se autoloadó, no hizo falta instalar programa. [Bitácora LACP](sesiones/2026-10-13-b2-lacp-8023ad-verificado.md).

**S01 ahora 63% técnico estimado (+4 LACP, de 0/10 a 4/10; 37 pts totales pendientes), #1 aún ABIERTA**; no confundir LACP con dual-NIC VMware, switch/host de respaldo ni disponibilidad sin cortes.

**EVIDENCIAS VISUALES RECIBIDAS 20/20:** Usuario adjuntó todos los PNG B2_L2_02–07 (6), B2_L3_01–04_FINAL (4), B3_05–14 (10). **18 VÁLIDAS y 2 VÁLIDAS CON OBSERVACIÓN** (B2_L2_06 líneas nftwrap; B3_09_FINAL prompt sudo sin contraseña); 0 rechazadas, 20 SHA256 individuales registrados en [auditoría lote03](evidencias/04-auditoria-visual-lote03-2026-10-13.md). Paquete ZIP descargable en la conversación `NETLAB360_LOTE03_20PNG_AUDITADOS_2026-10-13.zip` (1,011,954 bytes, SHA256 `9e11e1c3181ba62f53b1bde894f77ae4af0c6417beba1ebf10e578b90a342585`) y CSV manifiesto SHA256 generado. **ATENCIÓN: los 20 PNG están recibidos y auditados, pero NO FUERON subidos binariamente a GitHub aún**; transferir ZIP al clon Ubuntu, verificar SHA256, extraer 20 nuevos PNG a `evidencias/capturas/B2_B3_lote03` y commit/push verificado. **Los 24 PNG anteriores (lotes 01/02) SÍ están subidos**, no volver a solicitarlos ni duplicarlos.

**ÚNICAS FOTOS OBLIGATORIAS PENDIENTES DE RECEPCIÓN INMEDIATA:** `B2_LACP_01_Agregacion_Dos_Enlaces.png`, `B2_LACP_02_Falla_Un_Enlace.png`, `B2_LACP_03_Restauracion_Dos_Enlaces.png`, `B2_LACP_04_Postcheck_Final.png`. Fueron ejecutados los bloques de terminal LACP_01–03 y postcheck 04, pero **no se han recibido estas cuatro imágenes PNG para auditoría visual**. Tres fotos antiguas opcionales siguen opcionales. [Inventario actualizado](evidencias/03-inventario-pendientes-auditoria-2026-10-13.md), issue #43.

**SIGUIENTE SCRIPT PREPARADO EN REPO, NO EJECUTADO:** `scripts/laboratorio/b2-dualnic-activebackup-http.sh` dos namespaces propios, bond `mode active-backup`, dos NIC veth por extremo, HTTP en primaria → falla primaria → HTTP por secundaria → recuperación de primaria disponible; limpieza en trap y prechecks de ens33/GW. [Diseño](sesiones/2026-10-13-b2-dualnic-activebackup-preparado.md). **NO** atribuir puntos dualNIC al mero script. NO es dual NIC física VMware, ni redundancia de equipo real.

**SIGUIENTE RESPUESTA CON 10 PASOS** por preferencia del usuario, cubrir descarga ZIP Windows, SCP al guest, verificación SHA256, extracción segura/importación sólo 20 PNG, commit/push y verificación, 4 fotos LACP desde log, precheck y ejecución del ensayo dual-NIC si entorno libre. Si script falla, abortar pasos dependientes y hacer postcheck sin relanzar. Nunca tocar VMnet8/ens33/firewall/rutas de host.

---


## ESTADO FOTOGRÁFICO VIGENTE — 13/10/2026 | NO PEDIR ARCHIVOS YA PUBLICADOS

Se creó y se verificó en GitHub el [inventario maestro de evidencias pendientes](https://github.com/recm0708/netlab360/blob/main/docs/evidencias/03-inventario-pendientes-auditoria-2026-10-13.md): **24 PNG B1/B2+B3 histórico ya inspeccionados y alojados físicamente** en `evidencias/capturas/B1_B2_lote01` (19) y `evidencias/capturas/B3_lote02` (5), excluidos expresamente de nuevas solicitudes.

**20 PNG prioritarios pendientes de recepción visual:** B2_L2_02–07 (6), B2_L3_01/02/03/04_FINAL (4), B3_05/06/07/08/09_FINAL/10/11/12/13/14 (10). El usuario enviará fotos junto con las salidas del próximo laboratorio. **3 opcionales históricas:** B3_04_Final, B3_09 intermedio y B2_L3_04 del intento fallido; no repetir ensayos para obtenerlas. **4 LACP futuras:** B2_LACP_01/02/03/04, no contarlas hasta ejecutar la prueba. B3_08 navegador debe confirmarse si existe. El hecho de haber recibido resultados de consola solo acredita la prueba, **no revisión de píxeles ni publicación de PNG**.

**Ultimo hito realmente probado:** B2-L3 HTTP HQ→S1 correcto en tres WAN y rollback 19:44; S01 59% estimado; Git sincronizado a `6a3e50f` antes de commits posteriores. **Próximo paso operativo 105–114:** pull Git ff-only, revisión de sintaxis del LACP script y de módulos/red, precheck no hay namespaces, luego único ensayo LACP 802.3ad modo 2→1→2 puertos con HTTP y rollback; inspeccionar log sin reejecutar, capturas LACP_01–03 y final LACP_04. Si falla, enviar resultados y no repetir a ciegas. No tocar ens33 `192.168.47.40/24`, default `192.168.47.2`, VMnet8, firewall ni IPAM del host. **Issue #43** actualizada con inventario y distinción pendiente/pub.

---


## CHECKPOINT ACTUAL — 2026-10-13 19:45 PANAMÁ | HTTP HQ-S1 REAL SUPERADO, LACP SIGUIENTE

**PREVALECE sobre notas anteriores que decían HTTP E2E fallido o pendiente.** El usuario ejecutó el script corregido `b2-l3-http-clientes-wan.sh --snapshot-confirmado` y mostró: `OSPF_DUAL_FULL: SI`, `RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK`, `RESULTADO_B2_DUALWAN_UP=0`. Dos hosts namespace (cliente HQ `10.70.10.10/32`, servidor S1 `10.71.10.20/32:8080` unidos vía veth P2P al FRR, sin integración a trunk VLAN) se comunicaron HTTP correctamente tras seleccionar **WAN-P → WAN-B → WAN-P**. Marcadores `HTTP_WAN_PRINCIPAL=OK`, `HTTP_WAN_RESPALDO=OK`, `HTTP_WAN_RESTAURADA=OK`, `B2_L3_HTTP_TRES_ESTADOS=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`, `RESULTADO_EJECUCION_E2E=0`, limpieza B2 código0. **No se probó ausencia absoluta de interrupciones HTTP durante la transición**. [Bitácora real](sesiones/2026-10-13-b2-l3-http-hq-s1-wan-tres-estados-verificados.md).

**Postcheck real 19:44:57:** Docker/netns vacíos, marcador B2 ausente, ens33 `192.168.47.40/24`, GW `192.168.47.2`, servicios docker/ssh/open-vm-tools activos, Git limpio sincronizado con `6a3e50f` (antes de nuevos commits). B2_L3_01/02/03/04_FINAL con bloques console realmente emitidos y extraídos, considerados tomados según usuario **pero los PNG no se han recibido ni auditado ni versionado físicamente**. Conservar captura B2_L3_04 anterior como histórico de primer intento fallido. Log original `~/netlab360-bootstrap/evidencias/b2-l3-http-wan-20261013-194254.log` solo VM.

**Matriz S01 ahora 59% técnico provisional** (B2-L3 18/18, +1 pt; resto 41 puntos). La fase S01 está ABIERTA (11 criterios integrales pendientes); semana académica 9. Evitar más pruebas OSPF/HTTP repetidas. El siguiente bloque es LACP/dual-NIC y luego IaC: [plan LACP](sesiones/2026-10-13-lacp-8023ad-preparado-tras-http-wan.md).

**NUEVO SCRIPT YA EN REPO, SIN EJECUTAR:** `scripts/laboratorio/b2-lacp-8023ad-dos-enlaces.sh`. Pide snapshot confirmado, crea solo namespaces `nl360-lacpa` y `nl360-lacpb`, bonds modo IEEE802.3ad a ambos lados con 2 enlaces veth, `miimon100`, `lacp_rate fast`. Prueba agregador realmente activo **2→1→2 puertos** según `/proc/net/bonding/bond0`, HTTP de A→B funcional en tres estados, trap cleanup de sus namespaces y resguardo ens33/rutas. **No acredita doble NIC de VM o equipos, no modifica VMnet8 ni host firewall.** Módulo `bonding` antes no visible en /sys/module; no significa ausencia: si no soportado, aborta con log y cleanup. **No declarar probado/sumar puntos aún.**

**Próxima tanda de 10 pasos, solicitada expresamente:** 105 pull y sintaxis, 106 precheck recursos y gestión, 107 verificar capacidades/soporte bonding no destructivo, 108 imagen/estado Git y preflight snapshot, 109 ejecutar UNA sola vez LACP, 110 inspeccionar resumen log y `LACP_8023AD_TRES_ESTADOS`, 111–113 capturas B2_LACP_01/02/03 desde log sin relanzar, 114 postcheck B2_LACP_04_Final con Docker/netns y ens33/GW intactos, Git limpio. **Si falla alguna guardia, no avanzar al ensayo; si ejecución LACP falla, detener y compartir error sin repetir.** Tras LACP, dar bloque de 8–12 pasos para dual NIC/host y IaC. El usuario pidió mínimo 8–10 pasos por turno, no microfragmentar avances.

---


## ALERTA DE REANUDACIÓN MÁS RECIENTE — 13/10/2026 19:32 PANAMÁ | PRIMER ENSAYO CLIENTE HTTP HQ-S1 FALLÓ ANTES DE CAPTURAS; ROLLBACK OK

**IMPORTANTE: este nuevo estado prevalece sobre el anterior que decía `b2-l3-http-clientes-wan.sh` solo preparado.** El operador ejecutó `bash scripts/laboratorio/b2-l3-http-clientes-wan.sh --snapshot-confirmado` a **19:30:38** tras pull a `722a347`, con `RESULTADO_SINTAXIS_E2E=0`, precheck Docker/netns vacíos, red ens33=192.168.47.40/24, gateway=192.168.47.2. FRR B2 up creó routers y alcanzó **2 vecinos Full por router**; acto seguido, **antes de preparar los clientes ni consultar HTTP**, devolvió `RTNETLINK answers: Network is unreachable`, `ERROR: up interrumpido (2)`. Orquestador original hacía `ip route get` de LAN remota **inmediatamente** después de vecinos Full; la instalación OSPF de rutas FIB puede retrasarse. **Es la causa probable, aún por validar con nuevo ensayo**.

**LIMPIEZA REAL CONFIRMADA:** `RESULTADO_B2_LIMPIEZA=0`, `RED_GESTION_INTACTA=SI`, `RESULTADO_B2_L3_HTTP_WAN=2`, `RESULTADO_EJECUCION_E2E=2`. Postcheck **19:32:20** contenedores/netns vacíos, `ESTADO_B2_LIMPIO: SI`, host/red/servicios intactos, Git sincronizado con commit `722a347` **antes** de los nuevos commits. S01 mantiene **58% técnico estimado**, sin puntos nuevos por intento fallido. [Bitácora](sesiones/2026-10-13-b2-l3-e2e-primer-intento-fib-pendiente.md).

**CAPTURAS REALES DE ESTE INTENTO:** usuario reportó que **SOLO TOMÓ `B2_L3_04_Postcheck_HTTP_WAN.png`** y que B2_L3_01/02/03 estaban vacías al extraer de log: los tres marcadores nunca se emitieron. **No volver a pedir la captura B2_L3_04 fallida; es evidencia válida de postcheck/rollback, aunque su PNG aún no fue recibido/inspeccionado.** En nuevo intento exitoso se solicitará `B2_L3_01/02/03` por primera vez y **`B2_L3_04_Postcheck_HTTP_WAN_Final.png`** como cierre funcional.

**DOS CORRECCIONES PUBLICADAS EN GITHUB, SIN EJECUTAR AÚN EN VM:**
- `scripts/laboratorio/b2-dualwan-ospf.sh` nueva función `wait_remote_routes`: después de `wait_full`, hasta 60 sondeos de 1 segundo hasta que HQ→10.71.10.1 y S1→10.70.10.1 **sean alcanzables por FIB dev wan-p**; caso contrario error4 y rollback B2. No modifica rutas del host.
- `scripts/laboratorio/b2-l3-http-clientes-wan.sh` trasladó `check_route wan-p/wan-b/wan-p` **dentro de los delimitadores B2_L3_01/02/03**, para que cada nueva captura incluya la FIB bidireccional y el HTTP real juntos. El script usa clientes `/32` unidos vía veth punto-a-punto a routers FRR y NO demuestra conexión VLAN física al trunk.

**SIGUIENTES PASOS AGRUPADOS:** Ubuntu `cd ~/proyectos/netlab360`, `GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main`, `bash -n` **ambos** scripts; `grep -n 'wait_remote_routes\|RUTAS_OSPF_BIDIRECCIONALES_WAN_P' scripts/laboratorio/b2-dualwan-ospf.sh`, comprobar Docker/netns sin recursos, no `estado-b2-dualwan`, ens33/GW intactos, Git limpio. Si pasa, ejecutar **UNA SOLA VEZ** `bash scripts/laboratorio/b2-l3-http-clientes-wan.sh --snapshot-confirmado`; ahora exigir `RUTAS_OSPF_BIDIRECCIONALES_WAN_P=OK` antes de HTTP. Si funciona, `HTTP_WAN_PRINCIPAL=OK`, `HTTP_WAN_RESPALDO=OK`, `HTTP_WAN_RESTAURADA=OK`, `B2_L3_HTTP_TRES_ESTADOS=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`; capturas B2_L3_01..03 y B2_L3_04_Final de postcheck. Si vuelve a fallar, no repetir y enviar error/log para revisar origen preciso. Ningún paquete requiere instalación por este diagnóstico.

---


## NUEVO CHECKPOINT — 2026-10-13 19:16 PANAMÁ | ACL/HTTP INTRA-HQ OK, E2E WAN PREPARADO

**Supera los bloques anteriores que decían ACL pendiente.** El usuario ejecutó realmente y validó `scripts/laboratorio/b2-l2-acl-http-real.sh --snapshot-confirmado` entre 19:14 y 19:15: cliente VLAN110 `10.70.10.10`, servidor VLAN120 `10.70.20.20`, switches con trunk y router con `eth0.110 10.70.10.1` / `eth0.120 10.70.20.1`. Baseline sin ACL: **HTTP8080 OK, HTTP8081 OK** desde cliente. Luego `nft` exclusivamente en router: HTTP8080 permitido, HTTP8081 bloqueado con `curl (28) Connection timed out` esperado **aunque el servicio 8081 seguía activo**; nft contadores **8080 accept 1 pkt/60 bytes, 8081 drop 2 pkt/120 bytes**. `ACL_ROUTER_NAMESPACE=OK`, `RESULTADO_B2_L2_ACL_HTTP=0`, `RESULTADO_EJECUCION_ACL_HTTP=0`, `RED_GESTION_INTACTA=SI`. Postcheck 19:15:56 Docker/netns vacíos, `ens33 192.168.47.40/24`, default `192.168.47.2`, docker/ssh/open-vm-tools activos. `GIT_SINCRONIZADO: SI`, commit local `89c2541` antes de nuevos cambios en GitHub. Bitácora oficial [`docs/sesiones/2026-10-13-b2-l2-acl-http-real-validado.md`](sesiones/2026-10-13-b2-l2-acl-http-real-validado.md). Log original local `~/netlab360-bootstrap/evidencias/b2-l2-acl-http-20261013-191413.log`, **no subido**.

**S01 ACTUALIZADO A 58% TÉCNICO ESTIMADO** (+3 de 55, B2-L2 8/10); mantener issue #1/#30 abiertas por criterios integrales aún pendientes. Capturas **B2_L2_05/06/07** solicitadas/tomadas por convención, pero PNG no recibidos/inspeccionados ni versionados. Los 24 PNG originales auditados permanecen versionados. Importante no confundir HTTP inter-VLAN HQ con HTTP entre HQ-S1.

**PRÓXIMO SCRIPT VERSIONADO, NO EJECUTADO:** [`scripts/laboratorio/b2-l3-http-clientes-wan.sh`](../scripts/laboratorio/b2-l3-http-clientes-wan.sh), hace una sola secuencia automatizada `B2 precheck→up→cliente HQ real 10.70.10.10/32 en namespace→servidor Python HTTP S1 10.71.10.20/32 en namespace→HTTP WAN-P→fail y rutas bidireccionales wan-b→HTTP WAN-B→restore y wan-p→HTTP WAN-P→EXIT cleanup`. Los hosts se conectan a R-HQ/R-S1 **por enlaces veth P2P aislados 169.254.70/71 y rutas /32**, preservando las LAN dummy que anuncia OSPF: es HTTP WAN real pero **NO** significa que los hosts se hayan conectado físicamente al trunk 802.1Q ni que haya VLAN entre sedes. `trap EXIT` borra namespaces y servidores propios y después ejecuta `b2-dualwan-ospf.sh down`, revisa IP/tabla de rutas del host. Scripts nuevos GitHub están por delante de Ubuntu: requiere `git pull --ff-only origin main` y `bash -n` antes de probar.

**SIGUIENTE BLOQUE AGRUPADO:** 1) pull + sintaxis, precheck ningún contenedor ni `nl360-e2e-*` ni `estado-b2-dualwan`, red ens33/GW intactos; 2) ejecutar `bash scripts/laboratorio/b2-l3-http-clientes-wan.sh --snapshot-confirmado` UNA VEZ (puede tardar por OSPF ~60s); 3) capturas `B2_L3_01` (HTTP WAN-P), `B2_L3_02` (HTTP WAN-B), `B2_L3_03` (HTTP WAN-P restaurada), postcheck `B2_L3_04`; 4) exigir `HTTP_WAN_PRINCIPAL=OK`, `HTTP_WAN_RESPALDO=OK`, `HTTP_WAN_RESTAURADA=OK`, `RESULTADO_B2_L3_HTTP_WAN=0`. Cualquier fallo: NO repetir, verificar cleanup y enviar salida. No instalar paquetes ni modificar VMnet8/ens33, firewall o rutas del host. El script **no debe contarse como probado ni sumar puntos hasta ejecución observada**. Después dirigir esfuerzos a LACP/dual NIC e IaC, y documentación académica en paralelo por retraso semana 9.

---


## PUNTO MÁS RECIENTE — 13/10/2026 19:01 PANAMÁ | B2-L2 TRUNK/ISOLAMIENTO 802.1Q REAL APROBADO

**Previo a la próxima sesión en VM:** pull ff-only de nuevos commits GitHub de este turno. El usuario ejecutó **realmente** `bash scripts/laboratorio/b2-l2-trunk-8021q.sh --snapshot-confirmado`; resultados **`RESULTADO_SINTAXIS_TRUNK=0`**, `PRUEBA_TRUNK_VLAN110=OK` (3/3 ping), `PRUEBA_TRUNK_VLAN120=OK` (3/3), aislamientos negativos entre VLAN con prefijo on-link **0 recibidos/3 enviados** y mensajes `Destination Host Unreachable`, ping dentro VLAN110/120 conservó 2/2 cada, `B2_L2_TRUNK_Y_AISLAMIENTO=OK`; `RESULTADO_B2_L2_TRUNK=0` y `RESULTADO_EJECUCION_TRUNK=0`, `RED_GESTION_INTACTA=SI`. Postcheck a **19:01:44** Docker/netns vacíos, `ens33=192.168.47.40/24`, gateway `192.168.47.2`, 3 servicios activos, Git limpio respecto `main...origin/main` del momento. Log ORIGINAL local `~/netlab360-bootstrap/evidencias/b2-l2-trunk-20261013-190000.log`, no copiado al repo. **No repetir trunk aislado** salvo diagnóstico justificado.

**Matriz S01 actualizada a 55% técnico estimado** (+2 B2-L2, de 3/10 a 5/10). Sólo se acreditó VLAN trunk en **dos switches dentro de HQ**, no WAN intersedes, no ACL L3, no servicio HTTP. [Bitácora de prueba realmente superada](sesiones/2026-10-13-b2-l2-trunk-8021q-verificado-y-acl-preparada.md), matriz `docs/control/01-avance-s01.md`, issues #1/#30/#35/#42/#43 actualizadas.

**Nuevo script LISTO, PERO SIN EJECUTAR NI VALIDAR EN VM:** [`scripts/laboratorio/b2-l2-acl-http-real.sh`](../scripts/laboratorio/b2-l2-acl-http-real.sh). Crea exclusivamente namespaces con prefijo `nl360-acl`, switches VLAN110/120 unidos por trunk y router aislado con subinterfaces eth0.110/eth0.120, hosts 10.70.10.10 y 10.70.20.20 y dos servidores Python `HTTP 8080/8081`. Baseline demuestra que **ambos puertos responden antes de ACL**. Después nftables en **network namespace del router, nunca host**, permite TCP8080 y bloquea TCP8081, confirmado con curl y nft counters; cleanup via trap mata servidores en namespaces propios y retira solo recursos creados, comprueba ens33 y tabla host inalterados. Capturas **B2_L2_05** baseline, **B2_L2_06** ACL/negativa, **B2_L2_07** postcheck. **NO concede puntos adicionales hasta ejecución real**; si falla, no repetir. Esta prueba es **intra-HQ**, no convierte LAN de R-S1 ni prueba WAN HQ-S1. **Próxima integración** será cliente/servicio verdaderos atravesando WAN OSPF ya validada (no repetir solo por repetir failover).

**Próximas acciones agrupadas solicitadas por usuario:** pull ff-only; `bash -n scripts/laboratorio/b2-l2-acl-http-real.sh`, herramientas nft/curl, IPAM, precheck red, Docker/netns vacíos, confirmar no hay names `nl360-acl*`. Ejecutar **una sola vez** `bash scripts/laboratorio/b2-l2-acl-http-real.sh --snapshot-confirmado`; exigir `BASELINE_HTTP_8080=OK`, `BASELINE_HTTP_8081=OK`, `ACL_HTTP_8080_PERMITIDO=OK`, `SERVICIO_8081_EN_VLAN120=ACTIVO`, `ACL_HTTP_8081_DENEGADO=OK`, `RESULTADO_B2_L2_ACL_HTTP=0`. Postcheck Docker/netns vacíos, host intacto, Git limpio. Si falla, revisar log y residuo de namespace **sin tocar host firewall, ens33, VMnet8 ni gateway**. B2_L2_02/03/04 consideradas capturadas por usuario, PNG aún no recibidos/inspeccionados.

---


## ACCIÓN VIGENTE — 13/10/2026 18:51 PANAMÁ | PRECHECK B2-L2 OK; ENSAYO TRUNK VERSIONADO NO EJECUTADO

**Este bloque se añade al checkpoint del ciclo Prometheus 18:36, que continúa válido.** Usuario hizo pull a `6e6d500`; ejecutó precheck `scripts/validacion/precheck-b2-l2-trunk-acl.sh` con salida **`REQUERIDOS_FALTANTES=0`, `B2_L2_PREFLIGHT=OK`, `RESULTADO_PRECHECK_L2=0`** a 18:51:04. Herramientas `ip,bridge,nsenter,python3,ping,sudo,git` y `nftables v1.1.6` disponibles; Linux bridge módulo visible, `8021q` y `bonding` no visibles en sysfs, **no significa ausencia de soporte**. `ens33 192.168.47.40/24`, default GW `192.168.47.2`, Docker/netns vacíos, Git `main...origin/main` limpio en ese corte. Log local `~/netlab360-bootstrap/evidencias/b2-l2-precheck-20261013-185104.log`, no publicado.

**Nuevo script publicado después del último pull del usuario:** [`scripts/laboratorio/b2-l2-trunk-8021q.sh`](../scripts/laboratorio/b2-l2-trunk-8021q.sh) (commit `aceefee`). Despliega solo namespaces propios, dos switches **dentro de HQ**, VLAN110 usuarios `10.70.10/24`, VLAN120 servicios `10.70.20/24`, trunk 802.1Q con ambos VID tagged, puertos access untagged; pruebas de ping positivo por VLAN y aislamiento negativo sin confundir falta de ruta IP; cleanup automático exclusivo, comparaciones ens33/ruta protegidas. **NO EJECUTADO AÚN; no otorgar puntos adicionales ni afirmar capturas existentes.** Exige `--snapshot-confirmado`, snapshot anterior ya confirmado por operador. [Bitácora de precheck y plan](sesiones/2026-10-13-b2-l2-precheck-trunk-acl-y-plan-ensayo.md).

**PRÓXIMOS PASOS (varios de una sola vez):** pull ff-only, `bash -n` y grep script, `sudo -v`, comprobar namespaces prefijo `nl360-t` ausentes, red intacta, ejecutar **una sola vez** `bash scripts/laboratorio/b2-l2-trunk-8021q.sh --snapshot-confirmado`. Captura solicitada B2_L2_02 desde INICIO/FIN de trunk 110/120; B2_L2_03 desde INICIO/FIN aislamiento negativo + ping positivos; ejecutar postcheck Docker/netns/ens33/GW/git. Exigir `RESULTADO_B2_L2_TRUNK=0` antes de documentar prueba completa. Si falla, NO repetir, enviar error + `RESIDUO_NAMESPACE` y revisar. Después desarrollar ACL en namespace y cliente/servicio real sin tocar firewall del host.

**S01 todavía 53% estimado**; 47 puntos pendientes repartidos B1 2, B2L2 7, L3 1, LACP/dual-NIC 10, IaC 9, B3 5, IA 5, documentación 3, release/OVA 5. El bloque de documentación teórica puede desarrollarse en paralelo, pero aceptación S01 exige requisitos completos o aprobación docente de recorte (#36). No confundir semana académica 9 con semana S01 del repositorio.

---


## CHECKPOINT VIGENTE — 13/10/2026 18:36 PANAMÁ | PROMETHEUS ALERTAS FIRING/RESUELTAS, LABORATORIO LIMPIO

**SIGUIENTE PRECHECK YA VERSIONADO, AÚN NO EJECUTADO:** `scripts/validacion/precheck-b2-l2-trunk-acl.sh` (solo lectura) para capacidades `bridge`, `ip`, módulo 8021q/bonding, disponibilidad `nft`, IPAM/ens33 y recursos de Docker/netns. Luego diseñar/trabajar trunk 802.1Q + ACL + cliente real. **No se ha desplegado esta topología nueva ni hay evidencias nuevas de L2.**

**Este bloque prevalece sobre todas las notas anteriores que indican reglas no cargadas o puertos ocupados.** El usuario completó pasos 70–80 y compartió salida real de las tres terminales: **Prometheus 3.7.0 cargó tres reglas** después de generar glob absoluto en `scripts/observabilidad/ejecutar-prometheus-local.sh`; `/api/v1/rules` mostró 1 grupo, 3 reglas, scrape `up=1`, `B3_REGLAS_LISTAS=SI`, código0, evidencia **B3_11**. `b2-dualwan-ospf.sh up` obtuvo doble OSPF Full y ruta WAN-P (código0); `fail` conmutó a WAN-B (`RESULTADO_FAIL_PROMETHEUS=0`). A **18:33:35** Prometheus devolvió **`NETLAB360WANPrimaryDown=firing` (warning)** y **`NETLAB360WanBackupSelected=firing` (info)**; evidencia **B3_12**. A **18:34:09** `restore` retornó WAN-P (`RESULTADO_RESTORE_PROMETHEUS=0`); a 18:34:36 API `ALERTAS_WAN_ACTIVAS=0`, `ALERTAS_WAN_RESUELTAS=SI`, evidencia **B3_13**.

**Cierre confirmado:** `down` B2 código 0, exporter topology OFFLINE, Terminales 1 y 2 detenidas con Ctrl+C limpio. Postcheck **18:36:03** (**B3_14**) `PUERTO_9090_LIBRE:SI`, `PUERTO_9108_LIBRE:SI`, Docker sin contenedores, netns vacíos, `ens33 UP 192.168.47.40/24`, GW `192.168.47.2`, docker/ssh/open-vm-tools activos. `git status` `## main...origin/main` limpio a la hora de esa comprobación **antes** de nuevos commits de documentación. **No volver a ejecutar WAN-P fail/restore por segunda vez** para constatar Prometheus: está demostrado. No hay servicios de laboratorio que dejar corriendo según postcheck.

**Estado de capturas:** B3_05–B3_14 y B3_09_FINAL se presumen **tomadas** por regla del usuario, con resultados de consola del nuevo grupo B3_11–14 inspeccionados textualmente; **sus PNG todavía NO han sido enviados/auditados visualmente ni subidos**. Los 24 PNG originales de lotes 01/02 B1/B2/B3 sí fueron recibidos, visualmente auditados y físicamente publicados GitHub; no confundir conjuntos.

**Resultado y límites:** matriz [`docs/control/01-avance-s01.md`](control/01-avance-s01.md) ahora **53% técnico estimado** (B3 10/15) tras alertas reales. **No Alertmanager ni receptores/notificaciones**, ni dashboard NOC multisitio integral ni SLI/SLO formal. S01 issue #1 permanece ABIERTA; no afirmar aceptación 11/11. [Bitácora B3 Prometheus firing/recuperación](sesiones/2026-10-13-b3-prometheus-alertas-firing-y-resolucion-verificadas.md). [Plan de recuperación desde semana 9](control/02-plan-recuperacion-semana-09.md): prioridad siguiente **B2-L2 VLAN/trunk/ACL y cliente-servicio realmente extremo a extremo**, seguido de LACP/dual-NIC, IaC OpenTofu/Ansible, IA evaluada y entregables/release/OVA, con consulta docente en #36. Evitar seguir sobreoptimizando OSPF y Prometheus.

**Para retomar en Ubuntu:** `cd ~/proyectos/netlab360; GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main; git status --short --branch; sudo docker ps -a; sudo ip netns list; ip -4 -br addr show ens33; ip -4 route show default`. Verificar que los archivos `.gitignore`, scripts y docs nuevos bajaron. **NO** tocar `ens33`, VMnet8, default gateway, NetworkManager ni la red de administración. **No** ejecutar cierre/apagado automáticamente; solo si el usuario lo solicita. Entregar varios pasos de una vez por preferencia expresa del usuario.

---


## PUNTO MÁS RECIENTE — 13/10/2026 18:15 PANAMÁ | PROMETHEUS REAL SCRAPE OK, REGLAS AÚN NO CARGADAS

**PREVALECE SOBRE NOTAS DE 17:45:** Usuario envió salida de pasos 60–69. A 18:08:52 postcheck final `B3_09_FINAL` demostró **PUERTO_9108_LIBRE: SI**, Docker/netns vacíos, `ens33 192.168.47.40/24`, GW `192.168.47.2`, docker/ssh/open-vm-tools activos. `git pull` llevó a `a1390bb`, nueva `.gitignore` ignoró `__pycache__`, `GIT_SINCRONIZADO: SI` antes de los commits posteriores.

**PROMETHEUS REAL VERIFICADO:** `quay.io/prometheus/prometheus:v3.7.0` image digest `sha256:29c1e0b48ad816750245dea3d65ac3ce57dda30547e67b1e9a5176e2953cc4dc`; binarios `prometheus` y `promtool` 3.7.0 extraídos en `~/netlab360-bootstrap/prometheus/bin/`. `promtool check config` SUCCESS; `promtool check rules` SUCCESS, **3 reglas válidas de archivo**; script preparación código 0. Exporter Python local `127.0.0.1:9108` ejecutado en **Terminal 1 foreground** con `B3_TOPOLOGIA=OFFLINE` (correcto, sin routers); HTTP /metrics 200 por scraping cada 2 segundos. Prometheus local `127.0.0.1:9090` ejecutado en **Terminal 2 foreground**, TSDB arrancada y `Server is ready to receive web requests`. Terminal 3 `/-/healthy` OK y consulta Prometheus `up{job="netlab360-frr-live"}=1`, `netlab360_live_source_up=1`, datos insertados en TSDB. Evidencia `B3_10_Prometheus_Scrape_Real.png` 18:12:46 considerada tomada, **imagen NO recibida todavía para inspección visual**.

**BLOQUEO:** API Prometheus `/api/v1/rules` devolvió `{"groups":[]}` — aunque el YAML y 3 reglas son sintácticamente válidas, **NO hay reglas activas ni alertas firing**. El glob `servicios/observabilidad/prometheus/rules/*.yml` de config es relativo y podría no resolverse desde directorio de ejecución esperado. Se publicó **fix SOLO EN GITHUB, SIN EJECUTAR AÚN** en `scripts/observabilidad/ejecutar-prometheus-local.sh`: renderiza `~/netlab360-bootstrap/prometheus/prometheus-runtime.yml` con glob ABSOLUTO basado en repo, valida usando promtool y ejecuta Prometheus con esa config. Necesario **detener solo Prometheus en Terminal 2 con Ctrl+C**, mantener exporter Terminal 1 operando, `git pull --ff-only origin main` desde Terminal3, `bash -n` del script y verificar nuevo contenido; volver a arrancar Prometheus Terminal2 y consultar API `/api/v1/rules` con los **3 nombres de regla**, sino parar antes de ejecutar `up/fail/restore`. Comprobar `up=1` de nuevo.

**S01 = 50% técnico estimado** (B3 7/15 por Prometheus real y scrape, +2 desde 48%, NO por reglas). Fase 1 sigue abierta en semana 9; priorizar MVP/entregables y revisar viabilidad de alcance. Fuente [bitácora](sesiones/2026-10-13-b3-prometheus-scrape-real-sin-reglas.md), [matriz](control/01-avance-s01.md). Issues #1/#12/#15/#20/#21/#35 actualizadas. NO repetir prueba WAN anterior solo para validar scrape; cuando reglas cargadas, sí habrá un único nuevo failover controlado para demostrar *alerta real* `firing` y resolución. NO alterar VMnet8/ens33/rutas host, no abrir puertos 9090/9108 fuera de loopback, no instalar programas otra vez.

---


## ACTUALIZACIÓN MÁS RECIENTE — 13/10/2026 17:45 PANAMÁ | B3 LIVE WAN COMPLETADO, CIERRE DE PUERTOS PENDIENTE

**Falla real y recuperación observadas, NO repetir la topología B2:** prueba 17:38–17:45 reportada por usuario: `status` OSPF 2 vecinos Full, WAN-P UP; `fail` código 0, ruta WAN-B y eventos del exporter `WAN_PRIMARY_DOWN` + `WAN_ROUTE_CHANGED` a **17:39:33.189**. `restore` código 0, `WAN_PRIMARY_RESTORED` a **17:42:05.813** (aún FIB WAN-B) y FIB WAN-P `WAN_ROUTE_CHANGED` a **17:42:15.841**. Contadores down=1, restored=1, route_changed=2; `down` B2 con limpieza código0, `TOPOLOGY_STOPPED` 17:44:56; exporter reflejó `topology=offline`. Cinco eventos JSONL guardados localmente `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`; **no versionados físicamente**. [Bitácora completa](sesiones/2026-10-13-b3-live-ciclo-incidente-wan-verificado.md).

**Resultado crítico de postcheck:** captura B3_09 a 17:45:10 imprimió `PUERTO_9108_LIBRE: NO`, ya que exporter aún estaba activo; Docker/netns vacíos, host ens33 `192.168.47.40/24`, gateway `192.168.47.2` y servicios activos. PowerShell 3 seguía con túnel `ssh -N -L 9108:127.0.0.1:9108 netlab360` y errores repetidos `Connection refused` hacia destino; **primero terminar con Ctrl+C en PowerShell 3 y Terminal SSH 1 SI AÚN ESTÁN ACTIVAS, sin matar procesos al azar**, luego comprobar con `ss` puerto 9108 libre. Captura adicional **B3_09_Postcheck_Telemetria_Viva_Final.png** solo consulta read-only. B3_05–B3_09 se asumen tomadas según usuario, **sus PNG aún no están recibidos/inspeccionados**, a diferencia de los 24 PNG auditados de B1/B2/B3 anterior.

**Git local sincronizado en commit `2c468d1` pero `git status` NO limpio** por `?? servicios/observabilidad/__pycache__/` y `?? tests/__pycache__/` creados por Python. NUEVA [`.gitignore`](../.gitignore) en GitHub para excluirlos; `git pull --ff-only origin main` debe dejarlos ignorados, sin `reset --hard`. **S01 actualizado a 48% estimado** (B3 5/15 por eventos live, Prometheus NO realizado; antes 45%).

**PRÓXIMA ETAPA VERSIONADA PERO NO EJECUTADA:** [plan Prometheus real](operaciones/plan-b3-prometheus-local.md), archivos `servicios/observabilidad/prometheus/prometheus.yml`, `rules/wan-alerts.yml`, `scripts/observabilidad/preparar-prometheus-local.sh` y `ejecutar-prometheus-local.sh`. Estrategia segura: extraer binarios de imagen versionada `quay.io/prometheus/prometheus:v3.7.0` desde contenedor temporal `--network none`, **no se ha comprobado todavía la existencia de esa etiqueta en Ubuntu**, ejecutar Prometheus como proceso de usuario en `127.0.0.1:9090` y exporter habitual en `127.0.0.1:9108`; sin alterar host NIC/gateway, no usar Docker host network ni publicar puertos de VMware. El objetivo es demostrar **scrape real/TSDB y reglas cargadas**; luego un nuevo ensayo de alerta real con WAN-P DOWN/UP si procede. No atribuir Prometheus instalado ni alerta firing antes de pruebas.

**Issues #1/#12/#15/#20/#21/#35/#43** actualizadas; S01 sigue abierta. Evitar nuevos fallos mediante preflight, separación clara de terminales y verificación de puertos.

---


## REANUDACIÓN MÁS RECIENTE — 13/10/2026 17:31 PANAMÁ | EXPORTER B3 LIVE OK; TERMINAL 1 EN ESPERA NORMAL

**Más nuevo que diagnósticos antiguos de preflight:** usuario envió resultados reales 17:29–17:31: dos FRR `nl360-b2-r-hq` y `nl360-b2-r-s1` activos, marcador `netlab360-b2-dualwan`, red ens33 `192.168.47.40/24` y gateway `192.168.47.2` intactos. Git pull a `c4f3d47` limpio antes del commit de esta bitácora; `ast.parse` y `bash -n` OK; **5/5 tests de regresión OK**; auditoría de dependencias **0 programas requeridos ausentes** (Docker 29.9, Compose 5.6, FRR 10.7.1, Python y PyYAML, OpenTofu, Ansible, gh, Node/NPM verificados). Fallo de parseo Docker minúsculas YA REPARADO Y VALIDADO realmente.

**Terminal SSH 1**: `live_exporter.py --check` devolvió `B3_LIVE_PREFLIGHT=OK`, `B3_TOPOLOGIA=ACTIVE`, código 0. Luego `python3 servicios/observabilidad/live_exporter.py --serve` se inició correctamente y **SIGUE corriendo en primer plano como servidor** en `127.0.0.1:9108`; esto es normal, **NO Ctrl+C hasta finalizar las pruebas**, no iniciar otro servidor. A ~17:31:26 respondió HTTP `/healthz` 200, `/api/v1/live` 200, `/metrics` 200; `fresh=true`, `live_monitoring=true`, HQ=1, S1=1, `wan_primary_admin_up=1`, `selected_link=wan-p`, `source_up=1`, eventos down/restored/route_changed=0 **ANTES** de generar falla. **No hay todavía evento WAN real en las últimas salidas recibidas**.

**PRÓXIMA ACCIÓN INMEDIATA SIN REDESPLEGAR B2:** Terminal SSH 2: `sudo -v`, `bash scripts/laboratorio/b2-dualwan-ospf.sh status`, `curl` a live con WAN-P UP, captura **B3_05**, un único `bash ... fail`, aguardar ~4s, consultar `/api/v1/live` y `/api/v1/events` y capturar **B3_06** (down y wan-b). Opcional túnel SSH desde Windows `ssh -N -L 9108:127.0.0.1:9108 netlab360` para screenshot HTML **B3_08**. `bash ... restore`, aguardar 4s, comprobar WAN-P UP/wan-p y eventos **B3_07**. `bash ... down` debe retirar solo recursos B2 válidos; exporter verá topología OFFLINE; detener túnel y Terminal1 con Ctrl+C, puerto 9108 libre, Docker/netns vacíos y ens33/GW intactos, captura **B3_09**. Si fail/restore fallan, diagnosticar y restaurar/retirar sin repetir up ni crear recursos. **No apagar con routers activos**.

**Fuente documentada:** [bitácora de preflight y baseline live](sesiones/2026-10-13-b3-live-precheck-y-baseline-verificada.md). Issues #1/#12/#15/#20/#21 actualizadas con el hito real; **S01 45% provisional**, sin incrementar hasta comprobar fail/restore y limpieza. NO Prometheus scraper ni Alertmanager instalados/validados. El usuario quiere **varios pasos en un mensaje, sin «seguimos» intermedio**, y considera capturas tomadas salvo aviso; no afirmar revisión visual o subida de futuras PNG hasta recibirlas. **GitHub remoto avanza con esta bitácora y checkpoints, pero no hacer pull mientras haya trabajos a medio ejecutar si se desea reducir interferencia; sincronizar al finalizar.**

---


## ACTUALIZACIÓN PRIORITARIA — 2026-10-13 ~16:40 PANAMÁ | B3 LIVE PRECHECK FALLÓ POR BUG, NO FALTAN PROGRAMAS

**Último usuario aportó logs completos de Terminales 1–3; este bloque prevalece sobre anteriores promesas de exporter live.** `git pull` llevó VM a `9defd03` antes de nuevas correcciones. `ast.parse` de `servicios/observabilidad/live_exporter.py` era OK, pero `python3 ... --check` devolvió **`B3_LIVE_PREFLIGHT=ERROR`, `B3_TOPOLOGIA=DEGRADED`, rc=4** al interpretar Docker `error: no such object: nl360-b2-r-hq` en minúsculas como fallo real, cuando era el estado esperado de routers apagados. El código comparaba `"No such object"` con mayúscula. Por el error, `--serve` no abrió puerto `9108`, y `curl: (7) Failed to connect` / túnel Windows `channel ... Connection refused` son consecuencias, **NO falta de programas ni paquetes**.

A las **16:40:11** el usuario ejecutó realmente **un precheck B2 exitoso y un `up --snapshot-confirmado` EXITOSO**: `OSPF_DUAL_FULL: SI`, **dos adyacencias Full por router**, ruta a LAN S1 vía `wan-p`, `RESULTADO_UP_B3=0`. A las **16:40:39** ejecutó otro precheck/`up`, que devolvió `ERROR: recursos previos B2` / RC=3 porque YA había routers desplegados; esta negativa **ES CORRECTA**. **No consta `down` ni `fail/restore` posterior**: NO ejecutar `up` de nuevo ni destruir redes a ciegas; primero verificar `sudo docker ps -a --filter name=nl360-b2-`, marcador `~/netlab360-bootstrap/estado-b2-dualwan/.nl360-owner`, `bash scripts/laboratorio/b2-dualwan-ospf.sh status` solo si marker válido, ens33 y rutas. Evitar túnel Windows hasta tener `ss` mostrando LISTEN en 9108. `sudo` rechazó un primer intento de contraseña en Terminal 2; no representa software faltante.

**Fix YA EN GITHUB, AÚN NO PROBADO POR USUARIO:** [`servicios/observabilidad/live_exporter.py`](../servicios/observabilidad/live_exporter.py) compara salida `.lower()` y distingue contenedor ausente (OFFLINE) de error real de permiso/daemon (DEGRADED); [pruebas unitarias](../tests/test_b3_live_exporter.py) con 5 casos; [auditoría preventiva solo lectura](../scripts/validacion/auditar-dependencias-netlab360.sh); [matriz de herramientas](operaciones/matriz-dependencias-s01.md); [bitácora de fallos y guardas](sesiones/2026-10-13-b3-exporter-preflight-docker-case.md). Primer paso: pull seguro + `bash -n`, `python3 -m unittest discover -s tests -p test_b3_live_exporter.py -v`, `sudo -v`, `bash scripts/validacion/auditar-dependencias-netlab360.sh`, `python3 servicios/observabilidad/live_exporter.py --check`. **No subir puntos del S01 45% solo por fix.**

**Captura B3_05 de intento fallido:** terminal mostró `curl` al puerto sin servidor. Si el usuario la capturó, registrar como `B3_05_Diagnostico_Exporter_No_Escucha.png` y no como éxito. **NO pedir repetir despliegue para la captura**; completar ensayos B3 live con el nuevo código y capturas de éxito después. Git del usuario estaba limpio `9defd03` a las 16:40; tras commits nuevos remoto está por delante, requiere pull.

---


## CHECKPOINT ACTUAL — 13/10/2026 16:26+, EVIDENCIAS COMPLETADAS Y EXPORTER B3 LIVE PREPARADO

**PREVALECE SOBRE LAS NOTAS ANTERIORES QUE DECIAN QUE LOS PNG NO ESTABAN SUBIDOS.**
- Usuario verificó y publicó correctamente en GitHub **19 PNG B1/B2** más manifiesto (`evidencias/capturas/B1_B2_lote01`), commit **[`d62d33b`](https://github.com/recm0708/netlab360/commit/d62d33b3dd5876a795ca2dadc47b2a1474c86104)**, y **5 PNG B3** más manifiesto (`evidencias/capturas/B3_lote02`), commit **[`a21b8f8`](https://github.com/recm0708/netlab360/commit/a21b8f8d1b76c2f7cebfd657213bc4c7c7b21bc2)**. 24 archivos PNG realmente auditados y físicamente en `main`. SHA256 internos correctos, comprobación GitHub de commits confirmó **19 y 5 PNG**. Git del usuario a 16:26:20 `a21b8f8`, `## main...origin/main` limpio, `GIT_SINCRONIZADO: SI`. El problema original de identidad del autor fue corregido **en scope local del repo**, rebase/push sin problemas. Lote 01 y lote 02 cerrados en cuanto a importación; issue #43 ABIERTA para nuevas fases y la imagen B3_04_FINAL.
- Postcheck real `B3_04_FINAL` a las 16:25:50: `PUERTO_8765_LIBRE: SI`, contenedores/netns vacíos, `ens33 UP 192.168.47.40/24`, default `192.168.47.2`, servicios docker/ssh/open-vm-tools activos. Captura B3_04_FINAL considerada tomada por instrucción del usuario, pero **no recibida todavía como PNG**, no está subida.
- **S01 45% estimado y 55% pendiente** (matriz `docs/control/01-avance-s01.md`); API y dashboard **HISTÓRICOS** funcionales y auditados, pero SIN Prometheus, exporter live o alerta WAN en NOC. Issues #1/#12/#15/#20/#21 ABIERTAS.
- **NUEVO ARTEFACTO SOLO VERSIONADO, NO EJECUTADO:** [`servicios/observabilidad/live_exporter.py`](../servicios/observabilidad/live_exporter.py) y [protocolo](../servicios/observabilidad/README.md). Exporter Python de solo lectura `127.0.0.1:9108` consulta Docker/FRR mediante `sudo -n docker inspect`, `nsenter ip`, FIB WAN-P/WAN-B; API `/api/v1/live`, `/api/v1/events`, `/metrics`, `/healthz`, dashboard dinámico `/`; eventos por cambios reales `WAN_PRIMARY_DOWN`, `WAN_PRIMARY_RESTORED`, `WAN_ROUTE_CHANGED` guardados localmente en `~/netlab360-bootstrap/evidencias/b3-live/b3-wan-live-events.jsonl`. **TODAVÍA NO VALIDADO EN UBUNTU, ni Prometheus real**. Se debe hacer `git pull --ff-only`, `ast.parse` y `sudo -v` misma terminal, `python3 ... --check`, y ejecutar foreground. Solo después, en otra terminal, `bash scripts/laboratorio/b2-dualwan-ospf.sh up --snapshot-confirmado` y secuencia `status/fail/restore/down` **si hay aprobación precheck/Full**, consultando live API y /events tras cada paso. Desplegar WAN únicamente en `--network none` y never alterar VMnet8/ens33. Capturas planificadas B3_05–B3_09. No repetir ensayos anteriores salvo que esta prueba viva los requiera.
- **Advertencia de precisión:** cualquier muestra de WAN es temporal/discreta; no demostrar disponibilidad total ni segundos exactos de convergencia. `/metrics` de exporter no acredita por sí solo scrape de Prometheus, Alertmanager ni alarmas de producción. Si no hay routers, `B3_TOPOLOGIA=OFFLINE` es correcto. El exporter requiere `sudo -n -v` exitoso tras `sudo -v`; sin ello se detiene. No dar por probada implementación hasta recibir salidas reales. No aumentar el 45% solo por crear archivos.
- **IMPORTANTE SOBRE SINCRONIZACIÓN:** usuario en Ubuntu acabó en `a21b8f8` **antes** de nuevos commits de GitHub de esta respuesta: para bajar live_exporter y docs nuevos, usar `git pull --ff-only origin main`; no asumir que el checkout actual contiene script.

---


## PUNTO VIGENTE — 13/10/2026 DESPUÉS DE 16:09 | 24 PNG AUDITADOS; GIT COMMIT BINARIOS PENDIENTE

**Este bloque tiene prioridad sobre anotaciones antiguas dentro del archivo.** Se recibieron **19 PNG B1/B2** y **5 PNG B3**, y se inspeccionaron visualmente los **24 archivos reales**. Inventarios con SHA-256: [lote 01](evidencias/01-auditoria-visual-b1-b2-2026-10-13.md), [lote 02](evidencias/02-auditoria-visual-b3-2026-10-13.md). B3_03 partes 1/2 prueban interfaz NOC **HISTÓRICA** visible desde Windows mediante túnel SSH con 76/76 datos CSV y tabla FIB; B3_02 prueba JSON/metrics. **No confundir prototipo histórico con Prometheus real, exporter live, eventos o alarmas operativas.** S01 ahora **45% técnico estimado** (+2 puntos B3 prototipo validado) y 55% restante; issue #1 y B3 issues abiertas.

**B3_04 evidencia auténtica pero INTERMEDIA:** a 15:52:24 `PUERTO_8765_LIBRE: NO`; a las **16:09:58 el usuario aportó nueva salida terminal `PUERTO_8765_LIBRE: SI`**, con Docker y netns vacíos y ens33 192.168.47.40/24 GW 192.168.47.2 intactos. Ese estado posterior corrige el pendiente técnico de puerto, pero no hay PNG de la consulta posterior; opcional nueva captura solo de lectura `B3_04_Postcheck_Servicio_NOC_Final.png`. La tercera PowerShell probablemente mantiene túnel Windows `ssh -N -L 8765:127.0.0.1:8765 netlab360`; cerrar con Ctrl+C en dicha PowerShell, sin matar procesos de Ubuntu.

**Bloqueo Git REPRODUCIDO POR USUARIO:** el ZIP B1/B2 se transfirió, SHA-256 ZIP e internos OK, `CAPTURAS_VERIFICADAS:19`; se hizo `git add evidencias/capturas/B1_B2_lote01`, pero `git commit` falló `Identidad del autor desconocido` (sin `user.name/user.email`). El `git push` siguiente imprimió `Everything up-to-date`: **NINGUNO de esos PNG está commiteado ni subido aún**. `git status` muestra 20 archivos staged (19 imágenes + MANIFIESTO_SHA256.csv). **Siguiente paso:** `git config --local user.name "recm0708"`, `git config --local user.email "220997176+recm0708@users.noreply.github.com"` (identidad noreply derivada de cuenta autenticada); comprobar `git diff --cached --stat`, `git commit`, luego `git fetch origin main; git rebase origin/main; git push origin main`, verificar repo remoto. No `reset --hard`, no `push --force`. Si rebase falla, detenerse y reportar salida; no resolver a ciegas.

**Lote B3 pendiente de transferencia:** se preparó ZIP `NETLAB360_Evidencias_Oficiales_B3_Lote02_2026-10-13.zip`, 5 PNG sin modificar, SHA256 ZIP `747edb1eeee115e9bcbd68c64d50c043692b0015d76781416fd74da13921695e`, CSV interno con `canonico` + `sha256`, carpeta `capturas/`. Tras pasar ZIP a Ubuntu, validarlo antes de extraer a `evidencias/capturas/B3_lote02/` y hacer un segundo commit/push. NO declarar binarios publicados hasta comprobar los commits reales. Issue #43 ABIERTA, no repetir experimentos B2.

---


## ACTUALIZACIÓN PRIORITARIA — 13/10/2026 (DESPUÉS DE 15:52) | LOTE 01 DE 19 PNG AUDITADO; API B3 PROBADA, POSTCHECK PENDIENTE

**ESTA SECCIÓN PREVALECE SOBRE LAS MENCIONES HISTÓRICAS "CAPTURAS SUPUESTAS" EN DOCUMENTOS ANTERIORES.**
- **Lote 01 de 19 capturas B1/B2:** archivos **realmente recibidos e inspeccionados visualmente**. Hay registro oficial con nombres canónicos, clasificación de éxito/diagnóstico, observaciones y 19 SHA256 en [`docs/evidencias/01-auditoria-visual-b1-b2-2026-10-13.md`](evidencias/01-auditoria-visual-b1-b2-2026-10-13.md). La issue #43 está actualizada; sigue ABIERTA para otros lotes e importación de bytes PNG al repositorio. Los **PNG aún NO están físicamente subidos al repo**, pero se preparó un ZIP con los 19 sin alterar sus píxeles, los nombres normalizados, manifiesto CSV y registro. SHA256 ZIP `a81a6ceaf8daace88f740d288327231ea6818bac80241d0017d5ca32438bef66`. En el ZIP `B2_06_Arranque_FRR_V2_Exitoso.png` → `B2_06_Diagnostico_FRR_V2_Permisos.png` (resultado original smoke v2=2) y `B2_16_Diagnostico_Convergencia.png` → `B2_16_Medicion_Continua_Convergencia.png` (76/76 muestras y cleanup OK). B2_L2_01, B2_15, B2_16 tienen notas de encuadre; NO repetir ensayo solo por ese detalle.
- **B3 API realmente probada** por usuario (salida de 3 terminales a 15:48–15:52): `B3_SINTAXIS: OK`, `--check` código0 y 76 muestras, `python3 servicios/noc-historico/app.py --serve` escuchó en `127.0.0.1:8765`. `GET /healthz`, `GET /api/v1/baseline`, `GET /metrics`, `GET /` todos **200**, URL inexistente **404**, POST **405**. `/healthz` dice `historical`, `live_monitoring:false`; no confundir con exporter actual, Prometheus desplegado, dashboard de incidente real ni alarma. [Bitácora](sesiones/2026-10-13-b3-api-noc-historico-probada.md). Túnel `ssh -N -L 8765:127.0.0.1:8765 netlab360` iniciado, **imagen de navegador B3_03 todavía NO enviada para validación visual**.
- **PENDIENTE OPERATIVO INMEDIATO:** La salida de B3_04 a las 15:52:24 mostraba **`PUERTO_8765_LIBRE: NO`**, sin salida de Ctrl+C ni `B3_SERVIDOR_DETENIDO=SI`. Detener túnel PowerShell (Ctrl+C), detener Python en Terminal SSH 1 (Ctrl+C), verificar con `ss -H -ltn '( sport = :8765 )'` que puerto no quede ocupado. NO cerrar el postcheck B3 antes de salida de `PUERTO_8765_LIBRE: SI`; no matar procesos ajenos.
- **S01 ~43% provisional**, pendiente de reevaluación tras cierre, evidencia visual de UI y siguientes controles B3; issues #1, #12, #15, #20, #21, #35, #42, #43 ABIERTAS. Git local verificado en `07c2731` **antes de nuevos commits remotos de auditoría**. Hace falta `git pull --ff-only origin main` cuando no haya cambios locales; no repetir smoke FRR/OSPF/ICMP de B2.
- **Próxima incorporación de PNG:** transferir ZIP desde el chat a Windows y Ubuntu, verificar SHA256, extraer en carpeta de evidencias dentro de repositorio, `git add/commit/push` solo tras inspección. No afirmar subida GitHub sin verificar commit real. El usuario enviará las capturas restantes para auditar una segunda tanda; no volver a cuestionar la existencia de las 19 del lote 01.

---


## PUNTO DE REANUDACIÓN ACTUAL — 2026-10-13 15:29 PANAMÁ | B3-01 DATOS OK; API NOC NO PROBADA

**PREVALECE SOBRE LOS REGISTROS DE LAS 11:52 O ANTERIORES:** el usuario volvió a encender `NETLAB360-Ubuntu-Desktop`; SSH `netlab360-lab` OK, Ubuntu 26.04.1 kernel 7.0.0-38; `ens33 UP 192.168.47.40/24`, GW `192.168.47.2` inalterados; servicios docker/ssh/open-vm-tools activos, Docker/netns vacíos; raíz 9% ocupada, memoria disponible 13Gi; APT upgrade/autoclean 0 paquetes, dpkg audit limpio, no reboot. `git pull --ff-only` a `c53f0a6`, estado Git limpio/sincronizado **ANTES DE LOS NUEVOS COMMITS DE ESTA RESPUESTA**.

**B3-01 RESULTADO REAL COMPROBADO:** CSV de `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.csv` existe, **76 filas/76 recibidas/0 pérdidas**, `CSV_INTEGRIDAD: OK`. Se ejecutó el generador de línea base y dio **`B3_ANALISIS_RETROSPECTIVO=OK`**; produjo realmente `~/netlab360-bootstrap/evidencias/b3-linea-base/b3-resumen-convergencia.json` (1.3 KiB), `b3-metricas-retrospectivas.prom` (~653 B). Fases: normal 14, cambio_respaldo 1, respaldo 16, cambio_principal 29, restaurada 16. Rutas FIB normal WAN-P, respaldo WAN-B, retorno wan-b:27/wan-p:2, restaurada WAN-P. `python3 -m json.tool` y formato Prom revisados. Captura **`B3_01_Linea_Base_Observabilidad_ICMP.png`** a 15:28 considerada tomada, aún NO auditada visualmente/subida (#43).

**Nuevo componente versionado, TODAVÍA NO EJECUTADO EN VM:** `servicios/noc-historico/app.py` y [su manual](../servicios/noc-historico/README.md). Python biblioteca estándar, `--check`, `--serve` solamente `127.0.0.1:8765`, HTML con banner **HISTÓRICO / NO EN VIVO**, API `/api/v1/baseline`, salud `/healthz` y `/metrics` de exposición estática. No es Prometheus instalado ni telemetría dinámica. Siguiente acción: `git pull --ff-only`, `ast.parse`, `--check`, ejecutar servidor en foreground de primera terminal SSH, `curl` desde segunda terminal, túnel Windows `ssh -N -L 8765:127.0.0.1:8765 netlab360` para comprobar panel, Ctrl+C túnel/servidor y postcheck. **No declarar API funcional hasta recibir resultados reales**.

**GitHub:** nueva [bitácora B3](sesiones/2026-10-13-b3-linea-base-retrospectiva-validada.md), issues #1/#12/#15/#20/#21/#35/#43 actualizadas, todas abiertas. S01 **43% estimado**, sin puntos B3 adicionales hasta probar aplicación. No reejecutar B2 FRR/ping por costumbre; no modificar ens33/VMnet8, no subir credenciales, logs CSV ni PNG sin revisar y permiso. Evidencias nuevas al probar app: B3_02 API y métricas históricas; B3_03 panel NOC histórico, indicadas en manual. **La línea base NO refleja datos en vivo ni alarma real**.

---


## ACTUALIZACIÓN DEFINITIVA DEL ENSAYO — 13/10/2026 11:52 | MEDICIÓN REAL TERMINADA

**El mensaje anterior de que el ensayo está “NO EJECUTADO” es histórico.** El usuario SÍ ejecutó `scripts/laboratorio/b2-dualwan-medicion-continua.py --snapshot-confirmado` entre 11:51:41–11:52:40 Panamá; `RESULTADO_EJECUCION_CONVERGENCIA=0`. El nuevo registro [2026-10-13-b2-convergencia-icmp-continuo-verificada.md](sesiones/2026-10-13-b2-convergencia-icmp-continuo-verificada.md) es la referencia autorizada:
- `up` OSPF dual Full correcto, 14/14 muestras ICMP normal por WAN-P; en el corte 1/1 muestra ICMP en respaldo; 16/16 estable por WAN-B; durante retorno 29/29 muestras ICMP (cambio WAN-B→WAN-P en muestra #59); y 16/16 final por WAN-P. **76/76 muestras correctas, 0 pérdidas observadas**. Origen HQ LAN dummy `10.70.10.1`→destino LAN dummy S1 `10.71.10.1`.
- Primera observación FIB `wan-b` **0.186 s** después del inicio de acción de falla; primera observación del regreso `wan-p` **10.147 s** después de acción de restauración. Intervalo muestreo ~0.37s. **NO son segundos exactos de convergencia FRR ni prometen cero pérdidas fuera de las ventanas muestreadas.**
- `down` código 0, `LIMPIEZA_FINAL=OK`, `CONTENEDORES_B2_RESIDUALES=0`, host protegido, postcheck Docker/netns vacíos y `ens33` con GW intactos. Archivo local `~/netlab360-bootstrap/evidencias/17-b2-convergencia-20261013-115141.log` + `.csv` (~76 filas); PNG `B2_16_Medicion_Continua_Convergencia.png` asumido tomado y pendiente auditoría #43.
- **S01 nuevo avance estimado 43/100**, antes 42/100; +1 punto B2-L3 por observación de transición, total 17/18 de B2-L3, quedan clientes y servicios finales. Issues #1, #12, #42, #43, #35 permanecen abiertas. No aumentar % solamente por documentación.
- **USUARIO SOLICITÓ CIERRE INMEDIATO (SIN ESPERAR A LAS 12:00)**: detener pruebas, traer commits GitHub a Ubuntu con `git pull --ff-only`, verificar hashes HEAD/origin/main, git limpio, Docker/netns vacíos, ens33/GW/servicios OK; `sync; sudo systemctl poweroff`, esperar VMware Powered Off y apagar Windows. Apagado todavía NO confirmado. No empezar nuevos ensayos.
---

## NUEVO ENSAYO PREPARADO — 13/10/2026 ~11:46 | TODAVÍA NO EJECUTADO

**No sustituye el último hito real de 11:24:** el laboratorio dual-WAN con 30/30 ICMP entre LAN simuladas SÍ fue probado y limpiado. Aún **NO se ha medido** la pérdida durante la transición.

- Se creó `scripts/laboratorio/b2-dualwan-medicion-continua.py` que automatiza el ensayo en un solo proceso: `precheck` / `up`, lanza un hilo para ping `HQ 10.70.10.1 → S1 10.71.10.1` y consulta FIB, espera baseline, activa `fail`, observa respaldo, activa `restore`, observa retorno y realiza `down` en `finally`. Genera `17-b2-convergencia-*.log` y `17-b2-convergencia-*.csv` en `~/netlab360-bootstrap/evidencias/`. Los CSV no se suben automáticamente. **Script no validado ni ejecutado en VM todavía**.
- Antes de ejecutar, el usuario debe traer nuevos commits `git pull --ff-only`, comprobar sintaxis Python vía `python3 -c "import ast,pathlib; ast.parse(pathlib.Path('scripts/laboratorio/b2-dualwan-medicion-continua.py').read_text())"`, revisar script y precheck; ejecutar **solo una vez** con `python3 scripts/laboratorio/b2-dualwan-medicion-continua.py --snapshot-confirmado` si hora Panamá **anterior a 11:53** el 13/10, para dejar 12:00–12:15 libre para cierre.
- Seguridad: flujo con `--network none` usando scripts previos, no altera `ens33`; al terminar verificar `sudo docker ps -a`, `sudo ip netns list`, `ip -4 -br addr show ens33`, gateway y servicios. Ante error de cleanup, **NO apagar con recursos residuales**, evaluar logs y down.
- El ensayo contempla intervalos y sondeos discretos; el primer cambio de FIB detectado es una **aproximación limitada por sondeo**, no el tiempo exacto de convergencia OSPF; valores serán desconocidos hasta salida.
- Si la prueba no termina con suficiente margen o hay dudas, **no ejecutarla** hoy: el hito de ICMP de tres fases ya está preservado, y el script queda listo para próximo arranque.

---


**Última comprobación del usuario:** **2026-10-13 11:24:09, América/Panamá**.  
**Estado real observado:** **B2-L3 DUAL-WAN y tráfico ICMP bidireccional verificados, topología retirada correctamente.**  
**Fase general:** S01 **ABIERTA, 42% estimado y documentado** — no es nota oficial.  
**Plan del usuario:** debe salir y **apagar VM Ubuntu y Windows a más tardar 12:15 p. m. del 13/10/2026**. **A las 12:00 dejar de iniciar pruebas y comenzar el cierre GitHub/postcheck**. El apagado **NO está confirmado** hasta que el usuario lo ejecute.

> Si una conversación se corta, **leer ESTE archivo primero**, luego `docs/00-estado-y-continuidad.md`, `docs/control/01-avance-s01.md`, issues [#1](https://github.com/recm0708/netlab360/issues/1), [#42](https://github.com/recm0708/netlab360/issues/42), [#12](https://github.com/recm0708/netlab360/issues/12), [#43](https://github.com/recm0708/netlab360/issues/43). Los apartados cronológicos antiguos que dicen “FRR no ejecutado” o “ping pendiente” son históricos y han quedado superados.

## Infraestructura esencial que NO debe modificarse

- Host Windows 11 / VMware Workstation Pro 26.0.1; VM `NETLAB360-Ubuntu-Desktop`, hostname `netlab360-lab`, cuenta Ubuntu `rc-aa-ec`; acceso Windows: `ssh netlab360` con clave Ed25519 y passphrase local.
- Ubuntu Desktop **26.04.1 LTS**, kernel `7.0.0-38-generic`, 8 vCPU, 16 GB RAM, disco 160 GB.
- NIC de administración **`ens33=192.168.47.40/24`, default `192.168.47.2`, VMware VMnet8 NAT**. NO cambiar ens33, default route, NetworkManager, firewall host ni redes existentes Docker.
- Docker 29.9.0, Compose 5.6.0, FRRouting 10.7.1, Python 3.14, OpenTofu 1.13.1, Ansible 2.20.1, Node 24, GitHub CLI autenticado.
- Snapshot VMware **`NETLAB360-BASE-HERRAMIENTAS`** fue confirmado por el usuario. No solicitar ni regenerar el snapshot por costumbre. Nunca publicar tokens GitHub ni `~/.config/gh/hosts.yml`, clave SSH privada u OVA sin sanitizar.
- Git privado [`recm0708/netlab360`](https://github.com/recm0708/netlab360), checkout local `~/proyectos/netlab360`, rama `main`. Tras las actualizaciones remotas actuales, **debe ejecutarse un nuevo `git pull --ff-only` en Ubuntu**; `## main...origin/main` del usuario correspondía al checkout anterior a estos commits de documentación. No declarar sincronización local posterior sin salida.

## Qué quedó confirmado (no repetir salvo necesidad concreta)

1. Base Ubuntu y mantenimiento preventivo 13/10 10:47 OK: `apt update` sin paquetes pendientes, `dpkg --audit` vacío, no reboot-required; docker, ssh, open-vm-tools activos.
2. B1 IPAM `inventario/ipam/topologia-b1.yaml`: validación correcta; 3 sedes, 9 VLAN, 2 WAN previstas; todavía `draft`.
3. B2-L2: VLAN 110 conectividad, aislamiento VLAN 120 y recuperación (log previo).
4. FRRouting v5 en contenedor aislado: `FRR_MOUNT_READABLE: SI`, `FRR_DAEMONS_ACTIVOS: SI`, `OSPF_CONTROL_PLANE: OK`, `RESULTADO_SMOKE_FRR_V5=0`. **No repetir ensayos fallidos v1–v4**.
5. **B2-L3 doble WAN — primer ensayo 13/10 11:03–11:11:** script `scripts/laboratorio/b2-dualwan-ospf.sh` con `up/status/fail/restore/down`. Dos routers Docker `--network none` `nl360-b2-r-hq`/`nl360-b2-r-s1`; WAN primaria `10.78.0.0/30`, costo10, backup `10.78.0.4/30`, costo100; loopbacks `10.79.0.1/.2`, LAN dummy HQ `10.70.10.1/24` y S1 `10.71.10.1/24`. **Dos vecinos OSPF Full por router**, FIB normal `via 10.78.0.2 dev wan-p`, failover `via 10.78.0.6 dev wan-b`, retorno `wan-p`, códigos up/status/fail/restore/down=0. Logs `15-b2-dualwan-*.log`; bitácora `docs/sesiones/2026-10-13-b2-dualwan-ospf-failover-resultado.md`.
6. **B2-L3 tráfico ICMP de LAN — segundo ensayo 13/10 11:22–11:24:** script `scripts/laboratorio/b2-dualwan-ping-lan.sh`:
   - NORMAL, ruta `wan-p` simétrica: 5/5 HQ→S1 + 5/5 S1→HQ, **0% pérdida**.
   - RESPALDO tras `fail`, ruta `wan-b` simétrica: 5/5 + 5/5, **0% pérdida**.
   - RESTAURADA tras `restore`, ruta `wan-p` simétrica: 5/5 + 5/5, **0% pérdida**.
   - **30/30 ICMP** entre **IPs dummy de los routers** en tres estados, *después de estabilizar cada fase*, no tráfico continuo durante instante de falla. `RESULTADO_PING_LAN_normal/respaldo/restaurada=0`. `fail=0`, `restore=0`; `RESULTADO_DOWN=0`, `RESULTADO_B2_LIMPIEZA=0`. `sudo docker ps -a` y `sudo ip netns list` vacíos, `ens33` y GW intactos, servicios activos; Git limpio antes de nuevos commits. Bitácora `docs/sesiones/2026-10-13-b2-lan-icmp-tres-estados-verificado.md`.

**Logs originales LOCALES, no subidos automáticamente a GitHub:**
```text
~/netlab360-bootstrap/evidencias/15-b2-dualwan-precheck-20261013-112221.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-up-20261013-112226.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-normal-20261013-112307.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-fail-20261013-112313.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-respaldo-20261013-112317.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-restore-20261013-112324.log
~/netlab360-bootstrap/evidencias/16-b2-lan-ping-restaurada-20261013-112346.log
~/netlab360-bootstrap/evidencias/15-b2-dualwan-down-20261013-112352.log
```

**Capturas:** el usuario estableció que TODAS las capturas solicitadas se **consideran tomadas salvo aviso contrario**. B2_11 precheck, B2_12 vecinos/rutas Full, B2_13 failover, B2_14 restauración, B2_15 **30/30 ICMP**; no se han recibido los PNG para revisión gráfica ni subido archivos al repo. No solicitar que repita pruebas solo para fotografiar una terminal. Indicar siempre nombre PNG y marcador textual exacto **INICIO CAPTURA** hasta **FIN CAPTURA** con comando de consulta a logs, nunca `clear`.

## Control del proyecto e issues

- S01 **42% técnico ponderado**, frente a 40% previo, por dos puntos nuevos de B2-L3. Desglose `docs/control/01-avance-s01.md`: B0 12/12, B1 8/10, B2-L2 3/10, B2-L3 16/18, LACP 0/10, IaC 1/10, B3 0/15, B4 0/5, documentación 2/5, B5 0/5 = **42/100**. No es % oficial de docente.
- Hasta este corte: **43 issues, 3 cerradas** (#39 IP fija, #40 GitHub CLI, #41 herramientas/snapshot), 40 abiertas. #1 S01 **ABIERTA**, #42 dual-WAN **ABIERTA** pese a subhitos aprobados, #12 alerta/dashboard **ABIERTA**, #43 auditoría PNG **ABIERTA**, #35 documentos finales **ABIERTA**. No cerrar por adelantado.
- Pendiente **prioritario**: medir convergencia y pérdida durante caída con tráfico ICMP continuo/timestamps, y de ser necesario un cliente detrás de cada LAN; después B3 exporter/Prometheus, alarma y dashboard que muestren evento WAN. Otras áreas S01: VLAN trunks/ACL, LACP/dualNIC/redundancia, OpenTofu/Ansible, analítica, informe APA7/bitácora/manual, CI/tag/release, OVA sanitizada e importación/checksum, rúbrica docente.
- El éxito de 30/30 NO acredita cero paquetes perdidos **durante el instante de falla**, pues se hicieron pings después de la conmutación. Tampoco prueba hosts/servidores finales, solo las LAN `dummy` que residen en los routers.
- Estado S01 y futuros cierres deben mantenerse sincronizados en issue #1, #12, #42, #43 y matrices. No incrementar porcentaje solo por editar archivos.

## Pausa y comandos de cierre obligatorio (12:00–12:15, 13/10)

**A las 12:00 parar nuevos ensayos**. Para sincronizar `main` *después* de las actualizaciones del asistente:

```bash
cd ~/proyectos/netlab360
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git status --short --branch
git rev-parse HEAD
git rev-parse origin/main
sudo docker ps -a
sudo ip netns list
ip -4 -br address show ens33
ip -4 route show default
systemctl is-active docker ssh open-vm-tools
```

Comprobar Git limpio, **ambos hashes idénticos**, docker/netns vacíos, IP/GW correctos, servicios activos. Los logs originales siguen en la VM fuera de Git; si se solicita respaldarlos/subirlos, revisar sensibilidad y agregarlos de modo explícito. **No afirmar apagado ejecutado hasta que el usuario reporte**. Tras verificaciones exitosas:

```bash
sync
sudo systemctl poweroff
```

Esperar VMware **Powered Off** y apagar Windows. Si aparece un contenedor B2, ejecutar exclusivamente `bash scripts/laboratorio/b2-dualwan-ospf.sh down` tras revisar marcador del estado, sin destruir recursos ajenos; no apagar con recursos no identificados. Si quedan problemas, capturar/loguear y detener proceso de apagado para resolver, sin correr experimentos nuevos.

**Preferencias operativas del usuario:** entregar paquetes de 6–10 pasos cuando sea útil, no microconfirmaciones; explicar de qué marca a cuál va cada captura; actualizar GitHub continuamente y preservar checkpoint para cambios de conversación; cada vez que VM arranca, mantenimiento preventivo antes de trabajo; al final apagar ordenadamente.
