# NETLAB360 S03 — OpenTofu sobre Fuente Unica de Verdad (SoT) S02.
# SOLO MANIFIESTO/ESTADO LOCAL. terraform_data NO despliega FRR ni configura VMnet8.
# Ejecutar desde copia en $HOME/netlab360-bootstrap/iac/s03/work (fuera de Git).
terraform {
  required_version = ">= 1.13.0"
}

variable "sot_path" {
  type        = string
  description = "Ruta absoluta al inventario/ipam/topologia-s02.yaml"
}

locals {
  sot   = yamldecode(file(var.sot_path))
  sites = { for name, site in local.sot.sites : name => site if site.status == "candidate" }
  wans  = { for link in local.sot.wan_links : link.id => link if link.status == "candidate" }
  vlans = merge([
    for site_name, site in local.sites : {
      for vlan in site.vlans : format("%s-%d", site_name, vlan.id) => merge(vlan, { site = site_name })
    }
  ]...)
}

resource "terraform_data" "management_guard" {
  input = local.sot.management_host

  lifecycle {
    precondition {
      condition = (
        local.sot.schema_version == "0.2" &&
        local.sot.status == "candidate" &&
        local.sot.management_host.locked == true &&
        local.sot.management_host.interface == "ens33" &&
        local.sot.management_host.host_ip == "192.168.47.40" &&
        local.sot.management_host.network == "192.168.47.0/24" &&
        local.sot.management_host.gateway == "192.168.47.2" &&
        length(local.sites) == 3 &&
        contains(keys(local.sites), "HQ") &&
        contains(keys(local.sites), "S1") &&
        contains(keys(local.sites), "S2") &&
        length(local.wans) == 4 &&
        length(local.vlans) == 9 &&
        alltrue([
          for id, wan in local.wans :
          wan.ospf_cost == (length(regexall("PRIMARIA", id)) > 0 ? 10 : 100)
        ])
      )
      error_message = "NETLAB360 S03: Inventario incompatible con 3 sedes/9 VLAN/4 WAN o proteccion VMnet8."
    }
  }
}

resource "terraform_data" "site" {
  for_each   = local.sites
  input      = merge(each.value, { site_id = each.key })
  depends_on = [terraform_data.management_guard]
}

resource "terraform_data" "wan" {
  for_each   = local.wans
  input      = each.value
  depends_on = [terraform_data.management_guard]
}

resource "terraform_data" "vlan" {
  for_each   = local.vlans
  input      = each.value
  depends_on = [terraform_data.management_guard]
}

output "s03_manifest" {
  description = "Inventario de estado OpenTofu, NO aprovisionamiento ni ownership de FRR live"
  value = {
    source_sha256 = filesha256(var.sot_path)
    management    = terraform_data.management_guard.output
    sites         = { for name, obj in terraform_data.site : name => obj.output }
    wan_links     = { for name, obj in terraform_data.wan : name => obj.output }
    vlans         = { for name, obj in terraform_data.vlan : name => obj.output }
    scope         = "metadata_only_no_live_network_apply"
    status        = "candidate_manifest"
  }
}
