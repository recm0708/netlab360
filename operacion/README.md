# Instalación y operación de NETLAB360

## Descripción

Centralizamos los procedimientos necesarios para preparar,
desplegar, comprobar y recuperar el laboratorio.

Reutilizamos los componentes versionados de scripts,
servicios, inventario, topologías y configuración,
sin duplicar sus implementaciones.

## Componentes disponibles

| Componente | Función |
|---|---|
| [Catálogo de comandos](comandos/README.md) | Procedimientos organizados por fase y alcance |
| [preparar-runtime.sh](preparar-runtime.sh) | Preparar configuraciones y binarios de ejecución |
| [instalar_servicios.py](instalar_servicios.py) | Instalar unidades y política de observación revisadas |
| [reconstruir.py](reconstruir.py) | Reconstruir la topología de referencia en una VM nueva preparada |
| [desplegar.sh](desplegar.sh) | Consultar la secuencia de reconstrucción |
| [estado.sh](estado.sh) | Comprobar el estado operacional de referencia |
| [ciclo_vida.py](ciclo_vida.py) | Organizar las dependencias del despliegue y la detención |
| [instalar-protegidos.sh](instalar-protegidos.sh) | Preparar e instalar ejecutores protegidos en una VM nueva |
| [configurar.sh](configurar.sh) | Generar configuraciones sin activar el laboratorio |
| [componentes-protegidos.tsv](componentes-protegidos.tsv) | Fuentes y destinos de los ejecutores privilegiados |
| [instalar.sh](instalar.sh) | Instalar dependencias del laboratorio |
| [verificar.sh](verificar.sh) | Comprobar requisitos del sistema sin instalar paquetes |
| [imagenes.tsv](imagenes.tsv) | Registrar referencias inmutables de imágenes OCI |
| [Perfil Ubuntu 26.04](perfiles/ubuntu-26.04-amd64/README.md) | Inventario de dependencias del sistema |
| [Dependencias científicas](../requirements-cientifico.txt) | Versiones de bibliotecas Python observadas |

## Verificación inicial

Ejecutamos el siguiente comando desde la raíz del repositorio:

```bash
bash operacion/verificar.sh
```

La comprobación distingue paquetes ausentes, dependencias
opcionales y diferencias respecto del entorno de referencia.

## Instalación de dependencias

Utilizamos una máquina virtual Linux dedicada, sin una
topología NETLAB360 previa ni contenedores de terceros.

Consultamos primero el plan:

```bash
bash operacion/instalar.sh --plan
```

Para instalar las dependencias en una VM limpia:

```bash
bash operacion/instalar.sh --apply --confirm-clean-host
```

El administrador debe comprobar las huellas de las llaves
oficiales antes de autorizar los repositorios externos.

Podemos solicitar las versiones exactas observadas mediante
`--exact-versions`. Si las versiones no están disponibles,
el procedimiento debe detenerse y revisarse; no utilizamos
una degradación automática de paquetes.

El modo normal utiliza versiones disponibles en las fuentes
APT y comunica las diferencias frente al inventario de referencia.
Las distribuciones Python se instalan con versiones exactas
y las imágenes OCI se descargan por digest.

La opción `--with-optional` incorpora utilidades auxiliares.
Las herramientas específicas de VMware, escritorio y eBPF
requieren una selección acorde con la plataforma.

Docker Engine, Open vSwitch y otros paquetes pueden crear
servicios, interfaces virtuales o reglas propias durante su
instalación. Por ello utilizamos exclusivamente un anfitrión
dedicado y no un equipo de producción.

Si una instalación falla parcialmente, revisamos su estado
antes de continuar. No eliminamos automáticamente paquetes,
fuentes APT, entornos virtuales ni contenedores para repetirla.

El modo de instalación real aún requiere una validación
independiente desde un sistema limpio. El modo de planificación
no acredita por sí solo el éxito de la instalación.

## Preparación de configuraciones

Generamos los archivos de configuración desde el inventario
versionado, sin utilizar los estados privados de nuestra
instalación original.

Consultamos el procedimiento:

```bash
bash operacion/configurar.sh --plan
```

Preparamos un directorio nuevo, fuera del repositorio:

```bash
bash operacion/configurar.sh --prepare "$HOME/netlab360-configuracion"
```

El generador produce tres configuraciones FRRouting, trece
fuentes de ejecutores protegidos, siete unidades systemd,
configuración Prometheus, reglas de alertas, configuración
Faucet y una regla sudoers candidata de alcance fijo.

El directorio generado no constituye una instalación activa.
Los ejecutores preparados todavía pertenecen al usuario que
generó el paquete y no deben ejecutarse como root desde allí.

Para instalar componentes privilegiados se requiere una
fuente confiable revisada por el administrador, propiedad
root, permisos verificados y ausencia de enlaces simbólicos
o rutas modificables por usuarios no autorizados.

Las unidades conservan inicialmente las rutas del perfil
histórico. La adaptación a otros usuarios, interfaces,
direcciones y nombres de anfitrión debe mantener las
comprobaciones de identidad y autorización.

La unidad permanente de Prometheus es candidata y no
sustituye automáticamente una instancia activa.

Generaremos nuevas identidades de routers únicamente
después de validar la topología reconstruida. No copiamos
pins de contenedores, solicitudes RFC, locks, temporizadores,
autorizaciones ni bases de datos históricas.

## Instalación de componentes protegidos

Separamos la preparación de configuraciones de la instalación
privilegiada. Consultamos los ejecutores, destinos, propietarios
y permisos mediante:

```bash
bash operacion/instalar-protegidos.sh --plan
```

La instalación efectiva requiere una VM dedicada y limpia,
con el perfil de referencia verificado, sin namespaces,
contenedores, unidades NETLAB360 ni estados anteriores.

El administrador debe obtener una copia independiente de las
fuentes, verificar su procedencia, revisar el código y conservar
esa copia en un directorio protegido, propiedad de root:root,
sin escritura para usuarios no autorizados.

Desde esa copia administrativa revisada:

```bash
sudo /usr/bin/python3 -I operacion/instalar_protegidos.py     --apply     --confirm-clean-host     --confirm-reviewed-source
```

No ejecutar el modo de instalación desde un repositorio
modificable por un usuario ordinario. Las confirmaciones no
sustituyen la revisión administrativa de las fuentes.

El instalador no sobrescribe ejecutores ni directorios de estado.
Si una instalación queda incompleta, deben inspeccionarse los
destinos antes de repetirla. No se elimina automáticamente
ningún componente existente.

La preparación de las identidades de los routers se realiza
después de reconstruir y validar OSPF y FIB. El registro de
identidades no equivale a la aprobación de una actuación RFC.

Los directorios temporales de los controladores y watchdogs
se crean mediante sus respectivos ejecutores. No trasladamos
solicitudes RFC, bases de datos, identidades ni autorizaciones
de otras instalaciones.

Las unidades systemd y la regla sudoers requieren una etapa
independiente de validación e instalación. No se activan
durante la instalación de los ejecutores protegidos.

El modo de planificación y las pruebas offline no acreditan
todavía la instalación efectiva en una VM nueva.

## Preparación del runtime y servicios

Preparamos los archivos que consumen FRRouting, Faucet y
Prometheus sin iniciar los componentes del laboratorio.

Consultamos el plan desde el repositorio del operador:

```bash
bash operacion/preparar-runtime.sh --plan
```

La preparación efectiva se realiza exclusivamente en una
VM nueva, después de instalar y verificar las dependencias:

```bash
sudo -v
bash operacion/preparar-runtime.sh --apply --confirm-clean-host
```

El procedimiento comprueba el aislamiento, conserva los
destinos existentes y utiliza configuraciones generadas
desde las fuentes versionadas.

Preparamos el directorio de logs de Faucet con propiedad root,
grupo del operador y permisos 0750, conforme al perfil de
referencia observado. Prometheus utiliza la referencia
inmutable registrada en el inventario de imágenes OCI.

Instalamos los ejecutores protegidos antes de las unidades
systemd. Para las operaciones administrativas utilizamos
una copia independiente del repositorio, revisada,
propiedad de root y sin escritura para usuarios ordinarios.

Consultamos las unidades y destinos:

```bash
python3 operacion/instalar_servicios.py --plan
```

Desde la copia administrativa protegida y revisada:

```bash
sudo /usr/bin/python3 -I operacion/instalar_servicios.py --apply --confirm-clean-host --confirm-reviewed-source
```

El instalador comprueba las fuentes, los destinos, la
sintaxis de systemd y sudoers. La política del observador
autoriza exclusivamente la operación snapshot.

No habilitamos ni iniciamos las unidades durante su
instalación. Su inicio corresponde a la secuencia de
reconstrucción, después de comprobar las redes necesarias.

No utilizamos estos instaladores para sustituir servicios
activos ni para actualizar una instalación existente.

La instalación efectiva en una VM limpia requiere
validación independiente.

## Ciclo de vida del laboratorio

Organizamos el despliegue desde las dependencias del sistema
hasta la aceptación operacional de las siete primeras fases.

Consultamos la secuencia de reconstrucción:

```bash
bash operacion/desplegar.sh --plan
```

El plan identifica los componentes existentes, su orden,
los argumentos de confirmación y las puertas de aceptación.
No ejecuta acciones de construcción.

Iniciamos los routers antes de construir WAN y LAN.
Después incorporamos las redes HTTP HA, LACP y SDN.
Los servicios de aplicación y observabilidad requieren
sus dependencias de red y configuración previamente
validadas.

Las identidades de los nuevos routers se registran mediante
el ejecutor protegido después de comprobar la línea base.

No iniciamos automáticamente sesiones experimentales,
entrenamiento, fallas controladas ni actuaciones RFC.

### Reconstrucción operacional en una VM nueva

Separamos la reconstrucción de la recuperación de una instalación
existente. La primera exige una VM dedicada, sin contenedores,
namespaces, bridges OVS ni registros de propiedad anteriores.

El perfil actual conserva la identidad administrativa de referencia.
No conectamos simultáneamente dos máquinas con la misma dirección IP.

Antes de reconstruir, instalamos las dependencias y las fuentes
protegidas revisadas. Preparamos las configuraciones FRR, Faucet
y Prometheus, los directorios de trabajo, los binarios y las siete
unidades systemd. La instalación de las unidades y de la política
del observador requiere revisión administrativa separada.

Los componentes de observabilidad se inician después de validar
la WAN y las VLAN. El precheck HA requiere el exporter y el NOC.
Los cuatro servicios HTTP deben estar activos antes de LACP.

Consultamos la secuencia:

```bash
python3 operacion/reconstruir.py --plan
```

Comprobamos las precondiciones de la VM nueva:

```bash
sudo -v
python3 operacion/reconstruir.py --check-clean
```

El modo de ejecución requiere confirmación explícita de la VM
nueva, una salvaguarda real, la revisión de configuraciones
y el registro de identidades nuevas.

Una vez satisfechas todas las precondiciones, el comando
candidato de reconstrucción en una VM nueva es:

```bash
python3 operacion/reconstruir.py --apply --confirm-clean-host --confirm-snapshot --confirm-reviewed-config --confirm-new-identity
```

Este comando no constituye una autorización para reconstruir
una instalación existente ni acredita un despliegue completo
hasta que se ejecute y valide en una VM independiente.


No utilizamos el modo de ejecución para reparar una VM existente.
Ante un resultado incompleto conservamos los registros y no
repetimos automáticamente la construcción.

El procedimiento genera identidades nuevas, no restaura
autorizaciones RFC anteriores ni reproduce los conjuntos
de datos y modelos históricos de aprendizaje automático.

La ejecución completa desde una VM limpia y la recuperación
después de un arranque en frío requieren validación independiente.

### Consulta del estado operacional

Con el laboratorio de referencia activo:

```bash
sudo -v
bash operacion/estado.sh
```

Comprobamos la red administrativa, los cuatro contenedores,
los 21 namespaces, los siete servicios, el preflight protegido,
la disponibilidad del NOC y el objetivo de Prometheus.

Esta consulta es no mutadora respecto de la infraestructura
de red. El preflight utiliza su mecanismo de exclusión mutua.
No sustituye los ensayos de conectividad y aceptación integral.

### Detención y recuperación

Consultamos el orden inverso de dependencias mediante:

```bash
python3 operacion/ciclo_vida.py shutdown-plan
```

La detención de servicios es distinta del desmontaje de
topología. La retirada requiere comprobar la propiedad
de los recursos y conservar los estados que correspondan.

La reconstrucción automática y la recuperación después
de un arranque en frío requieren aceptación independiente.

## Alcance y seguridad

La instalación de dependencias, el despliegue de topología,
la recuperación y los ensayos de intervención constituyen
operaciones diferentes.

Conservamos las protecciones de la red administrativa,
la identidad de los recursos y los controles de autorización.

No trasladamos llaves privadas, estados de ejecución,
identidades temporales, credenciales ni bases de datos
privadas al repositorio público.

La reproducción funcional del laboratorio no equivale
a la reproducción de resultados científicos históricos.

## Estado de validación

La reconstrucción integral desde un sistema limpio y
la portabilidad entre distribuciones permanecen pendientes
de aceptación técnica.

## Documentación relacionada

- [Preparación de Ubuntu](../docs/infraestructura/ubuntu-desktop-y-ssh.md).
- [Arquitectura multisede](../docs/arquitectura/arquitectura-multisede-implementada.md).
- [Cobertura académica](../docs/gestion/cobertura-academica-netlab360.md).
