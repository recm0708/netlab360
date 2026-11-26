/* Diagrama SVG de inventario, sin HTML externo ni acciones sobre la red. */
(function(root){
  "use strict";
  const ns="http://www.w3.org/2000/svg";
  // Un único encuadre conserva todo el inventario del contrato NOC.
  const config={box:"0 0 1440 1250",width:430,height:420,sites:{HQ:[20,245],S1:[980,15],S2:[980,515]}};
  function geometry(mode){
    if(mode!=="detailed")throw Error("TOPOLOGY_MODE");
    const layout={},groups=[];
    for(const [site,[x,y]] of Object.entries(config.sites)){
      groups.push({site,x,y});
      layout["R-"+site]=[x+210,y+75];
      layout["SW-"+site]=[x+210,y+145];
      layout["LACP-"+site]=[x+210,y+285];
      const prefix={HQ:1,S1:2,S2:3}[site];
      [10,20,30].forEach((v,i)=>layout["H-"+site+"-"+(prefix*100+v)]=[x+70+i*140,y+225]);
    }
    layout.BACKEND_HQ=[120,590];layout.FRONTAL_HQ=[330,590];layout.BACKEND_S1=[1190,360];
    Object.assign(layout,{FAUCET:[300,1040],OVS:[720,1040],"SDN-A":[440,1160],"SDN-B":[720,1160],"SDN-C":[1000,1160]});
    return {config,layout,groups};
  }
  const layout=geometry("detailed").layout;
  const baseIds=new Set(Object.keys(layout).filter(id=>!id.startsWith("LACP-")&&!id.startsWith("SDN-")&&!["OVS","FAUCET"].includes(id)));
  const mounted=new WeakMap();

  // Una observación vencida conserva la geometría, nunca el estado anterior.
  function fresh(meta,elapsed){
    return meta?.quality==="VALID"&&Number.isFinite(meta.age_seconds)&&
      Number.isFinite(meta.max_age_seconds)&&meta.age_seconds>=0&&
      elapsed>=0&&meta.age_seconds+elapsed<meta.max_age_seconds;
  }
  function aged(data,elapsed,unavailable=false){
    const graph=!unavailable&&fresh(data.graph,elapsed);
    const tele=graph&&fresh(data.telemetry,elapsed);
    const http=graph&&fresh(data.http,elapsed);
    const safe=item=>{
      const valid=item.scope==="HTTP_FROM_S2"?http:
        ["ADMIN_STATE_ONLY","CONTAINER_ONLY"].includes(item.scope)?tele:graph;
      const copy={...item};
      if(!valid)copy.status="unknown";
      copy.observation_valid=valid;
      if("vlan_admin" in copy&&!tele)copy.vlan_admin="unknown";
      if("route_selection" in copy&&!tele){
        copy.route_selection="unknown";copy.route_gateway=null;
      }
      if("application_selection" in copy&&!http)copy.application_selection="unknown";
      return copy;
    };
    return {...data,nodes:data.nodes.map(safe),links:data.links.map(safe)};
  }

  function view(data,mode="detailed"){
    if(mode!=="detailed")throw Error("TOPOLOGY_MODE");
    return {nodes:data.nodes,links:data.links};
  }

  function valid(data){
    if(data?.project!=="NETLAB360"||data.schema_version!==1||data.source!=="NOC"||
      data.network_mutations_authorized!==false||data.traffic_measured!==false||
      !Array.isArray(data.nodes)||data.nodes.length!==18||!Array.isArray(data.links)||data.links.length!==21) return false;
    const nodes=new Set(data.nodes.map(n=>n.id)),links=new Set(data.links.map(l=>l.id));
    return nodes.size===18&&links.size===21&&data.nodes.every(n=>baseIds.has(n.id)&&typeof n.label==="string")&&
      data.links.every(l=>nodes.has(l.from)&&nodes.has(l.to)&&["wan","lan","access","redundancy"].includes(l.type));
  }

  // La composición usa el grafo NOC original y el lote autenticado de fuentes.
  // Los dos miembros LACP se dibujan como un único recurso agregado: el lector
  // solo conoce recuentos por extremo, no el estado individual de cada puerto.
  function augment(data,rows){
    const nodes=data.nodes.slice(),links=data.links.slice();
    const read=id=>rows.find(r=>r.source==="NOC_S05"&&r.resource===id&&r.quality==="VALID");
    for(const [i,site] of ["HQ","S1","S2"].entries()){
      const id="LACP-"+site,row=read(id),d=row?.details||{};
      const a=d.switch_members,b=d.client_members;
      const counts=[a,b].every(n=>Number.isInteger(n)&&n>=0&&n<=2);
      const expected=counts?(Math.min(a,b)===2?"NORMAL":Math.min(a,b)===1?"DEGRADED":"FAULT"):null;
      const confirmed=counts&&row.state===expected;
      const evidence=confirmed?{status:{NORMAL:"bond-normal",DEGRADED:"bond-degraded",FAULT:"bond-down"}[expected],
        observation_valid:true,switch_members:a,client_members:b,observed_at_utc:row.stamp}:{status:"unknown",observation_valid:false};
      const vlan=(i+1)*100+20,ip="10."+ (70+i)+".20.40/24";
      nodes.push({id,site,type:"lacp-client",label:"Cliente LACP",detail:ip+" · VLAN "+vlan+" · bond0",
        scope:"BOND_MEMBER_STATE",...evidence});
      links.push({id:"BOND-"+site,from:"SW-"+site,to:id,type:"lacp",role:"Agregado 802.3ad",
        detail:"s5bond0 ↔ bond0 · s5p1/s5c1 y s5p2/s5c2 · VLAN "+vlan,
        scope:"BOND_MEMBER_STATE",...evidence});
    }
    const row=read("FAUCET"),d=row?.details||{};
    const connected=d.connected===true&&row.state==="NORMAL"&&Number.isSafeInteger(d.flow_count)&&d.flow_count>0&&d.flow_count<=1e9;
    const disconnected=d.connected===false&&row.state==="FAULT"&&d.flow_count===null;
    const known=connected||disconnected;
    const control={status:connected?"controller-connected":disconnected?"controller-disconnected":"unknown",
      observation_valid:known,observed_at_utc:known?row.stamp:null};
    nodes.push({id:"FAUCET",site:"SDN",type:"controller",label:"Faucet",detail:"nl360-s05-faucet · OpenFlow 1.3",scope:"CONTROLLER_ONLY",...control});
    nodes.push({id:"OVS",site:"SDN",type:"ovs",label:"Open vSwitch",detail:"br-s05-sdn · datapath independiente",scope:"FLOW_COUNT_ONLY",
      status:connected?"flows-observed":"unknown",observation_valid:connected,flow_count:connected?d.flow_count:null,observed_at_utc:connected?row.stamp:null});
    links.push({id:"SDN-CONTROL",from:"FAUCET",to:"OVS",type:"control",role:"OpenFlow 1.3",detail:"Relación de control; no representa tráfico de datos",scope:"CONTROLLER_ONLY",...control});
    for(const [i,suffix] of ["A","B","C"].entries()){
      const id="SDN-"+suffix,vlan=i===2?420:410,port="sdn"+suffix.toLowerCase()+"0";
      nodes.push({id,site:"SDN",type:"sdn-host",label:"Host "+suffix,detail:"nl360-s05-sdn-"+suffix.toLowerCase()+" · VLAN "+vlan,
        scope:"INVENTORY_ONLY",status:"unknown",observation_valid:false});
      links.push({id:"SDN-ACCESS-"+suffix,from:"OVS",to:id,type:"sdn-access",role:"Acceso VLAN "+vlan,detail:port+" · inventario; sin estado individual observado",
        scope:"INVENTORY_ONLY",status:"unknown",observation_valid:false});
    }
    return {...data,nodes,links};
  }

  const statuses={ "bond-normal":"Dos miembros por extremo","bond-degraded":"Agregado degradado","bond-down":"Agregado sin miembros en un extremo",
    "controller-connected":"Controlador conectado","controller-disconnected":"Controlador desconectado","flows-observed":"Flujos observados",running:"En ejecución",offline:"Fuera de línea observado","namespace-present":"Namespace presente",
    "admin-up":"Administrativamente habilitada","admin-down":"Administrativamente deshabilitada",unknown:"Sin verificar"};
  const choices={selected:"Seleccionada",standby:"En espera",unavailable:"No disponible",unknown:"Sin verificar"};
  function name(item){
    if(item.label) return item.type==="host"?"VLAN "+item.vlan:item.label;
    if(item.type==="wan") return (item.role==="primary"?"WAN principal":"WAN respaldo")+" · "+item.from+" ↔ "+item.to;
    return item.role+" · "+item.from+" ↔ "+item.to;
  }
  function details(item,format){
    const scopes={CONTAINER_ONLY:"Existencia del contenedor",NAMESPACE_ONLY:"Existencia del namespace",
      HTTP_FROM_S2:"HTTP observado desde S2",ADMIN_STATE_ONLY:"Estado administrativo",INVENTORY_ONLY:"Inventario",
      BOND_MEMBER_STATE:"Recuento de miembros por extremo",CONTROLLER_ONLY:"Conexión OpenFlow",FLOW_COUNT_ONLY:"Recuento de flujos; no acredita forwarding"};
    const types={router:"Router FRR",switch:"Switch L2",host:"Host de prueba",server:"Servidor HTTP",wan:"Enlace WAN",lan:"Troncal LAN",access:"Acceso LAN",redundancy:"Relación HTTP","lacp-client":"Cliente LACP",lacp:"Agregado LACP",controller:"Controlador SDN",ovs:"Datapath OVS","sdn-host":"Host SDN","sdn-access":"Acceso SDN",control:"Relación OpenFlow"};
    const rows=[["Identificador",item.id],["Tipo",types[item.type]||item.type],["Inventario",item.detail]];
    if(item.role)rows.push(["Función",({primary:"Principal",backup:"Respaldo"})[item.role]||item.role]);
    if(item.from)rows.push(["Origen",item.from],["Destino",item.to]);
    if(item.site) rows.push(["Sede",item.site]);
    if(item.vlan) rows.push(["VLAN",String(item.vlan)],["Gateway",item.gateway]);
    rows.push(["Alcance observado",scopes[item.scope]||"Sin verificar"],["Estado observado",statuses[item.status]||"Sin verificar"],["Vigencia",item.observation_valid===true?"Fuente vigente":item.observation_valid===false?"Sin observación vigente":"Sin verificar"]);
    if(item.vlan)rows.push(["Estado VLAN",statuses[item.vlan_admin]]);
    if(item.a) rows.push(["Extremo A",item.a],["Extremo B",item.b],["Selección FIB",choices[item.route_selection]],
      ["Próximo salto",item.route_gateway||"Sin verificar"]);
    if(item.application_selection) rows.push(["Selección HTTP",choices[item.application_selection]]);
    if(item.scope==="BOND_MEMBER_STATE"){
      rows.push(["Miembros switch",Number.isInteger(item.switch_members)?item.switch_members+" / 2":"Sin verificar"],
        ["Miembros cliente",Number.isInteger(item.client_members)?item.client_members+" / 2":"Sin verificar"],
        ["Límite","Sin estado individual de cada puerto ni tráfico medido"]);
    }
    if(item.scope==="FLOW_COUNT_ONLY")rows.push(["Flujos observados",Number.isSafeInteger(item.flow_count)?String(item.flow_count):"Sin verificar"]);
    if(["BOND_MEMBER_STATE","CONTROLLER_ONLY","FLOW_COUNT_ONLY"].includes(item.scope))rows.push(["Fuente","NOC S05 · observaciones autorizadas"]);
    if(item.observed_at_utc&&typeof format==="function")rows.push(["Última observación",format(new Date(item.observed_at_utc))]);
    return rows.filter(row=>typeof row[1]==="string");
  }

  function element(tag,attrs={},label){
    const e=document.createElementNS(ns,tag);
    for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,String(v));
    if(label!==undefined)e.textContent=label;
    return e;
  }
  function edgePath(l,mode){
    const {layout,config}=geometry(mode);
    const [ax,ay]=layout[l.from],[bx,by]=layout[l.to];
    if(l.type==="lacp"){
      const path=offset=>"M"+(ax-54)+" "+(ay+offset)+" H"+(ax-70+offset)+" V"+(by+offset)+" H"+(bx-54);
      return path(-4)+" "+path(4);
    }
    if(l.type==="control")return "M"+(ax+54)+" "+ay+" H"+(bx-54);
    if(l.type==="sdn-access")return "M"+ax+" "+(ay+23)+" V1100 H"+bx+" V"+(by-23);
    if(l.type==="wan"){
      const north=l.to==="R-S1",primary=l.role==="primary";
      const start=north?(primary?-17:-6):(primary?6:17);
      const end=primary?-9:9;
      const mid=(north?510:735)+(primary?0:28);
      return "M"+(ax+54)+" "+(ay+start)+" H"+mid+" V"+(by+end)+" H"+(bx-54);
    }
    // Los accesos a servidores parten del switch, por corredores laterales.
    if(l.id==="S05-HA-ACCESO-HQ"){
      const x=config.sites.HQ[0]+7;
      return "M"+(ax-54)+" "+ay+" H"+x+" V"+by+" H"+(bx-54);
    }
    if(l.id==="S05-HA-ACCESO-FRONTAL"||l.id==="S05-HA-ACCESO-S1"){
      const site=l.to==="FRONTAL_HQ"?"HQ":"S1",x=config.sites[site][0]+419;
      return "M"+(ax+54)+" "+ay+" H"+x+" V"+by+" H"+(bx+54);
    }
    // La relación HTTP es lógica, no un cable conectado a una VLAN.
    if(l.id==="S05-HA-HTTP-PRINCIPAL")return "M"+(ax-54)+" "+ay+" H"+(bx+54);
    if(l.id==="S05-HA-HTTP-RESPALDO")return "M"+ax+" "+(ay+23)+" V690 H905 V"+by+" H"+(bx-54);
    return "M"+ax+" "+(ay+23)+" V"+((ay+by)/2)+" H"+bx+" V"+(by-23);
  }
  function state(item){
    if(["offline","admin-down","bond-down","controller-disconnected"].includes(item.status))return "fault";
    if(item.status==="bond-degraded")return "warn";
    if(["bond-normal","controller-connected","flows-observed"].includes(item.status))return "ok";
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

  function render(svg,data,selected,onSelect,mode="detailed"){
    const {config,layout,groups}=geometry(mode),display=view(data,mode);
    const items=[...display.links,...display.nodes];
    const key=mode+":"+items.map(i=>i.id).sort().join("|");
    let cache=mounted.get(svg);
    if(!cache||cache.key!==key||!svg.firstChild){
      svg.replaceChildren();
      svg.setAttribute("viewBox",config.box);
      const elements=new Map();
      for(const {site,x,y} of groups){
        svg.append(element("rect",{x,y,width:config.width,height:config.height,rx:12,class:"topology-site"}));
        svg.append(element("text",{x:x+18,y:y+30,class:"topology-site-label"},site==="HQ"?"SEDE CENTRAL · HQ":"SUCURSAL · "+site));
      }
      if(display.nodes.some(n=>n.id==="OVS")){
        svg.append(element("rect",{x:20,y:975,width:1390,height:250,rx:12,class:"topology-site"}));
        svg.append(element("text",{x:38,y:1005,class:"topology-site-label"},"DOMINIO SDN INDEPENDIENTE · OVS / FAUCET"));
      }
      for(const item of display.links){
        const d=edgePath(item,mode),g=element("g",{class:"topology-item topology-link"});
        const backup=item.role==="backup"||["redundancy","control"].includes(item.type);
        g.append(element("path",{d,class:"topology-highlight"}));
        g.append(element("path",{d,class:"topology-edge"+(backup?" backup":"")}));
        g.append(element("path",{d,class:"topology-hit"}));
        if(item.type==="wan"){
          const [bx,by]=layout[item.to],y=by+(item.role==="primary"?-9:9);
          const label=(item.role==="primary"?"Principal":"Respaldo")+" · "+item.to.slice(2);
          g.append(element("text",{x:bx-65,y:y-4,"text-anchor":"end",class:"topology-edge-label"},label));
        }
        if(item.type==="lacp")g.append(element("text",{x:layout[item.to][0]-62,y:layout[item.to][1]-12,"text-anchor":"end",class:"topology-edge-label"},"802.3ad"));
        if(item.type==="control")g.append(element("text",{x:(layout[item.from][0]+layout[item.to][0])/2,y:layout[item.from][1]-9,"text-anchor":"middle",class:"topology-edge-label"},"OpenFlow 1.3"));
        activate(g,item,selected,onSelect);svg.append(g);elements.set(item.id,g);
      }
      for(const item of display.nodes){
        const [x,y]=layout[item.id],g=element("g",{class:"topology-item topology-node"});
        g.append(element("rect",{x:x-54,y:y-23,width:108,height:46,rx:8,class:"topology-node-box"}));
        g.append(element("text",{x,y:y-3,"text-anchor":"middle",class:"topology-node-label"},item.type==="server"?(item.id==="FRONTAL_HQ"?"Frontal HA":"Backend "+item.site):name(item)));
        const sub=item.type==="router"?"FRR":item.type==="switch"?"Bridge L2":item.type==="server"?"HTTP":item.type==="lacp-client"?"bond0 · VLAN "+({HQ:120,S1:220,S2:320}[item.site]):item.type==="controller"?"OpenFlow 1.3":item.type==="ovs"?"br-s05-sdn":item.type==="sdn-host"?"VLAN "+(item.id==="SDN-C"?420:410):"Host de prueba";
        g.append(element("text",{x,y:y+13,"text-anchor":"middle",class:"topology-node-sub"},sub));
        activate(g,item,selected,onSelect);svg.append(g);elements.set(item.id,g);
      }
      cache={key,elements};mounted.set(svg,cache);
    }
    // Solo cambian atributos de estado y selección; los nodos SVG no se recrean.
    for(const item of items){
      const g=cache.elements.get(item.id),active=selected===item.id;
      g.setAttribute("data-state",state(item));
      g.classList.toggle("selected",active);
      g.setAttribute("aria-pressed",String(active));
    }
  }
  // El encuadre es local a cada pestaña y no cambia los datos ni la selección.
  function viewport(mode,site="all"){
    const {config}=geometry(mode);
    const [x,y,w,h]=config.box.split(" ").map(Number);
    if(site==="all")return [x,y,w,h];
    if(site==="SDN")return [10,965,1410,270];
    if(!Object.hasOwn(config.sites,site))throw new Error("SITE");
    const [sx,sy]=config.sites[site];
    return [Math.max(0,sx-10),Math.max(0,sy-10),config.width+20,config.height+20];
  }
  function moveViewport(mode,box,zoom=1,dx=0,dy=0){
    const [, ,maxW,maxH]=viewport(mode);
    const [x,y,w,h]=box;
    const scale=Math.max(0.2*maxW/w,0.2*maxH/h,Math.min(zoom,maxW/w,maxH/h));
    const nw=Math.min(maxW,w*scale),nh=Math.min(maxH,h*scale);
    const nx=Math.min(maxW-nw,Math.max(0,x+(w-nw)/2+dx*w));
    const ny=Math.min(maxH-nh,Math.max(0,y+(h-nh)/2+dy*h));
    return [nx,ny,nw,nh];
  }
  function reset(svg){mounted.delete(svg);svg.replaceChildren();}
  root.NetlabTopology=Object.freeze({valid,augment,name,details,render,reset,view,aged,isFresh:fresh,edgePath,geometry,viewport,moveViewport});
})(typeof window==="undefined"?globalThis:window);
