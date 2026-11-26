# Ejecución de paneles Grafana

Contrastamos las consultas del dashboard aprovisionado mediante la API de ejecución de fuentes de Grafana y la API directa del Prometheus existente. Conservamos la expresión, fuente, modalidad, leyenda, identidad de sonda y corte temporal. Fijamos un intervalo de consulta de 10 s y un tramo de 300 s alineado al corte, separado de las ventanas de agregación de 5, 15 y 60 minutos.

Esperamos 19 consultas: cuatro de rango (496 puntos entre las cinco sondas y la sonda HTTP) y quince instantáneas (75 puntos). Verificamos todos los timestamps, sondas y valores con tolerancia absoluta de 1e-9; rechazamos huecos, duplicados, valores no finitos y errores de transporte. No se generan muestras ni se modifica Prometheus.

La ejecución inicial utiliza autenticación administrativa local exclusivamente para el contraste, sin transmitir secretos fuera de loopback ni incorporarlos a la evidencia. Esta comprobación no acredita todavía el acceso nativo de un usuario Viewer, la presentación en navegador ni el enlace desde el portal oficial; estas pruebas se realizan por separado.
