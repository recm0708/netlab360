# Ensayos operacionales y escenarios compuestos

## Descripción

La evaluación relaciona las degradaciones controladas de HTTP HA, LACP, WAN y SDN con observaciones normalizadas, hipótesis RCA y recomendaciones de lectura. Se diferencia la evidencia directa de la inferencia diagnóstica. Los estímulos requieren autorización explícita del administrador; los supervisores no conceden permisos desde RCA.

## Procedimientos y alcance

| Escenario | Recurso experimental | Evidencia directa |
|---|---|---|
| HTTP HA | Backend HQ | Selección HQ → S1 → HQ y consulta HTTP desde S2 |
| LACP | Miembro s5c1 del agregador S1 | Miembros activos 2 → 1 → 2, cuatro sondas ICMP y HTTP |
| WAN | Interfaz HQ/s1p | Estado administrativo, FIB y retorno de las rutas preferidas |
| SDN | Puerto aislado sdna0 | A → B permitido/denegado/permitido, B → C aislado, Faucet conectado |
| Compuesto | WAN HQ/s1p y backend HTTP HQ | Degradaciones simultáneas y retorno de ambos recursos |

Los [ensayos HTTP y LACP](../../scripts/s07/ensayos_servicios_s07.py) reutilizan los procedimientos de disponibilidad y agregación. [La guarda WAN](../../scripts/s07/wan_trial_guard.py) fija la identidad del router, su sesión y la interfaz mediante pin, índice, dirección IPv4 y MAC. Se comprueba la identidad antes y después de la lectura. El temporizador independiente de retorno se arma antes del estímulo y el journal protegido registra sus estados. El [supervisor WAN/SDN](../../scripts/s07/ensayos_wan_sdn_s07.py) verifica las sondas y el alcance de los recursos. El [supervisor compuesto](../../scripts/s07/ensayo_compuesto_s07.py) exige dos retornos previamente armados y una ventana común a las dos degradaciones.

En cada escenario se adquieren tres ventanas: línea base, degradación y recuperación, con 58 observaciones por ventana. La aceptación exige señales elegibles del recurso, hipótesis y runbook correspondientes cuando la fuente tiene cobertura, y observación posterior al retorno. Se preservan los intentos no coincidentes. El preflight compara costos, FIB, OSPF y gestión; las ventanas se conservan separadas del historial operacional y de los datos de los modelos históricos.

## Validación

| Escenario | Ventanas aceptadas | Hipótesis durante la degradación | Incertidumbre |
|---|---:|---|---|
| HTTP | 3 | HTTP_BACKUP_SELECTED | SCOPED |
| LACP | 3 | LACP_MEMBER_DEVIATION | SCOPED |
| WAN | 3 | Tres FIB_BACKUP_SELECTED y WAN_ADMIN_DEVIATION | LIMITED y AMBIGUOUS |
| SDN | 3 | Ninguna hipótesis de fallo de puerto | Evidencia directa |
| Compuesto | 3 | HTTP_BACKUP_SELECTED, tres FIB_BACKUP_SELECTED y WAN_ADMIN_DEVIATION | SCOPED, LIMITED y AMBIGUOUS |
| Total | 15 | 11 | Según contexto |

En el ensayo WAN se verificaron selecciones de respaldo en HQ→S1, S1→HQ y S1→S2 y el retorno de las seis rutas preferidas. El escenario compuesto produjo cinco hipótesis, con dos brechas de cobertura en línea base/recuperación y seis durante la degradación. En los escenarios simples HTTP/LACP se verificó el retorno 3/3 de sus respectivas ventanas; la evaluación consolidada reprodujo las 15 ventanas seleccionadas y sus 870 observaciones. Las 11 hipótesis objetivo coincidieron y los 11 conjuntos de recomendaciones fueron correctos dentro de la selección evaluada, sin hipótesis inesperadas o faltantes.

El [evaluador histórico](../../scripts/s07/evaluar_ensayos_s07.py) contrasta contexto, argumentos, incertidumbre y ausencia de autorización. Una ventana derivada fuera de plazo produjo ABSTAIN_NO_CHANGE sin hipótesis; este control es offline, no un nuevo ensayo real. Se revalidó el rechazo real RESTORATION_APPROVAL_DENIED de OSPF y las pruebas aisladas de recuperación parcial. Los journals originales, siete servicios, gestión y 116 registros históricos se conservaron. La evaluación histórica terminó con 1226 pruebas ejecutadas, una omitida y cero fallos.

## Limitaciones

Las 870 observaciones de ventanas no son muestras estadísticamente independientes. La coincidencia de las hipótesis seleccionadas no permite estimar tasas poblacionales de falsas alarmas ni confirmar causalidad. El contrato de eventos observa el controlador SDN, no cada puerto; la falla de sdna0 fue verificada por evidencia directa. Las sondas son puntuales y no demuestran disponibilidad continua. Los mecanismos de retorno dependen del host y del proceso de recuperación operativo; no acreditan tolerancia a la pérdida del host. No se reentrenaron los modelos históricos congelados ni se autorizan acciones automáticamente.

## Documentación relacionada

[Correlación RCA](s07-contexto-y-correlacion-rca.md) · [Recuperación OSPF](s07-intervencion-ospf-y-watchdog.md) · [Evidencias de AIOps](../../evidencias/capturas/fase7/README.md).
