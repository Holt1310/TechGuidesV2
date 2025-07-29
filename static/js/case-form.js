// Basic dependent field handler
function setupDependencies(relations) {
  Object.keys(relations).forEach(fieldId => {
    const config = relations[fieldId];
    const el = document.querySelector(`[name="${fieldId}"]`);
    if (el) {
      el.addEventListener('change', () => {
        fetch('/api/case/related-data/' + config.table, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            match_column: config.match_column,
            value: el.value,
            return_columns: config.return_columns
          })
        })
        .then(r => r.json())
        .then(data => {
          if(data.success){
            config.targets.forEach((target, idx) => {
              const dest = document.querySelector(`[name="${target}"]`);
              if(dest){
                dest.value = data.data[config.return_columns[idx]] || dest.value;
              }
            });
          }
        });
      });
    }
  });
}
