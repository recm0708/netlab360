# NOC histórico — Prototipo inicial

## Descripción

Desarrollamos este prototipo de observabilidad como prototipo inicial de NETLAB360 para estudiar la presentación básica de estados y eventos de un laboratorio de red virtualizado.

## Implementación

El prototipo utiliza una [aplicación local](app.py) y consultas a las fuentes de laboratorio disponibles en el prototipo inicial. Sus resultados sirvieron de referencia para la evolución del centro de operaciones de red.

## Evolución

La observabilidad multisede se desarrolló posteriormente en la [NOC de observabilidad multisede](../noc-s04/README.md), mientras que el panel de topología integrado se documenta en el [NOC topológico](../topologia-s05/README.md). El prototipo se conserva por su valor técnico como versión inicial, sin presentarlo como la consola principal del sistema.

## Limitaciones

El módulo histórico no representa por sí mismo la supervisión completa de las tres sedes.
