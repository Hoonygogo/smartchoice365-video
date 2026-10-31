// Smart Choice 365: private one-hour image handoff; never commits image bytes to Git.
const SIZE=8*1024*1024, TTL=3600;
const reply=(x,status=200)=>new Response(JSON.stringify(x),{status,headers:{"content-type":"application/json","cache-control":"no-store"}});
const equal=(a,b)=>{let v=a.length^b.length;for(let i=0;i<Math.max(a.length,b.length);i++)v|=(a.charCodeAt(i)||0)^(b.charCodeAt(i)||0);return v===0;};
export default {async fetch(req,env){
 const url=new URL(req.url);
 if(url.pathname==="/health"&&req.method==="GET")return reply({ok:true});
 if(!env.ASSETS||!env.HANDOFF_TOKEN)return reply({error:"Missing KV binding or secret"},503);
 const auth=(req.headers.get("authorization")||"").replace(/^Bearer /i,"");
 if(!auth||!equal(auth,env.HANDOFF_TOKEN))return reply({error:"Unauthorized"},401);
 const m=url.pathname.match(/^\/assets\/([A-Za-z0-9_-]{8,80})$/);
 if(!m)return reply({error:"Not found"},404);
 const key="temporary:"+m[1];
 if(req.method==="PUT"){
   const type=(req.headers.get("content-type")||"").split(";")[0].toLowerCase();
   if(!["image/png","image/jpeg","image/webp"].includes(type))return reply({error:"Invalid image type"},415);
   if(Number(req.headers.get("content-length")||0)>SIZE)return reply({error:"Image too large"},413);
   const data=await req.arrayBuffer(),b=new Uint8Array(data);
   if(!b.length||b.length>SIZE)return reply({error:"Invalid image size"},413);
   const png=[137,80,78,71,13,10,26,10].every((x,i)=>b[i]===x);
   const jpg=b[0]===255&&b[1]===216&&b[2]===255;
   const webp=String.fromCharCode(...b.slice(0,4))==="RIFF"&&String.fromCharCode(...b.slice(8,12))==="WEBP";
   if(!((type==="image/png"&&png)||(type==="image/jpeg"&&jpg)||(type==="image/webp"&&webp)))return reply({error:"File signature mismatch"},415);
   const sha=Array.from(new Uint8Array(await crypto.subtle.digest("SHA-256",data))).map(x=>x.toString(16).padStart(2,"0")).join("");
   await env.ASSETS.put(key,data,{expirationTtl:TTL,metadata:{type,sha,size:b.length}});
   return reply({stored:true,id:m[1],sha256:sha,size:b.length,expires_in_seconds:TTL},201);
 }
 if(req.method==="GET"){
  const item=await env.ASSETS.getWithMetadata(key,"arrayBuffer");
  if(!item.value)return reply({error:"Expired or missing"},404);
  return new Response(item.value,{headers:{"content-type":item.metadata?.type||"application/octet-stream","cache-control":"no-store","x-content-sha256":item.metadata?.sha||""}});
 }
 if(req.method==="DELETE"){await env.ASSETS.delete(key);return reply({deleted:true});}
 return reply({error:"Method not allowed"},405);
}};