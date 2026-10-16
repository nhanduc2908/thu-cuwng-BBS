(() => {
  const themeButton = document.getElementById('themeToggle');
  const savedTheme = localStorage.getItem('waggy-product-theme');
  if (savedTheme === 'dark') document.documentElement.dataset.theme = 'dark';
  themeButton?.addEventListener('click', () => {
    const dark = document.documentElement.dataset.theme !== 'dark';
    if (dark) document.documentElement.dataset.theme = 'dark';
    else delete document.documentElement.dataset.theme;
    localStorage.setItem('waggy-product-theme', dark ? 'dark' : 'light');
  });
})();
