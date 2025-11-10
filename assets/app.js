
async function loadConfig(){ const res = await fetch('site.config.json'); return res.json(); }
async function loadTools(){ const res = await fetch('tools.json?ts='+Date.now()); return res.json(); }

function toolCard(t, lang='ar'){
  const title = lang==='ar' ? t.title_ar : t.title_en;
  const desc  = lang==='ar' ? t.desc_ar  : t.desc_en;
  return `<article class="card">
    <h3>${title}</h3>
    <p>${desc}</p>
    <a class="btn" href="${t.path}" target="_blank" rel="noopener">فتح الأداة</a>
    <span class="tag">${(t.tags||[]).slice(0,3).join(' • ')}</span>
  </article>`;
}

async function renderTools(filter='', lang='ar'){
  const tools = await loadTools();
  const q = (filter || '').toLowerCase();
  const filtered = tools.filter(t => {
    const hay = [t.title_ar, t.title_en, t.desc_ar, t.desc_en, ...(t.tags||[])].join(' ').toLowerCase();
    return hay.includes(q);
  });
  const list = (q ? filtered : tools);
  document.getElementById('tools').innerHTML = list.map(t => toolCard(t, lang)).join('');
}

async function applyLang(lang){
  const cfg = await loadConfig();
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  document.getElementById('site-title').textContent = (lang==='ar'? cfg.site_name_ar : cfg.site_name_en);
  document.getElementById('site-desc').textContent  = (lang==='ar'? cfg.site_description_ar : cfg.site_description_en);
  await renderTools(document.getElementById('tool-search').value, lang);
}

document.addEventListener('DOMContentLoaded', async () => {
  const cfg = await loadConfig();
  const langToggle = document.getElementById('lang-toggle');
  const input = document.getElementById('tool-search');
  const clearBtn = document.getElementById('clear-search');
  let current = cfg.language_default || 'ar';

  langToggle.textContent = current === 'ar' ? 'EN' : 'AR';
  await applyLang(current);

  langToggle.addEventListener('click', async () => {
    current = current === 'ar' ? 'en' : 'ar';
    langToggle.textContent = current === 'ar' ? 'EN' : 'AR';
    await applyLang(current);
  });

  input.addEventListener('input', () => renderTools(input.value, current));
  clearBtn.addEventListener('click', () => { input.value=''; renderTools('', current); });
});
