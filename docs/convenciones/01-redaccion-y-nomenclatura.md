# Convenciones editoriales de NETLAB360

Estas convenciones se aplican a README, arquitectura, decisiones, operación, evidencias, bitácoras e informes técnicos del proyecto.

## Voz del equipo

Escribimos de forma profesional, precisa y cohesionada desde el trabajo del grupo: «configuramos», «comprobamos», «registramos», «se verificó» o «la prueba confirmó». Evitamos narraciones externas como «el usuario solicitó», «el asistente verificó» o «el estudiante indicó» para describir nuestras propias actividades. No atribuimos aprobaciones a la docente sin respaldo específico.

Usamos pasado para ensayos completados y futuro para actividades planificadas. Distinguimos explícitamente **diseñado**, **implementado**, **comprobado**, **documentado** y **pendiente**; no convertimos un código fusionado, un precheck o un plan en resultado operativo sin evidencia.

## Estructura documental

Cada archivo cumple una responsabilidad definida. El README raíz presenta la plataforma; los README de componentes describen sus funciones y referencias; el tablero mantiene el estado actual; el informe académico integra los resultados; y las bitácoras fechadas registran el desarrollo histórico. No añadimos una alerta «vigente» en archivos históricos ni replicamos el tablero entero en cada README.

[Índice de responsabilidades](../gestion/INDICE-DOCUMENTAL.md).

## Nomenclatura y trazabilidad

- Utilizamos «fase 1», «fase 2» y sucesivas en la narración académica, y los identificadores técnicos S01–S08 en archivos, scripts, capturas y referencias.
- Conservamos denominaciones exactas como FRRouting/FRR, OSPF, VLAN, WAN, LACP, Open vSwitch, Faucet, HA, IaC, SoT, NOC y SHA-256.
- Respetamos nombres y hashes originales de la evidencia; una corrección editorial no autoriza modificar bytes de registros o imágenes.
- Cada afirmación experimental incluye condiciones, resultado, limitación y fuente verificable. No confundimos reglas OpenFlow con tráfico exitoso, `terraform_data` con aprovisionamiento externo ni HA lógica con redundancia física.
- Nunca incorporamos cédulas, contraseñas, llaves privadas, tokens o estados de infraestructura con secretos.
- En el informe institucional aplicamos citas/referencias APA 7 y numeración consistente con la versión editable del documento.

Antes de fusionar modificaciones comprobamos enlaces internos, nombres de archivos y referencias a documentación vigente, preservando el valor probatorio de los registros históricos.
