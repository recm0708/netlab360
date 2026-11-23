# S06-049 — Auditoría de preparación para TEST prospectivo y deriva (sin mutación)

## Propósito

Después de S06-048 (NOC 9130, LACP 2/2 por sede, Faucet conectado y 25 reglas verificados), evaluar **si realmente existen datos que permitan cerrar las obligaciones predictivas de S06**. La respuesta esperada con el corpus S06-041–044 es **NO**, porque el TEST NORMAL histórico precede a parte de TRAIN DEGRADED, no hay FAULT etiquetado, no existe un segundo TEST etiquetado capturado posteriormente y no se ha establecido horizonte de pronóstico.

No confundir **auditoría exitosa** (`S06_049_AUDITORIA_READONLY=OK`) con **criterio prospectivo cumplido** (`S06_049_GATE=PENDING_NEW_PROSPECTIVE_EVIDENCE`). No se reutiliza el TEST original para elegir hiperparámetros ni se suman las capturas de tres ICMP en vivo como nuevas ventanas supervisadas.

## Código

- `scripts/s06/auditar_gates_prospectivos.py` lee el reporte privado validado de S06-044, comprueba el corpus NORMAL original y los cuatro pares DEGRADED/RECOVERY completos a través de lectores existentes (con verificaciones de integridad y tokens de guardia). Valida no solapamiento entre IDs de sesión TRAIN/TEST y compara la **última fecha TRAIN** contra la **primera fecha TEST**.
- `tests/test_s06_gates_prospectivos.py` cubre cronología frente a separación por sesión, rechazo de duplicados, tamaños de corpus, tokens de evento y negativa a reportar pronóstico/detección de otra clase no demostrada.
- En `~/netlab360-bootstrap/s06/auditorias-prospectivas/` se conserva un JSON privado de resultados (`--save`). No incluye las mediciones crudas ni modelos. No toca red, servicio, interfaz, qdisc, entrenamiento o capturas anteriores.

## Criterios reales de cierre de S06, no negociables por buena puntuación anterior

1. **Cronología y exclusión TRAIN/TEST**: reservar sesiones con inicio posterior a todos los datos de calibración y entrenamiento; sin reutilizar las observaciones de decisión ya vistas en S06-044 ni variantes triviales del mismo evento.
2. **Evento positivo futuro comprobable**: documentar previamente el evento/estímulo y su recuperación, con autorización humana específica y watchdog si implica cambiar un recurso real. No utilizar eventos anteriores para afirmar prueba independiente.
3. **Cobertura y honestidad**: la clase FAULT solo se agrega si existe observación propia y fuente de verificación externa; no inferir falla WAN/OSPF/HA/SDN a partir del retardo fijo de 40 ms. Si queda excluida, consignarlo como limitación explícita.
4. **Predicción y deriva**: distinguir *detector del estado presente* de *pronóstico con horizonte futuro*. MAE y alerta temprana requieren objetivo t+h real, ventanas de características sin datos del futuro y suficientes sucesos. Data drift necesita muestreo comparable al entrenamiento; concept drift necesita etiquetas posteriores. Si no hay datos suficientes, registrar `NO_EVALUABLE`, nunca una métrica inventada.
5. **Cierre documental**: comparar resultados por ruta y evento, incorporar falsos positivos/negativos, incertidumbre, seguridad y conclusiones restringidas. Se actualiza el mismo trabajo académico en Word/PDF al concluir las pruebas, no con hipótesis no verificadas.

## Secuencia de aceptación del código

```bash
cd ~/proyectos/netlab360
python3 -m unittest discover -s tests -p 'test_s06_gates_prospectivos.py' -v
python3 -m unittest discover -s tests -p 'test_*.py'
python3 scripts/s06/auditar_gates_prospectivos.py --save
```

Se espera 60 NORMAL, 16 DEGRADED, 24 RECOVERY y 0 FAULT **por ruta**, TRAIN/TEST por sesiones sin coincidencias pero sin holdout cronológico global; ninguna prueba prospectiva independiente, ningún pronóstico con horizonte y ninguna deriva validada con ground truth. `S06_049_GATE=PENDING_NEW_PROSPECTIVE_EVIDENCE` confirma la insuficiencia del conjunto original, **no** que el código haya fallado.

Registrar salud `ens33`/gateway, 21 namespaces, cuatro contenedores, controlador HQ `NONE/BASELINE`, qdisc `noqueue`, NOC 9130, LACP/SDN y Prometheus después. Evitar nuevas capturas académicas mientras la auditoría solo confirme limitaciones ya conocidas; el JSON y bitácora bastan para preparar el texto del informe. S06 y #6/#25/#26 continúan abiertas.
