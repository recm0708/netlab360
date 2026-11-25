# Contrato y persistencia de trabajos de diagnóstico

El catálogo unificado admite 34 combinaciones de acción, ruta y perfil. Calculamos el plazo máximo desde los perfiles internos. Rechazamos parámetros adicionales, comandos, direcciones, tasas y volúmenes libres. El catálogo indica ejecución deshabilitada hasta disponer del servicio protegido.

## Ciclo de vida

Reutilizamos las tablas jobs y audit_events del esquema vigente sin migración. Cada trabajo conserva su selección, plazo, actor, marcas temporales y resultado. Una transacción BEGIN IMMEDIATE reserva una única plaza activa por base, incluidos los trabajos en cola. Solo un operador habilitado puede solicitar, consultar o cancelar su propio trabajo. La identidad se obtendrá de la sesión autenticada al integrar HTTP; no se aceptará un actor suministrado por el navegador.

Las transiciones son QUEUED a RUNNING, QUEUED a CANCELLED y RUNNING a SUCCEEDED o FAILED. SUCCEEDED significa que se obtuvo una medición, no que la conectividad sea satisfactoria. La cancelación de un trabajo activo se incorporará con el mecanismo de terminación y limpieza. No liberamos una plaza activa por simple vencimiento de tiempo ni damos por terminada una ejecución sin verificar limpieza. La recuperación después de interrupción requiere reconciliar el estado del servicio protegido.

## Frontera de ejecución

Esta implementación no abre rutas HTTP, sockets ni procesos. La exclusión de SQLite solo cubre una base; el servicio protegido impondrá una exclusión independiente del número de instancias web y bases. Instalaremos código revisado de propiedad root en una ruta no modificable por el usuario web y una interfaz Unix con identidad de servicio, validación del par y solicitudes de tamaño limitado. No otorgaremos sudo genérico a FastAPI ni ejecutaremos código editable del repositorio con privilegios. Los workers de contenido se ejecutarán con identidad sin privilegios.

Antes de habilitar ejecución se requieren pruebas de autorización, límites, cancelación, limpieza, recuperación y aislamiento de sesiones. Se conservarán las mediciones y los eventos de progreso reales sin presentar resultados simulados como observaciones. No se autoriza desde este contrato una intervención WAN, LACP o HA.
