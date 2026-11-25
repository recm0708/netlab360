# Sondas de servicio y presupuesto de errores

Reutilizamos Prometheus S04 y su TSDB. No sustituimos las métricas administrativas de WAN/VLAN por inferencias de disponibilidad extremo a extremo. Las sondas Blackbox son independientes del colector y se ejecutan en los clientes HQ y S2 existentes, sin añadir interfaces, rutas ni namespaces. El catálogo inicial admite ICMP desde HQ hacia S1 y S2, e ICMP, TCP y HTTP desde S2 hacia el frontal HQ. El TCP observa apertura del puerto; HTTP comprueba una respuesta 200 sin redirecciones; ICMP observa alcance. Ninguna medición aislada acredita disponibilidad desde todas las sedes ni continuidad de sesiones.

## Contrato de observación

El piloto ejecuta exportadores dentro de los namespaces, exclusivamente en loopback y bajo una identidad sin capacidades. No publica la interfaz genérica de sondas en el host. La integración continua necesitará un colector de destinos fijos que limite los parámetros y preserve la identidad de origen. Se verifican direcciones, ruta y ausencia de puertos ocupados. Una falla de sonda se diferencia de un error de transporte hacia el exporter. El contexto S1 como origen y otros destinos requerirán autorización explícita en el catálogo.

## Objetivos y calidad

Proponemos un objetivo de laboratorio de 99 % para cada combinación, con cadencia de 10 s y ventanas de 5, 15 y 60 minutos. No se presenta como SLA contractual. El SLI mide éxitos entre sondas registradas y el error budget discreto utiliza el número de observaciones válidas. Burn rate es la fracción de errores observados dividida por el 1 % tolerado. Una ventana sin muestras no tiene disponibilidad ni burn rate calculables. Las ausencias de scrape o de métrica se informan separadamente; no se imputan éxitos ni fallas. El conteo nominal no acredita por sí solo continuidad de timestamps; la integración con Prometheus deberá comprobar la frescura y emparejamiento de series antes de una evaluación formal.

## Alertas y rendimiento

El piloto de Alertmanager utiliza únicamente una entrega webhook local de prueba, distinguida de incidentes reales, sin correo ni mensajería externa. Se comprobará agrupación y resolución antes de conectar reglas operacionales. iPerf3 conserva sus límites actuales: el piloto captura las tramas de ambos extremos usando el modo JSON por líneas. Esas tramas permitirán desarrollar un parser compatible sin estimar progreso por duración ni atribuir al receptor contadores del emisor.

No se cambia la configuración operacional de Prometheus durante este incremento. Grafana se evaluará después de disponer de series nuevas, sin duplicar el portal oficial. Los paquetes extraídos para el piloto no constituyen una instalación permanente.
