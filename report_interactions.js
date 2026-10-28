/* Embedded into report.html; no network or external runtime required. */
(() => {
  const table = document.querySelector('.analysis');
  const menu = document.getElementById('correctness-filter');
  const filterButton = document.querySelector('.correctness-filter-trigger');
  const categoryMenu = document.getElementById('category-filter');
  const categoryButton = document.querySelector('.category-filter-trigger');
  const categories = [...table.querySelectorAll('.analysis-group')].map(group => group.dataset.category);
  let selectedCategories = new Set(categories);
  const categoryBoxes = () => [...categoryMenu.querySelectorAll('input[name="category"]')];
  const statuses = ['passed', 'failed', 'partial', 'skipped', 'not_run'];
  let selected = new Set(statuses);
  const rows = () => [...table.querySelectorAll('.operator-row')];
  const boxes = () => [...menu.querySelectorAll('input[name="correctness"]')];
  const detailStatuses = ['passed', 'failed', 'error', 'skipped', 'not_run'];
  const detailSelections = new WeakMap();
  const detailBoxes = dialog => [...dialog.querySelectorAll('input[name="detail-accuracy"]')];

  function refreshDetailDraft(dialog) {
    const checked = detailBoxes(dialog).filter(box => box.checked).length;
    const all = dialog.querySelector('[data-detail-select-all]');
    all.checked = checked === detailStatuses.length;
    all.indeterminate = checked > 0 && checked < detailStatuses.length;
  }

  function openDetailFilter(button) {
    const dialog = button.closest('.operator-details-view');
    const popup = dialog.querySelector('.detail-filter-menu');
    if (popup.matches(':popover-open')) { popup.hidePopover(); return; }
    const selection = detailSelections.get(dialog) || new Set(detailStatuses);
    detailBoxes(dialog).forEach(box => { box.checked = selection.has(box.value); });
    refreshDetailDraft(dialog);
    popup.querySelectorAll('[data-detail-count]').forEach(span => {
      span.textContent = [...dialog.querySelectorAll('.detail-row')].filter(row => row.dataset.accuracy === span.dataset.detailCount).length;
    });
    positionMenu(popup, button);
  }

  function applyDetailFilter(dialog) {
    const selection = new Set(detailBoxes(dialog).filter(box => box.checked).map(box => box.value));
    detailSelections.set(dialog, selection);
    const detailRows = [...dialog.querySelectorAll('.detail-row')];
    let matches = 0;
    detailRows.forEach(row => { row.hidden = !selection.has(row.dataset.accuracy); if (!row.hidden) matches++; });
    dialog.querySelector('.detail-empty').hidden = matches !== 0;
    dialog.querySelector('[data-detail-filter-status]').textContent = `筛选匹配 ${matches} / ${detailRows.length} 条明细`;
    const button = dialog.querySelector('.detail-filter-trigger');
    button.classList.toggle('is-filtered', selection.size !== detailStatuses.length);
    button.querySelector('.filter-mark').hidden = selection.size === detailStatuses.length;
    dialog.querySelector('.detail-filter-menu').hidePopover();
  }

  function refreshRows() {
    let totalMatches = 0;
    for (const group of table.querySelectorAll('.analysis-group')) {
      const toggle = group.querySelector('.category-toggle');
      const collapsed = toggle.getAttribute('aria-expanded') === 'false';
      let matches = 0;
      for (const row of group.querySelectorAll('.operator-row')) {
        const match = selectedCategories.has(group.dataset.category) && selected.has(row.dataset.correctness);
        if (match) matches++;
        row.hidden = collapsed || !match;
      }
      group.hidden = matches === 0;
      totalMatches += matches;
      const count = group.querySelectorAll('.operator-row').length;
      group.querySelector('.category-count').textContent = matches === count ? `${count} 个算子` : `${matches} / ${count} 个算子`;
      toggle.querySelector('.group-caret').textContent = collapsed ? '▸' : '▾';
    }
    document.getElementById('analysis-empty').hidden = totalMatches !== 0;
    document.getElementById('analysis-filter-status').textContent = `筛选匹配 ${totalMatches} / ${rows().length} 个算子 · 点击分类行可折叠或展开`;
    filterButton.classList.toggle('is-filtered', selected.size !== statuses.length);
    filterButton.querySelector('.filter-mark').hidden = selected.size === statuses.length;
    categoryButton.classList.toggle('is-filtered', selectedCategories.size !== categories.length);
    categoryButton.querySelector('.filter-mark').hidden = selectedCategories.size === categories.length;
  }

  function refreshDraft() {
    const checked = boxes().filter(box => box.checked).length;
    const all = document.getElementById('filter-select-all');
    all.checked = checked === statuses.length;
    all.indeterminate = checked > 0 && checked < statuses.length;
  }

  function openFilter() {
    boxes().forEach(box => { box.checked = selected.has(box.value); });
    refreshDraft();
    const counts = Object.fromEntries(statuses.map(status => [status, rows().filter(row => selectedCategories.has(row.closest('.analysis-group').dataset.category) && row.dataset.correctness === status).length]));
    menu.querySelectorAll('[data-status-count]').forEach(span => { span.textContent = counts[span.dataset.statusCount]; });
    positionMenu(menu, filterButton);
  }

  function positionMenu(popup, button) {
    popup.showPopover();
    const rect = button.getBoundingClientRect();
    popup.style.left = `${Math.max(8, Math.min(rect.left, window.innerWidth - popup.offsetWidth - 8))}px`;
    popup.style.top = `${Math.max(8, Math.min(rect.bottom + 6, window.innerHeight - popup.offsetHeight - 8))}px`;
  }

  function refreshCategoryDraft() {
    const checked = categoryBoxes().filter(box => box.checked).length;
    const all = document.getElementById('category-select-all');
    all.checked = checked === categories.length;
    all.indeterminate = checked > 0 && checked < categories.length;
  }

  function openCategories() {
    categoryBoxes().forEach(box => { box.checked = selectedCategories.has(box.value); });
    refreshCategoryDraft();
    categoryMenu.querySelectorAll('[data-category-count]').forEach(span => {
      const group = [...table.querySelectorAll('.analysis-group')].find(group => group.dataset.category === span.dataset.categoryCount);
      span.textContent = [...group.querySelectorAll('.operator-row')].filter(row => selected.has(row.dataset.correctness)).length;
    });
    positionMenu(categoryMenu, categoryButton);
  }

  function applyCategories() {
    selectedCategories = new Set(categoryBoxes().filter(box => box.checked).map(box => box.value));
    refreshRows();
    categoryMenu.hidePopover();
  }

  function applyFilter() {
    selected = new Set(boxes().filter(box => box.checked).map(box => box.value));
    refreshRows();
    menu.hidePopover();
  }

  function revealTarget() {
    const target = document.getElementById(location.hash.slice(1));
    if (!target) return;
    if (target.tagName === 'DIALOG') {
      if (!target.open) target.showModal();
    } else {
      target.scrollIntoView({ behavior: 'instant', block: 'start' });
    }
  }

  async function copyCode(button) {
    const text = document.getElementById(button.dataset.copyid).textContent;
    const previous = button.textContent;
    button.disabled = true;
    let copied = false;
    if (navigator.clipboard && window.isSecureContext) {
      try { await navigator.clipboard.writeText(text); copied = true; } catch (_) { /* fall through for local files */ }
    }
    if (!copied) {
      const textarea = document.createElement('textarea');
      textarea.value = text;
      textarea.style.cssText = 'position:fixed;left:0;top:0;opacity:0;pointer-events:none';
      const owner = button.closest('dialog') || document.body;
      owner.appendChild(textarea);
      textarea.select();
      try { copied = document.execCommand('copy'); } catch (_) { copied = false; }
      textarea.remove();
      button.focus({ preventScroll: true });
    }
    button.textContent = copied ? '已复制' : '复制失败';
    button.dataset.copyState = copied ? 'copied' : 'failed';
    button.disabled = false;
    setTimeout(() => { button.textContent = previous; delete button.dataset.copyState; }, 1800);
  }

  document.addEventListener('click', event => {
    const detailLink = event.target.closest('[data-detailid]');
    if (detailLink) {
      event.preventDefault();
      const dialog = document.getElementById(detailLink.dataset.detailid);
      if (!dialog.open) dialog.showModal();
      return;
    }
    if (event.target.tagName === 'DIALOG') {
      const rect = event.target.getBoundingClientRect();
      if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) event.target.close();
      return;
    }
    const trigger = event.target.closest('.code-trigger');
    if (trigger) { document.getElementById(trigger.dataset.codeid).showModal(); return; }
    const close = event.target.closest('.close-dialog');
    if (close) { close.closest('dialog').close(); return; }
    const copy = event.target.closest('.copy-code');
    if (copy) { copyCode(copy); return; }
    const category = event.target.closest('.category-toggle');
    if (category) { category.setAttribute('aria-expanded', String(category.getAttribute('aria-expanded') === 'false')); refreshRows(); return; }
    const detailFilter = event.target.closest('.detail-filter-trigger');
    if (detailFilter) { openDetailFilter(detailFilter); return; }
    const detailAction = event.target.closest('[data-detail-action]');
    if (detailAction) {
      const dialog = detailAction.closest('.operator-details-view');
      if (detailAction.dataset.detailAction === 'cancel') dialog.querySelector('.detail-filter-menu').hidePopover();
      else {
        detailBoxes(dialog).forEach(box => { box.checked = detailAction.dataset.detailAction === 'clear' || box.value === 'passed'; });
        applyDetailFilter(dialog);
      }
      return;
    }
    if (event.target.closest('.category-filter-trigger')) {
      if (categoryMenu.matches(':popover-open')) categoryMenu.hidePopover(); else openCategories();
      return;
    }
    if (event.target.closest('[data-category-action="clear"]')) {
      categoryBoxes().forEach(box => { box.checked = true; }); applyCategories(); return;
    }
    if (event.target.closest('[data-category-action="cancel"]')) { categoryMenu.hidePopover(); return; }
    if (event.target.closest('.correctness-filter-trigger')) {
      if (menu.matches(':popover-open')) menu.hidePopover(); else openFilter();
      return;
    }
    if (event.target.closest('[data-filter-action="passed"]')) {
      boxes().forEach(box => { box.checked = box.value === 'passed'; }); applyFilter(); return;
    }
    if (event.target.closest('[data-filter-action="clear"]')) {
      boxes().forEach(box => { box.checked = true; }); applyFilter(); return;
    }
    if (event.target.closest('[data-filter-action="cancel"]')) { menu.hidePopover(); return; }
    const link = event.target.closest('a[href^="#op-"]');
    if (link && link.hash === location.hash) revealTarget();
  });
  document.addEventListener('change', event => {
    if (event.target.matches('.code-variant')) {
      const select = event.target;
      document.querySelectorAll('.code-variant-pane').forEach(pane => {
        if (pane.dataset.variantGroup === select.dataset.group) pane.hidden = pane.dataset.variant !== select.value;
      });
    }
    if (event.target.id === 'filter-select-all') boxes().forEach(box => { box.checked = event.target.checked; });
    if (menu.contains(event.target)) refreshDraft();
    if (event.target.id === 'category-select-all') categoryBoxes().forEach(box => { box.checked = event.target.checked; });
    if (categoryMenu.contains(event.target)) refreshCategoryDraft();
    const detailDialog = event.target.closest('.operator-details-view');
    if (detailDialog && event.target.closest('.detail-filter-menu')) {
      if (event.target.hasAttribute('data-detail-select-all')) detailBoxes(detailDialog).forEach(box => { box.checked = event.target.checked; });
      refreshDetailDraft(detailDialog);
    }
  });
  document.addEventListener('submit', event => {
    if (event.target.matches('.detail-filter-form')) { event.preventDefault(); applyDetailFilter(event.target.closest('.operator-details-view')); }
  });
  document.querySelectorAll('.operator-details-view').forEach(dialog => {
    const popup = dialog.querySelector('.detail-filter-menu');
    popup.addEventListener('toggle', event => { dialog.querySelector('.detail-filter-trigger').setAttribute('aria-expanded', String(event.newState === 'open')); });
    dialog.addEventListener('close', () => { if (popup.matches(':popover-open')) popup.hidePopover(); });
  });
  menu.querySelector('form').addEventListener('submit', event => { event.preventDefault(); applyFilter(); });
  menu.addEventListener('toggle', event => { filterButton.setAttribute('aria-expanded', String(event.newState === 'open')); });
  categoryMenu.querySelector('form').addEventListener('submit', event => { event.preventDefault(); applyCategories(); });
  categoryMenu.addEventListener('toggle', event => { categoryButton.setAttribute('aria-expanded', String(event.newState === 'open')); });
  window.addEventListener('hashchange', revealTarget);
  window.addEventListener('load', revealTarget);
  refreshRows();
})();
