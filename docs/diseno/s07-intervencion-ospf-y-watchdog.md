# Intervención OSPF y recuperación independiente

## Descripción

El alcance experimental es R-S1/s1b, con costo OSPF deseado 100, desviación temporal 150 y retorno a 100. No se persiste la configuración FRRouting. La recuperación independiente protege frente a la pérdida del proceso supervisor mientras el host, Docker y systemd permanecen operativos.

## Ensayo aislado

El [ensayo protegido](../../scripts/s07/recovery_rehearsal.py) utiliza un archivo root-owned, no un router. Registra PREPARED, ARMED, APPLYING, DRIFT_APPLIED, RECOVERING, RECOVERED y ESCALATION_REQUIRED mediante escrituras atómicas sincronizadas. Vincula identificador, boot ID y valores permitidos.

El temporizador systemd de 15 s exige un margen mínimo de 4 s y se arma antes de modificar el archivo. La recuperación compara identidad y valor observado; no altera valores inesperados. Se verificó la secuencia 100→150→100 en 15,089 s, con gestión, OSPF, FIB y bases SQLite intactas. Este resultado demuestra recuperación aislada, no rollback de OSPF.

## Ejecutor operacional

El [ejecutor](../../scripts/s07/ospf_trial.py) fija el perfil y verifica estado inicial, boot ID, identidades Docker, PID y ticks de inicio, costos, adyacencias, rutas, seis sondas ICMP y el frontal HTTP desde S2. El watchdog de 90 s se arma antes de escribir y comparte el bloqueo cooperativo del preflight. La restauración se realiza mediante segunda aprobación administrativa o retorno de emergencia; exige identidad y costo conocido, no depende de que las adyacencias o HTTP estén sanos. Solo admite comandos FRR fijos, sin write memory.

Las postcondiciones completas permiten VERIFIED. Una restauración no comprobada se identifica como RESTORED_UNVERIFIED o ESCALATION_REQUIRED según corresponda. El mecanismo de autorización posterior se describe en [Intent Assurance y RFC](s07-intent-assurance-y-rfc.md).

## Validación y métricas

Dos ensayos reales independientes verificaron 100→150→100. En el primero, la frase incorrecta de restauración fue rechazada con RESTORATION_APPROVAL_DENIED y el watchdog realizó el retorno. En el segundo, la segunda confirmación fue aceptada y el origen del retorno fue HUMAN_APPROVED. Ambos finalizaron VERIFIED.

| Métrica (s) | Watchdog | Aprobación humana |
|---|---:|---:|
| Verificación del drift | 0,700264 | 0,698642 |
| Decisión y revalidación | No aplicable | 11,179696 |
| Actuación desde aprobación | No aplicable | 0,500384 |
| Restauración efectiva | 0,384864 | 0,399483 |
| Postverificación | 0,704518 | 0,703804 |
| Ciclo desde DRIFT_APPLIED | 91,275855 | 13,082526 |

Se conservaron los siete costos no intervenidos, ocho adyacencias FULL, seis selecciones FIB principales, seis sondas ICMP y HTTP disponible en las observaciones. La gestión, siete servicios y 116 registros históricos permanecieron intactos. El [comparador](../../scripts/s07/comparar_ciclos_ospf.py) reprodujo los intervalos a partir de los journals protegidos, sin nuevos estímulos. La regresión de la comparación comprendió 1177 pruebas, una omitida y ninguna fallida.

## Limitaciones

Los intervalos derivan del reloj monotónico. La diferencia descriptiva de 78,193329 s incluye la espera programada del watchdog y no constituye SLA, comparación estadística ni tiempo de reacción humana aislado. Las sondas no miden disponibilidad continua. Los dos ensayos corresponden al ejecutor administrativo; el broker operacional y la API se validaron posteriormente con solicitudes independientes. El bloqueo es cooperativo y no acredita protección frente a un administrador malicioso, sustitución externa del recurso ni arranque frío.

## Documentación relacionada

[Pruebas de recuperación aislada](../../tests/test_s07_recovery_rehearsal.py) · [Pruebas del ejecutor](../../tests/test_s07_ospf_trial.py) · [Evidencias de la fase 07](../../evidencias/capturas/fase7/README.md).
