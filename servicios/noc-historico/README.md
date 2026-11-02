# NOC histórico — Prototipo S01

Desarrollamos este componente como visualizador de datos de un ensayo inicial de **76 sondeos ICMP**. Su [aplicación](app.py) permite consultar el historial local y rutas observadas mediante `127.0.0.1:8765`.

Los datos son **históricos**: no representan el estado actual de HQ, S1 o S2, ni generan cambios sobre FRRouting, Docker o las interfaces. Conservamos el prototipo para reproducibilidad de S01 y lo distinguimos del [NOC multisede S04](../noc-s04/README.md), que utiliza observación real y SQLite.
