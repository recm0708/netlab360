# NETLAB360 — Plan operativo, seguridad y pausas

**Vigente 14/10/2026.** La última sesión de red terminó con postcheck válido 13/10 23:35:02. La VM se encontraba sin contenedores ni namespaces, gestión ens33 192.168.47.40/24, gateway 192.168.47.2 y servicios activos. No se ha ordenado apagado en este turno.

## Prioridad actual
No empezar S02 ni introducir funcionalidades B4/AIOps adicionales: acordar y redactar tres únicos documentos acumulativos S01–S08 en el formato institucional del usuario. Resolver rúbrica y brechas S01 exigibles. [Checkpoint](REANUDAR-AQUI.md) y [documentación](entregables/00-politica-editorial-y-entrega-acumulativa.md).

## Método de trabajo
- Agrupar pasos sustanciales, sin instrucciones repetitivas de un comando por turno.
- Después de cada práctica: precheck, ejecución una vez, observación/salida, rollback propietario y postcheck.
- Indicar exactamente el tramo INICIO CAPTURA / FIN CAPTURA; si el texto no cabe, fragmentos numerados. Evitar repetir laboratorios aprobados por fotos.
- Evidencias originales en carpeta plana e índices SHA256, commits reproducibles; mantener secrets fuera de Git.
- Diferenciar diseños/prototipos y resultados reales; no presentar S01 cerrada hasta aceptación de rúbrica.

## Seguridad del entorno
- Proteger VMnet8 y ens33; no cambiar ni puente ni default route del host por laboratorios.
- Nunca forzar git push, borrar estado IaC, ni ejecutar docker rm globalmente por error de un escenario específico.
- Instalar solo herramientas necesarias y justificadas por un criterio de aceptación.
- Antes de exportar VM deben planificarse sanitización de tokens, credenciales y datos privados, snapshot y prueba de importación.

## Pausas y reanudación
- En pausas cortas: no dejar ensayos disruptivos corriendo salvo requerimiento explícito, recoger evidencias y comprobar estado Git.
- En pausa larga o para entregar VM: detener laboratorios con sus scripts, revisar Docker/netns y puertos, validar ens33/gateway, Git limpio y respaldos antes de apagar desde Ubuntu. No ejecutar `poweroff` sin instrucción del operador.
- Reanudar desde [REANUDAR-AQUI](REANUDAR-AQUI.md) y tabla de criterios, no desde checkpoints históricos.

**Versiones previas:** Git conserva instrucciones antiguas de pausas y horarios que ya no aplican; no reutilizarlas como órdenes actuales.
