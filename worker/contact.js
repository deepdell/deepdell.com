const ALLOWED_ORIGINS = new Set(['https://deepdell.com', 'https://www.deepdell.com']);
const TO = 'bonjour.deepdell@gmail.com';
const FROM = 'DEEPDELL Website <leads@support.deepdell.com>';
const MAX_AUDIT_BODY = 12000;
const MAX_FETCH_BYTES = 300000;
const MAX_REDIRECTS = 5;
const FETCH_TIMEOUT = 1800;
const HOME_TIMEOUT = 3500;

const esc = (value) => String(value ?? '')
  .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;')
  .replace(/\"/g, '&quot;').replace(/'/g, '&#039;');
const clean = (value, max = 3000) => String(value ?? '').trim().slice(0, max);

function requestOrigin(request) {
  const origin = request.headers.get('Origin');
  return ALLOWED_ORIGINS.has(origin) ? origin : 'https://deepdell.com';
}
function originAllowed(request) {
  const origin = request.headers.get('Origin');
  return !origin || ALLOWED_ORIGINS.has(origin);
}
function response(body, status = 200, request) {
  return new Response(JSON.stringify(body), {
    status,
    headers: {
      'Content-Type': 'application/json; charset=utf-8',
      'Access-Control-Allow-Origin': requestOrigin(request || new Request('https://deepdell.com')),
      'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
      'Access-Control-Allow-Headers': 'Content-Type, Accept',
      'Vary': 'Origin',
      'Cache-Control': 'no-store'
    }
  });
}
function fail(message, status, request) { return response({ error: message }, status, request); }

function isIPv4(host) { return /^\d{1,3}(?:\.\d{1,3}){3}$/.test(host); }
function isPrivateIPv4(host) {
  if (!isIPv4(host)) return false;
  const p = host.split('.').map(Number);
  if (p.some(n => n > 255)) return true;
  const [a,b] = p;
  return a === 0 || a === 10 || a === 127 || (a === 169 && b === 254) || (a === 192 && b === 168) || (a === 172 && b >= 16 && b <= 31) || (a === 100 && b >= 64 && b <= 127) || (a === 198 && (b === 18 || b === 19)) || a >= 224;
}
function isPrivateHostname(host) {
  const h = host.toLowerCase().replace(/^\[|\]$/g, '').replace(/\.$/, '');
  return !h || h === 'localhost' || h.endsWith('.localhost') || h.endsWith('.local') || h.endsWith('.internal') || isPrivateIPv4(h) || h.includes(':');
}
function validPublicUrl(raw) {
  let u;
  try { u = new URL(String(raw || '').trim()); } catch { throw new Error('Please enter a valid public website URL.'); }
  if (!['http:','https:'].includes(u.protocol)) throw new Error('Only HTTP and HTTPS websites can be audited.');
  if (u.username || u.password) throw new Error('Authenticated URLs cannot be audited.');
  if (u.port && !['80','443'].includes(u.port)) throw new Error('Only standard HTTP/HTTPS ports are supported.');
  if (isPrivateHostname(u.hostname)) throw new Error('Please enter a public website accessible from the Internet.');
  u.hash = '';
  u.pathname = u.pathname || '/';
  return u;
}

const rateMap = new Map();
function rateLimited(request, keyPrefix, limit) {
  const ip = request.headers.get('CF-Connecting-IP') || 'unknown';
  const key = `${keyPrefix}:${ip}`;
  const now = Date.now();
  const old = rateMap.get(key);
  if (!old || now - old.start >= 60000) {
    rateMap.set(key, { start: now, count: 1 });
    if (rateMap.size > 500) rateMap.clear();
    return false;
  }
  old.count += 1;
  return old.count > limit;
}

const checks = [
  ['Core Discovery','robots.txt','/robots.txt',true],['Core Discovery','sitemap.xml','/sitemap.xml',true],['Core Discovery','sitemap index','/sitemap_index.xml',false],['Core Discovery','security.txt','/security.txt',false],
  ['AI Discovery','llms.txt','/llms.txt',true],['AI Discovery','llms-full.txt','/llms-full.txt',false],['AI Discovery','llms.md','/llms.md',false],['AI Discovery','llms-full.md','/llms-full.md',false],
  ['Agent Documents','agent.md','/agent.md',false],['Agent Documents','agents.md','/agents.md',false],['Agent Documents','agent.json','/agent.json',false],['Agent Documents','agents.json','/agents.json',false],['Agent Documents','ai.txt','/ai.txt',false],['Agent Documents','ai.md','/ai.md',false],['Agent Documents','ai.json','/ai.json',false],['Agent Documents','model-context.md','/model-context.md',false],
  ['Machine Context','machine-readable.md','/machine-readable.md',false],['Machine Context','machine-readable.txt','/machine-readable.txt',false],['Machine Context','ai-agent.md','/ai-agent.md',false],['Machine Context','agentic.md','/agentic.md',false],['Machine Context','agentic.json','/agentic.json',false],
  ['Additional Discovery','humans.txt','/humans.txt',false],['Additional Discovery','sitemap.txt','/sitemap.txt',false],['Additional Discovery','security.txt (well-known)','/.well-known/security.txt',false],['Additional Discovery','favicon.svg','/assets/favicon.svg',false]
];

async function fetchPublic(url, timeoutMs = FETCH_TIMEOUT) {
  let current;
  try { current = validPublicUrl(url); } catch { return { status:0, ok:false, text:'', finalUrl:url, error:'blocked' }; }
  for (let hop=0; hop<=MAX_REDIRECTS; hop++) {
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), timeoutMs);
    try {
      const r = await fetch(current.href, { method:'GET', redirect:'manual', cache:'no-store', headers:{'User-Agent':'DEEPDELL-Agentic-Audit/2.1','Accept':'text/html,text/plain,application/json,*/*;q=0.1'}, signal:controller.signal });
      if (r.status>=300 && r.status<400) {
        const location = r.headers.get('Location');
        if (!location || hop===MAX_REDIRECTS) return {status:r.status,ok:false,text:'',finalUrl:current.href,error:'redirect'};
        try { current=validPublicUrl(new URL(location,current.href).href); } catch { return {status:r.status,ok:false,text:'',finalUrl:current.href,error:'redirect-blocked'}; }
        continue;
      }
      if (r.status<200 || r.status>=400) return {status:r.status,ok:false,text:'',finalUrl:current.href};
      const len=Number(r.headers.get('Content-Length')||0);
      if (len>MAX_FETCH_BYTES) return {status:r.status,ok:false,text:'',finalUrl:current.href,error:'too-large'};
      const reader=r.body?.getReader();
      if (!reader) return {status:r.status,ok:true,text:'',finalUrl:current.href};
      const decoder=new TextDecoder(); let text='',bytes=0;
      while(bytes<MAX_FETCH_BYTES){const {value,done}=await reader.read();if(done)break;bytes+=value.byteLength;if(bytes>MAX_FETCH_BYTES){try{await reader.cancel()}catch{}return {status:r.status,ok:false,text:'',finalUrl:current.href,error:'too-large'};}text+=decoder.decode(value,{stream:true});}
      text+=decoder.decode();
      return {status:r.status,ok:true,text,finalUrl:current.href};
    } catch { return {status:0,ok:false,text:'',finalUrl:current.href,error:'timeout'}; }
    finally { clearTimeout(timer); }
  }
  return {status:0,ok:false,text:'',finalUrl:current.href,error:'redirect'};
}
function stripHtml(html){return html.replace(/<script[\s\S]*?<\/script>/gi,' ').replace(/<style[\s\S]*?<\/style>/gi,' ').replace(/<[^>]+>/g,' ').replace(/&nbsp;/gi,' ').replace(/\s+/g,' ').trim();}
function meta(html,name,attr='name'){const re=new RegExp(`<meta[^>]+${attr}=[\"']${name}[\"'][^>]+content=[\"']([^\"']*)[\"']|<meta[^>]+content=[\"']([^\"']*)[\"'][^>]+${attr}=[\"']${name}[\"']`,'i');const m=html.match(re);return m?(m[1]||m[2]||''):'';}
function linkHref(html,rel){const m=html.match(new RegExp(`<link[^>]+rel=[\"']${rel}[\"'][^>]+href=[\"']([^\"']+)[\"']|<link[^>]+href=[\"']([^\"']+)[\"'][^>]+rel=[\"']${rel}[\"']`,'i'));return m?(m[1]||m[2]||''):'';}
function title(html){const m=html.match(/<title[^>]*>([\s\S]*?)<\/title>/i);return m?stripHtml(m[1]):'';}
function count(html,tag){return(html.match(new RegExp(`<${tag}(?:\s|>)`,'gi'))||[]).length;}
function hasLd(html){return/<script[^>]+type=[\"']application\/ld\+json[\"'][^>]*>/i.test(html);}
function validJson(text){try{JSON.parse(text);return true}catch{return false}}

async function audit(request,body){
  if(!originAllowed(request))return fail('Origin not allowed.',403,request);
  if(rateLimited(request,'audit',6))return fail('Too many audit requests. Please wait a minute and try again.',429,request);
  let u;try{u=validPublicUrl(body.url)}catch(e){return fail(e.message,400,request)}
  const base=`${u.protocol}//${u.host}`;
  const home=await fetchPublic(u.href,HOME_TIMEOUT);
  if(!home.ok||!home.text)return fail('The public website could not be fetched. The URL must be reachable from the public Internet without login, VPN, IP allowlisting, or a blocked server-side request.',422,request);
  const html=home.text;
  const canonicalRaw=linkHref(html,'canonical');
  let canonical=false;try{canonical=!!canonicalRaw&&new URL(canonicalRaw,u.href).href.replace(/\/$/,'')===u.href.replace(/\/$/,'')}catch{}
  const lang=(html.match(/<html[^>]+lang=[\"']([^\"']+)/i)||[])[1]||'';
  const titleText=title(html),desc=meta(html,'description'),og=!!meta(html,'og:title','property');
  const bodyText=stripHtml(html),h1=count(html,'h1')>0,headings=count(html,'h1')+count(html,'h2')+count(html,'h3'),links=count(html,'a'),schema=hasLd(html);
  const results=[];
  for(let i=0;i<checks.length;i+=8){const batch=checks.slice(i,i+8);const out=await Promise.all(batch.map(async([group,name,path,standard])=>{const r=await fetchPublic(base+path,FETCH_TIMEOUT);let found=r.ok&&r.status>=200&&r.status<300&&!!r.text.trim();if((name==='UCP profile'||name==='A2A Agent Card')&&found)found=validJson(r.text);if(name.includes('MCP endpoint')&&[400,401,403,405,406].includes(r.status))found=true;return{group,name,path,standard,found,status:r.status}}));results.push(...out)}
  const found=n=>!!results.find(x=>x.name===n)?.found;
  const seoPoints=(u.protocol==='https:'?3:0)+(home.status>=200&&home.status<400?2:0)+(canonical?3:0)+(titleText.length>=20&&titleText.length<=65?2:0)+(desc.length>=70&&desc.length<=170?3:0)+(!!lang?1:0)+(og?1:0)+(schema?3:0)+(h1&&bodyText.length>=500&&headings>=3?2:0);
  const machinePoints=(found('robots.txt')?5:0)+(found('sitemap.xml')?5:0)+(found('sitemap index')?2:0)+(found('security.txt')?1:0)+(found('sitemap.txt')?1:0)+Math.min(6,results.filter(x=>x.group==='Additional'&&x.found&&!['security.txt','sitemap.txt'].includes(x.name)).length*2);
  const agentDocs=results.filter(x=>x.group==='Agent docs'&&x.found).length;
  const llmPoints=(found('llms.txt')?8:0)+(found('llms-full.txt')?4:0)+(found('llms.md')?2:0)+(found('llms-full.md')?2:0)+(agentDocs>0?4:0);
  const identityPoints=(found('machine-readable.md')?5:0)+(found('machine-readable.txt')?4:0)+(found('ai-agent.md')?4:0)+(found('agentic.md')?4:0)+(found('agentic.json')?3:0);
  const protocolPoints=0;
  const clamp=n=>Math.max(0,Math.min(20,Math.round(n)));
  const categories={technicalSeo:clamp(seoPoints),machineDiscovery:clamp(machinePoints),llmReadability:clamp(llmPoints),agentIdentity:clamp(identityPoints),agentProtocols:clamp(protocolPoints)};
  return response({ok:true,base:u.href.replace(/\/$/,''),mode:'server',homepage:{status:home.status,finalUrl:home.finalUrl,title:titleText,description:desc,canonical:canonicalRaw,canonicalPass:canonical,lang,og,structuredData:schema,h1,headings,links,textLength:bodyText.length},results,categories},200,request);
}

export default { async fetch(request,env){
  const url=new URL(request.url);
  if(request.method==='OPTIONS')return response({ok:true},200,request);
  if(url.pathname==='/api/config'){
    if(!originAllowed(request))return fail('Origin not allowed.',403,request);
    return response({ok:true,auditAvailable:true,emailAvailable:!!env.RESEND_API_KEY},200,request);
  }
  if(url.pathname==='/api/audit'){
    if(request.method==='POST'){
      const length=Number(request.headers.get('Content-Length')||0);if(length>MAX_AUDIT_BODY)return fail('Request is too large.',413,request);
      let body;try{body=await request.json()}catch{return fail('Invalid request.',400,request)}
      return audit(request,body);
    }
    if(request.method==='GET'){
      const raw=url.searchParams.get('url')||'';
      if(raw.length>4000)return fail('Audit URL is too long.',413,request);
      return audit(request,{url:raw});
    }
    return fail('Method not allowed.',405,request);
  }
  if(url.pathname!=='/api/contact')return fail('Not found.',404,request);
  if(request.method!=='POST')return fail('Method not allowed.',405,request);
  if(!originAllowed(request))return fail('Origin not allowed.',403,request);
  if(rateLimited(request,'contact',8))return fail('Too many requests. Please wait a minute and try again.',429,request);
  const length=Number(request.headers.get('Content-Length')||0);if(length>20000)return fail('Request is too large.',413,request);
  let data;try{data=await request.json()}catch{return fail('Invalid request.',400,request)}
  if(clean(data.website_field,200))return response({ok:true},200,request);
  const name=clean(data.name,120),email=clean(data.email,254),company=clean(data.company,160),website=clean(data.website,500),service=clean(data.service,120),phone=clean(data.phone,80),message=clean(data.message,5000),auditUrl=clean(data.audit_url,1000);
  if(!name||!email||!service||!message)return fail('Please complete all required fields.',400,request);
  if(!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email))return fail('Please enter a valid work email.',400,request);
  const subject=auditUrl?`New DEEPDELL lead — Agentic audit — ${company||name}`:`New DEEPDELL project enquiry — ${company||name}`;
  const html=`<!doctype html><html><body style="margin:0;background:#011434;color:#fff;font-family:Arial,Helvetica,sans-serif;padding:32px"><div style="max-width:680px;margin:auto"><div style="font-size:12px;letter-spacing:2px;color:#20f3fb">DEEPDELL / NEW LEAD</div><h1 style="font-size:28px;margin:12px 0 24px">${esc(name)}${company?` <span style="color:#89f9fd">· ${esc(company)}</span>`:''}</h1><table style="width:100%;border-collapse:collapse"><tr><td style="padding:12px 0;color:#89f9fd;width:150px">EMAIL</td><td style="padding:12px 0">${esc(email)}</td></tr><tr><td style="padding:12px 0;color:#89f9fd">SERVICE</td><td style="padding:12px 0">${esc(service)}</td></tr>${website?`<tr><td style="padding:12px 0;color:#89f9fd">WEBSITE</td><td style="padding:12px 0">${esc(website)}</td></tr>`:''}${phone?`<tr><td style="padding:12px 0;color:#89f9fd">PHONE</td><td style="padding:12px 0">${esc(phone)}</td></tr>`:''}${auditUrl?`<tr><td style="padding:12px 0;color:#89f9fd">AUDIT</td><td style="padding:12px 0"><a style="color:#20f3fb" href="${esc(auditUrl)}">${esc(auditUrl)}</a></td></tr>`:''}</table><div style="margin-top:22px;padding:20px;background:#021c3d;border:1px solid #17446b"><div style="font-size:11px;letter-spacing:1px;color:#89f9fd;margin-bottom:10px">PROJECT DETAILS</div><div style="white-space:pre-wrap;line-height:1.7">${esc(message)}</div></div><p style="color:#7189a3;font-size:12px;margin-top:24px">Reply directly to this email to respond to the lead.</p></div></body></html>`;
  const text=`DEEPDELL NEW LEAD\n\nName: ${name}\nEmail: ${email}\nCompany: ${company||'-'}\nWebsite: ${website||'-'}\nService: ${service}\nPhone: ${phone||'-'}\nAudit URL: ${auditUrl||'-'}\n\nMessage:\n${message}`;
  if(!env.RESEND_API_KEY)return fail('Email service is not configured.',503,request);
  try{const r=await fetch('https://api.resend.com/emails',{method:'POST',headers:{Authorization:`Bearer ${env.RESEND_API_KEY}`,'Content-Type':'application/json'},body:JSON.stringify({from:FROM,to:[TO],reply_to:email,subject,html,text})});const result=await r.json().catch(()=>({}));if(!r.ok)return fail(result?.message||'Unable to send your message right now.',502,request);return response({ok:true,id:result.id||null},200,request)}catch{return fail('Unable to reach the email service. Please try again.',502,request)}
}};