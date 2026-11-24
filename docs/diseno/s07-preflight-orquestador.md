# Preflight privilegiado del orquestador — Fase 07

## Descripción e identidad protegida

Implementamos el [preflight](../../scripts/s07/preflight_protegido.py) y sus [pruebas](../../tests/test_s07_preflight_protegido.py) como primera frontera de lectura de #194. El administrador registra una sola vez los IDs de los tres routers existentes, comprobando identidad Docker, proyecto, modo de red none, perfil de ocho costos, ocho vecinos FULL y seis selecciones FIB principales. El pin root-owned 0600 no se reemplaza automáticamente; el alta inicial confía en el administrador del laboratorio. Se revalida identidad y PID durante cada lectura, se protege ens33 y gateway, se comprueba carga por CPU y memoria disponible, y se limita la ventana a 30 segundos. El bloqueo flock no bloqueante protege solo las ejecuciones que cooperan con el mismo archivo; no sustituye una exclusión global de todas las herramientas del host. Los parsers se reutilizan de las fases 03 y 07 sin importar archivos ejecutables de un HOME editable.

## Operaciones y límites

El módulo tiene únicamente operaciones enroll/check, no recibe comandos ni rutas de red arbitrarios y no escribe configuración. La única escritura funcional es la identidad inicial protegida y el archivo de bloqueo. Se instala root-owned fuera del repositorio editable. No utiliza el resultado de un RFC preview como permiso de intervención. Una lectura completa puede demostrar estado de control/selección local; no mide disponibilidad extremo a extremo ni autoriza una mutación. La aprobación operacional, la ejecución y la recuperación se implementan en componentes separados; el preflight conserva su carácter de solo lectura.

## Validación

Comprobamos en S07-005A–C: tres identidades protegidas, ocho costos conformes, ocho vecinos FULL y seis rutas principales. Preflight 0,567451 s, carga por CPU 0,090, memoria disponible 13362,3 MiB. Bloqueo cooperativo, rechazo de acción execute, reemplazo del pin y ejecución sin root comprobados. 1122 pruebas ejecutadas (una omitida), CI 45322244337 satisfactoria. Gestión y siete servicios intactos.
