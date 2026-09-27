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
const targets=document.querySelectorAll('.service,.ai-grid article,.why-grid article,.steps article,.reveal,.arch-card,.vertical,.engagement,.digital-card,.protocol,.agent-step,.ops-copy,.live-console,.page-card,.agentic-home');if('IntersectionObserver'in window&&!reduce){const io=new IntersectionObserver(es=>es.forEach(e=>{if(e.isIntersecting){e.target.classList.add('visible');io.unobserve(e.target)}}),{threshold:.08,rootMargin:'0px 0px -30px'});targets.forEach(el=>{el.classList.add('reveal-item');io.observe(el)})}else targets.forEach(el=>el.classList.add('visible'));
const art=document.querySelector('.hero-art');if(art&&!reduce&&!coarse){const dots=[...art.querySelectorAll('.dot')];art.addEventListener('pointerenter',()=>art.classList.add('is-hovering'));art.addEventListener('pointermove',e=>{const r=art.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;art.style.setProperty('--mx',`${x*16}px`);art.style.setProperty('--my',`${y*12}px`);art.style.setProperty('--rx',`${-y*4}deg`);art.style.setProperty('--ry',`${x*5}deg`);dots.forEach((d,i)=>{const dx=((i*29)%100)/100-.5,dy=((i*47)%100)/100-.5,p=Math.max(0,1-Math.hypot(x-dx,y-dy)*2.8);d.style.transform=`translate(${(x-dx)*-18*p}px,${(y-dy)*-18*p}px) scale(${1+p*.35})`;d.style.boxShadow=p?`0 0 ${14+p*18}px rgba(32,243,251,.75)`:''})});art.addEventListener('pointerleave',()=>{art.classList.remove('is-hovering');['--mx','--my','--rx','--ry'].forEach(v=>art.style.setProperty(v,v.includes('r')?'0deg':'0px'));dots.forEach(d=>{d.style.transform='';d.style.boxShadow=''})});art.addEventListener('pointerdown',()=>{art.classList.remove('hit');void art.offsetWidth;art.classList.add('hit')})}
if(!reduce&&!coarse){document.querySelectorAll('.service,.page-card,.ai-grid article,.why-grid article,.steps article,.arch-card,.engagement,.digital-card,.protocol,.live-console,.agentic-card,.tech-item').forEach(card=>{card.addEventListener('pointermove',e=>{const r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;card.style.setProperty('--card-rx',`${-y*5}deg`);card.style.setProperty('--card-ry',`${x*6}deg`);card.style.setProperty('--spot-x',`${(x+.5)*100}%`);card.style.setProperty('--spot-y',`${(y+.5)*100}%`)});card.addEventListener('pointerleave',()=>{card.style.setProperty('--card-rx','0deg');card.style.setProperty('--card-ry','0deg')})});document.querySelectorAll('.btn').forEach(el=>{el.addEventListener('pointermove',e=>{const r=el.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;el.style.transform=`translate(${x*3}px,${y*3}px) translateY(-2px)`});el.addEventListener('pointerleave',()=>el.style.transform='')})}
const intro=document.querySelector('.intro');if(intro&&!document.querySelector('.agentic-home')){const s=document.createElement('section');s.className='section-pad agentic-home';s.innerHTML=`<div class="section-kicker">02 / AGENTIC READINESS</div><div class="agentic-home-grid"><div class="agentic-home-copy"><div class="agentic-badge"><span></span>AI-READY CHECKER</div><h2>Check if your e-commerce site is <span>agentic-ready.</span></h2><p>See what autonomous shopping agents and AI systems can discover from your public website — and where the machine-readable layer needs improvement.</p><form class="agentic-mini-form" id="home-agentic-form"><input id="home-agentic-url" type="url" inputmode="url" autocomplete="url" placeholder="https://yourwebsite.com" aria-label="Website URL" required><input id="home-agentic-email" type="email" autocomplete="email" placeholder="Business email" aria-label="Business email" required><button class="btn primary" type="submit">START AUDIT <span>↗</span></button></form><p class="agentic-form-note">Your audit is public-signal based. No password, admin access or private data is requested.</p><a class="text-link" href="agentic-check.html">Open full Agentic Readiness Checker <span>↗</span></a></div><div class="agentic-preview" aria-label="Agentic checker preview"><div class="preview-window"><div class="preview-bar"><span></span><span></span><span></span><b>AGENTIC READINESS</b></div><div class="preview-body"><div class="preview-url">https://yourwebsite.com</div><div class="preview-line strong">PUBLIC DISCOVERY SCAN</div><div class="preview-checks"><i>✓</i><span>robots.txt</span><b>FOUND</b><i>✓</i><span>sitemap.xml</span><b>FOUND</b><i>✓</i><span>llms.txt</span><b>FOUND</b><i>✓</i><span>/.well-known/ucp</span><b>FOUND</b><i>✓</i><span>agent-card.json</span><b>FOUND</b><i>!</i><span>MCP endpoint</span><b class="muted">CHECK</b></div><div class="preview-score"><strong>86</strong><span>/ 100<br>READINESS</span></div></div></div></div></div><div class="agentic-how"><div><strong>01</strong><span>Enter URL</span><small>Public website address</small></div><b>→</b><div><strong>02</strong><span>Discover</span><small>Protocols & machine files</small></div><b>→</b><div><strong>03</strong><span>Report</span><small>Availability & gaps</small></div><b>→</b><div><strong>04</strong><span>Improve</span><small>DEEPDELL engineering</small></div></div>`;intro.after(s);s.querySelector('#home-agentic-form')?.addEventListener('submit',e=>{e.preventDefault();const u=s.querySelector('#home-agentic-url').value.trim(),email=s.querySelector('#home-agentic-email').value.trim();if(!u||!email)return;try{sessionStorage.setItem('deepdell-audit-email',email)}catch(err){}location.href='agentic-check.html?url='+encodeURIComponent(u)+'&email='+encodeURIComponent(email)})}
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
// DEEPDELL / FREE GOOGLE CONSENT MODE — BASIC MODE
// Google tags do not load until the visitor chooses.
// No paid CMP is required for this implementation.
// ─────────────────────────────────────────────────────────────
(function(){
  const GA_ID='G-K592HB9G99';
  const KEY='deepdell-consent-v1';

  // Google tag is installed statically in each page <head>.
  // This file only applies the visitor's Consent Mode choice.
  function loadGA(){
    return typeof window.gtag==='function';
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
    loadGA();
    applyConsent(value);
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
    // Always load the Google tag with Consent Mode default-denied.
    // This lets Google/Tag Assistant detect the tag without enabling
    // analytics storage before the visitor makes a choice.
    loadGA();
    if(choice==='accepted') applyConsent('accepted');
    else if(choice==='declined') applyConsent('declined');
    else showBanner();
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init,{once:true});
  else init();
})();
