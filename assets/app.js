
async function loadConfig(){
  const res = await fetch('site.config.json');
  const cfg = await res.json();
  return cfg;
}

function cardHTML(p, lang='ar'){
  const title = lang === 'ar' ? p.title_ar || p.title_en || p.title : p.title_en || p.title_ar || p.title;
  const desc = lang === 'ar' ? p.summary_ar || p.summary_en || '' : p.summary_en || p.summary_ar || '';
  const read = lang === 'ar' ? 'قراءة' : 'Read';
  return `
  <article class="card">
    <div class="meta">${new Date(p.date).toLocaleDateString()}</div>
    <h3>${title}</h3>
    <p>${desc}</p>
    <div style="display:flex;gap:8px;align-items:center">
      <a href="${p.path}" class="badge">${read}</a>
      <span class="lang-note">${p.lang || ''}</span>
    </div>
  </article>`;
}

async function loadPosts(lang='ar'){
  const res = await fetch('posts/index.json?ts='+Date.now());
  const posts = await res.json();
  const container = document.getElementById('posts');
  container.innerHTML = posts.map(p => cardHTML(p, lang)).join('');
}

async function applyLang(lang){
  const cfg = await loadConfig();
  const title = document.getElementById('site-title');
  const desc = document.getElementById('site-desc');
  const footer = document.getElementById('footer-text');
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  if(lang === 'ar'){
    title.textContent = cfg.site_name_ar;
    desc.textContent = cfg.site_description_ar;
  }else{
    title.textContent = cfg.site_name_en;
    desc.textContent = cfg.site_description_en;
  }
  await loadPosts(lang);
}

document.addEventListener('DOMContentLoaded', async () => {
  const cfg = await loadConfig();
  const langToggle = document.getElementById('lang-toggle');
  let current = cfg.language_default || 'ar';
  await applyLang(current);
  langToggle.textContent = current === 'ar' ? 'EN' : 'AR';
  langToggle.addEventListener('click', async () => {
    current = current === 'ar' ? 'en' : 'ar';
    langToggle.textContent = current === 'ar' ? 'EN' : 'AR';
    await applyLang(current);
  });
});
