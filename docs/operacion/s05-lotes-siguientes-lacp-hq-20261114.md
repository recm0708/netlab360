# NETLAB360 S05 — Próximos cuatro lotes agrupados (14/11/2026)

**Corte probado:** HQ LACP 802.3ad y VLAN120/HTTP HA operativos; diagnóstico 111D-R/S OK. S1/S2 sin bonds, OVS/Faucet no implementado. **No volver a ejecutar UP de HQ ni reiniciar la VM.**

**Acceso:** una sesión SSH PowerShell con túnel 127.0.0.1:9130 a rc-aa-ec@192.168.47.40. Código en ~/proyectos/netlab360. No usar clear.

## Corrección de ejecución para LOTE114A-R

**Corte operativo posterior (14/11/2026):** lote 114A falló **en el paso 553**, `status` por `TimeoutExpired` de ping `-c 2 -W 2` con timeout externo 10s; dos ejecuciones: primero destino S2 `10.72.20.20` y luego frontal HQ `10.70.20.23`. **14/14 tests offline OK**, switch/cliente HQ 2/2 puertos, sin evidencia de fallo LACP. Lote 114B no pasó su gate (no había `LOTE114A_R_PRECHECK=OK`), **NO ocurrió failover real**. Ya existe [PR #109](https://github.com/recm0708/netlab360/pull/109), CI OK y merge en `1e2d12a9184c83caf71306bede14d76e88787fff`: reintentos ICMP auditados hasta 3 veces, timeout 15s, fallo cerrado si persiste y aplicado a status/ensayo. Rehacer **solo** 114A como validación de lectura sobre el código nuevo; 114B está prohibido hasta marcador final `OK`. No ejecutar UP HQ ni reiniciar.

**Nueva versión mínima exigida:** `1e2d12a9184c83caf71306bede14d76e88787fff`. Los bloques de esta guía **ya incluyen** este SHA y el nuevo marcador `LOTE114A_R_PRECHECK=OK` en el archivo `29_Precheck_Failover_HQ_y_S1S2_Corregido.txt`. No reutilizar el archivo anterior sin marcador. 

## Lote 114A — Sincronización, tests, verificación HQ y precheck S1/S2 (SOLO CONSULTA)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
mkdir -p "$DIR"
sudo -v
{
echo "========== 551 SYNC MAIN =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git merge-base --is-ancestor 1e2d12a9184c83caf71306bede14d76e88787fff HEAD
git log -1 --oneline
echo "========== 552 TESTS LACP =========="
python3 -m unittest discover -s tests -p 'test_s05_lacp_hq_falla_retorno.py' -v 2>&1 | tee "$DIR/22_Tests_Failover_HQ.txt"
grep -Fxq OK "$DIR/22_Tests_Failover_HQ.txt"
python3 -m unittest discover -s tests -p 'test_s05_lacp_integracion_precheck.py' -v 2>&1 | tee "$DIR/23_Tests_Precheck_Selectivo.txt"
grep -Fxq OK "$DIR/23_Tests_Precheck_Selectivo.txt"
echo "========== 553 HQ STATUS =========="
python3 scripts/laboratorio/s05-lacp-hq-integracion.py status
echo "========== 554 HQ FALLA PRECHECK =========="
python3 scripts/laboratorio/s05-lacp-hq-falla-retorno.py precheck
echo "========== 555 S1 S2 PRECHECK =========="
python3 scripts/validacion/s05-lacp-integracion-precheck.py precheck --sites S1 S2
echo "========== 556 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE114A_R_PRECHECK=OK =========="
} 2>&1 | tee "$DIR/29_Precheck_Failover_HQ_y_S1S2_Corregido.txt"
BASH
~~~

Si no aparece LOTE114A_R_PRECHECK=OK, no ejecutar 114B. Los tests de error simulado son intencionales y deben terminar en OK.

## Lote 114B — Falla real solo del miembro s5c1 y restauración 2→1→2

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
test -f "$DIR/29_Precheck_Failover_HQ_y_S1S2_Corregido.txt"
grep -Fxq 'LOTE114A_R_PRECHECK=OK' "$DIR/29_Precheck_Failover_HQ_y_S1S2_Corregido.txt"
{
echo "========== 557 FAILOVER HQ 2_1_2 =========="
python3 scripts/laboratorio/s05-lacp-hq-falla-retorno.py run --confirm-failover
echo "========== 558 HQ POSTCHECK =========="
python3 scripts/laboratorio/s05-lacp-hq-integracion.py status
echo "========== 559 S02 LACP VLAN =========="
sudo -n ip netns exec nl360-s02-sw-hq bridge vlan show dev s5bond0
echo "========== 560 FINAL HOST =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE114B_FALLA_RETORNO=OK =========="
} 2>&1 | tee "$DIR/25_Falla_Retorno_HQ_2_1_2.txt"
BASH
~~~

Si SSH vuelve a caer, no repetir run: hay un rescate transitorio de systemd de 120 segundos y restauración del miembro en finally. Reconectar y diagnosticar antes de cualquier modificación.

## Lote 114C — Secciones para capturas S05_48 y S05_49

Solo si LOTE114B acabó correctamente:

~~~bash
bash <<'BASH'
set -Eeuo pipefail
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
LOG="$DIR/25_Falla_Retorno_HQ_2_1_2.txt"
grep -Fxq 'LOTE114B_FALLA_RETORNO=OK' "$LOG"
grep -Fxq 'S05_LACP_HQ_PRUEBA=OK_2_1_2' "$LOG"
{
for N in 48 49; do
  echo "========== EVIDENCIA S05_$N =========="
  awk -v n="$N" '
    index($0,"INICIO_CAPTURA_S05_" n) {shown=1}
    shown {print}
    index($0,"FIN_CAPTURA_S05_" n) {exit}
  ' "$LOG"
done
echo "========== LOTE114C_EVIDENCIAS=OK =========="
} 2>&1 | tee "$DIR/26_Secciones_Capturas_48_49.txt"
BASH
~~~

- Captura 48: S05_48_LACP_HQ_Operacion_Con_Un_Enlace — 1 miembro activo por extremo, ping y HTTP real.
- Captura 49: S05_49_LACP_HQ_Restauracion_Dos_Enlaces — 2 miembros activos de nuevo, HTTP/gestión recuperados.
La salida de terminal NO sustituye al PNG original de cada captura.

## Lote 114D — Precheck de S1/S2 para preparar el despliegue siguiente (SOLO CONSULTA)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
{
echo "========== 561 PLAN S1 S2 =========="
python3 scripts/validacion/s05-lacp-integracion-precheck.py plan --sites S1 S2
echo "========== 562 PRECHECK S1 S2 =========="
python3 scripts/validacion/s05-lacp-integracion-precheck.py precheck --sites S1 S2
echo "========== 563 ESTADO HQ CONSERVADO =========="
python3 scripts/laboratorio/s05-lacp-hq-integracion.py status
echo "========== LOTE114D_S1S2_PRECHECK=OK =========="
} 2>&1 | tee "$DIR/27_Precheck_Solo_S1_S2.txt"
BASH
~~~

El precheck global por defecto asume que HQ está libre, por lo que detectaría la dirección 10.70.20.40 como ocupada. Ahora esa IP está **legítimamente asignada**. Usar siempre --sites S1 S2 para el siguiente trabajo.

## GitHub y alcance pendiente

- Issue madre #5 (S05), #31 LACP, #32 redundancia, #23 OVS/Faucet, #64 NOC y #105 evidencias abiertas. #24 cuarta sede/WireGuard cerrada not planned; milestone S05 ABIERTA.
- Informe maestro #27: actualizado solo hasta S04. No confundir el guion S05 con edición ya hecha del Word.
- #106 en S08: recuperación de servicios/namespaces después de reinicio. **No reiniciar la VM durante S05.**
- Estado y archivos fuente: docs/gestion/s05-tablero-vigente.md; docs/REANUDAR-AQUI.md; docs/gestion/historico-issues/.
- Orden posterior: bonds S1/S2 con rollback, redundancia real de instancia/equipo, SDN OVS/Faucet aislado, observabilidad NOC, importación PNG/JSON/CSV y manifiestos SHA-256, auditoría de cierre; después actualizar el **mismo informe Word/PDF**.
