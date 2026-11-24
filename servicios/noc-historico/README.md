# NOC histórico — Prototipo inicial

## Descripción

Desarrollamos este prototipo de observabilidad durante la primera fase de NETLAB360 para estudiar la presentación básica de estados y eventos de un laboratorio de red virtualizado.

## Implementación

El prototipo utiliza una [aplicación local](app.py) y consultas a las fuentes de laboratorio disponibles durante S01. Sus resultados sirvieron de referencia para la evolución del centro de operaciones de red.

## Evolución

La observabilidad multisede se desarrolló posteriormente en [S04](../noc-s04/README.md), mientras que el panel de topología integrado corresponde a [S05](../topologia-s05/README.md). El prototipo se conserva por su valor técnico como versión inicial, sin presentarlo como la consola principal del sistema.

## Limitaciones

El módulo histórico no representa por sí mismo la supervisión completa de las tres sedes.
