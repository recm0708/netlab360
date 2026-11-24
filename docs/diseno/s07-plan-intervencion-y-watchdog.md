# Plan de intervención y ensayo de recuperación independiente S07

## Alcance S07-005G y S07-006A–D

[Plan y ensayo protegido](../../scripts/s07/recovery_rehearsal.py) define exclusivamente el perfil experimental R-S1/s1b: costo deseado 100, desviación controlada prevista 150 y retorno a 100, sin persistir configuración FRR. Este bloque NO habilita el ejecutor OSPF. El backend habilitado es un archivo aislado protegido, no un router. La máquina de estados registra PREPARED, ARMED, APPLYING, DRIFT_APPLIED, RECOVERING, RECOVERED y ESCALATION_REQUIRED. El journal se escribe de forma atómica con sincronización a disco. Se vinculan identificador del ensayo, boot ID, alcance y valores permitidos.

## Watchdog independiente

Se arma una unidad transitoria systemd con temporizador de 15 s antes de alterar el archivo de ensayo. Se exige temporizador activo y margen mínimo de 4 s. El temporizador ejecuta el mismo artefacto root-owned en un proceso independiente; el proceso de ensayo termina sin restaurar el archivo. La recuperación compara la identidad y el valor observado, restaura únicamente el valor experimental conocido y comprueba la postcondición; no modifica estados inesperados. La prueba de reinicio de proceso no representa arranque frío del host. El bloqueo es cooperativo; la recuperación se limita al artefacto aislado. [Pruebas](../../tests/test_s07_recovery_rehearsal.py).

## Gate real

El perfil experimental no es aún un RFC operacional de cambio. Antes del primer estímulo real, integrar aprobación explícita de experimento y restauración, identidad de contenedor y sesión, preflight reciente, guardia independiente sobre el router, verificación de configuración y disponibilidad, y escalamiento. No reutilizar un RFC de lectura ni un preview. Los resultados del ensayo de archivo no prueban rollback de OSPF ni tolerancia a caída de Docker. Aceptación del ensayo aislado S07-005G–006AD-R: recuperación 100→150→100 en 15,089 s; temporizador transitorio ya descargado, sin repetir el estímulo. Costos, vecinos, FIB y gestión intactos, tres bases SQLite íntegras, 1153 pruebas ejecutadas (una omitida); CI 45323731597 satisfactoria.

## Primer ciclo OSPF real supervisado — S07-006E

[Ejecutor acotado](../../scripts/s07/ospf_trial.py), [pruebas](../../tests/test_s07_ospf_trial.py). El administrador solicita un ensayo para un único perfil, aprueba explícitamente 100→150 y autoriza el retorno de emergencia. Se vincula el journal protegido al estado inicial, boot ID, IDs Docker, PID y ticks de inicio; se verifica el perfil completo, adyacencias, rutas, seis sondas ICMP entre loopbacks y el frontal HTTP desde S2-320. El watchdog de 90 s se arma antes de escribir y utiliza el mismo bloqueo cooperativo del preflight. Una segunda aprobación explícita autoriza restaurar 150→100; si no llega, el temporizador intenta recuperar independientemente. La restauración no depende de que HTTP o las adyacencias estén sanos; sí de que la sesión del objetivo y el costo conocido coincidan. Solo se ejecutan comandos FRR fijos, sin write memory. Se exige postcondición completa, de lo contrario RESTORED_UNVERIFIED o ESCALATION_REQUIRED. La aprobación de este ensayo se realiza por un administrador Linux con sudo y terminal; no es una identidad independiente del solicitante ni integración completa del broker RFC operacional. El watchdog depende del host y Docker disponibles; no acredita arranque frío. La aceptación del estímulo y del retorno de emergencia se obtuvo en S07-006E; la restauración humana explícita fue aceptada en S07-006F.

## Resultados de recuperación real — S07-006E (23/11/2026)

RFC 2f7d1cbf60444b90bb7281125a65fb4f. El administrador aprobó el estímulo 100→150 en R-S1/s1b. Se verificó el drift en 0,700264 s desde DRIFT_APPLIED. La confirmación de restauración utilizó por error la frase de aprobación del ensayo, fue rechazada con RESTORATION_APPROVAL_DENIED y no se canceló el watchdog. El temporizador restauró el costo 100; estado VERIFIED con origen WATCHDOG y 91,275855 s desde DRIFT_APPLIED hasta la postcondición completa. Los otros siete costos, ocho adyacencias FULL, seis selecciones FIB principales, seis sondas ICMP y el frontal HTTP desde S2 fueron conformes en las observaciones de línea base, drift y recuperación; no se infiere disponibilidad continua. Gestión, siete servicios y 116 registros operacionales conservados. 1168 pruebas ejecutadas, una omitida, cero fallos; CI 45327785372 satisfactoria. El rechazo consta en la salida del comando, no como evento separado del journal protegido de esta versión. No se atribuye este retorno a una aprobación manual. S07-006F verificó una segunda solicitud independiente con restauración HUMAN_APPROVED, conservando los registros de S07-006E.

## Restauración humana explícita — S07-006F (23/11/2026)

RFC c9db14c3cd87496db05073bf4484f8d0: ambas confirmaciones administrativas aceptadas, watchdog armado previamente, costo 100→150→100 y estado VERIFIED con origen HUMAN_APPROVED. Ocho costos conformes al cierre, ocho vecinos FULL, seis rutas principales, seis sondas ICMP y HTTP desde S2 disponibles en las observaciones. Temporizador retirado únicamente tras verificar. Los 116 registros históricos permanecieron intactos; 1168 pruebas ejecutadas (una omitida, cero fallos). El journal del primer ensayo fue revalidado sin cambios. No se observó una ejecución CI para el commit exclusivamente documental durante S07-006F; la CI del código ejecutado fue 45327785372.

| Métrica (s) | Watchdog S07-006E | Aprobación humana S07-006F |
| --- | ---: | ---: |
| Verificación del drift | 0,700264 | 0,698642 |
| Decisión y revalidación | No aplicable | 11,179696 |
| Actuación desde aprobación | No aplicable | 0,500384 |
| Postverificación desde restauración | 0,704518 | 0,703804 |
| Ciclo desde DRIFT_APPLIED | 91,275855 | 13,082526 |

Los intervalos principales se derivan del reloj monotónico del journal. La diferencia entre los dos ciclos incluye la espera programada del watchdog. No representa un SLA ni una comparación estadística generalizable. La decisión incluye la revalidación previa, no exclusivamente reacción humana. El flujo sudo de intervención no equivale todavía a un broker operacional con separación de roles. El comparador [de ciclos OSPF](../../scripts/s07/comparar_ciclos_ospf.py) usa únicamente registros históricos, comprueba las postcondiciones y distingue los orígenes de recuperación. No modifica la red.

S07-007A revalidó ambos journals contra los registros protegidos originales, sin repetir estímulos. Restauración efectiva (RESTORING→RESTORED_UNVERIFIED): 0,384864 s y 0,399483 s; diferencia descriptiva del ciclo: 78,193329 s. 1177 pruebas ejecutadas (una omitida), CI 45328939211 satisfactoria.
