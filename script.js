/* i18n runtime: translate text that scripts create on translated pages (see tools/i18n_build.py). */
(function(){
  const D=window.DD_I18N; if(!D||!window.MutationObserver) return;
  const phrases=Object.keys(D).filter(k=>k.length>=8&&/\s/.test(k)).sort((a,b)=>b.length-a.length);
  const esc=s=>s.replace(/[.*+?^${}()|[\]\\]/g,'\\$&');
  const big=phrases.length?new RegExp(phrases.map(esc).join('|'),'g'):null;
  function tr(v){
    const key=v.replace(/\s+/g,' ').trim(); if(!key) return null;
    if(Object.prototype.hasOwnProperty.call(D,key)) return v.replace(v.trim(),()=>D[key]);
    if(big&&big.test(v)){big.lastIndex=0;return v.replace(big,m=>D[m]);}
    return null;
  }
  const ATTR=['placeholder','aria-label','title','alt'];
  const done=new WeakMap(); // node -> value we wrote; never re-translate our own output
  function walk(node){
    if(node.nodeType===3){const p=node.parentNode;if(p&&/^(SCRIPT|STYLE)$/.test(p.nodeName))return;if(done.get(node)===node.nodeValue)return;const t=tr(node.nodeValue);if(t!=null&&t!==node.nodeValue){node.nodeValue=t;}done.set(node,node.nodeValue);return;}
    if(node.nodeType!==1||/^(SCRIPT|STYLE)$/.test(node.nodeName))return;
    const seen=done.get(node)||{};
    for(const a of ATTR){const v=node.getAttribute&&node.getAttribute(a);if(v&&seen[a]!==v){const t=tr(v);const out=(t!=null?t:v);if(out!==v)node.setAttribute(a,out);seen[a]=out;}}
    done.set(node,seen);
    if((node.nodeName==='INPUT'||node.nodeName==='BUTTON')&&/^(button|submit)$/i.test(node.type)&&node.value){const t=tr(node.value);if(t)node.value=t;}
    for(let c=node.firstChild;c;c=c.nextSibling)walk(c);
  }
  const run=()=>{walk(document.body);new MutationObserver(list=>{for(const m of list){if(m.type==='characterData')walk(m.target);else m.addedNodes.forEach(walk);}}).observe(document.body,{childList:true,subtree:true,characterData:true});};
  if(document.body) run(); else document.addEventListener('DOMContentLoaded',run,{once:true});
  // Keep visitors inside their language when scripts build links to English pages.
  document.addEventListener('click',e=>{const a=e.target.closest&&e.target.closest('a[href^="/"]');if(!a)return;const h=a.getAttribute('href');const L=window.DD_LANG;if(L&&/^\/[\w-]+\.html/.test(h)&&!h.startsWith('/'+L+'/'))a.setAttribute('href','/'+L+h);},true);
})();
(()=>{
const path=location.pathname;
if(path==='/index.html'||path==='/index.htm'){location.replace('/'+location.search+location.hash);return}
const body=document.body,loader=document.getElementById('site-loader'),progress=document.querySelector('.scroll-progress'),header=document.querySelector('.site-header'),menu=document.querySelector('.menu');
body.classList.remove('light');try{localStorage.removeItem('deepdell-theme')}catch(e){}document.querySelectorAll('.theme-toggle,.contact-backup').forEach(el=>el.remove());
const meta=document.querySelector('meta[name="theme-color"]');if(meta)meta.content='#011434';

/* Keep the Agentic Readiness Checker visible in the primary navigation on every page. */
document.querySelectorAll('.nav').forEach(nav=>{if(!nav.querySelector('a[href="agentic-check.html"]')){const a=document.createElement('a');a.href='agentic-check.html';a.textContent='Agentic Check';nav.appendChild(a)}});
/* Group interactive tools into one DEEPDELL Lab submenu. */
document.querySelectorAll('.nav').forEach(nav=>{
 const agent=nav.querySelector('a[href="agentic-check.html"]');
 if(!agent||nav.querySelector('.nav-group'))return;
 const group=document.createElement('div');group.className='nav-group';
 const toggle=document.createElement('button');toggle.type='button';toggle.className='nav-group-toggle';toggle.setAttribute('aria-expanded','false');toggle.textContent='DEEPDELL Lab';
 const submenu=document.createElement('div');submenu.className='nav-submenu';submenu.setAttribute('aria-label','DEEPDELL Lab');
 const items=[['agentic-check.html','Agentic Check'],['commerce-calculator.html','E-Commerce Calculator'],['game.html','Commerce Reset Game']];
 items.forEach(([href,label])=>{const a=document.createElement('a');a.href=href;a.textContent=label;submenu.appendChild(a)});
 group.append(toggle,submenu);agent.replaceWith(group);
 toggle.addEventListener('click',e=>{e.stopPropagation();const open=group.classList.toggle('open');toggle.setAttribute('aria-expanded',String(open))});
document.addEventListener('click',e=>{if(!group.contains(e.target)){group.classList.remove('open');toggle.setAttribute('aria-expanded','false')}});
document.addEventListener('keydown',e=>{if(e.key==='Escape'){group.classList.remove('open');toggle.setAttribute('aria-expanded','false')}});
 submenu.querySelectorAll('a').forEach(a=>a.addEventListener('click',()=>{group.classList.remove('open');toggle.setAttribute('aria-expanded','false');header?.classList.remove('menu-open')}));
});
/* Enforce DEEPDELL Lab submenu behavior across desktop and mobile. */
const labNavStyle=document.createElement('style');
labNavStyle.textContent=`
.site-header .nav .nav-group{position:relative!important;display:flex!important;align-items:center!important;height:100%!important}
.site-header .nav .nav-group-toggle{appearance:none!important;border:0!important;background:transparent!important;color:#d5e3ef!important;font:600 13px Inter,Arial,sans-serif!important;line-height:1!important;cursor:pointer!important;padding:12px 10px!important;display:inline-flex!important;align-items:center!important;gap:7px!important;white-space:nowrap!important;border-radius:0!important}
.site-header .nav .nav-group-toggle:after{content:'⌄'!important;font-size:11px!important;color:#20f3fb!important;line-height:1!important;transition:transform .15s ease!important}
.site-header .nav .nav-group.open .nav-group-toggle:after{transform:rotate(180deg)!important}
.site-header .nav .nav-submenu{position:absolute!important;top:100%!important;left:50%!important;transform:translateX(-50%)!important;width:238px!important;box-sizing:border-box!important;padding:8px!important;background:#011434!important;border:1px solid rgba(137,249,253,.18)!important;border-radius:5px!important;box-shadow:0 18px 40px rgba(0,0,0,.48)!important;display:none!important;flex-direction:column!important;gap:2px!important;z-index:6000!important}
.site-header .nav .nav-submenu:before{content:''!important;position:absolute!important;left:0!important;right:0!important;top:-10px!important;height:10px!important;background:transparent!important}
.site-header .nav .nav-group:hover .nav-submenu,.site-header .nav .nav-group:focus-within .nav-submenu,.site-header .nav .nav-group.open .nav-submenu{display:flex!important}
.site-header .nav .nav-submenu a{display:flex!important;align-items:center!important;justify-content:flex-start!important;width:100%!important;box-sizing:border-box!important;min-height:40px!important;padding:10px 13px!important;color:#d5e3ef!important;text-decoration:none!important;white-space:nowrap!important;font:600 12px/1.2 Inter,Arial,sans-serif!important;border-radius:3px!important;position:relative!important}
.site-header .nav .nav-submenu a:after,.site-header .nav .nav-submenu a[aria-current="page"]:after{content:none!important;display:none!important}
.site-header .nav .nav-submenu a[aria-current="page"]{color:#20f3fb!important;background:rgba(32,243,251,.05)!important}
.site-header .nav .nav-submenu a:hover,.site-header .nav .nav-submenu a:focus-visible{color:#20f3fb!important;background:rgba(32,243,251,.07)!important}
@media(max-width:950px){
  .site-header.menu-open .nav .nav-group{display:block!important;width:100%!important;height:auto!important}
  .site-header.menu-open .nav .nav-group-toggle{width:100%!important;justify-content:space-between!important;padding:14px 4px!important}
  .site-header.menu-open .nav .nav-submenu,
  .site-header.menu-open .nav .nav-group:hover .nav-submenu,
  .site-header.menu-open .nav .nav-group:focus-within .nav-submenu{position:static!important;left:auto!important;top:auto!important;transform:none!important;width:100%!important;display:none!important;padding:3px 0 7px 10px!important;border:0!important;border-left:1px solid rgba(137,249,253,.18)!important;border-radius:0!important;box-shadow:none!important;background:transparent!important}
  .site-header.menu-open .nav .nav-group.open .nav-submenu{display:flex!important}
  .site-header.menu-open .nav .nav-submenu:before{display:none!important}
  .site-header.menu-open .nav .nav-submenu a{min-height:40px!important;padding:9px 10px!important;font-size:13px!important;color:#9db3ca!important}
  .site-header.menu-open .nav .nav-submenu a[aria-current="page"]{color:#20f3fb!important;background:transparent!important}
  .site-header.menu-open .nav .nav-submenu a:after{content:none!important;display:none!important}
}
`;
document.head.appendChild(labNavStyle);

/* Prefer the self-hosted icon assets. CDN icons are retained only as a compatibility fallback. */
document.querySelectorAll('img[src*="cdn.simpleicons.org/"]').forEach(img=>{const m=(img.getAttribute('src')||'').match(/cdn\.simpleicons\.org\/([^/?#]+)/);if(!m)return;const fallback=`https://cdn.jsdelivr.net/npm/simple-icons@v16/icons/${m[1]}.svg`;img.addEventListener('error',()=>{if(img.src!==fallback)img.src=fallback},{once:true});img.src=fallback});
const finish=()=>{if(!loader||loader.dataset.done)return;loader.dataset.done='1';loader.classList.add('loader-done');setTimeout(()=>loader.remove(),500)};addEventListener('load',()=>setTimeout(finish,120),{once:true});setTimeout(finish,1800);
menu?.addEventListener('click',()=>{const open=header?.classList.toggle('menu-open');menu.setAttribute('aria-expanded',String(!!open))});document.querySelectorAll('.nav a').forEach(a=>a.addEventListener('click',()=>header?.classList.remove('menu-open')));
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches,coarse=matchMedia('(pointer: coarse)').matches;let ticking=false;
const scroll=()=>{const y=scrollY,max=document.documentElement.scrollHeight-innerHeight;if(progress)progress.style.width=`${max>0?Math.min(100,y/max*100):0}%`;header?.classList.toggle('scrolled',y>20);if(!reduce){document.querySelectorAll('.hero-art,.shopify-visual,.dashboard,.architecture,.contact-panel,.page-hero>div').forEach(el=>{const r=el.getBoundingClientRect(),d=(r.top+r.height/2-innerHeight/2)/innerHeight;el.style.setProperty('--scroll-tilt',`${Math.max(-5,Math.min(5,-d*7))}deg`);el.style.setProperty('--scroll-depth',`${Math.max(-32,Math.min(32,-d*24))}px`)});const a=document.querySelector('.hero-art');if(a)a.style.setProperty('--scroll-y',`${Math.max(-38,Math.min(18,y*.035))}px`)}ticking=false};addEventListener('scroll',()=>{if(!ticking){ticking=true;requestAnimationFrame(scroll)}},{passive:true});scroll();
const targets=document.querySelectorAll('.service,.ai-grid article,.why-grid article,.steps article,.reveal,.arch-card,.vertical,.engagement,.digital-card,.protocol,.agent-step,.ops-copy,.live-console,.page-card,.agentic-home');if('IntersectionObserver'in window&&!reduce){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){const t=e.target,i=+(getComputedStyle(t).getPropertyValue('--i'))||0;if(i){t.style.transitionDelay=i*70+'ms';setTimeout(()=>{t.style.transitionDelay=''},900+i*70)}t.classList.add('visible');io.unobserve(t)}}),{threshold:.08,rootMargin:'0px 0px -30px'});targets.forEach(el=>{el.classList.add('reveal-item');io.observe(el)})}else targets.forEach(el=>el.classList.add('visible'));
const art=document.querySelector('.hero-art');if(art&&!reduce&&!coarse){const dots=[...art.querySelectorAll('.dot')];art.addEventListener('pointerenter',()=>art.classList.add('is-hovering'));art.addEventListener('pointermove',e=>{const r=art.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;art.style.setProperty('--mx',`${x*16}px`);art.style.setProperty('--my',`${y*12}px`);art.style.setProperty('--rx',`${-y*4}deg`);art.style.setProperty('--ry',`${x*5}deg`);dots.forEach((d,i)=>{const dx=((i*29)%100)/100-.5,dy=((i*47)%100)/100-.5,p=Math.max(0,1-Math.hypot(x-dx,y-dy)*2.8);d.style.transform=`translate(${(x-dx)*-18*p}px,${(y-dy)*-18*p}px) scale(${1+p*.35})`;d.style.boxShadow=p?`0 0 ${14+p*18}px rgba(32,243,251,.75)`:''})});art.addEventListener('pointerleave',()=>{art.classList.remove('is-hovering');['--mx','--my','--rx','--ry'].forEach(v=>art.style.setProperty(v,v.includes('r')?'0deg':'0px'));dots.forEach(d=>{d.style.transform='';d.style.boxShadow=''})});art.addEventListener('pointerdown',()=>{art.classList.remove('hit');void art.offsetWidth;art.classList.add('hit')})}
if(!reduce&&!coarse){document.querySelectorAll('.service,.page-card,.ai-grid article,.why-grid article,.steps article,.arch-card,.engagement,.digital-card,.protocol,.live-console,.agentic-card,.tech-item').forEach(card=>{card.addEventListener('pointermove',e=>{const r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;card.style.setProperty('--card-rx',`${-y*5}deg`);card.style.setProperty('--card-ry',`${x*6}deg`);card.style.setProperty('--spot-x',`${(x+.5)*100}%`);card.style.setProperty('--spot-y',`${(y+.5)*100}%`)});card.addEventListener('pointerleave',()=>{card.style.setProperty('--card-rx','0deg');card.style.setProperty('--card-ry','0deg')})});document.querySelectorAll('.btn').forEach(el=>{el.addEventListener('pointermove',e=>{const r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;el.style.transform=`translate(${x*3}px,${y*3}px) translateY(-2px)`});el.addEventListener('pointerleave',()=>el.style.transform='')})}
const intro=document.querySelector('.intro');if(intro&&!document.querySelector('.agentic-home')){const s=document.createElement('section');s.className='section-pad agentic-home';s.innerHTML=`<div class="section-kicker">02 / AGENTIC READINESS</div><div class="agentic-home-grid"><div class="agentic-home-copy"><div class="agentic-badge"><span></span>AI-READY CHECKER</div><h2>Check if your e-commerce site is <span>agentic-ready.</span></h2><p>See what autonomous shopping agents and AI systems can discover from your public website — and where the machine-readable layer needs improvement.</p><form class="agentic-mini-form" id="home-agentic-form"><input id="home-agentic-url" type="url" inputmode="url" autocomplete="url" placeholder="https://yourwebsite.com" aria-label="Website URL" required><button class="btn primary" type="submit">START AUDIT <span>↗</span></button></form><p class="agentic-form-note">Your audit is public-signal based. No password, admin access or private data is requested.</p><a class="text-link" href="agentic-check.html">Open full Agentic Readiness Checker <span>↗</span></a></div><div class="agentic-preview" aria-label="Agentic checker preview"><div class="preview-window"><div class="preview-bar"><span></span><span></span><span></span><b>AGENTIC READINESS</b></div><div class="preview-body"><div class="preview-url">https://yourwebsite.com</div><div class="preview-line strong">PUBLIC DISCOVERY SCAN</div><div class="preview-checks"><i>✓</i><span>robots.txt</span><b>FOUND</b><i>✓</i><span>sitemap.xml</span><b>FOUND</b><i>✓</i><span>llms.txt</span><b>FOUND</b><i>✓</i><span>machine-readable.md</span><b>FOUND</b><i>✓</i><span>agent.json</span><b>FOUND</b><i>✓</i><span>ai-agent.md</span><b>FOUND</b></div><div class="preview-score"><strong>25</strong><span>PUBLIC SIGNALS<br>CHECKED</span></div></div></div></div></div><div class="agentic-how"><div><strong>01</strong><span>Enter URL</span><small>Public website address</small></div><b>→</b><div><strong>02</strong><span>Discover</span><small>Public machine-readable signals</small></div><b>→</b><div><strong>03</strong><span>Report</span><small>Availability & gaps</small></div><b>→</b><div><strong>04</strong><span>Improve</span><small>DEEPDELL engineering</small></div></div>`;intro.after(s);s.querySelector('#home-agentic-form')?.addEventListener('submit',e=>{e.preventDefault();const u=s.querySelector('#home-agentic-url').value.trim();if(!u)return;location.href='agentic-check.html?url='+encodeURIComponent(u)})}
if(false){const graph={'@context':'https://schema.org','@graph':[{'@type':'Organization','@id':'https://deepdell.com/#organization','name':'DEEPDELL','url':'https://deepdell.com/','logo':'https://deepdell.com/assets/deepdell-lockup.svg','description':'Digital engineering company specialising in Shopify Plus, AI agents, agentic automation, systems integration, data and business intelligence, custom software and digital commerce.','email':'bonjour.deepdell@gmail.com','knowsAbout':['Shopify Plus','Shopify','AI agents','Agentic AI','AI automation','Digital commerce','B2B commerce','B2C commerce','Systems integration','GraphQL','React','Next.js','Node.js','TypeScript','PHP','Magento','Python','Data engineering','Business intelligence','Cloud infrastructure','Technical SEO','CRO']},{'@type':'WebSite','@id':'https://deepdell.com/#website','url':'https://deepdell.com/','name':'DEEPDELL','description':'Deep technology. Clear impact. Shopify Plus, AI, automation, data and digital engineering.','publisher':{'@id':'https://deepdell.com/#organization'}},{'@type':'WebPage','@id':'https://deepdell.com/#webpage','url':'https://deepdell.com/','name':'DEEPDELL — Shopify Plus, AI & Digital Engineering','description':'DEEPDELL engineers Shopify Plus commerce platforms, AI agents, agentic automation, business integrations, data systems and custom digital products.','isPartOf':{'@id':'https://deepdell.com/#website'},'about':{'@id':'https://deepdell.com/#organization'}}]};const sc=document.createElement('script');sc.type='application/ld+json';sc.dataset.deepdellSchema='1';sc.textContent=JSON.stringify(graph);document.head.appendChild(sc)}
// GA4 conversion events — emitted only after consent has loaded GA.
function deepdellEvent(name,params){try{if(typeof window.gtag==='function')window.gtag('event',name,params||{})}catch(e){}}
window.deepdellEvent=deepdellEvent;
document.addEventListener('click',e=>{const a=e.target.closest('a');if(!a)return;const href=a.getAttribute('href')||'';if(href.includes('agentic-check.html'))deepdellEvent('agentic_check_started',{link_location:path});if(href.includes('audit='))deepdellEvent('audit_cta_clicked',{link_location:path});if(href.includes('contact.html'))deepdellEvent('contact_cta_clicked',{link_location:path});if(href.includes('shopify-plus.html'))deepdellEvent('shopify_plus_cta_click',{link_location:path});if(href.includes('services.html'))deepdellEvent('service_cta_click',{link_location:path});if(href.includes('contact-card.html'))deepdellEvent('contact_card_clicked',{link_location:path});if(a.hasAttribute('download')&&href.includes('contact.vcf'))deepdellEvent('contact_card_downloaded',{link_location:path});if(href.startsWith('mailto:'))deepdellEvent('email_cta_click',{link_location:path})});
document.addEventListener('submit',e=>{const id=e.target?.id||'';if(id==='home-agentic-form')deepdellEvent('agentic_check_started',{link_location:'homepage'});if(id==='scan-form')deepdellEvent('agentic_check_started',{link_location:'agentic-check'});if(id==='deepdell-contact-form')deepdellEvent('contact_form_submitted',{link_location:path});});
document.addEventListener('focusin',e=>{if(e.target.closest?.('#deepdell-contact-form'))deepdellEvent('contact_form_started',{link_location:path});});
const page=path.split('/').pop()||'';document.querySelectorAll('.nav a').forEach(a=>{if(a.getAttribute('href')===page)a.setAttribute('aria-current','page')});
})();


// ─────────────────────────────────────────────────────────────
// DEEPDELL / WEB3FORMS — FREE CLIENT-SIDE DELIVERY
// Web3Forms requires its free API to be called from the browser.
// The access key is a public Web3Forms identifier, not a secret.
// We keep the key in the Worker environment and expose only that
// public identifier through /api/config, then submit directly to
// Web3Forms from the visitor's browser.
// ─────────────────────────────────────────────────────────────
(function(){
  const API='https://deepdell-contact.deepdell-api.workers.dev';
  let accessKeyPromise=null;

  async function getAccessKey(){
    if(!accessKeyPromise){
      accessKeyPromise=fetch(API+'/api/config',{headers:{'Accept':'application/json'},cache:'no-store'})
        .then(async response=>{
          const json=await response.json().catch(()=>({}));
          if(!response.ok || !json.ok || !json.web3formsAccessKey){
            throw new Error('Contact delivery is not configured.');
          }
          return json.web3formsAccessKey;
        })
        .catch(error=>{
          accessKeyPromise=null;
          throw error;
        });
    }
    return accessKeyPromise;
  }

  // Lightweight spam protection: a hidden honeypot field in every form plus a minimum
  // time-on-page. Bots that fill every field or submit instantly get a silent fake success.
  const pageStart=Date.now();
  function addHoneypots(){
    document.querySelectorAll('form').forEach(form=>{
      if(form.querySelector('input[name="botcheck"]')) return;
      const trap=document.createElement('input');
      trap.type='text';trap.name='botcheck';trap.tabIndex=-1;trap.autocomplete='off';trap.setAttribute('aria-hidden','true');
      trap.style.cssText='position:absolute!important;width:1px!important;height:1px!important;margin:-1px!important;padding:0!important;border:0!important;overflow:hidden!important;clip:rect(0 0 0 0)!important;clip-path:inset(50%)!important;white-space:nowrap!important;opacity:0!important;pointer-events:none!important';
      form.appendChild(trap);
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',addHoneypots,{once:true}); else addHoneypots();
  function looksAutomated(){
    const filled=[...document.querySelectorAll('input[name="botcheck"]')].some(i=>i.value.trim()!=='');
    return filled || Date.now()-pageStart<3000;
  }

  window.deepdellWeb3FormsConfigured=true;
  window.submitDeepdellForm=async function(payload){
    if(looksAutomated()) return {success:true,message:'Submitted.'};
    const accessKey=await getAccessKey();
    const response=await fetch('https://api.web3forms.com/submit',{
      method:'POST',
      headers:{'Content-Type':'application/json','Accept':'application/json'},
      body:JSON.stringify({access_key:accessKey,subject:'DEEPDELL Website Lead',from_name:'DEEPDELL Website',botcheck:'',...payload})
    });
    const json=await response.json().catch(()=>({}));
    if(!response.ok || json.success===false){
      throw new Error(json.message || json.body?.message || 'Web3Forms submission failed.');
    }
    return json;
  };
})();

// ─────────────────────────────────────────────────────────────
// DEEPDELL / FREE GOOGLE CONSENT MODE — BASIC MODE
// Google and Ahrefs scripts are not requested until the visitor allows analytics.
// No paid CMP is required for this implementation.
// ─────────────────────────────────────────────────────────────
(function(){
  const GA_ID='G-K592HB9G99';
  const AHREFS_KEY='O2AUj4tmiR8cKN9efAkM5Q';
  const KEY='deepdell-consent-v1';

  // Each page <head> only defines gtag() and the default-denied consent state.
  // gtag.js itself is requested from Google only after the visitor allows analytics.
  function loadGA(){
    if(typeof window.gtag!=='function') return false;
    if(document.querySelector('script[data-deepdell-ga]')) return true;
    window.gtag('js',new Date());
    window.gtag('config',GA_ID);
    const s=document.createElement('script');s.async=true;s.src='https://www.googletagmanager.com/gtag/js?id='+GA_ID;s.dataset.deepdellGa='1';document.head.appendChild(s);
    return true;
  }

  function loadAhrefs(){
    if(document.querySelector('script[data-deepdell-ahrefs]')) return;
    const s=document.createElement('script');s.src='https://analytics.ahrefs.com/analytics.js';s.async=true;s.dataset.key=AHREFS_KEY;s.dataset.deepdellAhrefs='1';document.head.appendChild(s);
  }

  function applyConsent(value){
    if(typeof window.gtag!=='function') return;
    window.gtag('consent','update',{
      analytics_storage:value==='accepted'?'granted':'denied',
      ad_storage:'denied',
      ad_user_data:'denied',
      ad_personalization:'denied'
    });
  }

  function setConsent(value){
    try{localStorage.setItem(KEY,value)}catch(e){}
    const banner=document.getElementById('deepdell-consent');
    if(banner) banner.remove();
    applyConsent(value);
    if(value==='accepted'){ loadGA(); loadAhrefs(); }
  }

  function showBanner(){
    if(document.getElementById('deepdell-consent')) return;
    const el=document.createElement('aside');
    el.id='deepdell-consent';
    el.setAttribute('aria-label','Cookie and analytics consent');
    el.innerHTML=
      '<div class="deepdell-consent-inner">'+
        '<div class="deepdell-consent-copy">'+
          '<div class="deepdell-consent-kicker">PRIVACY / ANALYTICS</div>'+
          '<strong>Help us improve DEEPDELL.</strong>'+
          '<p>We use Google Analytics to understand website usage and improve the experience. Analytics is off until you choose.</p>'+
          '<a href="/privacy.html">Privacy details</a>'+
        '</div>'+
        '<div class="deepdell-consent-actions">'+
          '<button type="button" class="deepdell-consent-secondary" data-consent="declined">Reject</button>'+
          '<button type="button" class="deepdell-consent-primary" data-consent="accepted">Allow analytics</button>'+
        '</div>'+
      '</div>';
    document.body.appendChild(el);
    el.querySelectorAll('[data-consent]').forEach(btn=>{
      btn.addEventListener('click',()=>setConsent(btn.dataset.consent));
    });
  }

  function init(){
    let choice=null;
    try{choice=localStorage.getItem(KEY)}catch(e){}
    // Nothing is requested from Google or Ahrefs until analytics is allowed.
    if(choice==='accepted'){ applyConsent('accepted'); loadGA(); loadAhrefs(); }
    else if(choice==='declined') applyConsent('declined');
    else showBanner();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();


/* ==== motion layer ==== */
(function(){
  const doc=document,root=doc.documentElement;
  const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
  const fine=matchMedia('(hover: hover) and (pointer: fine)').matches;
  const $$=(s,r)=>[...(r||doc).querySelectorAll(s)];
  const raf=fn=>{let q=0,a;return(...x)=>{a=x;if(!q){q=1;requestAnimationFrame(()=>{q=0;fn(...a)})}}};

  /* stagger index for grid children, used by the reveal observer */
  $$('.service-grid,.ai-grid,.why-grid,.steps,.tech-grid,.tool-cloud,.vertical-grid,.cap-list,.engagement-grid,.protocol-grid').forEach(g=>{[...g.children].forEach((c,i)=>c.style.setProperty('--i',i%7))});

  /* animated counters for the dashboard metrics */
  function counter(el){
    const m=el.textContent.match(/^([^\d-]*)(\d[\d.,]*)(.*)$/);if(!m)return null;
    const dec=(m[2].split('.')[1]||'').length,grp=m[2].includes(','),end=parseFloat(m[2].replace(/,/g,''));
    const nf=new Intl.NumberFormat('en-US',{minimumFractionDigits:dec,maximumFractionDigits:dec,useGrouping:grp});
    const final=el.textContent;
    return{reset(){el.textContent=m[1]+nf.format(0)+m[3]},run(){const t0=performance.now(),D=1500;const step=n=>{const p=Math.min(1,(n-t0)/D),e=p===1?1:1-Math.pow(2,-10*p);el.textContent=m[1]+nf.format(end*e)+m[3];if(p<1)requestAnimationFrame(step);else el.textContent=final};requestAnimationFrame(step)}};
  }
  if(!reduce&&'IntersectionObserver'in window){
    const io=new IntersectionObserver(es=>es.forEach(e=>{if(!e.isIntersecting)return;io.unobserve(e.target);const c=e.target._fxc;if(c)c.run();if(e.target.classList.contains('bars'))e.target.classList.add('in-view')}),{threshold:.35});
    $$('.metric-row strong').forEach(el=>{const c=counter(el);if(c){c.reset();el._fxc=c;io.observe(el)}});
    $$('.bars').forEach(b=>io.observe(b));
  }else $$('.bars').forEach(b=>b.classList.add('in-view'));

  if(reduce)return;

  /* ambient aurora behind the page */
  const au=doc.createElement('div');au.className='fx-aurora';au.setAttribute('aria-hidden','true');au.innerHTML='<i></i><i></i><i></i>';doc.body.prepend(au);

  /* button shine */
  $$('.btn.primary,.header-cta').forEach(b=>{const s=doc.createElement('i');s.className='fx-shine';s.setAttribute('aria-hidden','true');b.appendChild(s)});

  if(!fine)return;

  /* cursor glow, card spotlight and magnetic buttons (mouse devices only) */
  const cur=doc.createElement('div');cur.className='fx-cursor';cur.setAttribute('aria-hidden','true');doc.body.appendChild(cur);
  const cards=$$('.service,.ai-grid article,.why-grid article,.steps article,.vertical,.arch-card,.engagement,.protocol,.tech-item,.page-card,.digital-card,.agentic-card,.live-console');
  cards.forEach(c=>{if(getComputedStyle(c).position==='static')c.style.position='relative';c.classList.add('fx-card');const g=doc.createElement('i');g.className='fx-glow';g.setAttribute('aria-hidden','true');c.appendChild(g)});
  const mags=$$('.btn.primary,.header-cta');
  const move=raf((x,y,t)=>{cur.style.setProperty('--cx',x+'px');cur.style.setProperty('--cy',y+'px');cur.classList.add('on');
    const card=t.closest&&t.closest('.fx-card');if(card){const r=card.getBoundingClientRect();card.style.setProperty('--gx',(x-r.left)+'px');card.style.setProperty('--gy',(y-r.top)+'px')}
    mags.forEach(b=>{const r=b.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2,dx=x-cx,dy=y-cy,d=Math.hypot(dx,dy),R=Math.max(r.width,r.height)/2+46;
      if(d<R){b.style.setProperty('--tx',Math.max(-7,Math.min(7,dx*.16))+'px');b.style.setProperty('--ty',Math.max(-5,Math.min(5,dy*.2))+'px')}else{b.style.setProperty('--tx','0px');b.style.setProperty('--ty','0px')}})});
  addEventListener('pointermove',e=>move(e.clientX,e.clientY,e.target),{passive:true});
  doc.addEventListener('pointerleave',()=>cur.classList.remove('on'));

  /* drifting network canvas behind page heroes */
  $$('.hero,.page-hero').forEach(host=>{
    const cv=doc.createElement('canvas');cv.className='fx-net';cv.setAttribute('aria-hidden','true');host.appendChild(cv);
    const ctx=cv.getContext('2d');let w=0,h=0,nodes=[],run=false,id=0,mx=-1e3,my=-1e3;
    const size=()=>{const r=host.getBoundingClientRect(),d=Math.min(devicePixelRatio||1,1.5);w=r.width;h=r.height;cv.width=w*d;cv.height=h*d;ctx.setTransform(d,0,0,d,0,0);
      const n=Math.max(20,Math.min(60,Math.round(w*h/22000)));nodes=Array.from({length:n},()=>({x:Math.random()*w,y:Math.random()*h,vx:(Math.random()-.5)*.3,vy:(Math.random()-.5)*.3,r:Math.random()*1.4+.7}))};
    const draw=()=>{ctx.clearRect(0,0,w,h);
      for(const a of nodes){a.x+=a.vx;a.y+=a.vy;if(a.x<0||a.x>w)a.vx*=-1;if(a.y<0||a.y>h)a.vy*=-1;const dx=mx-a.x,dy=my-a.y,d=Math.hypot(dx,dy);if(d<160&&d>1){a.x+=dx/d*.35;a.y+=dy/d*.35}}
      for(let i=0;i<nodes.length;i++){const a=nodes[i];
        for(let j=i+1;j<nodes.length;j++){const b=nodes[j],d=Math.hypot(a.x-b.x,a.y-b.y);if(d<135){ctx.strokeStyle='rgba(32,243,251,'+(.2*(1-d/135)).toFixed(3)+')';ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(b.x,b.y);ctx.stroke()}}
        const dm=Math.hypot(a.x-mx,a.y-my);if(dm<170){ctx.strokeStyle='rgba(137,249,253,'+(.5*(1-dm/170)).toFixed(3)+')';ctx.beginPath();ctx.moveTo(a.x,a.y);ctx.lineTo(mx,my);ctx.stroke()}
        ctx.fillStyle='rgba(137,249,253,.75)';ctx.beginPath();ctx.arc(a.x,a.y,a.r,0,6.283);ctx.fill()}};
    const loop=()=>{draw();id=run?requestAnimationFrame(loop):0};
    const start=()=>{if(!run&&!doc.hidden){run=true;id=requestAnimationFrame(loop)}},stop=()=>{run=false;cancelAnimationFrame(id)};
    size();new ResizeObserver(raf(size)).observe(host);
    new IntersectionObserver(es=>es[0].isIntersecting?start():stop()).observe(host);
    doc.addEventListener('visibilitychange',()=>doc.hidden?stop():start());
    host.addEventListener('pointermove',e=>{const r=host.getBoundingClientRect();mx=e.clientX-r.left;my=e.clientY-r.top},{passive:true});
    host.addEventListener('pointerleave',()=>{mx=-1e3;my=-1e3});
  });
})();
