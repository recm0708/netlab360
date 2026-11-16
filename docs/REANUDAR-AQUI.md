# Punto de reanudación del proyecto

**Corte verificado:** S05, lote 158, 15 de noviembre de 2026.

## Estado operativo

NETLAB360 tiene 21 namespaces de red, cuatro contenedores (FRR ×3 y Faucet), seis servicios `systemd` activos y el NOC saludable. La gestión de Ubuntu continúa por `ens33 192.168.47.40/24`, gateway `192.168.47.2`. El ensayo real de backend HTTP demostró `HQ → S1 → HQ` con 17 muestras, y el rescate programado quedó cancelado tras la recuperación.

## Evidencias pendientes de publicación

En `~/proyectos/netlab360`, la rama local `evidencias/s05-70png-verificados-20261115` contiene **77 archivos nuevos**: 71 PNG y seis complementarios (inventario, tres manifiestos, JSONL y TXT). Se validaron 71/71 PNG con SHA-256 y decodificación, 2/2 registros HA y una revisión visual. La ejecución del lote 159 **se detuvo antes del commit** porque `git diff --cached --check` señaló terminaciones CRLF en el CSV y espacios históricos en un TXT de salida; no se deben modificar las evidencias originales para corregirlo.

**Orden de continuidad:**

1. Conservar los 77 archivos y su índice en la rama local; no repetir `--import` ni los ensayos WAN/LACP/SDN/HA.
2. Verificar los tres manifiestos y los 77 elementos preparados en el índice de Git. Aplicar el control de espacios de manera compatible con archivos de evidencia inmutables; efectuar commit y push sin alterar los bytes originales.
3. Crear, revisar y fusionar el PR de evidencias en `main`. Verificar en el remoto 71 PNG, CSV, tres manifiestos y dos registros HA.
4. Completar acta de aceptación documental S05, actualizar checklists de las issues y cerrar la milestone S05 solo cuando la evidencia esté efectivamente publicada.
5. Normalizar ramas locales y remotas sin borrar cambios exclusivos. Conservar una sola rama operativa: `main`.
6. Para suspender el trabajo, usar **Suspend** en VMware; no ejecutar `poweroff`, `reboot` ni desmontaje de redes hasta contar con reconstrucción y copia de recuperación comprobadas.
7. Retomar la actualización del informe académico único y después los trabajos técnicos S06/S07, con las verificaciones correspondientes.

## Documentos de referencia

[Estado consolidado](00-estado-y-continuidad.md) · [Tablero técnico S05](gestion/s05-tablero-vigente.md) · [Plan de conservación](05-plan-operativo-y-pausas.md) · [Catálogo de evidencias](../evidencias/capturas/README.md).

Los registros anteriores siguen disponibles en `docs/sesiones/` y `docs/gestion/` exclusivamente para trazabilidad histórica.
