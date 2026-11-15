# S05 — Lotes 136–138: SDN aceptado, enlace A degradado y restaurado (15/11/2026)

Corte real de 135A–135C:
- 135A: 23/23 pruebas, HQ/S1/S2 mantienen IPv4 ens33 y gateway. El único cambio en main fue la ruta 172.17.0.0/16 de docker0: ya no indica linkdown.
- 135B: tres LACP en 2/2 extremos, 12 comprobaciones de ping por sitio (4 cada uno), OSPF via s1p/s2p, seis servicios activos, SDN conectado y segmentación validada, NTP y Git OK.
- 135C: 13/13 tests, VLAN410 A→B RC0 2/2, VLAN420 A→C y C→A RC1 con 0 recibidos/100% pérdida, marcadores S05_SDN_CAPTURA60 y LOTE135C OK. El usuario confirma PNG S05_60 tomado (hash original aún pendiente).

Se introdujo scripts/laboratorio/s05-sdn-falla-retorno-puerto-a.py. El experimento afecta ÚNICAMENTE sdna0, un veth S05 propio unido al bridge br-s05-sdn. Precheck read-only exige estado active, propiedad bridge+contenedor, OFPORT1, tres puertos exclusivos, C aislado, A/B conectados, infraestructura previa intacta y systemd-run disponible. Antes de bajar el puerto, arma timer transitorio restore-only de 120 s que ejecuta ip link set dev sdna0 up incluso tras desconexión SSH. El script restaura en finally, exige status SDN completo + OpenFlow + servicios activos y cancela el timer solo después de la aceptación. Ni ens33, VLAN existentes, WAN, FRR, LACP, Faucet container, NetworkManager ni el host se modifican. Es **resiliencia de enlace**, no tolerancia a falla del equipo/router/VM/controller.

## Lote 136 — Aceptar resultado estático y hashes de TXT (pasos 774–779)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
{
echo "========== 774 GIT =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git log -1 --oneline
echo "========== 775 LOGS 135A/B/C =========="
grep -Fxq '========== LOTE135A_BASELINE_POSTRESUME=OK ==========' "$DIR/20_Auditoria_Baseline_Gestion_PostResume.txt"
grep -Fxq '========== LOTE135B_VMWARE_REANUDACION_COMPLETA=OK ==========' "$DIR/21_Validacion_Integral_Tras_Resume_VMware.txt"
grep -Fxq '========== LOTE135C_EVIDENCIA60=OK ==========' "$DIR/22_Captura60_Tras_Reanudar_VMware.txt"
grep -Fxq 'S05_SDN_CAPTURA60=OK_BLOQUEO_VALIDADO_SIN_TIMEOUT_EXTERNO' "$DIR/22_Captura60_Tras_Reanudar_VMware.txt"
echo "========== 776 SDN =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status
echo "========== 777 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 778 GIT LIMPIO =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== 779 CORTE =========="
echo "========== LOTE136_SDN_ESTABLE_Y_CAPTURA60=OK =========="
} 2>&1 | tee "$DIR/23_Aceptacion_Estatica_SDN_Recuperado.txt"

sha256sum \
 "$DIR/08_Precheck_Reparacion_Permisos_Faucet.txt" \
 "$DIR/09_Recuperacion_Controlador_Faucet.txt" \
 "$DIR/10_Validacion_OpenFlow_VLAN410_420_Recuperado.txt" \
 "$DIR/20_Auditoria_Baseline_Gestion_PostResume.txt" \
 "$DIR/21_Validacion_Integral_Tras_Resume_VMware.txt" \
 "$DIR/22_Captura60_Tras_Reanudar_VMware.txt" \
 "$DIR/23_Aceptacion_Estatica_SDN_Recuperado.txt" \
 > "$DIR/24_Manifiesto_SHA256_Aceptacion_SDN.txt"
sha256sum -c "$DIR/24_Manifiesto_SHA256_Aceptacion_SDN.txt"
BASH
~~~

## Lote 137A — suite/precheck del enlace SDN, SIN CAMBIOS (780–785)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
grep -Fxq '========== LOTE136_SDN_ESTABLE_Y_CAPTURA60=OK ==========' "$DIR/23_Aceptacion_Estatica_SDN_Recuperado.txt"
{
echo "========== 780 COMPROBAR SCRIPT =========="
test -f scripts/laboratorio/s05-sdn-falla-retorno-puerto-a.py
git log -1 --oneline
echo "========== 781 SINTAXIS =========="
python3 -m py_compile scripts/laboratorio/s05-sdn-falla-retorno-puerto-a.py
echo "========== 782 TESTS SEGURIDAD =========="
python3 -m unittest discover -s tests -p 'test_s05_sdn_falla_retorno_puerto_a.py' -v
echo "========== 783 PRECHECK =========="
python3 scripts/laboratorio/s05-sdn-falla-retorno-puerto-a.py precheck
echo "========== 784 CONTROLADOR =========="
sudo -n ovs-vsctl --timeout=12 --format=table --columns=target,is_connected,status list Controller
ip -4 -br address show ens33
ip -4 route show default
echo "========== 785 REPO =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE137A_PRECHECK_FALLA_SDN=OK =========="
} 2>&1 | tee "$DIR/25_Precheck_Falla_Puerto_SDN_A.txt"
BASH
~~~

## Lote 137B — FALLA CONTROLADA de sdna0 con timer de rescate (786–789)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
grep -Fxq '========== LOTE137A_PRECHECK_FALLA_SDN=OK ==========' "$DIR/25_Precheck_Falla_Puerto_SDN_A.txt"
{
echo "========== 786 FALLA/RESTAURACION RESGUARDADA =========="
python3 scripts/laboratorio/s05-sdn-falla-retorno-puerto-a.py run --confirm-fault
echo "========== 787 REVALIDAR SDN =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status
echo "========== 788 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 789 GIT =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE137B_FALLA_RETORNO_SDN=OK =========="
} 2>&1 | tee "$DIR/26_Falla_Retorno_SDN_Puerto_A.txt"
BASH
~~~

Si SSH se desconecta durante 137B: **NO volver a ejecutar run**. Reconectar y consultar systemctl list-timers --all, ip -br link show sdna0, ovs-vsctl show, y el estado inspect de S05. El watchdog solo puede subir sdna0. No cancelar el timer si la validación posterior falla.

Si 137B termina OK, sin repetir la falla, extraer capturas desde TXT:

~~~bash
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
for id in 61_SDN_A_ENLACE_CAIDO 62_SDN_A_ENLACE_RESTAURADO; do
 echo "========== CAPTURA_$id =========="
 awk -v id="$id" 'index($0,"INICIO_CAPTURA_S05_"id){p=1}p{print}index($0,"FIN_CAPTURA_S05_"id){exit}' \
  "$DIR/26_Falla_Retorno_SDN_Puerto_A.txt"
done
~~~

Nombres de PNG sin extensión: S05_61_SDN_Puerto_A_Interrumpido y S05_62_SDN_Puerto_A_Restaurado. 61 debe incluir down y ping bloqueado con OpenFlow/servicios conservados; 62 sdna0 UP, ping/aislamiento validado y rescate cancelado en el log. Confirmar cada imagen desde marcador INICIO a FIN.

## Lote 138 — regresión final y SHA256 del fallo SDN (790–795)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/sdn-despliegue"
sudo -v
grep -Fxq '========== LOTE137B_FALLA_RETORNO_SDN=OK ==========' "$DIR/26_Falla_Retorno_SDN_Puerto_A.txt"
grep -Fxq 'S05_SDN_FALLA_RETORNO=OK_DOWN_UP_ENLACE_A' "$DIR/26_Falla_Retorno_SDN_Puerto_A.txt"
{
echo "========== 790 SDN POST-FALLA =========="
python3 scripts/laboratorio/s05-sdn-ovs-faucet-aislado.py status
echo "========== 791 LACP MULTISEDE =========="
for sede in hq s1 s2; do
 python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done
echo "========== 792 OSPF =========="
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.71.20.0/24'
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.72.20.0/24'
echo "========== 793 SERVICIOS =========="
for servicio in \
 netlab360-s04-exporter netlab360-s05-noc \
 netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 \
 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
 test "$(systemctl is-active "$servicio")" = active
 echo "S05_SERVICE_$servicio=active"
done
echo "========== 794 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== 795 ACEPTACION =========="
echo "========== LOTE138_REGRESION_FALLA_SDN=OK =========="
} 2>&1 | tee "$DIR/27_Regresion_Multisede_Tras_Falla_SDN.txt"
sha256sum \
 "$DIR/25_Precheck_Falla_Puerto_SDN_A.txt" \
 "$DIR/26_Falla_Retorno_SDN_Puerto_A.txt" \
 "$DIR/27_Regresion_Multisede_Tras_Falla_SDN.txt" \
 > "$DIR/28_Manifiesto_SHA256_Falla_Retorno_SDN.txt"
sha256sum -c "$DIR/28_Manifiesto_SHA256_Falla_Retorno_SDN.txt"
BASH
~~~

Los hashes de TXT NO verifican PNG originales. S05 sigue abierta por NOC con datos LACP/SDN reales (#64), HA de instancia/equipo (#32), caracterización P1/P1B (#31), evidencia binaria (#105) y aprobación del milestone (#5). No presentar fallo de puerto como redundancia física del servidor/VM ni reiniciar el guest Ubuntu antes de completar la recuperación de namespaces.
