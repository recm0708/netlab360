# Perfil de Ubuntu 26.04 amd64

## Descripción

Utilizamos Ubuntu Desktop 26.04.1 LTS sobre arquitectura
amd64 como plataforma de referencia de NETLAB360.

Registramos las versiones observadas antes de incorporar
la consola interactiva. El inventario no constituye una
garantía de disponibilidad futura de versiones idénticas
ni acredita una instalación desde un sistema limpio.

## Dependencias

El archivo [paquetes.tsv](paquetes.tsv) distingue tres
categorías:

- Base: herramientas del sistema y dependencias utilizadas.
- Externo: herramientas obtenidas de repositorios adicionales.
- Opcional: utilidades administrativas, gráficas y auxiliares.

La clasificación es operativa; no representa un análisis
definitivo de dependencias transitivas de cada aplicación.

Conservamos las dependencias científicas en
[requirements-cientifico.txt](../../../requirements-cientifico.txt)
y las referencias de imágenes en
[imagenes.tsv](../../imagenes.tsv).

## Compatibilidad

La presencia de los paquetes no demuestra por sí sola
que la infraestructura pueda reconstruirse.

Ubuntu Server y otras distribuciones requieren comprobar
sus gestores de paquetes, versiones de Python, kernel,
systemd, Docker y capacidades de red.

No modificamos automáticamente la red administrativa
para adaptar el perfil.

## Fuentes de instalación

Utilizamos las instrucciones oficiales de los proveedores
como referencia para configurar los repositorios externos:

- [Docker Engine](https://docs.docker.com/engine/install/ubuntu/).
- [GitHub CLI](https://github.com/cli/cli/blob/trunk/docs/install_linux.md).
- [OpenTofu](https://opentofu.org/docs/intro/install/deb/).
- [NodeSource](https://github.com/nodesource/distributions).
- [Python Package Index](https://pypi.org/).

Las llaves de los repositorios se restringen mediante
Signed-By. La comprobación de sus huellas corresponde
al administrador antes de autorizar su instalación.

Las imágenes de FRRouting, Faucet y Prometheus utilizan
las referencias inmutables del inventario OCI.
