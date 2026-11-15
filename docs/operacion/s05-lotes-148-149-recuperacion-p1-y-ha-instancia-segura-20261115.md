# NETLAB360 S05 — Lotes 148A, 148B y 149: procedencia P1 y HA instancia protegida

**Fecha:** 15/11/2026. **Exclusivo S05.** Evitar repetir WAN/LACP/SDN, 145A/B, pruebas iperf3 o reiniciar Ubuntu. 147A **COMPLETADO**: 4/4 tests; TAR P1 del 10/11 con 4/4 miembros/hashes; los JSON actuales tienen mtime del 11/11 y existe segundo log del 11/11, sin confirmar todavía correspondencia exacta; P1B 5/5 SHA OK. Milestones #5/#6/#7/#8: sus **descripciones fueron efectivamente actualizadas mediante gh api** (marcador MILESTONES_CORTE146A=OK) conservando estado abierto.

## Lote 148A — Recuperar copia íntegra SIN SOBREESCRIBIR

El script s05-recuperar-p1-tar-historico.py realiza precheck de los hashes de los cuatro miembros históricos dentro del TAR. En --recover crea exclusivamente un directorio nuevo y extrae solo los cuatro archivos previstos, escribe un manifiesto derivado nuevo con rutas relativas; no modifica el TAR, manifiesto original, JSON actuales del 11/11, Git, namespaces o tráfico.

Orden: sincronizar main, tests de recuperación, --check, --recover **una sola vez**, ejecutar sha256sum -c en la carpeta nueva. Registrar la salida y comprobar los JSON con python json.tool sin regenerar tráfico. Si destino ya existe, abortar intencionalmente; NO borrarlo para repetir.

## Lote 148B — Conciliación de dos sesiones sin mezclar resultados

Comparar el registro local S05_P1_20261111-100600.log con sus 3 JSON vigentes del 11/11, marcas de escenario y hashes, y el registro original TAR del 10/11, identificando ejecución y fecha. No modificar el manifiesto original del 10/11. Mantener **dos conjuntos separados** en informe y evitar atribuir al 10/11 resultados del 11/11. P1B integridad SHA 5/5.

## Lote 149 — Una sola caída reversible de backend HQ con watchdog systemd

El script s05-lote-ha-instancia-con-watchdog.sh tiene dos modos:
1. --precheck: lectura del host, Git, seis servicios y NOC/FIB; verifica marcador de 147A, sudo no interactivo; **no provoca caída**.
2. --run --confirm-fault: exige precheck, arma timer transitorio systemd-run --on-active=120s cuyo ÚNICO comando es systemctl start netlab360-s05-ha-backend-hq.service, independiente del SSH; confirma timer active; llama al código previamente versionado de ciclo HA, que detiene exclusivamente backend HQ, espera BACKEND_S1/RESPALDO y restaura HQ en finally; verifica HQ/PRINCIPAL, servicios, IP/GW/Git; **solo tras éxito detiene timer**.
3. Si falla ciclo, deja timer armado e intenta iniciar HQ; no cerrar #32. Ante cierre abrupto SSH, timer en PID1 inicia el backend HQ transcurridos 120s si el invitado sigue en marcha. No garantiza recuperación de guest apagado/reiniciado.
4. No tocar ens33, VLAN, FRR, LACP, Faucet, WAN ni NOC; no reiniciar Ubuntu. No repetir para forzar capturas: usar JSONL y TXT.

**Evidencia visual:** tras ciclo completo correcto, capturar resumen terminal como S05_64_HA_Instancia_HQ_Respaldo_S1_y_Retorno, nueva evidencia de instancia que sustituye la sugerencia histórica de 64 complementaria NOC.

## Cierre restante

- CSV Windows contiene 70 PNG, 5 588 763 bytes declarados, 70 SHA distintos. Importar archivos reales y contrastar bytes SHA con inventario; el CSV por sí solo no certifica blobs Git.
- Preparar acta de aceptación, documentar independencia frente a HA física y limitaciones mono-VM. Resolver #23/#31/#32/#64/#105 y entonces #5/milestone S05, manteniendo S06/S07/S08 abiertas.
- Antes de apagar la VM: respaldar evidencias y diseñar reconstrucción de namespaces o suspender VMware; shutdown guest destruye 21 namespaces activos.
