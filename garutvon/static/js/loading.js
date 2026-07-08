function showLoading() {
  if (document.querySelector('.loading-overlay')) return;
  const overlay = document.createElement('div');
  overlay.className = 'loading-overlay';
  overlay.innerHTML = '<div class="loading-spinner" role="status" aria-label="Loading"></div>';
  document.body.appendChild(overlay);
}

function hideLoading() {
  const el = document.querySelector('.loading-overlay');
  if (el) el.remove();
}

document.addEventListener('DOMContentLoaded', () => {
  document.querySelectorAll('form[data-loading="true"]').forEach((form) => {
    form.addEventListener('submit', () => {
      showLoading();
      setTimeout(hideLoading, 10000);
    });
  });
});
