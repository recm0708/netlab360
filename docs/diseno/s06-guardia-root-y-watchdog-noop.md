# S06-038A — Guardia protegida, temporizador root y prueba sin cambios de red

## Criterio de entrada: S06-037 acreditado

En Ubuntu `S06-037_SIMULACION_VALIDADA=OK`, RC=0; 21 tests específicos y 478 offline aprobados. Los catorce casos de simulación incluyeron cuatro estados RESTORED, uno ABORTED, dos ESCALATED, cinco NEW y dos APPROVED. El reporte privado es `S06_037_20261123T051618Z_66720c/simulacion_rollback.json`. Las qdiscs reales permanecen noqueue; la gestión ens33 `192.168.47.40/24`, gateway `192.168.47.2`, y la topología NOC siguen intactas.

**Ninguna restauración real ni etiqueta de entrenamiento está acreditada.**

## Objetivo del incremento S06-038A

Instalar una copia protegida del programa `scripts/s06/guardia_protegida.py` en `/usr/local/libexec/netlab360/s06-guardia.py` con propietario root y permisos 0750. El script instalado requiere ejecución con privilegios de root, valida el propietario de su ruta y no acepta namespace ni interfaz arbitrarios.

El único recurso que escribe es su estado privado en `/run/netlab360-s06/guardia.json` y un lock del mismo directorio. El temporizador independiente de systemd vuelve a invocar el programa protegido con un token temporal para marcar la expiración. **La qdisc no se modifica jamás en S06-038A.** Este subpaso comprueba seguridad de instalación, privilegios, temporizador, estado y lock, pero todavía NO es un watchdog capaz de restaurar tráfico.

## Opciones permitidas

- `audit`: solo lectura de ens33, gateway y cliente `nl360-s02-h-hq-120/eth0` con IP `10.70.20.20/24`, ruta `10.70.20.1`, qdisc `noqueue`, conteo 21 namespaces.
- `arm-test --ttl 8`: estado root privado, lock exclusivo y temporizador systemd transitorio. TTL entre 5 y 30 segundos, sin ejecutar netem ni operaciones tc mutadoras.
- `status`: consulta el estado actual del temporizador en `/run/netlab360-s06`. Se espera `EXPIRED_NOOP` cuando el temporizador termine y los prechecks sigan correctos.
- `expire --token`: uso del temporizador exclusivamente; no debe invocarse manualmente. Solo acepta token hexadecimal exacto con registro root correspondiente.
- `cleanup`: libera el registro únicamente si el estado ha expirado satisfactoriamente y la qdisc/gestión siguen exactamente en el baseline. No borra archivos ajenos y no deshace redes.

## Instalación de laboratorio

El operador debe tener un repositorio limpio con el PR correspondiente fusionado y ejecutar el script de instalación con una llamada explícita a `sudo install`, jamás con `sudo bash` sobre un archivo mutable del repositorio. La carpeta `/usr/local/libexec/netlab360/` debe ser root-owned y no escribible por terceros. La copia instalada debe compararse con la versión versionada antes de invocarla. No se agregan reglas sudoers ni contraseñas en scripts.

Los ficheros del directorio protegido de ejecución efímera `/run/netlab360-s06/` son propiedad de root, modos 0700/0600; las opciones de estado no confían en enlaces simbólicos. Un estado activo, inconsistente o de origen desconocido impide iniciar otro.

## Validaciones exigidas

1. Git limpio y pruebas offline generales aprobadas antes de instalar.
2. Script y carpeta instalada propiedad de root, sin escritura de terceros, comparación con archivo fuente.
3. `audit` con ens33, gateway, cliente, rutas, namespaces y qdisc esperada.
4. `arm-test` programa timer temporal con token y TTL fijado.
5. `status` llega a `EXPIRED_NOOP` de forma independiente; fallo significa **no aprobado**, sin ejecutar cambios.
6. `cleanup` solo si la expiración fue confirmada; el siguiente `status` será NONE.
7. Pre/post invariantes: 21 namespaces, cuatro contenedores, qdisc noqueue, siete servicios, NOC 18/21, gestión y repositorio intactos.
8. Documentar rechazo ante parámetros incorrectos, concurrencia, estado extraño o configuración ajena.
9. No se ejecuta ni marca ninguna prueba REAL de rollback de qdisc. Los resultados de esta etapa no permiten todavía un experimento de degradación.

## Próximo gate: S06-038B/039

El mecanismo real todavía necesita un ejecutor privilegiado que pueda actuar únicamente sobre una qdisc PROPIA identificable, con tiempo máximo, aprobación humana y verificación independiente. El watchdog deberá estar armado antes de instalar la qdisc; la condición de propiedad no podrá inferirse solo del nombre de interfaz ni de archivos bajo control del usuario. Antes de intervenir, probar recuperación con fallas de proceso y carreras de estados en un escenario aislado.

No cerrar #6, #25 ni #26 hasta cumplir sus criterios. Los logs de guardianía y las sesiones observacionales permanecen privados.
