/* Optional visual QA: node report/tests/browser_check.cjs <chrome.exe> <report.html> <output-dir>
 * Uses only Node built-ins and a temporary, isolated headless Chrome profile.
 */
const fs = require('node:fs');
const path = require('node:path');
const { spawn } = require('node:child_process');
const { pathToFileURL } = require('node:url');
const [chrome, input, out] = process.argv.slice(2);
if (!chrome || !input || !out) throw new Error('expected Chrome path, report.html path, and output directory');
const output = path.resolve(out);
fs.mkdirSync(output, { recursive: true });
const profile = path.join(output, 'headless-profile');
const child = spawn(chrome, ['--headless', '--no-sandbox', '--disable-gpu', '--disable-software-rasterizer',
  '--disable-background-networking', '--disable-component-update', '--disable-sync', '--no-first-run',
  '--no-default-browser-check', '--remote-debugging-pipe', '--user-data-dir=' + profile, 'about:blank'],
  { stdio: ['ignore', 'ignore', 'ignore', 'pipe', 'pipe'], windowsHide: true });
let pending = new Map(), sequence = 0, buffer = '';
child.stdio[4].on('data', chunk => {
  buffer += chunk.toString();
  let end;
  while ((end = buffer.indexOf('\0')) !== -1) {
    const raw = buffer.slice(0, end); buffer = buffer.slice(end + 1);
    if (!raw) continue;
    const result = JSON.parse(raw), callback = pending.get(result.id);
    if (callback) { pending.delete(result.id); result.error ? callback.reject(new Error(JSON.stringify(result.error))) : callback.resolve(result.result); }
  }
});
const timer = setTimeout(() => { child.kill(); process.exitCode = 1; console.error('browser QA timeout'); }, 25000);
function call(method, params = {}, sessionId) {
  return new Promise((resolve, reject) => {
    const id = ++sequence; pending.set(id, { resolve, reject });
    child.stdio[3].write(JSON.stringify({ id, method, params, ...(sessionId ? { sessionId } : {}) }) + '\0');
  });
}
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));
(async () => {
  try {
    const { targetId } = await call('Target.createTarget', { url: 'about:blank' });
    const { sessionId } = await call('Target.attachToTarget', { targetId, flatten: true });
    const evaluate = async expression => {
      const result = await call('Runtime.evaluate', { expression, returnByValue: true, awaitPromise: true }, sessionId);
      if (result.exceptionDetails) throw new Error(JSON.stringify(result.exceptionDetails));
      return result.result.value;
    };
    await call('Page.enable', {}, sessionId);
    await call('Emulation.setDeviceMetricsOverride', { width: 1440, height: 1100, deviceScaleFactor: 1, mobile: false }, sessionId);
    await call('Page.navigate', { url: pathToFileURL(path.resolve(input)).href }, sessionId);
    for (let i = 0; i < 50; i++) {
      if (await evaluate("document.readyState==='complete' && !!document.querySelector('.analysis a')")) break;
      await delay(100);
    }
    if (!await evaluate("document.title==='Triton 算子评测报告'&&document.querySelector('h1').textContent==='Triton 算子评测报告'")) throw new Error('report title was not updated');
    const setupLayout = await evaluate(`(() => {
      const panels=[...document.querySelectorAll('.setup-grid > .setup-block:not(.host)')];
      return {equalHeight:Math.abs(panels[0].getBoundingClientRect().height-panels[1].getBoundingClientRect().height)<1,
        noTilelang:[...document.querySelectorAll('.setup-grid .kv-k')].every(cell=>cell.textContent.toLowerCase()!=='tilelang')};
    })()`);
    if (!setupLayout.equalHeight || !setupLayout.noTilelang) throw new Error('setup panel layout or environment fields incorrect');
    async function screenshot(name) {
      await delay(250);
      const { data } = await call('Page.captureScreenshot', { format: 'png', captureBeyondViewport: false }, sessionId);
      fs.writeFileSync(path.join(output, name), Buffer.from(data, 'base64'));
    }
    await screenshot('overview.png');
    await evaluate("document.querySelector('.analysis').closest('section').scrollIntoView({behavior:'instant',block:'start'})");
    const layout = await evaluate(`(() => {
      const rows=[...document.querySelectorAll('.operator-row')];
      return {numbers:rows.every((row,index)=>Number(row.cells[0].textContent)===index+1),
        cleanNames:rows.every(row=>!row.cells[2].querySelector('.cell-sub')),
        expanded:[...document.querySelectorAll('.category-toggle')].every(button=>button.getAttribute('aria-expanded')==='true'),
        detailButtons:document.querySelectorAll('.operator-block .code-trigger').length};
    })()`);
    if (!layout.numbers || !layout.cleanNames || !layout.expanded || layout.detailButtons) throw new Error('analysis layout is incorrect: '+JSON.stringify(layout));
    await screenshot('analysis.png');
    const collapse = await evaluate(`(() => {
      const group=document.querySelector('.analysis-group'),button=group.querySelector('.category-toggle');
      button.click();const collapsed=[...group.querySelectorAll('.operator-row')].every(row=>row.hidden);
      button.click();return collapsed&&[...group.querySelectorAll('.operator-row')].every(row=>!row.hidden);
    })()`);
    if (!collapse) throw new Error('category collapse/expand failed');
    await evaluate("document.querySelector('.category-filter-trigger').click()");
    await screenshot('category-filter.png');
    await evaluate(`(() => {
      document.getElementById('category-select-all').click();
      document.querySelector('input[name=category][value=normalization]').click();
      document.querySelector('#category-filter form').requestSubmit();
    })()`);
    const categoryFiltered = await evaluate(`(() => {
      const rows=[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden);
      return rows.length===7&&rows.every(row=>row.closest('.analysis-group').dataset.category==='normalization');
    })()`);
    if (!categoryFiltered) throw new Error('single category filter failed');
    await evaluate("document.querySelector('.correctness-filter-trigger').click();document.querySelector('[data-filter-action=passed]').click()");
    if (!await evaluate("!document.getElementById('analysis-empty').hidden")) throw new Error('category/correctness intersection failed');
    await evaluate(`(() => {
      document.querySelector('.category-filter-trigger').click();
      document.querySelector('input[name=category][value=elementwise]').click();
      document.querySelector('#category-filter form').requestSubmit();
    })()`);
    if (!await evaluate("[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden).length===2")) throw new Error('multiple categories with correctness filter failed');
    await evaluate("document.querySelector('.correctness-filter-trigger').click();document.querySelector('[data-filter-action=clear]').click()");
    if (!await evaluate("[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden).length===15")) throw new Error('clearing correctness should preserve category selection');
    await evaluate(`(() => {
      document.querySelector('.category-filter-trigger').click();
      document.getElementById('category-select-all').click();
      document.querySelector('[data-category-action=cancel]').click();
    })()`);
    if (!await evaluate("[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden).length===15")) throw new Error('cancelling category draft changed active selection');
    await evaluate("document.querySelector('.category-filter-trigger').click();document.querySelector('[data-category-action=clear]').click()");
    if (!await evaluate("[...document.querySelectorAll('.operator-row')].every(row=>!row.hidden)")) throw new Error('clear category filter failed');
    await evaluate("document.querySelector('.correctness-filter-trigger').click()");
    await screenshot('filter.png');
    await evaluate("document.querySelector('[data-filter-action=passed]').click()");
    const filtered = await evaluate(`(() => {
      const rows=[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden);
      return {count:rows.length,passed:rows.every(row=>row.dataset.correctness==='passed'),
        green:rows.every(row=>getComputedStyle(row.cells[3]).color==='rgb(26, 107, 60)')};
    })()`);
    if (filtered.count!==2 || !filtered.passed || !filtered.green) throw new Error('passed filter or green scores failed: '+JSON.stringify(filtered));
    await screenshot('filtered.png');
    const combined = await evaluate(`(() => {
      const button=document.querySelector('.analysis-group:not([hidden]) .category-toggle');
      button.click();const collapsed=[...document.querySelectorAll('.operator-row')].every(row=>row.hidden);
      button.click();return collapsed&&[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden).length===2;
    })()`);
    if (!combined) throw new Error('category collapse did not preserve correctness filter');
    await evaluate(`(() => {
      document.querySelector('.correctness-filter-trigger').click();
      document.querySelectorAll('input[name=correctness]').forEach(box=>box.checked=false);
      document.querySelector('#correctness-filter form').requestSubmit();
    })()`);
    if (!await evaluate("!document.getElementById('analysis-empty').hidden")) throw new Error('empty filter state failed');
    await evaluate("document.querySelector('.correctness-filter-trigger').click();document.querySelector('[data-filter-action=clear]').click()");
    if (!await evaluate("[...document.querySelectorAll('.operator-row')].every(row=>!row.hidden)")) throw new Error('clear filter failed');
    await evaluate(`(() => {
      const row=[...document.querySelectorAll('.operator-row')].find(row=>row.querySelector('.case-link').textContent==='gelu');
      row.querySelector('.code-trigger').click();
    })()`);
    const code = await evaluate(`(() => {
      const dialog=document.querySelector('dialog[open]');
      return {open:dialog.open,source:dialog.textContent.includes('_gelu_fwd_kernel'),cceir:dialog.textContent.includes('DEMO ONLY'),
        python:dialog.querySelectorAll('.language-python .syntax-keyword').length>0,
        cpp:dialog.querySelectorAll('.language-cpp .syntax-comment').length>0};
    })()`);
    if (!code.open || !code.source || !code.cceir || !code.python || !code.cpp) throw new Error('operator code/highlighting failed');
    await evaluate("Object.defineProperty(navigator,'clipboard',{configurable:true,value:{writeText:async text=>{window.__copiedCode=text;}}})");
    for (const language of ['python','cpp']) {
      await evaluate(`(() => {const code=document.querySelector('dialog[open] .language-${language}');window.__expectedCode=code.textContent;document.querySelector('[data-copyid="'+code.id+'"]').click();})()`);
      await delay(50);
      if (!await evaluate("window.__copiedCode===window.__expectedCode")) throw new Error('copy text differs from original '+language+' source');
    }
    await evaluate(`(() => {
      Object.defineProperty(navigator,'clipboard',{configurable:true,value:undefined});
      document.execCommand=command=>{window.__fallbackCode=document.querySelector('dialog[open] textarea').value;return command==='copy';};
      document.querySelector('dialog[open] .copy-code').click();
    })()`);
    if (!await evaluate("window.__fallbackCode===document.querySelector('dialog[open] code.language-python').textContent")) throw new Error('local-file copy fallback failed');
    await screenshot('code.png');
    await evaluate("document.querySelector('dialog[open] .close-dialog').click()");
    const detailLink = await evaluate(`(() => {
      const link=[...document.querySelectorAll('.analysis .case-link')].find(link=>link.textContent==='softcap');
      link.click();return link.getAttribute('href');
    })()`);
    await evaluate("document.querySelector('dialog[open] .detail-filter-trigger').click()");
    await screenshot('detail-filter.png');
    await evaluate("document.querySelector('dialog[open] [data-detail-action=passed]').click()");
    const detailPassed = await evaluate(`(() => {
      const dialog=document.querySelector('dialog[open]'),rows=[...dialog.querySelectorAll('.detail-row')].filter(row=>!row.hidden);
      return rows.length===1&&rows[0].dataset.accuracy==='passed';
    })()`);
    if (!detailPassed) throw new Error('detail pass-only filter failed');
    await evaluate(`(() => {
      const dialog=document.querySelector('dialog[open]');dialog.querySelector('.detail-filter-trigger').click();
      dialog.querySelectorAll('input[name=detail-accuracy]').forEach(box=>box.checked=box.value==='failed');
      dialog.querySelector('.detail-filter-form').requestSubmit();
    })()`);
    if (!await evaluate("[...document.querySelectorAll('dialog[open] .detail-row')].filter(row=>!row.hidden).every(row=>row.dataset.accuracy==='failed')&&[...document.querySelectorAll('dialog[open] .detail-row')].filter(row=>!row.hidden).length===1")) throw new Error('detail failure filter failed');
    await evaluate(`(() => {
      const dialog=document.querySelector('dialog[open]');dialog.querySelector('.detail-filter-trigger').click();
      dialog.querySelectorAll('input[name=detail-accuracy]').forEach(box=>box.checked=false);
      dialog.querySelector('[data-detail-action=cancel]').click();
    })()`);
    if (!await evaluate("[...document.querySelectorAll('dialog[open] .detail-row')].filter(row=>!row.hidden).length===1")) throw new Error('cancel changed detail filter');
    await evaluate("document.querySelector('dialog[open] .detail-filter-trigger').click();document.querySelector('dialog[open] [data-detail-action=clear]').click()");
    if (!await evaluate("[...document.querySelectorAll('dialog[open] .detail-row')].filter(row=>!row.hidden).length===2")) throw new Error('clear detail filter failed');
    await evaluate(`(() => {
      const dialog=document.querySelector('dialog[open]');dialog.querySelector('.detail-filter-trigger').click();
      dialog.querySelector('[data-detail-select-all]').click();dialog.querySelector('.detail-filter-form').requestSubmit();
    })()`);
    if (!await evaluate("!document.querySelector('dialog[open] .detail-empty').hidden")) throw new Error('empty detail filter state failed');
    await evaluate("document.querySelector('dialog[open] .detail-filter-trigger').click();document.querySelector('dialog[open] [data-detail-action=passed]').click();document.querySelector('dialog[open] .close-dialog').click()");
    await evaluate(`document.querySelector('a[href="${detailLink}"]').click()`);
    if (!await evaluate("[...document.querySelectorAll('dialog[open] .detail-row')].filter(row=>!row.hidden).length===1&&document.querySelector('dialog[open] .detail-filter-trigger').classList.contains('is-filtered')")) throw new Error('reopening operator lost detail filter state');
    await evaluate("document.querySelector('dialog[open] .close-dialog').click()");
    if (!await evaluate("[...document.querySelectorAll('.operator-row')].every(row=>!row.hidden)")) throw new Error('detail filtering changed main analysis selection');
    await evaluate("document.querySelector('.correctness-filter-trigger').click();document.querySelector('[data-filter-action=passed]').click()");
    const jump = await evaluate(`(() => {
      const a=[...document.querySelectorAll('.analysis a')].find(a=>a.textContent==='gelu');
      window.__beforeDetailsScroll=window.scrollY;
      window.__beforeDetailsRows=[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden).map(row=>row.dataset.rowNumber).join(',');
      a.click(); return a.hash;
    })()`);
    await delay(100);
    const opened = await evaluate(`(() => {const target=document.querySelector(${JSON.stringify(jump)});return target.open&&target.classList.contains('operator-details-view')&&target.textContent.includes('17_test_gelu')&&target.querySelectorAll('thead th').length===5&&target.querySelector('.detail-row').cells[0].textContent==='_gelu_fwd_kernel'&&!target.textContent.includes('normal')&&window.scrollY===window.__beforeDetailsScroll;})()`);
    if (!opened) throw new Error('operator details popup did not open without jumping the page');
    if (!await evaluate("!document.querySelector('dialog[open] .detail-filter-trigger').classList.contains('is-filtered')")) throw new Error('detail filter leaked between operators');
    await screenshot('operator.png');
    await evaluate("document.querySelector('dialog[open] .close-dialog').click()");
    const preserved = await evaluate("window.scrollY===window.__beforeDetailsScroll&&window.__beforeDetailsRows===[...document.querySelectorAll('.operator-row')].filter(row=>!row.hidden).map(row=>row.dataset.rowNumber).join(',')");
    if (!preserved) throw new Error('closing details changed analysis scroll or filter');
    await evaluate(`document.querySelector('a[href="${jump}"]').click()`);
    await call('Input.dispatchKeyEvent', { type:'keyDown', key:'Escape', code:'Escape', windowsVirtualKeyCode:27 }, sessionId);
    await call('Input.dispatchKeyEvent', { type:'keyUp', key:'Escape', code:'Escape', windowsVirtualKeyCode:27 }, sessionId);
    if (!await evaluate("!document.querySelector('dialog[open]')")) throw new Error('Escape did not close details');
    await evaluate(`document.querySelector('a[href="${jump}"]').click()`);
    await call('Input.dispatchMouseEvent', { type:'mousePressed', x:8, y:8, button:'left', clickCount:1 }, sessionId);
    await call('Input.dispatchMouseEvent', { type:'mouseReleased', x:8, y:8, button:'left', clickCount:1 }, sessionId);
    if (!await evaluate("!document.querySelector('dialog[open]')")) throw new Error('backdrop did not close details');
    await call('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 1, mobile: true }, sessionId);
    await evaluate(`document.querySelector('a[href="${jump}"]').click()`);
    await screenshot('operator-mobile.png');
    if (!await evaluate("document.documentElement.scrollWidth<=window.innerWidth")) throw new Error('details popup caused mobile document overflow');
    await evaluate("document.querySelector('dialog[open] .close-dialog').click()");
    await evaluate("window.scrollTo({top:0,left:0,behavior:'instant'})");
    await screenshot('mobile.png');
    const overflow = await evaluate('document.documentElement.scrollWidth>window.innerWidth');
    if (overflow) throw new Error('mobile page has document-level horizontal overflow');
    console.log(JSON.stringify({ title:true, setupLayout, detailPassed, detailFilterIndependent:true, operatorDetailsPopup: opened, detailsStatePreserved:preserved, escapeAndBackdrop:true, layout, collapse, categoryFiltered, categoryIntersection:true, categoryCancel:true, combined, filtered, code, copyExact:true, fallbackCopy:true, mobileOverflow: overflow, screenshots: output }));
  } catch (error) {
    process.exitCode = 1; console.error(error);
  } finally {
    clearTimeout(timer);
    await call('Browser.close').catch(() => {});
    child.kill();
  }
})();
