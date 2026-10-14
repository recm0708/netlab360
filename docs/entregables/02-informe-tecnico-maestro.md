# NETLAB360 — Documento 02: Manual técnico integral de implementación, administración y uso

**Índice V0.2 APROBADO por el usuario el 14/10/2026, sujeto a cambios si la profesora lo indica.** Entregable ÚNICO que reúne el antiguo informe de laboratorio y el antiguo manual de usuario. Debe permitir que un operador autorizado **reproduzca desde cero** la plataforma y luego la utilice. Redacción técnica impersonal y operativa, similar a un manual empresarial. **Portada institucional preparada por el usuario** y un índice general automático único.

## Preliminares
- Portada institucional (usuario).
- Presentación del manual, propósito y alcance de versión realmente entregada.
- Recomendación de lectura, destinatarios, símbolos de seguridad y convenciones.
- Índice general automático único.

## Índice general propuesto

1. **Introducción, finalidad y alcance del manual técnico.** Qué construye y qué permite operar NETLAB360; relación con Documento 01, destinatarios y límites reales.
2. **Objetivos técnicos de implementación y operación.**
   - 2.1 Objetivo general del manual.
   - 2.2 Objetivos específicos de instalación, validación, puesta en marcha y uso.
3. **Requisitos y planificación de la instalación.**
   - 3.1 Recursos del host, hipervisor y acceso necesario.
   - 3.2 Software y versiones compatibles **efectivamente comprobadas**.
   - 3.3 Plan de almacenamiento, VMnet8, red de gestión e IPAM de laboratorio.
   - 3.4 Prerrequisitos de seguridad, snapshot y respaldos.
4. **Preparación del equipo y creación de la máquina virtual.**
   - 4.1 Preparación y verificación del equipo anfitrión.
   - 4.2 Creación y asignación de recursos de la VM en VMware.
   - 4.3 Montaje e instalación de Ubuntu Desktop.
   - 4.4 Configuración inicial del sistema, actualizaciones y herramientas de VMware.
   - 4.5 Red de gestión, direccionamiento estático, SSH y comprobaciones.
   - 4.6 Instantánea inicial y punto de recuperación.
5. **Instalación y configuración de dependencias.**
   - 5.1 Sistema de paquetes, utilidades de red y seguridad.
   - 5.2 Docker, contenedores y namespaces.
   - 5.3 FRRouting y herramientas de verificación.
   - 5.4 Python, OpenTofu, Ansible y herramientas de automatización.
   - 5.5 Git/GitHub, pruebas automatizadas y entorno de desarrollo.
   - 5.6 Prometheus, exporter, componentes NOC y analítica efectivamente utilizados.
6. **Organización del proyecto y configuraciones base.**
   - 6.1 Estructura de directorios y convención de archivos.
   - 6.2 Obtención del repositorio y control de versiones.
   - 6.3 SoT/IPAM, VLAN, subredes, routers, enlaces WAN y roles.
   - 6.4 Separación entre red administrativa, redes de prueba y recursos temporales.
   - 6.5 Parámetros de operación y políticas de protección de datos.
7. **Implementación paso a paso de NETLAB360.** Recorrido desde un entorno limpio, por orden de dependencia; incorporar sólo módulos desarrollados. Cada módulo contendrá requisitos, comandos **válidos y depurados**, archivos usados, salidas esperadas y reales conocidas, figuras, pruebas, rollback y postcheck.
   - 7.1 Comprobaciones de laboratorio B0/B1 y validación IPAM.
   - 7.2 Segmentación VLAN, trunks 802.1Q y ACL/HTTP.
   - 7.3 Enrutamiento FRR/OSPF, WAN principal/respaldo y prueba de servicios.
   - 7.4 Agregación LACP y bonding active-backup de enlaces virtuales.
   - 7.5 Automatización SoT→OpenTofu→Ansible→FRRouting, idempotencia y compliance.
   - 7.6 Exporter, Prometheus, API y NOC inicial.
   - 7.7 Perfil estadístico y diagnóstico determinista de la evidencia B4.
   - 7.8 Módulos adicionales realmente terminados en las fases posteriores, integrados al mismo capítulo sin separar nuevos documentos.
8. **Verificación funcional, pruebas de aceptación y evidencias.**
   - 8.1 Precheck, verificaciones de conectividad y estado.
   - 8.2 Pruebas positivas, fallas controladas y restauración seguras.
   - 8.3 Pruebas de regresión, CI y contrastes con salidas esperadas.
   - 8.4 Capturas, interpretación, registros SHA256, control de versiones y criterios de aceptación.
9. **Puesta en marcha y acceso para el usuario.**
   - 9.1 Inicio de la VM y del entorno NETLAB360.
   - 9.2 Verificación de disponibilidad y acceso autorizado por CLI, SSH o navegador.
   - 9.3 Pantallas, navegación y paneles **realmente implementados**.
10. **Procedimientos de utilización y administración.**
    - 10.1 Consultar estado de sitios, interfaces y rutas.
    - 10.2 Iniciar y terminar escenarios de laboratorio.
    - 10.3 Simular fallas permitidas y verificar failover/restauración.
    - 10.4 Consultar telemetría, alertas y servicios.
    - 10.5 Inspeccionar resultados de automatización/compliance y datos históricos.
    - 10.6 Interpretar indicadores, restricciones y mensajes del sistema.
    - 10.7 Funciones añadidas y validadas en fases posteriores.
11. **Mantenimiento, actualización y recuperación.**
    - 11.1 Inicio/cierre seguro, parada de servicios y limpieza específica.
    - 11.2 Actualizaciones controladas del repositorio y dependencias.
    - 11.3 Backups, snapshots, restauración y comprobación de integridad.
    - 11.4 Gestión de credenciales y protección de la red administrativa.
12. **Diagnóstico preventivo y solución de problemas frecuentes.**
    - 12.1 Fallas de acceso SSH/gestión/VMware.
    - 12.2 Problemas Docker y namespaces, servicios/puertos ocupados.
    - 12.3 Configuración IPAM, VLAN, ACL, OSPF y conectividad HTTP.
    - 12.4 IaC, configuraciones y diferencias de compliance.
    - 12.5 Prometheus, exporter, alertas, dashboard y diagnóstico histórico.
    - 12.6 Restauración segura y escalamiento.
13. **Distribución y puesta en servicio de una copia.**
    - 13.1 Sanitización de datos privados y secretos EN COPIA destinada a entrega.
    - 13.2 Exportación OVF/OVA y SHA256, **sólo cuando realmente se realice**.
    - 13.3 Importación de prueba, primera ejecución y verificaciones.
14. **Recomendaciones de operación y seguridad.**
15. **Glosario y convenciones de comandos/indicadores.**
16. **Referencias técnicas.** Una sola bibliografía de fuentes externas efectivamente citadas.
17. **Anexos operativos, si se requieren.** Configuraciones extensas y tablas auxiliares; no usar anexos como reemplazo del procedimiento principal.

## Estructura fija de cada procedimiento (en el capítulo donde corresponda)

1. **Objetivo y función:** qué se prepara y para qué sirve.
2. **Requisitos, entradas y controles de seguridad:** imagen/snapshot, rutas de proyecto, permisos, interfaz de gestión a proteger.
3. **Preparación en orden comprobado:** comandos completos corregidos, sin repetir historiales de equivocaciones personales.
4. **Configuración y ejecución:** comando exacto validado, explicación de parámetros y ubicación de archivos.
5. **Resultado esperado, salida observada e interpretación:** no confundir salida histórica con nueva ejecución; evidencia y figura con preámbulo APA7.
6. **Validaciones funcionales:** comprobaciones, código de retorno, caso positivo/negativo y condiciones de aceptación.
7. **Si aparece un problema:** síntomas, causas posibles y acciones correctivas seguras **contemporáneas al paso**; indicar si solución verificada o recomendación pendiente.
8. **Cierre/limpieza/reversión y postcheck:** verificación de no afectar ens33/VMnet8, Docker/netns y Git.
9. **Trazabilidad:** script, archivo, log, PNG auditado y commit sin divulgar claves.

## Diferencia obligatoria frente al Documento 01

- Aquí **NO** se narran los incidentes históricos sufridos por el grupo. Se enseña la instalación **correcta desde cero**, con configuración depurada y un apartado contextual «si se produce X, verificar Y».
- En el Documento 01 **SÍ** se narran incidentes técnicos reales y cómo el equipo los mitigó, integrados en desarrollo de su fase.
- No documentar como implementados un NOC integral, IA/ML entrenada, recuperación de switches físicos ni OVA no probada; agregar solo cuando existan evidencias.
- No pegar 86 capturas indiscriminadamente. Seleccionar imágenes concretas y etiquetarlas con APA7 y explicación anterior. Una sola numeración de figuras en todo el manual.
- En la edición académica, redactar en tercera persona o instrucción profesional («compruebe», «ejecute», «se obtiene»), no en primera persona autobiográfica.
- El documento final cubre **hasta la última fase realmente concluida**, sin capítulos vacíos de etapas que no se realizaron; no falsear el plan original del repositorio ni cambiar la rúbrica sin acuerdo docente.

**Próximo inicio editorial:** 1. Introducción y finalidad del manual técnico, después de que el usuario avance con el Documento 01. La prioridad inicial del usuario será comenzar la redacción del Documento 01.
