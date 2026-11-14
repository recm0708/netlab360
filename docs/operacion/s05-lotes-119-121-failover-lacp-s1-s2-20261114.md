# NETLAB360 · Fase S05 · Lotes 119–121 (falla-retorno LACP S1 y S2)

Corte validado 14/11/2026: se ejecutaron los lotes 117R-A, 117R-B y 118-R, los 3 bonds IEEE 802.3ad tienen dos puertos por lado, las VLAN 120/220/320 operan, HQ y S1/S2 responden y OSPF mantiene s1p/s2p. Los seis servicios HA/NOC activos, ens33 192.168.47.40/24. Primera ejecución de 118-R abortó por KeyError S1 en respuesta NOC incompleta, segunda completó con OK. El operador confirma capturas tomadas; PNG originales no se han importado ni comprobado por SHA256 en el repositorio.

Cambios preparados y aprobados por CI:
- PR #117: scripts independientes de falla 2→1→2 en S1 y S2; solo s5c1, rescate systemd de 120s, restore en finally, pruebas de identidad y validación HTTP/OSPF.
- PR #118: vistas de NOC parciales manejadas mediante hasta tres observaciones, con rechazo estricto si nunca se ven HA principal y rutas s1p/s2p.

Seguridad: no reiniciar ni reconstruir HQ/S1/S2. Si SSH cae DURANTE un run, no repetir run; reconectar y comprobar estado, interfaces y temporizador. Las pruebas siguientes cambian temporalmente un miembro por sede, NO son solo lectura. Si falta marcador OK de un lote, no ejecutar el siguiente.

## Lote 119-A — sync, regresión y prechecks de ambas sedes (solo lectura)

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
mkdir -p "$DIR"
sudo -v
{
echo "========== 620 SINCRONIZACION =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git merge-base --is-ancestor d45b374407a6b38829dfc140b4523b33ce6ccb9b HEAD
git log -1 --oneline
grep -Fxq '========== LOTE118_R_TRES_BONDS=OK ==========' "$DIR/39_Tres_Sedes_LACP_Validadas.txt"

echo "========== 621 REGRESION OFFLINE =========="
python3 -m py_compile \
  scripts/laboratorio/s05-lacp-s1-falla-retorno.py \
  scripts/laboratorio/s05-lacp-s2-falla-retorno.py
for patron in \
  test_s05_lacp_s1_falla_retorno.py \
  test_s05_lacp_s2_falla_retorno.py \
  test_s05_lacp_hq_falla_retorno.py \
  test_s05_lacp_noc_fib_incompleto.py; do
  python3 -m unittest discover -s tests -p "$patron" -v
done

echo "========== 622 ESTADOS TRES SEDES =========="
for sede in hq s1 s2; do
  python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done

echo "========== 623 PRECHECK FAILOVER S1 =========="
python3 scripts/laboratorio/s05-lacp-s1-falla-retorno.py precheck

echo "========== 624 PRECHECK FAILOVER S2 =========="
python3 scripts/laboratorio/s05-lacp-s2-falla-retorno.py precheck

echo "========== 625 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE119A_PRECHECK_S1_S2=OK =========="
} 2>&1 | tee "$DIR/41_Precheck_Failover_LACP_S1_S2.txt"
BASH
~~~

## Lote 119-B — una falla controlada en S1, 2→1→2

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
grep -Fxq '========== LOTE119A_PRECHECK_S1_S2=OK ==========' "$DIR/41_Precheck_Failover_LACP_S1_S2.txt"
{
echo "========== 626 FALLA RETORNO S1 =========="
python3 scripts/laboratorio/s05-lacp-s1-falla-retorno.py run --confirm-failover
echo "========== 627 POSTCHECK TRES SEDES =========="
for sede in s1 hq s2; do
  python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done
echo "========== 628 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE119B_FAILOVER_S1=OK =========="
} 2>&1 | tee "$DIR/42_Falla_Retorno_LACP_S1.txt"
BASH
~~~

Captura 53: S05_53_LACP_S1_Operacion_Con_Un_Enlace, desde INICIO_CAPTURA_S05_53 a FIN_CAPTURA_S05_53 (1/1, 4 pings, HTTP, HA/FIB).
Captura 54: S05_54_LACP_S1_Restauracion_Dos_Enlaces, desde INICIO_CAPTURA_S05_54 a FIN_CAPTURA_S05_54 (2/2, servicios y recuperación).

## Lote 120 — falla controlada en S2, exclusivamente después de S1 OK

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
grep -Fxq '========== LOTE119B_FAILOVER_S1=OK ==========' "$DIR/42_Falla_Retorno_LACP_S1.txt"
{
echo "========== 629 PRECHECK FINAL S2 =========="
python3 scripts/laboratorio/s05-lacp-s2-falla-retorno.py precheck
echo "========== 630 FALLA RETORNO S2 =========="
python3 scripts/laboratorio/s05-lacp-s2-falla-retorno.py run --confirm-failover
echo "========== 631 POSTCHECK TRES SEDES =========="
for sede in s2 hq s1; do
  python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done
echo "========== 632 GESTION Y GIT =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE120_FAILOVER_S2=OK =========="
} 2>&1 | tee "$DIR/43_Falla_Retorno_LACP_S2.txt"
BASH
~~~

Captura 55: S05_55_LACP_S2_Operacion_Con_Un_Enlace.
Captura 56: S05_56_LACP_S2_Restauracion_Dos_Enlaces.
Seleccionar en logs las líneas delimitadas, no repetir ensayo para fotografía. No atribuir cero pérdida durante la transición.

## Lote 121 — aceptación de las tres sedes, evidencia condensada e integridad de logs

~~~bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion"
sudo -v
grep -Fxq '========== LOTE120_FAILOVER_S2=OK ==========' "$DIR/43_Falla_Retorno_LACP_S2.txt"
grep -Fxq 'S05_LACP_S1_PRUEBA=OK_2_1_2' "$DIR/42_Falla_Retorno_LACP_S1.txt"
grep -Fxq 'S05_LACP_S2_PRUEBA=OK_2_1_2' "$DIR/43_Falla_Retorno_LACP_S2.txt"
{
echo "========== 633 REGRESION Y EVIDENCIA FINAL =========="
echo "========== INICIO_CAPTURA_S05_57_LACP_MULTISEDE_RECUPERADA =========="
for sede in hq s1 s2; do
  salida="$DIR/44_Estado_LACP_Final_$sede.txt"
  python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status > "$salida"
  grep -Fqx "S05_LACP_$(echo "$sede" | tr '[:lower:]' '[:upper:]')_STATUS=OK" "$salida"
  test "$(grep -c 'PUERTOS_ACTIVOS=2' "$salida")" -eq 2
  printf 'S05_LACP_SEDE_%s=2_2_CONECTIVIDAD_HA_FIB_OK\n' "$sede"
done
echo "========== 634 ENRUTAMIENTO FRR =========="
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.71.20.0/24'
sudo -n docker exec nl360-s02-r-hq vtysh -c 'show ip route 10.72.20.0/24'
echo "========== 635 SERVICIOS =========="
for unit in netlab360-s04-exporter netlab360-s05-noc netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1 netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
  test "$(systemctl is-active "$unit")" = active
  echo "S05_UNIT_$unit=active"
done
echo "========== 636 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== FIN_CAPTURA_S05_57_LACP_MULTISEDE_RECUPERADA =========="
echo "========== LOTE121_LACP_MULTISEDE=OK =========="
} 2>&1 | tee "$DIR/45_Aceptacion_Final_LACP_Multisede.txt"

sha256sum \
 "$DIR/41_Precheck_Failover_LACP_S1_S2.txt" \
 "$DIR/42_Falla_Retorno_LACP_S1.txt" \
 "$DIR/43_Falla_Retorno_LACP_S2.txt" \
 "$DIR/45_Aceptacion_Final_LACP_Multisede.txt" \
 > "$DIR/46_Manifiesto_SHA256_Failover_LACP.txt"
sha256sum -c "$DIR/46_Manifiesto_SHA256_Failover_LACP.txt"
BASH
~~~

Captura 57: S05_57_LACP_Tres_Sedes_Conmutacion_y_Restauracion_Validada.
Esto prueba recuperación del protocolo bajo un enlace redundante por sede, NO alta disponibilidad física del único host VMware.

## Después de 121

Cerrar checkbox técnico de #31 solo tras verificar realmente las dos pruebas y guardar las imágenes 53–57. La issue #31 aún incluye caracterización estadística reproducible y auditoría de PNG que deben acreditarse. OVS/Faucet, HA de instancia/equipo, NOC y documentación académica S05 siguen pendientes, no se cierran sin evidencia.

No reiniciar Ubuntu: namespaces aún efímeros. Estado a retomar en docs/gestion/s05-tablero-vigente.md y docs/REANUDAR-AQUI.md.
