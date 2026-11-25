/* Diagrama SVG de inventario, sin HTML externo ni acciones sobre la red. */
(function(root){
  "use strict";
  const ns="http://www.w3.org/2000/svg";
  const sites={HQ:[20,215],S1:[850,10],S2:[850,430]};
  const layout={},groups=[];
  for(const [site,[x,y]] of Object.entries(sites)){
    groups.push({site,x,y});
    layout["R-"+site]=[x+185,y+75];
    layout["SW-"+site]=[x+185,y+140];
    const prefix={HQ:1,S1:2,S2:3}[site];
    [10,20,30].forEach((v,i)=>layout["H-"+site+"-"+(prefix*100+v)]=[x+65+i*120,y+220]);
  }
  layout.BACKEND_HQ=[100,555];layout.FRONTAL_HQ=[275,555];layout.BACKEND_S1=[1035,350];

  function valid(data){
    if(data?.project!=="NETLAB360"||data.schema_version!==1||data.source!=="NOC"||
      data.network_mutations_authorized!==false||data.traffic_measured!==false||
      !Array.isArray(data.nodes)||data.nodes.length!==18||!Array.isArray(data.links)||data.links.length!==21) return false;
    const nodes=new Set(data.nodes.map(n=>n.id)),links=new Set(data.links.map(l=>l.id));
    return nodes.size===18&&links.size===21&&data.nodes.every(n=>Object.hasOwn(layout,n.id)&&typeof n.label==="string")&&
      data.links.every(l=>nodes.has(l.from)&&nodes.has(l.to)&&["wan","lan","access","redundancy"].includes(l.type));
  }

  const statuses={running:"En ejecución",offline:"Fuera de línea observado","namespace-present":"Namespace presente",
    "admin-up":"Administrativamente habilitada","admin-down":"Administrativamente deshabilitada",unknown:"Sin verificar"};
  const choices={selected:"Seleccionada",standby:"En espera",unavailable:"No disponible",unknown:"Sin verificar"};
  function name(item){
    if(item.label) return item.type==="host"?"VLAN "+item.vlan:item.label;
    if(item.type==="wan") return (item.role==="primary"?"WAN principal":"WAN respaldo")+" · "+item.from+" ↔ "+item.to;
    return item.role+" · "+item.from+" ↔ "+item.to;
  }
  function details(item){
    const scopes={CONTAINER_ONLY:"Existencia del contenedor",NAMESPACE_ONLY:"Existencia del namespace",
      HTTP_FROM_S2:"HTTP observado desde S2",ADMIN_STATE_ONLY:"Estado administrativo",INVENTORY_ONLY:"Inventario"};
    const rows=[["Tipo",item.type],["Alcance",scopes[item.scope]||"Sin verificar"],
      ["Estado",statuses[item.status]||"Sin verificar"],["Detalle",item.detail]];
    if(item.site) rows.push(["Sede",item.site]);
    if(item.vlan) rows.push(["VLAN",String(item.vlan)],["Gateway",item.gateway],["Estado VLAN",statuses[item.vlan_admin]]);
    if(item.a) rows.push(["Extremo A",item.a],["Extremo B",item.b],["Selección FIB",choices[item.route_selection]],
      ["Próximo salto",item.route_gateway||"Sin verificar"]);
    if(item.application_selection) rows.push(["Selección HTTP",choices[item.application_selection]]);
    return rows.filter(row=>typeof row[1]==="string");
  }

  function element(tag,attrs={},label){
    const e=document.createElementNS(ns,tag);
    for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,String(v));
    if(label!==undefined)e.textContent=label;
    return e;
  }
  function edgePath(l){
    const [ax,ay]=layout[l.from],[bx,by]=layout[l.to];
    if(l.type==="wan"){
      const primary=l.role==="primary", north=l.to==="R-S1";
      const startOffset=north?(primary?-17:-6):(primary?6:17);
      const endOffset=primary?-9:9;
      const mid=(north?490:680)+(primary?0:28);
      return "M"+(ax+54)+" "+(ay+startOffset)+" H"+mid+" V"+(by+endOffset)+" H"+(bx-54);
    }
    if(l.type==="redundancy"){
      const y=l.to==="BACKEND_S1"?620:ay+36;
      return "M"+ax+" "+(ay+20)+" V"+y+" H"+bx+" V"+(by+20);
    }
    return "M"+ax+" "+ay+" V"+((ay+by)/2)+" H"+bx+" V"+by;
  }
  function state(item){
    if(["offline","admin-down"].includes(item.status))return "fault";
    if(item.type==="wan"&&item.route_selection==="selected")return item.role==="backup"?"recovery":"ok";
    if(item.type==="wan"||item.type==="redundancy")return item.application_selection==="selected"?"ok":"unknown";
    return ["running","namespace-present"].includes(item.status)?"ok":"unknown";
  }
  function activate(g,item,selected,onSelect){
    g.setAttribute("role","button");g.setAttribute("tabindex","0");
    g.setAttribute("data-resource",item.id);g.prepend(element("title",{},name(item)));
    g.setAttribute("aria-label",name(item));g.setAttribute("aria-pressed",String(selected===item.id));
    g.addEventListener("click",()=>onSelect(item.id));
    g.addEventListener("keydown",event=>{
      if(event.key==="Enter"||event.key===" "){event.preventDefault();onSelect(item.id);}
    });
  }

  function render(svg,data,selected,onSelect){
    const focused=svg.contains(document.activeElement)?document.activeElement.getAttribute("data-resource"):null;
    svg.replaceChildren();
    for(const {site,x,y} of groups){
      svg.append(element("rect",{x,y,width:370,height:site==="HQ"?395:385,rx:12,class:"topology-site"}));
      svg.append(element("text",{x:x+18,y:y+30,class:"topology-site-label"},site==="HQ"?"SEDE CENTRAL · HQ":"SUCURSAL · "+site));
    }
    for(const item of data.links){
      const d=edgePath(item);
      const g=element("g",{class:"topology-item topology-link"+(selected===item.id?" selected":""),"data-state":state(item)});
      const backup=item.role==="backup"||item.type==="redundancy";
      g.append(element("path",{d,class:"topology-edge"+(backup?" backup":"")}));
      g.append(element("path",{d,class:"topology-hit"}));
      if(item.type==="wan"){
        const [bx,by]=layout[item.to], y=by+(item.role==="primary"?-9:9);
        const label=(item.role==="primary"?"Principal":"Respaldo")+" · "+item.to.slice(2);
        g.append(element("text",{x:bx-65,y:y-4,"text-anchor":"end",class:"topology-edge-label"},label));
      }
      activate(g,item,selected,onSelect);svg.append(g);
    }
    for(const item of data.nodes){
      const [x,y]=layout[item.id],g=element("g",{class:"topology-item topology-node"+(selected===item.id?" selected":""),"data-state":state(item)});
      g.append(element("rect",{x:x-54,y:y-23,width:108,height:46,rx:8,class:"topology-node-box"}));
      g.append(element("text",{x,y:y-3,"text-anchor":"middle",class:"topology-node-label"},item.type==="server"?(item.id==="FRONTAL_HQ"?"Frontal HA":"Backend "+item.site):name(item)));
      const sub=item.type==="router"?"FRR":item.type==="switch"?"Bridge L2":item.type==="server"?"HTTP":"Host de prueba";
      g.append(element("text",{x,y:y+13,"text-anchor":"middle",class:"topology-node-sub"},sub));
      activate(g,item,selected,onSelect);svg.append(g);
    }
    if(focused) for(const g of svg.querySelectorAll("[data-resource]")) {
      if(g.getAttribute("data-resource")===focused) {g.focus({preventScroll:true});break;}
    }
  }
  root.NetlabTopology=Object.freeze({valid,name,details,render});
})(typeof window==="undefined"?globalThis:window);
