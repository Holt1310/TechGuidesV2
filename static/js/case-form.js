document.addEventListener('DOMContentLoaded', () => {
  const rulesEl = document.getElementById('case-rules');
  if (!rulesEl) return;
  let rules = [];
  try { rules = JSON.parse(rulesEl.dataset.rules || '[]'); } catch(e) { console.error(e); }

  rules.forEach(rule => {
    const src = document.querySelector(`[name="${rule.source}"]`);
    if (src) {
      src.addEventListener('change', () => applyRule(rule, src.value));
    }
  });

  function applyRule(rule, value) {
    if (!rule.table || !rule.match_column) return;
    const params = new URLSearchParams();
    params.append('column', rule.match_column);
    params.append('value', value);
    if (rule.map) {
      Object.values(rule.map).forEach(c => params.append('return', c));
    }
    fetch(`/api/data-tables/${rule.table}/related?` + params.toString())
      .then(r => r.json())
      .then(data => {
        if (data.success && data.row) {
          Object.entries(rule.map || {}).forEach(([fieldId, col]) => {
            if (data.row[col] !== undefined) {
              const tgt = document.querySelector(`[name="${fieldId}"]`);
              if (tgt) tgt.value = data.row[col];
            }
          });
        }
      })
      .catch(err => console.error('Case rule error', err));
  }
});
