/* Diagrama SVG de inventario, sin HTML externo ni acciones sobre la red. */
(function(root){
  "use strict";
  const ns="http://www.w3.org/2000/svg";
  // Ambas vistas comparten los identificadores del contrato NOC.
  const modes={
    summary:{box:"0 0 1250 620",width:420,height:285,sites:{HQ:[20,170],S1:[810,15],S2:[810,320]}},
    detailed:{box:"0 0 1440 955",width:430,height:420,sites:{HQ:[20,245],S1:[980,15],S2:[980,515]}}
  };
  function geometry(mode){
    const config=modes[mode],layout={},groups=[];
    for(const [site,[x,y]] of Object.entries(config.sites)){
      groups.push({site,x,y});
      layout["R-"+site]=[x+210,y+75];
      layout["SW-"+site]=[x+210,y+145];
      const prefix={HQ:1,S1:2,S2:3}[site];
      [10,20,30].forEach((v,i)=>layout["H-"+site+"-"+(prefix*100+v)]=[x+70+i*140,y+225]);
    }
    if(mode==="detailed"){
      layout.BACKEND_HQ=[120,590];layout.FRONTAL_HQ=[330,590];layout.BACKEND_S1=[1190,360];
    }
    return {config,layout,groups};
  }
  const layout=geometry("detailed").layout;
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
      if(!valid){copy.status="unknown";copy.detail="Sin observación vigente.";}
      if("vlan_admin" in copy&&!tele)copy.vlan_admin="unknown";
      if("route_selection" in copy&&!tele){
        copy.route_selection="unknown";copy.route_gateway=null;
      }
      if("application_selection" in copy&&!http)copy.application_selection="unknown";
      return copy;
    };
    return {...data,nodes:data.nodes.map(safe),links:data.links.map(safe)};
  }

  function view(data,mode){
    if(mode==="detailed")return {nodes:data.nodes,links:data.links};
    const nodes=data.nodes.filter(n=>n.type!=="server");
    const ids=new Set(nodes.map(n=>n.id));
    const links=data.links.filter(l=>l.type!=="wan"&&ids.has(l.from)&&ids.has(l.to));
    for(const site of ["S1","S2"]){
      const primary=data.links.find(l=>l.id==="WAN-PRIMARIA-HQ-"+site);
      const backup=data.links.find(l=>l.id==="WAN-RESPALDO-HQ-"+site);
      if(!primary||!backup)continue;
      links.push({id:"WAN-GENERAL-HQ-"+site,type:"wan-group",from:"R-HQ",to:"R-"+site,
        role:"logical",members:[primary,backup]});
    }
    return {nodes,links};
  }

  function down(item){return ["offline","admin-down"].includes(item.status);}
  function logicalState(item){
    const [p,b]=item.members;
    const selected=l=>l.route_selection==="selected"&&l.status==="admin-up";
    if(selected(p)&&selected(b))return "unknown";
    if(selected(b))return "recovery";
    if(selected(p))return down(b)?"warn":"ok";
    if(down(p)&&down(b))return "fault";
    return "unknown";
  }
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
    if(item.type==="wan-group")return "WAN lógica · HQ ↔ "+item.to.slice(2);
    if(item.label) return item.type==="host"?"VLAN "+item.vlan:item.label;
    if(item.type==="wan") return (item.role==="primary"?"WAN principal":"WAN respaldo")+" · "+item.from+" ↔ "+item.to;
    return item.role+" · "+item.from+" ↔ "+item.to;
  }
  function details(item){
    if(item.type==="wan-group"){
      const rows=[["Alcance","Resumen de dos enlaces; no acredita tráfico"]];
      for(const m of item.members){
        const label=m.role==="primary"?"Principal":"Respaldo";
        rows.push([label,statuses[m.status]||"Sin verificar"],
          ["FIB "+label,choices[m.route_selection]||"Sin verificar"],
          ["Extremos "+label,m.a+" ↔ "+m.b]);
      }
      return rows;
    }
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
  function edgePath(l,mode){
    const {layout,config}=geometry(mode);
    const [ax,ay]=layout[l.from],[bx,by]=layout[l.to];
    if(l.type==="wan"||l.type==="wan-group"){
      const north=l.to==="R-S1",primary=l.role==="primary",logical=l.type==="wan-group";
      const start=logical?(north?-10:10):north?(primary?-17:-6):(primary?6:17);
      const end=logical?0:primary?-9:9;
      const mid=(north?510:mode==="summary"?660:735)+(logical||primary?0:28);
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
    if(item.type==="wan-group")return logicalState(item);
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

  function render(svg,data,selected,onSelect,mode="summary"){
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
      for(const item of display.links){
        const d=edgePath(item,mode),g=element("g",{class:"topology-item topology-link"});
        const backup=item.role==="backup"||item.type==="redundancy";
        g.append(element("path",{d,class:"topology-highlight"}));
        g.append(element("path",{d,class:"topology-edge"+(backup?" backup":"")}));
        g.append(element("path",{d,class:"topology-hit"}));
        if(item.type==="wan"||item.type==="wan-group"){
          const [bx,by]=layout[item.to],y=by+(item.type==="wan-group"?0:item.role==="primary"?-9:9);
          const label=item.type==="wan-group"?"WAN · "+item.to.slice(2):(item.role==="primary"?"Principal":"Respaldo")+" · "+item.to.slice(2);
          g.append(element("text",{x:bx-65,y:y-4,"text-anchor":"end",class:"topology-edge-label"},label));
        }
        activate(g,item,selected,onSelect);svg.append(g);elements.set(item.id,g);
      }
      for(const item of display.nodes){
        const [x,y]=layout[item.id],g=element("g",{class:"topology-item topology-node"});
        g.append(element("rect",{x:x-54,y:y-23,width:108,height:46,rx:8,class:"topology-node-box"}));
        g.append(element("text",{x,y:y-3,"text-anchor":"middle",class:"topology-node-label"},item.type==="server"?(item.id==="FRONTAL_HQ"?"Frontal HA":"Backend "+item.site):name(item)));
        const sub=item.type==="router"?"FRR":item.type==="switch"?"Bridge L2":item.type==="server"?"HTTP":"Host de prueba";
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
  root.NetlabTopology=Object.freeze({valid,name,details,render,reset,view,aged,isFresh:fresh,logicalState,edgePath,geometry,viewport,moveViewport});
})(typeof window==="undefined"?globalThis:window);
