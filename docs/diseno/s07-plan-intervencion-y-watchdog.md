# Plan de intervención y ensayo de recuperación independiente S07

## Alcance S07-005G y S07-006A–D

[Plan y ensayo protegido](../../scripts/s07/recovery_rehearsal.py) define exclusivamente el perfil experimental R-S1/s1b: costo deseado 100, desviación controlada prevista 150 y retorno a 100, sin persistir configuración FRR. Este bloque NO habilita el ejecutor OSPF. El backend habilitado es un archivo aislado protegido, no un router. La máquina de estados registra PREPARED, ARMED, APPLYING, DRIFT_APPLIED, RECOVERING, RECOVERED y ESCALATION_REQUIRED. El journal se escribe de forma atómica con sincronización a disco. Se vinculan identificador del ensayo, boot ID, alcance y valores permitidos.

## Watchdog independiente

Se arma una unidad transitoria systemd con temporizador de 15 s antes de alterar el archivo de ensayo. Se exige temporizador activo y margen mínimo de 4 s. El temporizador ejecuta el mismo artefacto root-owned en un proceso independiente; el proceso de ensayo termina sin restaurar el archivo. La recuperación compara la identidad y el valor observado, restaura únicamente el valor experimental conocido y comprueba la postcondición; no modifica estados inesperados. La prueba de reinicio de proceso no representa arranque frío del host. El bloqueo es cooperativo; la recuperación se limita al artefacto aislado. [Pruebas](../../tests/test_s07_recovery_rehearsal.py).

## Gate real

El perfil experimental no es aún un RFC operacional de cambio. Antes del primer estímulo real, integrar aprobación explícita de experimento y restauración, identidad de contenedor y sesión, preflight reciente, guardia independiente sobre el router, verificación de configuración y disponibilidad, y escalamiento. No reutilizar un RFC de lectura ni un preview. Los resultados del ensayo de archivo no prueban rollback de OSPF ni tolerancia a caída de Docker. Aceptación en VM pendiente.
