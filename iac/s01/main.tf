# NETLAB360 — IaC S01: estado declarativo de topologia desde IPAM.
# terraform_data es recurso integrado: no configura interfaces, contenedores ni host.
terraform {
  required_version = ">= 1.5.0"
}

variable "sot_path" {
  type        = string
  description = "Ruta absoluta al Source of Truth YAML del proyecto"
}

locals {
  sot           = yamldecode(file(var.sot_path))
  active_sites  = { for id, s in local.sot.sites : id => s if s.status == "proposed" }
  active_links  = { for l in local.sot.wan_links : l.id => l if l.status == "proposed" }
}

resource "terraform_data" "management_guard" {
  input = local.sot.management_host
  lifecycle {
    precondition {
      condition = (
        local.sot.schema_version == "0.1" &&
        local.sot.status == "draft" &&
        local.sot.management_host.locked == true &&
        local.sot.management_host.interface == "ens33" &&
        local.sot.management_host.network == "192.168.47.0/24" &&
        local.sot.management_host.host_ip == "192.168.47.40" &&
        local.sot.management_host.gateway == "192.168.47.2" &&
        length(local.active_sites) == 2 &&
        contains(keys(local.active_sites), "HQ") &&
        contains(keys(local.active_sites), "S1") &&
        local.sot.sites.S2.status == "reserved" &&
        length(local.active_links) == 2 &&
        contains(keys(local.active_links), "WAN-PRIMARIA-HQ-S1") &&
        contains(keys(local.active_links), "WAN-RESPALDO-HQ-S1")
      )
      error_message = "NETLAB360 S01: SoT incompatible con topologia HQ/S1 o proteccion VMnet8."
    }
  }
}

resource "terraform_data" "site" {
  for_each   = local.active_sites
  input      = merge(each.value, { site_id = each.key })
  depends_on = [terraform_data.management_guard]
}

resource "terraform_data" "wan" {
  for_each   = local.active_links
  input      = each.value
  depends_on = [terraform_data.management_guard]
}

output "netlab360_manifest" {
  description = "Inventario consumible por Ansible; manifiesto de estado, NO despliegue"
  value = {
    inventory_sha256 = filesha256(var.sot_path)
    management_guard = terraform_data.management_guard.output
    sites            = { for id, obj in terraform_data.site : id => obj.output }
    wan_links        = [for id in sort(keys(terraform_data.wan)) : terraform_data.wan[id].output]
    s2_reserved      = local.sot.sites.S2.status == "reserved"
    topology_status  = "candidate_only"
  }
}
