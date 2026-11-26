/* Contrato visual de series históricas; no accede a sesiones ni a la red. */
(function(root) {
  "use strict";
  const catalog={
    collection:[["exporter","SCRAPE_AVAILABILITY","Exportador"],["collector","COLLECTOR_READ","Colector"]],
    routers:["HQ","S1","S2"].map(s=>["R-"+s,"CONTAINER_RUNNING_ONLY","Router "+s]),
    wan:["HQ","S1","S2"].flatMap((s,i)=>
      (i===0?["s1p","s1b","s2p","s2b"]:i===1?["s1p","s1b"]:["s2p","s2b"])
        .map(n=>["WAN-END-"+s+"-"+n,"ADMIN_STATE_ONLY",s+" / "+n])),
    vlan:[110,120,130,210,220,230,310,320,330].map(n=>["VLAN-"+n,"ADMIN_STATE_ONLY","VLAN "+n])
  };
  const windows={"5m":300,"15m":900,"1h":3600};
  // Paletas categóricas por identidad, independientes del significado del estado.
  const palettes=Object.freeze({
    dark:Object.freeze(["#82c7ff","#ffd078","#d3b2ff","#64e4d1","#ff9bd1","#ffb37e","#b8e77c","#b3c2d5","#ff9da4"]),
    light:Object.freeze(["#06468c","#654000","#55217c","#00544e","#831848","#843500","#30520b","#354353","#8b1020"])
  });

  function stateLabel(scope,value) {
    const labels={
      SCRAPE_AVAILABILITY:["Scrape no disponible","Scrape disponible"],
      COLLECTOR_READ:["Lectura fallida","Lectura disponible"],
      CONTAINER_RUNNING_ONLY:["Contenedor detenido","Contenedor en ejecución"],
      ADMIN_STATE_ONLY:["Administrativamente inactiva","Administrativamente activa"]
    };
    return value+" · "+labels[scope][value];
  }

  function allowed(group,span) {
    return Object.hasOwn(catalog,group)&&Object.hasOwn(windows,span);
  }

  function validate(data,group,span) {
    if(!allowed(group,span)||data?.project!=="NETLAB360"||data.schema_version!==1||
      data.source!=="PROMETHEUS_S04"||data.group!==group||data.window!==span||
      data.network_mutations_authorized!==false||data.scrape_interval_seconds!==2||
      !["OK","INVALID","UNAVAILABLE","NOT_STARTED"].includes(data.transport)||
      !Number.isSafeInteger(data.start_epoch)||!Number.isSafeInteger(data.end_epoch)||
      data.end_epoch-data.start_epoch!==windows[span]||
      !Array.isArray(data.series)||data.series.length!==catalog[group].length)
      throw new Error("INVALID_HISTORY");
    const seen=new Set();
    for(const row of data.series) {
      const expected=catalog[group].find(x=>x[0]===row?.id);
      if(!expected||seen.has(row.id)||row.scope!==expected[1]||
        !Array.isArray(row.points)||row.points.length>2000||
        (data.transport!=="OK"&&row.points.length)) throw new Error("INVALID_SERIES");
      seen.add(row.id);
      let last=data.start_epoch;
      for(const point of row.points) {
        if(!Array.isArray(point)||point.length!==2||typeof point[0]!=="number"||
          !Number.isFinite(point[0])||point[0]<=last||point[0]>data.end_epoch||
          ![null,0,1].includes(point[1])) throw new Error("INVALID_POINT");
        last=point[0];
      }
    }
    return data;
  }

  function counts(data) {
    let valid=0,missing=0,series=0;
    for(const row of data.series) {
      const n=row.points.filter(p=>p[1]!==null).length;
      valid+=n;missing+=row.points.length-n;series+=Number(n>0);
    }
    return {valid,missing,series};
  }

  function description(group) {
    return {collection:"Disponibilidad de scrape y lectura del colector.",
      routers:"Existencia de contenedores; no acredita adyacencias OSPF.",
      wan:"Estado administrativo de los extremos WAN; no acredita tráfico ni conectividad.",
      vlan:"Estado administrativo de subinterfaces; no acredita ACL ni conectividad."}[group];
  }

  function figure(data,format,colors) {
    const traces=[];
    const entries=catalog[data.group];
    const light=colors.theme === "light";
    const palette=palettes[light ? "light" : "dark"];
    // Eje numérico en epoch: la etiqueta y el hover se formatean en Panamá.
    // Cada serie tiene una banda propia para evitar superposición de estados.
    for(const [index,[id,scope,name]] of entries.entries()) {
      const row=data.series.find(s=>s.id===id);
      const points=row.points.filter(p=>p[1]!==null);
      const lane=(entries.length-index-1)*3;
      traces.push({
        type:"scatter",mode:"markers",name,
        x:points.map(p=>p[0]),y:points.map(p=>lane+p[1]),
        customdata:points.map(p=>[format(new Date(p[0]*1000)),stateLabel(scope,p[1])]),
        marker:{size:light?7:5,color:palette[index],symbol:points.map(p=>p[1]===1?"circle":"x")},
        hovertemplate:name+"<br>%{customdata[0]}<br>%{customdata[1]}<extra></extra>",
        showlegend:true
      });
    }
    const ticks=entries.map((_,i)=>(entries.length-i-1)*3+0.5);
    const span=data.end_epoch-data.start_epoch;
    const times=Array.from({length:5},(_,i)=>data.start_epoch+span*i/4);
    const plotHeight=Math.max(180,entries.length*56);
    const layout={
      height:plotHeight+90,autosize:true,separators:".,",uirevision:data.group+":"+data.window,
      paper_bgcolor:colors.surface,plot_bgcolor:colors.surface,font:{color:colors.text,size:12},
      margin:{l:130,r:20,t:12,b:78},hovermode:"closest",dragmode:"zoom",
      xaxis:{type:"linear",range:[data.start_epoch,data.end_epoch],tickmode:"array",
        tickvals:times,ticktext:times.map(t=>format(new Date(t*1000)).slice(11)),gridcolor:colors.line},
      yaxis:{tickmode:"array",tickvals:ticks,ticktext:entries.map(x=>x[2]),range:[-0.6,entries.length*3-0.8],
        fixedrange:true,gridcolor:colors.line,zeroline:false},
      legend:{orientation:"h",x:0.5,xanchor:"center",y:-36/plotHeight,yanchor:"top"},
      modebar:{color:colors.text,activecolor:palette[0],bgcolor:colors.surface},showlegend:true
    };
    return {traces,layout};
  }

  root.NetlabHistory=Object.freeze({allowed,validate,counts,description,figure});
})(typeof window==="undefined"?globalThis:window);
