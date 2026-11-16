# NETLAB360 — S04: observabilidad multisede y NOC sobre topología desmontada

**Fecha local de las pruebas:** 26 de octubre de 2026, UTC−05 (Panamá). **Naturaleza:** bitácora de operaciones reales, separada de ensayos sintéticos offline/CI. **Alcance:** primera integración del colector, Prometheus, alertas y NOC de HQ, S1 y S2.

## Precheck y desarrollo

1. Se comprobó Ubuntu Desktop 26.04.1 LTS, kernel `7.0.0-38-generic`, `ens33=192.168.47.40/24`, gateway `192.168.47.2`, SSH/Docker/open-vm-tools activos y estado OpenTofu S03 almacenado fuera de Git; inicialmente cero contenedores y cero namespaces.
2. Se sincronizó `main` mediante `git pull --ff-only`. La validación Python, Prometheus 3.7.0 (`promtool check config` y reglas), inventario SoT `candidate` de 3 routers/4 WAN/9 VLAN y ocho pruebas del exporter terminaron correctamente.
3. El primer colector de [PR #55](https://github.com/recm0708/netlab360/pull/55) realizó `--once`: `source_ok=true`, `topology=offline`, HQ/S1/S2 con `running=0`, ocho interfaces WAN y nueve VLAN con `admin_up=-1` por desmontaje voluntario.
4. Se inició exporter en `127.0.0.1:9110`. Evidencia **S04_01**: tres sedes, ocho WAN, nueve VLAN, 25 series, edad de muestra **3,86 s** y `S04_01_VERIFICACION=OK`.
5. Prometheus S04 aislado, de [PR #56](https://github.com/recm0708/netlab360/pull/56), se levantó en `127.0.0.1:9091`. Configuración válida, cuatro reglas y cuatro casos sintéticos `promtool test rules` SUCCESS. Evidencia real **S04_02**: target `up`, `scrape_up=1`, `source_up=1`, `topologia_offline=1`, WAN DOWN=0, VLAN DOWN=0, alertas activas=0, un grupo de reglas, `S04_02_VERIFICACION=OK`.
6. Se sincronizó [PR #57](https://github.com/recm0708/netlab360/pull/57) y se ejecutaron **20/20 pruebas S04 offline**. NOC `--check` devolvió `S04_NOC_PREFLIGHT=OK`; NOC `--once` entregó fuente fresca, sedes HQ/S1/S2, Prometheus `scrape=up`, cero alertas; el panel se sirvió en `127.0.0.1:9120`. Por túnel SSH Windows se inspeccionaron la **vista central** (S04_03, dos imágenes) y **Sucursal S1** (S04_04), ambas con estados consistentes.
7. **S04_05** registra `S04_05_VERIFICACION=OK` de API agregada: NOC saludable, `topology=offline`, tres sedes, scraping UP y alertas conocidas=0. NOC y exporter emitieron mensajes explícitos de parada tras Ctrl+C; Prometheus cerró scrape, rule manager y TSDB ordenadamente.
8. **S04_06** documenta postcheck: 9091/9110/9120 sin listeners, `ens33` y gateway originales, contenedores/namespaces vacíos, Git `main` limpio. No se modificaron FRR, WAN ni state OpenTofu.

## Evidencias entregadas y su estado de Git

Se recibieron **7 PNG auténticos**, que comprenden **6 identificadores** `S04_01`–`S04_06`, pues S04_03 representa una sola vista dividida en dos capturas. Los siete se inspeccionaron visualmente y se preparó un ZIP con manifiesto SHA256. [Auditoría del lote y hashes de cada PNG](https://github.com/recm0708/netlab360/issues/4#issuecomment-6433141415).

**Última salida observada de importación local:**
```text
S04_CAPTURAS_VERIFICADAS=7
S04_MANIFIESTO_VERIFICADO=SI
S04_IMPORTACION_RESULTADO=0
```
`git status --short` mostró **8 archivos sin seguimiento**: siete PNG de `evidencias/capturas/fase4/` y el CSV `evidencias/manifiestos/MANIFIESTO_SHA256_S04_LOTE01_2026-10-26.csv`. No aparece evidencia de push/PR todavía. **No aumentar el conteo de imágenes remotas de 107 a 114 hasta verificar la fusión.**

## Corte posterior — 26/10/2026: publicación y precheck activo

**Publicación auténtica:** el operador subió la rama `feat/s04-evidencias-lote01`, commit `ce0217e` con siete PNG originales y un manifiesto CSV. El control `git diff --cached --check` señaló finales CRLF del CSV; se normalizó **solo el manifiesto** a LF mediante commit `c34c824` sin modificar los PNG. [PR #58](https://github.com/recm0708/netlab360/pull/58) fusionado como `4babb2849890700462c8eff20dcc6cdc22d20096`. El árbol `main` verificado contiene **114 PNG**: S01 90, S02 9, S03 8, S04 7; no había PR adicionales abiertos y la rama remota se retiró automáticamente.

**Precheck REAL del operador (22:52 hora Panamá):** Git en rama `feat/s04-evidencias-lote01`, sin cambios locales; host `ens33=192.168.47.40/24`, gateway `.2`, `df` reportó **133 GiB disponibles de 157 GiB**, `free` mostró ~13 GiB memoria disponible. Docker sin contenedores, estados operativos WAN/LAN ausentes, directorios runtime FRR `R-HQ/R-S1/R-S2` presentes. `scripts/diagnostico/precheck-s02.sh` terminó `S02_PRECHECK_RESULTADO=0` y `RESULTADO_PRECHECK_S02=0`; validó tres sedes, nueve VLAN, cuatro WAN, 17 redes y 0 colisiones. `s02-wan-links.py plan` obtuvo `RESULTADO_PLAN_WAN=0` con primarias costo 10 y respaldos 100. `s02-lan-vlan.py plan` obtuvo `RESULTADO_PLAN_LAN=0`, tres switches/nueve VLAN/nueve hosts.

**Snapshot VMware:** el operador confirmó creación de la instantánea S04 inmediatamente después del precheck y eliminación de las **dos instantáneas anteriores**. Existe un único punto de retorno conservado según su confirmación; no se ha verificado su nombre ni restaurabilidad externamente, ni debe presumirse que se conservan snapshots viejos.

**Estado real al corte:** aún **NO** se ha iniciado ningún contenedor FRR ni desplegado WAN/LAN como parte de S04. Antes de los modos `up`, sincronizar el clon desde la rama local de evidencias a `main` ya fusionada, confirmar árbol limpio y ejecutar arrancador FRR→WAN→OSPF→LAN, usando `--snapshot-confirmado` únicamente porque el operador ya creó la instantánea. No ejecutar `tofu apply`.

## Aceptación y límites

**Validado:** observación fiable de topología OFFLINE sin falsas alarmas, captura de 25 series, scrape real de Prometheus, API agregada y navegación central/S1 en NOC, 20 pruebas S04 offline, cierre limpio.

**No validado aún:** cuatro WAN y nueve VLAN activas monitorizadas en ejecución, OSPF Full y HTTP reales en S04, caída/restauración WAN registrada simultáneamente como `firing/resolved`, persistencia histórica, alerta externa, SLI/SLO. La topología no estaba desplegada durante las capturas del primer lote.

Se conserva la [matriz de cierre S04](../operaciones/s04-cierre-observabilidad-multisede.md) y la [issue #4](https://github.com/recm0708/netlab360/issues/4); no cerrar S04 hasta completar o delimitar expresamente cada puerta. El informe académico se ampliará tras concluir las pruebas propias de esta fase, sin introducir resultados que no hayan sido observados.
