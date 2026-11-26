# Convención numérica de presentación

La consola utiliza un formateador compartido, NetlabNumbers, con agrupación de miles mediante coma y punto decimal, independientemente de la configuración regional del navegador. Cada componente selecciona una magnitud explícita; no se redondean las fuentes para adaptar una etiqueta. Las cantidades no disponibles se representan con raya y un cero medido conserva su precisión. Un valor no nulo que redondearía a cero se representa mediante un límite de resolución.

| Magnitud | Tipo de formato | Decimales |
| --- | --- | ---: |
| Bytes, paquetes, contadores y presupuesto en muestras | bytes, count | 0 |
| Volúmenes MB, GB y GiB | volume | 2 |
| Tasa Mbit/s y Gbit/s | rate | 3 |
| Latencia y RTT en ms | latency | 3 |
| Jitter en ms | jitter | 4 |
| Duraciones en segundos | seconds | 3 |
| Disponibilidad, utilización y confianza porcentual | percentage | 2 |
| Pérdida porcentual | loss | 3 |
| Burn rate | burn | 3 |
| Probabilidad normalizada | probability | 4 |
| Temperatura | temperature | 1 |

Los contadores requieren enteros representables de forma exacta; un dato inválido no se convierte en cero. Los identificadores, direcciones IP, VLAN, códigos HTTP, versiones y timestamps no son magnitudes de presentación numérica. Los ejes numéricos de futuras gráficas emplearán los especificadores del mismo contrato y separadores de Plotly explícitos; las etiquetas de valores muy pequeños usarán texto preformateado cuando sea necesario. Las series binarias y etiquetas temporales conservan su semántica.

En trabajos de transferencia distinguimos bytes acumulados y bytes de intervalo, tasa local y objetivo de volumen. No igualamos artificialmente la cantidad de intervalos de ambos extremos. La presentación de la cancelación conserva las muestras parciales y distingue la confirmación de limpieza. El resultado detallado JSON, las exportaciones JSON/CSV, las API, las bases de datos y las series originales no reciben redondeo de presentación. Los campos numéricos de CSV se conservan sin agrupación de miles, con punto decimal, para su análisis posterior. Las nuevas vistas reutilizarán esta convención y sus pruebas de regresión.
