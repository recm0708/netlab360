# NETLAB360 · Estimación del avance práctico y ruta de cierre (14/11/2026)

**Fuente:** resultados entregados por el operador de los lotes 119A, 119B, 120 y 121; issues de GitHub #5, #23, #31, #32, #64, #105, #6, #7, #8, #106 y criterios académicos versionados. **No es una calificación ni un porcentaje oficial**.

## Situación del desarrollo

| Fase interna | Estimación técnica | Evidencia / alcance pendiente |
|---|---:|---|
| S01 | 100 % según cierre del milestone | Base, soporte de laboratorio y control |
| S02 | 100 % según cierre del milestone | 3 sedes, WAN redundante, FRR/OSPF, 9 VLAN |
| S03 | 100 % según cierre del milestone | SoT, OpenTofu metadata-only, Ansible, GitOps; ampliación ownership #17 permanece aparte |
| S04 | 100 % según cierre del milestone | NOC/telemetría/incidencias/series de tiempo, con límites SLI |
| S05 | **~75 %** estimado del alcance práctico | WAN/HTTP y LACP 3 sedes completamente demostrados. Faltan OVS/Faucet real (#23), aceptación HA de instancia/equipo (#32), telemetría NOC LACP/SDN (#64), evidencias/importación (#105), estadística P1/P1B (#31) |
| S06 | **~0–5 %** de desarrollo ML evaluado | Datos y entrenamiento/validación IA no ejecutados. Reglas previas no son modelo entrenado (#6, #25, #26) |
| S07 | **~0 %** de integración AIOps | Ciclo supervisado detectar→recomendar→aprobar→actuar→verificar→revertir no implementado (#7) |
| S08 | Entregables en curso, NO mezclar con porcentaje práctico | Informe único 4.6 tiene 113 páginas y S01–S04; TAR, presentación y demo final pendientes (#8, #27, #44, #45) |

**Estimación de parte práctica S01–S07:** 4 fases cerradas + 0,75 de S05 + hasta 0,05 de S06 = **aprox. 68–69 %**, redondeado a **~70 %**, si se ponderan siete fases igual. Una estimación prudente es **65–70 %**, dado que hay incertidumbres en el alcance de HA/SDN/IA. El pendiente estimado **30–35 %** incluye las tareas de mayor complejidad (OVS/Faucet, IA/ML y AIOps), por lo que NO debe traducirse a horas de trabajo ni asumir que falta «poco».

**Cronograma:** la revisión prevista para **13/11/2026** ya pasó y su dictamen todavía no está comprobado; 30/10 se reportó realizada. El calendario S01–S08 es **interno**, NO una exigencia oficial de que esas fases coincidan con las semanas del semestre. No hay fecha final de demo confirmada en fuentes del repo. **Sí existe desfase técnico** por S06/S07 sin ejecutar y S05 aún abierta, pero no es posible calcular semanas oficiales de atraso sin fecha docente final.

## Log de cierre LACP del 14/11/2026

- [x] 119A: suites S1 8/8, S2 8/8, HQ 7/7, NOC 3/3: **26/26** pruebas; precheck S1/S2 y 3 bonds 2/2 sin modificar gestión.
- [x] 119B: S1 2/2→1/1→2/2; cuatro destinos alcanzables, HTTP BACKEND_HQ y FIB conservados. Timeout transitorio de ping al gateway S1 en intento 1; correcto en intento 2. Timer systemd cancelado tras recuperación.
- [x] 120: S2 2/2→1/1→2/2; HTTP/4 pings/FIB sanos; timer cancelado. Timeout transitorio de HQ→S2 en primer intento de postcheck, recuperación en segundo.
- [x] 121: tres sedes 2/2, rutas OSPF principales HQ→S1 s1p, HQ→S2 s2p, seis servicios activos, `ens33=192.168.47.40/24`, ruta por `.2`, Git limpio. Manifiesto SHA-256 de cuatro logs 41/42/43/45 **4/4 OK**.
- [ ] Confirmar originales PNG de 53–57 junto a anteriores y sus SHA-256 binarios, no inferir su integridad de un log TXT.
- **No repetir:** reinstalación bonds HQ/S1/S2, fallas LACP de esas tres sedes, HTTP HQ→S1→HQ ni fallas WAN comprobadas.

## Ruta crítica para terminar práctica

1. **S05 cierre operativo**: preflight OVS/Faucet aislado; diseñar y desplegar switch/controles SDN en recursos dedicados; demostrar políticas y falla/retorno sin tocar S02. En paralelo, completar aceptación HA de instancia/equipo sin afirmar tolerancia a fallo físico del único host.
2. **S05 integración NOC**: datos reales de bonds y controlador OVS/Faucet, expiración de muestras, alertas de falla/restauración y revisión visual, sin estados simulados; evidencias/manifiestos originales. Revisión P1/P1B, cerrar #23, #32, #64, #31, #105 y por último #5/milestone.
3. **S06 acotado y reproducible**: dataset etiquetado con trazabilidad real de incidentes, partición por sesión/fecha para evitar leakage; comparar reglas frente a modelo ML con métricas y limitaciones; no inventar precisión.
4. **S07 integración supervisada**: correlación de eventos, recomendación con aprobación humana, ejecución/rollback y verificación; aceptación de pruebas con observación NOC y sin interferir con gestión.
5. **Antes del reinicio Windows/VMware**: no reiniciar la VM mientras los namespaces estén activos sin recuperación comprobada. Desarrollar #106: inventario de dependencias, backup fuera de la VM e integridad, procedimiento idempotente de reconstrucción, prueba controlada y verificación tras arranque; asegurar evidencia antes de cualquier apagado. Luego apagar Ubuntu desde el invitado y confirmar apagada la VMware VM, solo entonces reiniciar Windows. No reiniciar Windows con la VM activa o suspendida sin un plan de conservación/recuperación aceptado.
6. **Escrito y entrega**: continuar el **mismo** informe Word 4.6 (113 páginas, hasta S04), incorporar S05–S07, revisar APA 7/figuras/conclusiones; TAR técnico externo sin secretos, presentación y demostración. Revisiones docentes y fecha final pendientes.

## Próximo lote 122: auditoría solo lectura (NO crea OVS, NO reinicia)

```bash
bash <<'BASH'
set -Eeuo pipefail
cd ~/proyectos/netlab360
DIR="$HOME/netlab360-bootstrap/s05/evidencias/cierre-practico"
mkdir -p "$DIR"
sudo -v
{
echo "========== 637 GIT Y CORTE =========="
test -z "$(git status --porcelain)"
GIT_TERMINAL_PROMPT=0 git pull --ff-only origin main
git log -1 --oneline
grep -Fxq '========== LOTE121_LACP_MULTISEDE=OK =========='   "$HOME/netlab360-bootstrap/s05/evidencias/lacp-integracion/45_Aceptacion_Final_LACP_Multisede.txt"
echo "========== 638 SO Y RECURSOS =========="
uname -a
free -h
df -h /
echo "========== 639 GESTION =========="
ip -4 -br address show ens33
ip -4 route show default
echo "========== 640 INVENTARIO NETWORK NAMESPACES =========="
sudo -n ip netns list
echo "========== 641 CONTENEDORES EXISTENTES =========="
sudo -n docker ps --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'
echo "========== 642 HERRAMIENTAS SDN =========="
for programa in ovs-vsctl ovs-ofctl ovs-appctl faucet ryu-manager; do
  if command -v "$programa" >/dev/null 2>&1; then
    printf 'SDN_%s=%s\n' "$programa" "$(command -v "$programa")"
  else
    printf 'SDN_%s=NO_INSTALADO_EN_PATH\n' "$programa"
  fi
done
echo "========== 643 SERVICIOS SDN =========="
systemctl list-unit-files 'openvswitch*' 'faucet*' --no-pager || true
echo "========== 644 IMAGENES SDN EN CACHE =========="
sudo -n docker images --format '{{.Repository}}:{{.Tag}}' |
  grep -Ei 'faucet|openvswitch|ryu' || true
echo "========== 645 SERVICIOS LACP/HA/NOC =========="
for sede in hq s1 s2; do
  python3 "scripts/laboratorio/s05-lacp-$sede-integracion.py" status
done
for svc in netlab360-s04-exporter netlab360-s05-noc            netlab360-s05-ha-backend-hq netlab360-s05-ha-backend-s1            netlab360-s05-ha-frontal-hq netlab360-s05-ha-monitor-s2; do
  printf 'SERVICE_%s=%s\n' "$svc" "$(systemctl is-active "$svc" || true)"
done
echo "========== 646 ALMACENAMIENTO Y ARRANQUE =========="
ls -lah "$HOME/netlab360-bootstrap/s05/lacp-multisede" || true
systemctl is-enabled netlab360-s05-noc netlab360-s04-exporter || true
echo "========== 647 CONTROL VERSION =========="
test -z "$(git status --porcelain)"
git status --short --branch
echo "========== LOTE122_AUDITORIA_PRE_SDN=OK =========="
} 2>&1 | tee "$DIR/01_Auditoria_SDN_HA_y_Reinicio_Pendiente.txt"
BASH
```

**El marcador OK del lote 122 indica que se ejecutaron las consultas; NO significa que el SDN esté instalado, que la HA esté aceptada o que sea seguro reiniciar.** Cualquier error anterior a ese marcador suspende la planificación del despliegue.
