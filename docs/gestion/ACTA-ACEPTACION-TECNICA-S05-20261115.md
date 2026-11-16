# Acta de aceptación técnica — fase 5

**Proyecto:** NETLAB360  
**Fecha de verificación:** 15 de noviembre de 2026  
**Alcance:** implementación, ensayos de alta disponibilidad y comprobación final de la infraestructura S05.

## Objeto

Verificamos la integración de redes empresariales virtuales para HQ, S1 y S2, incluyendo enrutamiento dinámico, tolerancia a fallas lógicas, agregación de enlaces, segmentación SDN y monitoreo centralizado.

## Criterios comprobados

| Dominio | Resultado |
|---|---|
| WAN/OSPF y red local | Cuatro WAN, nueve VLAN, conmutación y restauración verificadas |
| LACP | Tres agregadores con dos miembros; recuperación 2→1→2 por sede |
| SDN | Faucet/OpenFlow, VLAN410 A↔B permitida, VLAN420 C aislada y puerto restaurado |
| HTTP HA | Una interrupción real del backend HQ, selección S1 y retorno HQ en 17 muestras |
| NOC | Salud correcta, 18 nodos/21 enlaces, fuentes FIB/HA/LACP/SDN |
| Infraestructura del laboratorio | 21 namespaces, cuatro contenedores, seis servicios activos |
| Administración | `ens33 192.168.47.40/24`, gateway `192.168.47.2`, sin cambios |
| Integridad | P1 original 4/4, P1B 5/5, 71 PNG y dos registros HA correctos |

El ensayo HTTP se ejecutó con un rescate temporizado independiente de la sesión SSH. La validación comprobó cancelación posterior del timer, recuperación del backend y conservación del resto de los servicios.

## Limitaciones reconocidas

Las pruebas de WAN, LACP y HA se realizaron en una VM con recursos virtuales; no demuestran alta disponibilidad del anfitrión, controlador Faucet redundante ni recuperación tras reiniciar Ubuntu. Los 21 namespaces efímeros requieren suspensión VMware o un procedimiento de reconstrucción todavía pendiente.

## Resultado del acta

**Aceptación técnica operativa: conforme** al lote 158 de solo lectura.  
**Aceptación documental y cierre administrativo: pendientes** hasta comprobar que los 77 archivos nuevos de evidencias estén fusionados en `main`, validar la referencia cruzada con el manuscrito y resolver las issues vinculadas.

No interpretamos esta acta como certificación de servicios de producción o como entrega final del proyecto.

[Tablero S05](s05-tablero-vigente.md) · [Informe académico](../entregables/01-proyecto-investigacion-maestro.md) · [Catálogo de capturas](../../evidencias/capturas/README.md).
