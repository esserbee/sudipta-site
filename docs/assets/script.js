(function () {
  const root = document.documentElement;
  const themeToggle = document.querySelector('[data-theme-toggle]');
  const header = document.querySelector('.site-header');
  const navToggle = document.querySelector('.nav-toggle');

  // Theme bootstrap
  let current = root.getAttribute('data-theme') || 'dark';

  function setIcon(theme) {
    if (!themeToggle) return;
    if (theme === 'dark') {
      themeToggle.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="4"/><path d="M3 12h1M20 12h1M12 3v1M12 20v1M5.6 5.6l.7.7M17.7 17.7l.7.7M5.6 18.4l.7-.7M17.7 6.3l.7-.7"/></svg>';
      themeToggle.setAttribute('aria-label', 'Switch to light mode');
    } else {
      themeToggle.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 0 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
      themeToggle.setAttribute('aria-label', 'Switch to dark mode');
    }
  }

  root.setAttribute('data-theme', current);
  setIcon(current);

  if (themeToggle) {
    themeToggle.addEventListener('click', () => {
      current = current === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', current);
      setIcon(current);
    });
  }

  // Mobile nav
  if (navToggle && header) {
    navToggle.addEventListener('click', () => {
      const open = header.classList.toggle('nav-open');
      navToggle.setAttribute('aria-expanded', String(open));
    });
  }

  // Year in footer
  const yearEl = document.getElementById('year');
  if (yearEl) {
    yearEl.textContent = new Date().getFullYear();
  }
})();

// Live citation counts via Semantic Scholar API (falls back to hardcoded values on error)
(async function updateCitations() {
  const API_BASE = 'https://api.semanticscholar.org/graph/v1/paper/DOI:';
  const FIELDS = '?fields=citationCount';

  const articles = Array.from(document.querySelectorAll('[data-doi]'));
  if (!articles.length) return;

  const results = await Promise.all(
    articles.map(async (article) => {
      const doi = article.dataset.doi;
      const span = article.querySelector('.citation-count');
      try {
        const res = await fetch(API_BASE + doi + FIELDS);
        if (!res.ok) return null;
        const data = await res.json();
        const count = data.citationCount;
        if (typeof count === 'number') {
          if (span) span.textContent = count;
          return count;
        }
      } catch (_) {}
      return null;
    })
  );

  const allFetched = results.every((c) => c !== null);
  if (allFetched) {
    const total = results.reduce((sum, c) => sum + c, 0);
    document.querySelectorAll('.citation-total').forEach((el) => {
      el.textContent = total + '+';
    });
  }
})();
