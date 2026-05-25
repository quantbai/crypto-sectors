/* ==========================================================================
   crypto-sectors viz site — app.js
   D3 v7 + vanilla JS. No framework, no build step.
   ========================================================================== */

// ---------------------------------------------------------------------------
// State + pub-sub (10-line emitter)
// ---------------------------------------------------------------------------
const emitter = (() => {
  const listeners = {};
  return {
    on(event, fn) {
      (listeners[event] = listeners[event] || []).push(fn);
    },
    emit(event, data) {
      (listeners[event] || []).forEach(fn => fn(data));
    }
  };
})();

const state = {
  selectedAsset: null,   // asset object from assets_flat
  filterCellKey: null,   // "{sector_code}:{chain}" when heatmap cell active
  searchQuery: '',
  searchMatchIds: null,  // Set of asset_ids matching current search (null = no filter)
  sunburstMode: 'overview', // 'overview' | 'zoomed'
  zoomedSubSector: null,    // sub-sector node when zoomed
};

function setState(patch) {
  Object.assign(state, patch);
  Object.keys(patch).forEach(k => emitter.emit('state:' + k, state[k]));
  emitter.emit('state', state);
}

// ---------------------------------------------------------------------------
// Helpers
// ---------------------------------------------------------------------------
const CLASS_COLORS = {
  10: 'var(--class-10)',
  20: 'var(--class-20)',
  30: 'var(--class-30)',
  40: 'var(--class-40)',
};

const CLASS_COLORS_HEX = {
  10: 'hsl(36,78%,62%)',
  20: 'hsl(214,72%,64%)',
  30: 'hsl(286,56%,68%)',
  40: 'hsl(146,44%,56%)',
};

function getClassColor(classCode) {
  return CLASS_COLORS[classCode] || 'var(--fg-3)';
}

function getClassColorHex(classCode) {
  return CLASS_COLORS_HEX[classCode] || '#575a60';
}

// Derive sub-sector sibling color using L-delta from DESIGN.md §2.7
// In practice we use oklch approximation via HSL luminance shift.
// siblings sorted by asset count desc (already done in taxonomy.json build).
function subSectorColor(classCode, siblingPos, nSiblings) {
  const lDelta = nSiblings <= 1
    ? 0
    : -8 + (siblingPos / Math.max(nSiblings - 1, 1)) * 16;
  // We shift lightness in HSL as a proxy for OKLCH L-delta
  const base = {
    10: [36, 78, 62],
    20: [214, 72, 64],
    30: [286, 56, 68],
    40: [146, 44, 56],
  }[classCode] || [220, 10, 50];
  const l = Math.max(20, Math.min(90, base[2] + lDelta));
  return `hsl(${base[0]},${base[1]}%,${l}%)`;
}

function sectorColor(classCode) {
  const base = {
    10: [36, 78, 62],
    20: [214, 72, 64],
    30: [286, 56, 68],
    40: [146, 44, 56],
  }[classCode] || [220, 10, 50];
  const l = Math.max(20, Math.min(90, base[2] - 4));
  return `hsl(${base[0]},${base[1]}%,${l}%)`;
}

function srAnnounce(msg) {
  const el = document.getElementById('sr-status');
  if (el) { el.textContent = ''; requestAnimationFrame(() => { el.textContent = msg; }); }
}

function zoomAnnounce(msg) {
  const el = document.getElementById('zoom-status');
  if (el) { el.textContent = ''; requestAnimationFrame(() => { el.textContent = msg; }); }
}

function fmtSigned(v, decimals = 3) {
  if (v == null) return 'N/A';
  const s = Math.abs(v).toFixed(decimals);
  return (v >= 0 ? '+' : '-') + s;
}

function fmtPct(v, decimals = 1) {
  if (v == null) return 'N/A';
  return v.toFixed(decimals) + '%';
}

// ---------------------------------------------------------------------------
// Main entry
// ---------------------------------------------------------------------------
(async () => {
  // === QD-G v1.1: extend Promise.all to load descriptions.json ===
  // If descriptions.json is absent (e.g. fresh clone before first fetch),
  // degrade gracefully with empty descriptions map.
  let taxonomy, validation, descriptionsData;
  try {
    [taxonomy, validation] = await Promise.all([
      fetch('data/taxonomy.json').then(r => r.json()),
      fetch('data/validation.json').then(r => r.json()),
    ]);
  } catch (err) {
    console.error('[cs] Failed to load data:', err);
    document.getElementById('sunburst-chart').innerHTML =
      '<p style="padding:24px;color:var(--fg-2)">Failed to load data. Run build_viz_data.py and serve locally.</p>';
    return;
  }

  // descriptions.json is optional: load separately so core data failure
  // doesn't prevent descriptions from loading (and vice versa).
  try {
    const descResp = await fetch('data/descriptions.json');
    if (descResp.ok) {
      descriptionsData = await descResp.json();
    } else {
      descriptionsData = { assets: {} };
    }
  } catch (_) {
    descriptionsData = { assets: {} };
  }
  const descriptions = (descriptionsData && descriptionsData.assets) || {};
  // === end QD-G ===

  // Build asset lookup by asset_id
  const assetById = {};
  taxonomy.assets_flat.forEach(a => { assetById[a.asset_id] = a; });

  initHeader(taxonomy.metadata);

  const _inits = [
    ['Search',         () => initSearch(taxonomy.assets_flat)],
    ['Sunburst',       () => initSunburst(taxonomy.hierarchy, taxonomy.assets_flat)],
    ['DetailCard',     () => initDetailCard(descriptions)],   // QD-G: pass descriptions
    ['Legend',         () => initLegend(taxonomy.hierarchy, taxonomy.assets_flat)],  // QD-H
    ['Heatmap',        () => initHeatmap(taxonomy.chain_sector_matrix, taxonomy.assets_flat)],
    ['ValidationCard', () => initValidationCard(validation.headline, taxonomy.metadata)],
    ['KeyboardNav',    () => initKeyboardNav()],
  ];
  for (const [name, fn] of _inits) {
    try { fn(); } catch (err) { console.error(`[init:${name}]`, err); }
  }

  // Bind data to footer meta from taxonomy metadata
  document.querySelectorAll('[data-bind="n_assets"]').forEach(el => {
    el.textContent = taxonomy.metadata.n_assets;
  });
  document.querySelectorAll('[data-bind="n_classes"]').forEach(el => {
    el.textContent = taxonomy.metadata.n_classes;
  });
  document.querySelectorAll('[data-bind="n_sectors"]').forEach(el => {
    el.textContent = taxonomy.metadata.n_sectors;
  });
  document.querySelectorAll('[data-bind="n_sub_sectors"]').forEach(el => {
    el.textContent = taxonomy.metadata.n_active_sub_sectors;
  });

  // Update hero meta counts from taxonomy
  const m = taxonomy.metadata;
  const setId = (id, val) => { const el = document.getElementById(id); if (el) el.textContent = val; };
  setId('meta-assets', m.n_assets);
  setId('meta-classes', m.n_classes);
  setId('meta-sectors', m.n_sectors);
  setId('meta-subsectors', m.n_active_sub_sectors);
})();

// ---------------------------------------------------------------------------
// initHeader
// ---------------------------------------------------------------------------
function initHeader(metadata) {
  // Nothing dynamic needed — title is static HTML
  void metadata;
}

// ---------------------------------------------------------------------------
// initSearch
// ---------------------------------------------------------------------------
function initSearch(assetsFlat) {
  const input = document.getElementById('search-input');
  const resultsEl = document.getElementById('search-results');
  const clearBtn = document.getElementById('search-clear');
  const hintEl = document.querySelector('.search-hint');

  if (!input || !resultsEl) return;

  let debounceTimer = null;
  let activeIndex = -1;
  let currentResults = [];

  function matchAssets(query) {
    if (!query) return [];
    const q = query.toLowerCase();
    const exactSymbol = [];
    const symbolMatch = [];
    const nameMatch = [];
    assetsFlat.forEach(a => {
      const sym = a.symbol.toLowerCase();
      const name = a.name.toLowerCase();
      if (sym === q) exactSymbol.push(a);
      else if (sym.includes(q)) symbolMatch.push(a);
      else if (name.includes(q)) nameMatch.push(a);
    });
    return [...exactSymbol, ...symbolMatch, ...nameMatch];
  }

  function highlight(text, query) {
    if (!query) return text;
    const idx = text.toLowerCase().indexOf(query.toLowerCase());
    if (idx === -1) return text;
    return text.slice(0, idx) +
      '<mark>' + text.slice(idx, idx + query.length) + '</mark>' +
      text.slice(idx + query.length);
  }

  function renderResults(results, query) {
    resultsEl.innerHTML = '';
    activeIndex = -1;

    if (results.length === 0) {
      resultsEl.innerHTML = `<li class="search-result-no-results">No asset matches "${query}". The universe has assets &mdash; see <a href="https://github.com/quantbai/crypto-sectors/blob/main/UNIVERSE.md" target="_blank" rel="noopener" class="accent-link">UNIVERSE.md</a> for the full list.</li>`;
      resultsEl.hidden = false;
      input.setAttribute('aria-expanded', 'true');
      return;
    }

    const shown = results.slice(0, 20);
    const more = results.length - shown.length;

    shown.forEach((a, i) => {
      const li = document.createElement('li');
      li.className = 'search-result-item';
      li.setAttribute('role', 'option');
      li.setAttribute('id', 'sr-item-' + i);
      li.setAttribute('aria-selected', 'false');
      li.dataset.assetId = a.asset_id;

      const colorHex = getClassColorHex(a.class_code);
      li.innerHTML = `
        <span class="search-result-symbol mono">${highlight(a.symbol, query)}</span>
        <span class="search-result-name">${highlight(a.name, query)}</span>
        <span class="search-result-meta">
          <span class="code-chip">${a.sector_code}</span>
          <span class="class-dot" style="background:${colorHex}" title="${a.class_name}"></span>
        </span>
      `;
      li.addEventListener('click', () => selectResult(a));
      resultsEl.appendChild(li);
    });

    if (more > 0) {
      const footer = document.createElement('li');
      footer.className = 'search-result-more';
      footer.textContent = '+' + more + ' more results';
      resultsEl.appendChild(footer);
    }

    resultsEl.hidden = false;
    input.setAttribute('aria-expanded', 'true');
    currentResults = shown;
  }

  function closeResults() {
    resultsEl.hidden = true;
    input.setAttribute('aria-expanded', 'false');
    activeIndex = -1;
    currentResults = [];
  }

  function updateDimming(query) {
    // Live sunburst highlighting during typing (DESIGN-AMENDMENTS §6.1)
    if (!query) {
      setState({ searchMatchIds: null, searchQuery: '' });
      return;
    }
    const results = matchAssets(query);
    const ids = new Set(results.map(a => a.asset_id));
    setState({ searchMatchIds: ids, searchQuery: query });
  }

  function selectResult(asset) {
    input.value = asset.symbol;
    if (hintEl) hintEl.style.display = 'none';
    clearBtn.hidden = false;
    closeResults();
    updateDimming('');
    setState({ selectedAsset: asset, searchMatchIds: null, searchQuery: '' });
    emitter.emit('selectAndZoom', asset);
    srAnnounce('Selected ' + asset.name + ', class ' + asset.class_name + ', sector ' + asset.sector_name);
    // Scroll sunburst into view
    const sb = document.getElementById('sunburst-section');
    if (sb) sb.scrollIntoView({ behavior: 'smooth', block: 'start' });
  }

  input.addEventListener('input', () => {
    const q = input.value.trim();
    clearBtn.hidden = !q;
    if (hintEl) hintEl.style.display = q ? 'none' : '';
    clearTimeout(debounceTimer);
    debounceTimer = setTimeout(() => {
      updateDimming(q);
      if (!q) { closeResults(); return; }
      const results = matchAssets(q);
      renderResults(results, q);
    }, 120);
  });

  clearBtn.addEventListener('click', () => {
    input.value = '';
    clearBtn.hidden = true;
    if (hintEl) hintEl.style.display = '';
    closeResults();
    updateDimming('');
    input.focus();
  });

  input.addEventListener('keydown', e => {
    if (resultsEl.hidden) return;
    const items = resultsEl.querySelectorAll('.search-result-item');
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      activeIndex = Math.min(activeIndex + 1, items.length - 1);
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      activeIndex = Math.max(activeIndex - 1, 0);
    } else if (e.key === 'Enter') {
      e.preventDefault();
      if (activeIndex >= 0 && currentResults[activeIndex]) {
        selectResult(currentResults[activeIndex]);
      } else if (currentResults[0]) {
        selectResult(currentResults[0]);
      }
      return;
    } else if (e.key === 'Escape') {
      closeResults();
      updateDimming('');
      return;
    }
    items.forEach((item, i) => {
      item.setAttribute('aria-selected', i === activeIndex ? 'true' : 'false');
    });
    if (activeIndex >= 0) {
      input.setAttribute('aria-activedescendant', 'sr-item-' + activeIndex);
    }
  });

  // Click outside to close
  document.addEventListener('click', e => {
    if (!document.getElementById('search-container').contains(e.target)) {
      closeResults();
    }
  });

  // Global "/" shortcut
  document.addEventListener('keydown', e => {
    if (e.key === '/' && document.activeElement !== input &&
        document.activeElement.tagName !== 'INPUT' &&
        document.activeElement.tagName !== 'TEXTAREA') {
      e.preventDefault();
      input.focus();
    }
  });
}

// ---------------------------------------------------------------------------
// initSunburst
// ---------------------------------------------------------------------------
function initSunburst(hierarchy, assetsFlat) {
  const container = document.getElementById('sunburst-chart');
  if (!container || typeof d3 === 'undefined') return;

  // Hierarchy leaves are lean (no class/sector context). Look up full asset
  // record from assets_flat when wiring asset wedges to selectedAsset state.
  const assetById = {};
  assetsFlat.forEach(a => { assetById[a.asset_id] = a; });

  const DESKTOP_SIZE = 640;
  const MOBILE_SIZE = Math.min(window.innerWidth - 48, 540);
  let size = window.innerWidth >= 1024 ? DESKTOP_SIZE : MOBILE_SIZE;

  const PAD = 24;
  const INNER_R = 72;
  const RING_WIDTHS = [80, 72, 72]; // class, sector, sub-sector
  // Ring outer radii: ring3=144, ring2=216, ring1=296 (from center)
  // But we need to scale for container size
  const BASE_OUTER = [296, 216, 144]; // [class outer, sector outer, subsector outer]

  let svgEl = document.getElementById('sunburst-svg');
  if (!svgEl) return;

  function getScale() {
    const s = container.getBoundingClientRect().width || size;
    return s / DESKTOP_SIZE;
  }

  // Build D3 hierarchy
  const root = d3.hierarchy(hierarchy)
    .sum(d => d.assets ? d.assets.length : 0)
    .sort((a, b) => b.value - a.value);

  // Assign class codes throughout the tree
  root.each(node => {
    if (node.depth === 1) node.data._classCode = node.data.code;
    else if (node.parent) node.data._classCode = node.parent.data._classCode;
  });

  // Minimum angle floor: 1.5 degrees in radians
  const MIN_ARC = (1.5 * Math.PI) / 180;
  const TWO_PI = 2 * Math.PI;

  // Apply minimum wedge floor on a set of arc nodes at same depth
  function applyMinFloor(nodes) {
    if (!nodes.length) return;
    const total = TWO_PI;
    const floored = nodes.filter(n => (n.x1 - n.x0) < MIN_ARC && (n.x1 - n.x0) > 0);
    const large = nodes.filter(n => (n.x1 - n.x0) >= 4.5 * Math.PI / 180);
    const deficit = floored.reduce((sum, n) => sum + MIN_ARC - (n.x1 - n.x0), 0);
    const available = large.reduce((sum, n) => sum + (n.x1 - n.x0) - MIN_ARC, 0);
    if (available <= 0) return;
    const ratio = Math.min(1, deficit / available);
    floored.forEach(n => { n.x1 = n.x0 + MIN_ARC; });
    large.forEach(n => { n.x1 -= (n.x1 - n.x0 - MIN_ARC) * ratio; });
  }

  const partition = d3.partition().size([TWO_PI, 1]);
  partition(root);

  // Apply floor at depth 3 (sub-sector)
  const depth3 = root.descendants().filter(d => d.depth === 3);
  applyMinFloor(depth3);

  const arc = d3.arc()
    .startAngle(d => d.x0)
    .endAngle(d => d.x1)
    .padAngle(0.5 * Math.PI / 180)
    .padRadius(INNER_R)
    .innerRadius(d => d.innerR)
    .outerRadius(d => d.outerR);

  // Color assignment
  function getFill(node, mode) {
    const depth = node.depth;
    const classCode = node.data._classCode || (node.parent && node.parent.data._classCode);
    if (depth === 1) return getClassColorHex(classCode);
    if (depth === 2) return sectorColor(classCode);
    if (depth === 3) {
      const siblings = node.parent ? node.parent.children || [] : [];
      const pos = siblings.indexOf(node);
      return subSectorColor(classCode, pos, siblings.length);
    }
    if (depth === 4 && mode === 'zoomed') {
      // Assets in zoomed mode — use sub-sector parent color
      const ssParent = node.parent;
      const siblings = ssParent ? ssParent.children || [] : [];
      const pos = siblings.indexOf(node);
      return subSectorColor(ssParent.data._classCode || classCode, pos, siblings.length);
    }
    return 'var(--fg-3)';
  }

  // SVG setup
  const scale = getScale();
  d3.select(svgEl)
    .attr('width', size)
    .attr('height', size)
    .attr('viewBox', `0 0 ${DESKTOP_SIZE} ${DESKTOP_SIZE}`);

  const CENTER_X = DESKTOP_SIZE / 2;
  const CENTER_Y = DESKTOP_SIZE / 2;

  d3.select(svgEl).select('#sunburst-skeleton').remove();

  // Re-select (skeleton was removed, now append fresh)
  d3.select(svgEl).selectAll('g.sb-root').remove();
  const sbRoot = d3.select(svgEl).append('g')
    .attr('class', 'sb-root')
    .attr('transform', `translate(${CENTER_X},${CENTER_Y})`);

  // Tooltip
  let tooltipEl = document.getElementById('sb-tooltip');
  if (!tooltipEl) {
    tooltipEl = document.createElement('div');
    tooltipEl.id = 'sb-tooltip';
    tooltipEl.setAttribute('role', 'tooltip');
    tooltipEl.setAttribute('aria-hidden', 'true');
    document.body.appendChild(tooltipEl);
  }

  let hoverTimer = null;

  function showTooltip(event, node) {
    clearTimeout(hoverTimer);
    hoverTimer = setTimeout(() => {
      const d = node.data;
      const depth = node.depth;
      let codeStr = '';
      let nameStr = '';
      let metaStr = '';

      if (depth === 1) {
        codeStr = d.code;
        nameStr = d.name;
        metaStr = node.value + ' asset' + (node.value !== 1 ? 's' : '');
      } else if (depth === 2) {
        codeStr = d.code;
        nameStr = d.name;
        metaStr = node.value + ' asset' + (node.value !== 1 ? 's' : '') + ' — click to drill in';
      } else if (depth === 3) {
        codeStr = d.code;
        nameStr = d.name;
        const ext = d.is_extension ? ' [EXT]' : '';
        metaStr = node.value + ' asset' + (node.value !== 1 ? 's' : '') + ext + ' — click to drill in';
      } else if (depth === 4) {
        // Asset in zoomed mode
        codeStr = d.symbol;
        nameStr = d.name;
        metaStr = d.chain_ecosystem;
      }

      tooltipEl.innerHTML = `
        <div class="tooltip-code mono">${codeStr}</div>
        <div class="tooltip-name">${nameStr}</div>
        ${metaStr ? `<div class="tooltip-meta">${metaStr}</div>` : ''}
      `;
      tooltipEl.setAttribute('aria-hidden', 'false');
      tooltipEl.classList.add('visible');
      positionTooltip(event);
    }, 80);
  }

  function hideTooltip() {
    clearTimeout(hoverTimer);
    tooltipEl.classList.remove('visible');
    tooltipEl.setAttribute('aria-hidden', 'true');
  }

  function positionTooltip(event) {
    const margin = 12;
    const w = tooltipEl.offsetWidth || 200;
    const h = tooltipEl.offsetHeight || 60;
    let x = event.clientX + margin;
    let y = event.clientY + margin;
    if (x + w > window.innerWidth - margin) x = event.clientX - w - margin;
    if (y + h > window.innerHeight - margin) y = event.clientY - h - margin;
    tooltipEl.style.left = x + 'px';
    tooltipEl.style.top = y + 'px';
  }

  // ---------- Render functions ----------

  function computeNodeRadii(node) {
    const depth = node.depth;
    if (depth === 0) return { innerR: 0, outerR: 0 };
    // Ring 1 (class): inner=216, outer=296
    // Ring 2 (sector): inner=144, outer=216
    // Ring 3 (sub-sector): inner=72, outer=144
    if (depth === 1) return { innerR: 216, outerR: 296 };
    if (depth === 2) return { innerR: 144, outerR: 216 };
    if (depth === 3) return { innerR: 72, outerR: 144 };
    // depth 4 (assets in zoomed mode): fill ring 3 space
    if (depth === 4) return { innerR: 144, outerR: 296 };
    return { innerR: 0, outerR: 0 };
  }

  let currentMode = 'overview';
  let currentZoomedNode = null;
  let selectedWedgeId = null;

  function renderOverview() {
    currentMode = 'overview';
    currentZoomedNode = null;
    setState({ sunburstMode: 'overview', zoomedSubSector: null });
    document.getElementById('asset-weight-note').hidden = true;

    sbRoot.selectAll('*').remove();

    const nodes = root.descendants().filter(d => d.depth >= 1 && d.depth <= 3);

    const paths = sbRoot.selectAll('path.wedge-path')
      .data(nodes, d => d.data.code || d.data.asset_id)
      .join('path')
      .attr('class', 'wedge-path')
      .attr('role', 'button')
      .attr('tabindex', 0)
      .attr('aria-label', d => {
        const classCode = d.data._classCode;
        const label = d.depth === 1 ? 'Class' : d.depth === 2 ? 'Sector' : 'Sub-sector';
        return `${label}: ${d.data.name}, code ${d.data.code}, ${d.value} assets. Press Enter to drill in.`;
      })
      .attr('d', d => {
        const r = computeNodeRadii(d);
        return arc({ x0: d.x0, x1: d.x1, innerR: r.innerR, outerR: r.outerR });
      })
      .attr('fill', d => getFill(d, 'overview'))
      .attr('stroke', 'var(--bg-0)')
      .attr('stroke-width', 1)
      .style('cursor', 'pointer');

    paths
      .on('mousemove', (event, d) => {
        positionTooltip(event);
        showTooltip(event, d);
        // Dim siblings, brighten ancestors
        paths.classed('dimmed', n => {
          if (n === d) return false;
          if (d.ancestors().includes(n)) return false;
          if (n.ancestors().includes(d)) return false;
          return true;
        });
        // Highlight heatmap row
        if (d.depth === 2) {
          emitter.emit('heatmap:highlightRow', d.data.code);
        }
      })
      .on('mouseleave', () => {
        hideTooltip();
        paths.classed('dimmed', false);
        emitter.emit('heatmap:highlightRow', null);
      })
      .on('click', (event, d) => {
        event.stopPropagation();
        if (d.depth === 3) {
          // Drill into sub-sector
          renderZoomed(d);
        } else if (d.depth === 2) {
          // Drill to first sub-sector or just highlight
          if (d.children && d.children.length > 0) {
            renderZoomed(d.children[0]);
          }
        } else if (d.depth === 1) {
          // Select the class — highlight descendants
          // No zoom for class; highlight heatmap rows for this class's sectors
        }
      })
      .on('keydown', (event, d) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          if (d.depth === 3) renderZoomed(d);
        } else if (event.key === 'Escape') {
          // already in overview
        }
      });

    // Breadcrumb label in center
    drawBreadcrumb(['crypto-sectors'], false);

    // Mark data loaded
    container.setAttribute('aria-busy', 'false');

    // Apply search dimming if active
    applySearchDimming(paths);
  }

  function renderZoomed(subSectorNode) {
    currentMode = 'zoomed';
    currentZoomedNode = subSectorNode;
    setState({ sunburstMode: 'zoomed', zoomedSubSector: subSectorNode.data });
    document.getElementById('asset-weight-note').hidden = false;

    sbRoot.selectAll('*').remove();

    const assets = subSectorNode.data.assets || [];
    const n = assets.length;

    // Equal-angle wedges for assets
    const angleStep = n > 0 ? TWO_PI / n : 0;

    const classCode = subSectorNode.data._classCode;

    // Draw a single large donut representing the sub-sector
    // Ring 1 (72-144): sub-sector label background
    const bgArc = d3.arc()
      .innerRadius(INNER_R)
      .outerRadius(296)
      .startAngle(0)
      .endAngle(TWO_PI);

    sbRoot.append('path')
      .attr('d', bgArc())
      .attr('fill', getFill(subSectorNode, 'overview'))
      .attr('opacity', 0.15)
      .attr('stroke', 'none');

    // Individual asset wedges at radius 144-296
    const assetArc = d3.arc()
      .innerRadius(144)
      .outerRadius(296)
      .padAngle(0.5 * Math.PI / 180);

    const assetsFlat_local = assets;
    const assetNodes = assetsFlat_local.map((a, i) => ({
      data: a,
      x0: i * angleStep,
      x1: (i + 1) * angleStep,
    }));

    sbRoot.selectAll('path.wedge-path.asset')
      .data(assetNodes)
      .join('path')
      .attr('class', 'wedge-path asset')
      .attr('role', 'button')
      .attr('tabindex', 0)
      .attr('aria-label', d => `${d.data.name} (${d.data.symbol}), ${d.data.chain_ecosystem}. Press Enter to select.`)
      .attr('d', d => assetArc({ startAngle: d.x0, endAngle: d.x1 }))
      .attr('fill', (d, i) => subSectorColor(classCode, i, n))
      .attr('stroke', 'var(--bg-0)')
      .attr('stroke-width', 1)
      .attr('id', d => 'asset-wedge-' + d.data.asset_id)
      .on('mousemove', (event, d) => {
        positionTooltip(event);
        const fakeNode = { data: d.data, depth: 4 };
        showTooltip(event, fakeNode);
      })
      .on('mouseleave', hideTooltip)
      .on('click', (event, d) => {
        event.stopPropagation();
        // Resolve full asset record (hierarchy leaf lacks class/sector context)
        const asset = assetById[d.data.asset_id] || d.data;
        setState({ selectedAsset: asset });
        srAnnounce('Selected ' + asset.name + ', ' + asset.symbol);
        // Highlight this wedge
        sbRoot.selectAll('.wedge-path.asset').attr('stroke', 'var(--bg-0)').attr('stroke-width', 1);
        d3.select(event.currentTarget).attr('stroke', 'var(--accent)').attr('stroke-width', 2);
        selectedWedgeId = asset.asset_id;
      })
      .on('keydown', (event, d) => {
        if (event.key === 'Enter' || event.key === ' ') {
          event.preventDefault();
          const asset = assetById[d.data.asset_id] || d.data;
          setState({ selectedAsset: asset });
        }
      });

    // Breadcrumb
    const path = [];
    let node = subSectorNode;
    while (node) {
      if (node.data.name) path.unshift(node.data.name);
      node = node.parent;
    }
    drawBreadcrumb(path.filter(n => n !== 'crypto-sectors'), true);

    zoomAnnounce(`Zoomed into ${subSectorNode.data.name}, ${n} assets`);
  }

  function drawBreadcrumb(parts, showBack) {
    const labelGroup = sbRoot.append('g').attr('class', 'sb-breadcrumb-group');

    const label = parts.slice(-2).join(' / ');
    const truncated = label.length > 24 ? label.slice(0, 22) + '...' : label;

    labelGroup.append('text')
      .attr('class', 'sb-breadcrumb')
      .attr('dy', showBack ? '-8' : '5')
      .attr('fill', 'var(--fg-1)')
      .attr('font-size', 11)
      .attr('font-family', 'var(--font-mono)')
      .attr('text-anchor', 'middle')
      .text(truncated);

    if (showBack) {
      const backG = labelGroup.append('g')
        .attr('class', 'sb-back-btn')
        .attr('cursor', 'pointer')
        .attr('tabindex', 0)
        .attr('role', 'button')
        .attr('aria-label', 'Back to overview')
        .on('click', () => renderOverview())
        .on('keydown', e => { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); renderOverview(); } });

      backG.append('rect').attr('x', -30).attr('y', 10).attr('width', 60).attr('height', 22).attr('rx', 4);
      backG.append('text')
        .attr('dy', 25)
        .attr('fill', 'var(--fg-2)')
        .attr('font-size', 10)
        .attr('font-family', 'var(--font-mono)')
        .attr('text-anchor', 'middle')
        .text('← back');
    }

    // Click on donut hole to go back
    if (showBack) {
      sbRoot.append('circle')
        .attr('r', INNER_R - 4)
        .attr('fill', 'transparent')
        .attr('cursor', 'pointer')
        .attr('aria-label', 'Back to overview')
        .on('click', () => renderOverview());
    }
  }

  function applySearchDimming(paths) {
    if (!state.searchMatchIds) {
      paths.classed('dimmed', false);
      return;
    }
    // Dim wedges that don't contain any matching asset
    paths.classed('dimmed', d => {
      const leaves = d.leaves ? d.leaves() : [];
      const leafIds = leaves.map(l => l.data.asset_id).filter(Boolean);
      if (d.data.asset_id) return !state.searchMatchIds.has(d.data.asset_id);
      return !leafIds.some(id => state.searchMatchIds.has(id));
    });
  }

  // Listen for search state changes
  emitter.on('state:searchMatchIds', () => {
    if (currentMode === 'overview') {
      const paths = sbRoot.selectAll('path.wedge-path');
      applySearchDimming(paths);
    }
  });

  // Listen for zoom from search
  emitter.on('selectAndZoom', asset => {
    // Find the sub-sector node in the hierarchy
    const ssNode = root.descendants().find(d => d.depth === 3 && d.data.code == asset.sub_sector_code);
    if (ssNode) {
      renderZoomed(ssNode);
      // After rendering, select the asset wedge
      setTimeout(() => {
        sbRoot.selectAll('.wedge-path.asset')
          .filter(d => d.data.asset_id === asset.asset_id)
          .dispatch('click');
      }, 700);
    }
  });

  // Keyboard: Escape to zoom out
  document.addEventListener('keydown', e => {
    if (e.key === 'Escape' && currentMode === 'zoomed') {
      renderOverview();
    }
  });

  // Listen for heatmap cell filter
  emitter.on('heatmap:filterCell', cellKey => {
    setState({ filterCellKey: cellKey });
    if (!cellKey) {
      sbRoot.selectAll('path.wedge-path').classed('dimmed', false);
      return;
    }
    // Parse cellKey: "{sector_code}:{chain}"
    const [sectorCode, chain] = cellKey.split(':');
    if (currentMode !== 'overview') return;
    const paths = sbRoot.selectAll('path.wedge-path');
    paths.classed('dimmed', d => {
      // Find if any leaf of this node is in the cell
      const leaves = d.leaves ? d.leaves() : [];
      const match = leaves.some(l => {
        return l.parent && l.parent.parent &&
          String(l.parent.parent.data.code) === sectorCode &&
          l.data.chain_ecosystem === chain;
      });
      return !match;
    });
  });

  // Initial render
  renderOverview();
}

// ---------------------------------------------------------------------------
// initDetailCard
// ---------------------------------------------------------------------------
// === QD-G v1.1: accepts descriptions map {asset_id: {short_desc, cg_id, ok}} ===
function initDetailCard(descriptions) {
  const emptyState = document.getElementById('detail-empty-state');
  const content = document.getElementById('detail-content');

  if (!emptyState || !content) return;

  // Normalize to empty object if not provided (graceful degrade)
  const descMap = descriptions || {};

  function updateCard(asset) {
    if (!asset) {
      content.hidden = true;
      emptyState.hidden = false;
      return;
    }

    // Fade out -> update -> fade in
    content.classList.add('fading');
    setTimeout(() => {
      // Class color stripe
      const stripe = document.getElementById('detail-class-stripe');
      if (stripe) stripe.style.background = getClassColorHex(asset.class_code);

      document.getElementById('detail-symbol').textContent = asset.symbol;
      document.getElementById('detail-name').textContent = asset.name;

      // Fields
      function setField(id, text, isChip) {
        const el = document.getElementById(id);
        if (!el) return;
        if (isChip) {
          el.innerHTML = `<span class="code-chip">${text}</span>`;
        } else {
          el.textContent = text;
        }
      }

      setField('dv-class', `${asset.class_code} — ${asset.class_name}`);
      setField('dv-sector', `<span class="code-chip">${asset.sector_code}</span> ${asset.sector_name}`, false);
      document.getElementById('dv-sector').innerHTML =
        `<span class="code-chip">${asset.sector_code}</span> ${asset.sector_name}`;
      document.getElementById('dv-subsector').innerHTML =
        `<span class="code-chip">${asset.sub_sector_code}</span> ${asset.sub_sector_name}`;
      setField('dv-chain', asset.chain_ecosystem);
      setField('dv-assetid', asset.asset_id);
      setField('dv-effective', asset.effective_from);

      const decisionRow = document.getElementById('dv-decision-row');
      const decisionLink = document.getElementById('dv-decision-link');
      if (asset.decision_doc && decisionRow && decisionLink) {
        decisionRow.hidden = false;
        decisionLink.href = asset.decision_doc;
        decisionLink.setAttribute('tabindex', '0');
      } else if (decisionRow) {
        decisionRow.hidden = true;
        if (decisionLink) decisionLink.setAttribute('tabindex', '-1');
      }

      // === QD-G v1.1: About row — short description from descriptions.json ===
      const aboutRow = document.getElementById('dv-about-row');
      const aboutEl = document.getElementById('dv-about');
      const descEntry = descMap[asset.asset_id];
      const shortDesc = descEntry && descEntry.ok && descEntry.short_desc;
      if (aboutRow && aboutEl) {
        if (shortDesc) {
          aboutEl.textContent = shortDesc;
          aboutRow.hidden = false;
        } else {
          aboutRow.hidden = true;
        }
      }

      // === QD-G v1.1: Full page link row ===
      const fullpageRow = document.getElementById('dv-fullpage-row');
      const fullpageLink = document.getElementById('dv-fullpage-link');
      if (fullpageRow && fullpageLink) {
        fullpageLink.href = `coins/${asset.asset_id}/`;
        fullpageLink.setAttribute('tabindex', '0');
        fullpageRow.hidden = false;
      }
      // === end QD-G ===

      emptyState.hidden = true;
      content.hidden = false;
      content.classList.remove('fading');

      // Mobile bottom-sheet: open when an asset is selected
      const card = document.getElementById('detail-card');
      const closeBtn = document.getElementById('detail-card-close');
      if (card) card.classList.add('sheet-open');
      if (closeBtn) closeBtn.hidden = false;
    }, 180);
  }

  function closeSheet() {
    const card = document.getElementById('detail-card');
    const closeBtn = document.getElementById('detail-card-close');
    if (card) card.classList.remove('sheet-open');
    if (closeBtn) closeBtn.hidden = true;
    updateCard(null);
    setState({ selectedAsset: null });
  }

  // Wire close button
  const closeBtn = document.getElementById('detail-card-close');
  if (closeBtn) closeBtn.addEventListener('click', closeSheet);

  emitter.on('state:selectedAsset', asset => updateCard(asset));
}

// ---------------------------------------------------------------------------
// initHeatmap
// ---------------------------------------------------------------------------
function initHeatmap(chainSectorMatrix, assetsFlat) {
  const container = document.getElementById('heatmap-chart');
  if (!container || typeof d3 === 'undefined') return;

  // Clear any prior render (makes function idempotent across hot-reloads / retries)
  d3.select(container).selectAll('svg').remove();

  const chains = chainSectorMatrix.chains;
  const sectors = chainSectorMatrix.sectors;

  // Build cell lookup: {sector_code}:{chain} -> {count, asset_ids}
  const cellMap = {};
  chainSectorMatrix.cells.forEach(cell => {
    cellMap[`${cell.sector_code}:${cell.chain}`] = cell;
  });

  // Build asset symbol lookup
  const assetSymbols = {};
  assetsFlat.forEach(a => { assetSymbols[a.asset_id] = a.symbol; });

  const ROW_HEIGHT = 36;
  const COL_WIDTH = 60;
  const ROW_LABEL_W = 220;
  const HEADER_H = 40;
  const TOTAL_COL_W = 44;
  const TOTAL_ROW_H = 32;
  const PAD = 0;

  const totalW = ROW_LABEL_W + chains.length * COL_WIDTH + TOTAL_COL_W;
  const totalH = HEADER_H + sectors.length * ROW_HEIGHT + TOTAL_ROW_H;

  // Compute sector totals
  const sectorTotals = {};
  sectors.forEach(s => {
    sectorTotals[s.code] = chains.reduce((sum, ch) => {
      const cell = cellMap[`${s.code}:${ch}`];
      return sum + (cell ? cell.count : 0);
    }, 0);
  });

  // Compute chain totals
  const chainTotals = {};
  chains.forEach(ch => {
    chainTotals[ch] = sectors.reduce((sum, s) => {
      const cell = cellMap[`${s.code}:${ch}`];
      return sum + (cell ? cell.count : 0);
    }, 0);
  });

  // Intensity scale — neutral luminance ramp (DESIGN-AMENDMENTS §3.1)
  // Returns CSS intensity value 0%-72%
  function intensityPct(count) {
    if (count === 0) return 0;
    if (count === 1) return 12;
    if (count === 2) return 24;
    if (count <= 5) return 36;
    if (count <= 10) return 52;
    return 72;
  }

  // Class code lookup for row label color
  // We need sector->class mapping. Build from chainSectorMatrix sectors codes.
  const sectorClassCode = {};
  sectors.forEach(s => {
    sectorClassCode[s.code] = Math.floor(s.code / 1000) * 10;
  });

  const svg = d3.select(container).append('svg')
    .attr('width', totalW)
    .attr('height', totalH)
    .attr('viewBox', `0 0 ${totalW} ${totalH}`)
    .attr('role', 'grid')
    .attr('aria-label', 'Chain by sector asset distribution matrix');

  // --- Column headers ---
  chains.forEach((ch, ci) => {
    svg.append('text')
      .attr('x', ROW_LABEL_W + ci * COL_WIDTH + COL_WIDTH / 2)
      .attr('y', HEADER_H - 10)
      .attr('text-anchor', 'middle')
      .attr('fill', 'var(--fg-1)')
      .attr('font-family', 'var(--font-mono)')
      .attr('font-size', 11)
      .attr('font-weight', 500)
      .text(ch);
  });

  // "Chain" header label
  svg.append('text')
    .attr('x', ROW_LABEL_W + chains.length * COL_WIDTH / 2)
    .attr('y', 14)
    .attr('text-anchor', 'middle')
    .attr('fill', 'var(--fg-2)')
    .attr('font-size', 10)
    .attr('font-family', 'var(--font-mono)')
    .attr('letter-spacing', '0.04em')
    .text('CHAIN ECOSYSTEM');

  svg.append('text')
    .attr('x', ROW_LABEL_W + chains.length * COL_WIDTH + TOTAL_COL_W / 2)
    .attr('y', HEADER_H - 10)
    .attr('text-anchor', 'middle')
    .attr('fill', 'var(--fg-2)')
    .attr('font-size', 11)
    .attr('font-family', 'var(--font-mono)')
    .text('Σ');

  // Tooltip
  let hmTooltipEl = document.getElementById('hm-tooltip');
  if (!hmTooltipEl) {
    hmTooltipEl = document.createElement('div');
    hmTooltipEl.id = 'hm-tooltip';
    hmTooltipEl.setAttribute('role', 'tooltip');
    hmTooltipEl.setAttribute('aria-hidden', 'true');
    document.body.appendChild(hmTooltipEl);
  }

  function showHmTooltip(event, cell, sectorName, chain) {
    const count = cell ? cell.count : 0;
    const ids = cell ? cell.asset_ids : [];
    const syms = ids.map(id => assetSymbols[id] || id);
    const shown = syms.slice(0, 5);
    const more = syms.length - shown.length;
    hmTooltipEl.innerHTML = `
      <div class="hm-tooltip-title">${sectorName} &times; ${chain}</div>
      <div>${count} asset${count !== 1 ? 's' : ''}</div>
      ${shown.length ? `<div class="hm-tooltip-assets">${shown.join(', ')}${more > 0 ? ' +' + more + ' more' : ''}</div>` : ''}
    `;
    hmTooltipEl.setAttribute('aria-hidden', 'false');
    hmTooltipEl.classList.add('visible');
    const margin = 12;
    const w = hmTooltipEl.offsetWidth || 200;
    const h = hmTooltipEl.offsetHeight || 60;
    let x = event.clientX + margin;
    let y = event.clientY + margin;
    if (x + w > window.innerWidth - margin) x = event.clientX - w - margin;
    if (y + h > window.innerHeight - margin) y = event.clientY - h - margin;
    hmTooltipEl.style.left = x + 'px';
    hmTooltipEl.style.top = y + 'px';
  }

  function hideHmTooltip() {
    hmTooltipEl.classList.remove('visible');
    hmTooltipEl.setAttribute('aria-hidden', 'true');
  }

  let activeCellKey = null;

  // --- Rows ---
  sectors.forEach((sector, si) => {
    const rowY = HEADER_H + si * ROW_HEIGHT;
    const classCode = sectorClassCode[sector.code] || 20;
    const classColorHex = getClassColorHex(classCode);

    // Row label
    const labelG = svg.append('g').attr('transform', `translate(0,${rowY})`);
    labelG.append('rect')
      .attr('width', ROW_LABEL_W - 8)
      .attr('height', ROW_HEIGHT)
      .attr('fill', 'transparent');

    labelG.append('text')
      .attr('x', 8)
      .attr('y', ROW_HEIGHT / 2 + 1)
      .attr('dominant-baseline', 'middle')
      .attr('fill', classColorHex)
      .attr('font-family', 'var(--font-mono)')
      .attr('font-size', 10)
      .attr('font-weight', 500)
      .text(sector.code);

    labelG.append('text')
      .attr('x', 52)
      .attr('y', ROW_HEIGHT / 2 + 1)
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'var(--fg-1)')
      .attr('font-size', 12)
      .text(sector.name.length > 22 ? sector.name.slice(0, 20) + '…' : sector.name);

    // Grid line
    svg.append('line')
      .attr('x1', 0).attr('y1', rowY + ROW_HEIGHT)
      .attr('x2', totalW).attr('y2', rowY + ROW_HEIGHT)
      .attr('stroke', 'var(--chart-grid)').attr('stroke-width', 1);

    // Cells
    chains.forEach((chain, ci) => {
      const cellKey = `${sector.code}:${chain}`;
      const cell = cellMap[cellKey];
      const count = cell ? cell.count : 0;
      const cellX = ROW_LABEL_W + ci * COL_WIDTH;
      const pct = intensityPct(count);

      const cellG = svg.append('g').attr('class', 'hm-cell-group');

      const rect = cellG.append('rect')
        .attr('class', 'hm-cell')
        .attr('x', cellX + 2)
        .attr('y', rowY + 2)
        .attr('width', COL_WIDTH - 4)
        .attr('height', ROW_HEIGHT - 4)
        .attr('rx', 3)
        .attr('role', 'gridcell')
        .attr('tabindex', count > 0 ? 0 : -1)
        .attr('aria-label', () => {
          if (count === 0) return `${sector.name}, ${chain}: no assets`;
          const ids = cell.asset_ids;
          const syms = ids.map(id => assetSymbols[id] || id).join(', ');
          return `${sector.name}, ${chain}: ${count} asset${count !== 1 ? 's' : ''} — ${syms}`;
        })
        .attr('fill', count === 0
          ? 'var(--bg-2)'
          : `color-mix(in oklch, var(--bg-1) ${100 - pct}%, var(--fg-1) ${pct}%)`)
        .attr('stroke', 'none')
        .attr('stroke-width', 0);

      if (count > 0) {
        // Count label
        cellG.append('text')
          .attr('x', cellX + COL_WIDTH / 2)
          .attr('y', rowY + ROW_HEIGHT / 2 + 1)
          .attr('text-anchor', 'middle')
          .attr('dominant-baseline', 'middle')
          .attr('fill', count >= 3 ? 'var(--fg-0)' : 'var(--fg-2)')
          .attr('font-family', 'var(--font-mono)')
          .attr('font-size', 11)
          .attr('font-weight', 500)
          .attr('pointer-events', 'none')
          .text(count);

        cellG
          .on('mousemove', (event) => {
            rect.attr('stroke', 'var(--accent)').attr('stroke-width', 2);
            showHmTooltip(event, cell, sector.name, chain);
          })
          .on('mouseleave', () => {
            if (activeCellKey !== cellKey) {
              rect.attr('stroke', 'none').attr('stroke-width', 0);
            }
            hideHmTooltip();
          })
          .on('click', () => {
            if (activeCellKey === cellKey) {
              // Deselect
              activeCellKey = null;
              rect.attr('stroke', 'none').attr('stroke-width', 0);
              emitter.emit('heatmap:filterCell', null);
              setState({ filterCellKey: null });
            } else {
              // Deselect previous
              if (activeCellKey) {
                svg.selectAll('.hm-cell').attr('stroke', 'none').attr('stroke-width', 0);
              }
              activeCellKey = cellKey;
              rect.attr('stroke', 'var(--accent)').attr('stroke-width', 2);
              emitter.emit('heatmap:filterCell', cellKey);
              setState({ filterCellKey: cellKey });
            }
          })
          .on('keydown', (event) => {
            if (event.key === 'Enter' || event.key === ' ') {
              event.preventDefault();
              cellG.dispatch('click');
            }
          });
      }
    });

    // Row total
    const rowTotal = sectorTotals[sector.code] || 0;
    svg.append('text')
      .attr('x', ROW_LABEL_W + chains.length * COL_WIDTH + TOTAL_COL_W / 2)
      .attr('y', rowY + ROW_HEIGHT / 2 + 1)
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', 'var(--fg-1)')
      .attr('font-family', 'var(--font-mono)')
      .attr('font-size', 11)
      .text(rowTotal);
  });

  // Column totals row
  const totRowY = HEADER_H + sectors.length * ROW_HEIGHT;
  svg.append('line')
    .attr('x1', ROW_LABEL_W).attr('y1', totRowY)
    .attr('x2', totalW).attr('y2', totRowY)
    .attr('stroke', 'var(--border-strong)').attr('stroke-width', 1);

  chains.forEach((ch, ci) => {
    const x = ROW_LABEL_W + ci * COL_WIDTH + COL_WIDTH / 2;
    svg.append('text')
      .attr('x', x).attr('y', totRowY + 20)
      .attr('text-anchor', 'middle')
      .attr('fill', 'var(--fg-1)')
      .attr('font-family', 'var(--font-mono)')
      .attr('font-size', 11)
      .text(chainTotals[ch] || 0);
  });

  // Grand total
  const grandTotal = assetsFlat.length;
  svg.append('text')
    .attr('x', ROW_LABEL_W + chains.length * COL_WIDTH + TOTAL_COL_W / 2)
    .attr('y', totRowY + 20)
    .attr('text-anchor', 'middle')
    .attr('fill', 'var(--fg-0)')
    .attr('font-family', 'var(--font-mono)')
    .attr('font-size', 11)
    .attr('font-weight', 600)
    .text(grandTotal);

  // Vertical gridlines
  chains.forEach((ch, ci) => {
    svg.append('line')
      .attr('x1', ROW_LABEL_W + ci * COL_WIDTH)
      .attr('y1', HEADER_H)
      .attr('x2', ROW_LABEL_W + ci * COL_WIDTH)
      .attr('y2', totRowY + TOTAL_ROW_H)
      .attr('stroke', 'var(--chart-grid)')
      .attr('stroke-width', 1);
  });

  // Row highlight on sunburst hover
  emitter.on('heatmap:highlightRow', sectorCode => {
    svg.selectAll('.hm-row-highlight').remove();
    if (!sectorCode) return;
    const si = sectors.findIndex(s => s.code == sectorCode);
    if (si < 0) return;
    const rowY = HEADER_H + si * ROW_HEIGHT;
    svg.append('rect')
      .attr('class', 'hm-row-highlight')
      .attr('x', ROW_LABEL_W)
      .attr('y', rowY)
      .attr('width', chains.length * COL_WIDTH)
      .attr('height', ROW_HEIGHT)
      .attr('fill', 'none')
      .attr('stroke', 'var(--accent)')
      .attr('stroke-width', 1)
      .attr('pointer-events', 'none');
  });

  container.setAttribute('aria-busy', 'false');
}

// ---------------------------------------------------------------------------
// initValidationCard
// ---------------------------------------------------------------------------
function initValidationCard(headline, metadata) {
  function bindAll(key, value) {
    document.querySelectorAll(`[data-bind="${key}"]`).forEach(el => {
      el.textContent = value;
    });
  }

  const sp = headline.sector_spread;
  const ciLo = headline.sector_spread_ci_lo;
  const ciHi = headline.sector_spread_ci_hi;
  const rollPos = headline.rolling_n_positive;
  const rollTot = headline.rolling_n_total;
  const spreadOurs = headline.spread_ours;
  const spreadChain = headline.spread_chain;

  bindAll('sector_spread_fmt', fmtSigned(sp));
  bindAll('spread_ci_lo', fmtSigned(ciLo));
  bindAll('spread_ci_hi', fmtSigned(ciHi));
  bindAll('rolling_windows_fmt', `${rollPos}/${rollTot}`);
  // E5: show sector vs chain as delta
  const delta = (spreadOurs != null && spreadChain != null) ? spreadOurs - spreadChain : null;
  bindAll('e5_comparison_fmt', fmtSigned(delta));
  bindAll('spread_ours_fmt', fmtSigned(spreadOurs));
  bindAll('spread_chain_fmt', fmtSigned(spreadChain));

  // Metadata counts
  if (metadata) {
    bindAll('n_assets', metadata.n_assets);
    bindAll('n_classes', metadata.n_classes);
    bindAll('n_sectors', metadata.n_sectors);
    bindAll('n_sub_sectors', metadata.n_sub_sectors);
  }
}

// ---------------------------------------------------------------------------
// initKeyboardNav
// ---------------------------------------------------------------------------
function initKeyboardNav() {
  // Escape: handled per-component above (search + sunburst)
  // "/" shortcut: handled in initSearch
  // Tab order: natural document order (no override needed)
}

// ---------------------------------------------------------------------------
// initLegend
// Hierarchical legend: class -> sector -> sub-sector -> assets (symbol tokens).
// Layout decision: Option D — stacked in right column above the detail card.
// Chart stays full 640px. Legend and detail card share the right 1fr column.
//
// Bidirectional sync strategy:
//   legend -> chart:  emitter.emit('selectAndZoom', asset) for asset clicks.
//                     emitter.emit('heatmap:highlightRow', code) for sector hover.
//   chart -> legend:  listen on state:selectedAsset, state:zoomedSubSector.
//
// No new external deps. No rewrite of initSunburst internals.
// ---------------------------------------------------------------------------
function initLegend(hierarchy, assetsFlat) {
  const root = document.getElementById('legend-root');
  if (!root) return;

  // Full asset lookup by asset_id for click resolution
  const assetById = {};
  assetsFlat.forEach(a => { assetById[a.asset_id] = a; });

  // Class color map — CSS custom property references (no new hex values)
  const CLASS_COLORS_LEGEND = {
    10: 'var(--class-10)',
    20: 'var(--class-20)',
    30: 'var(--class-30)',
    40: 'var(--class-40)',
  };

  // DOM element registries for bidirectional sync
  const assetSymEls   = new Map(); // asset_id -> <button>
  const classHeaderEls = new Map(); // classCode -> .legend-class-header
  const sectorHeaderEls = new Map(); // sectorCode -> .legend-sector-header
  const classRowEls    = new Map(); // classCode  -> .legend-class
  const sectorRowEls   = new Map(); // sectorCode -> .legend-sector

  // Build legend DOM from taxonomy.hierarchy
  const classes = hierarchy.children || [];

  classes.forEach(cls => {
    const classCode = cls.code;
    const colorVar  = CLASS_COLORS_LEGEND[classCode] || 'var(--fg-3)';
    const totalAssets = (cls.children || []).reduce((sum, sec) => {
      return sum + (sec.children || []).reduce((s2, ss) => s2 + (ss.assets || []).length, 0);
    }, 0);

    // Class row container
    const classDiv = document.createElement('div');
    classDiv.className = 'legend-class';
    classDiv.setAttribute('role', 'treeitem');
    classDiv.setAttribute('aria-expanded', 'true');

    // Class header
    const classHeader = document.createElement('div');
    classHeader.className = 'legend-class-header';
    classHeader.setAttribute('tabindex', '0');
    classHeader.dataset.classCode = classCode;
    classHeader.innerHTML =
      '<span class="legend-class-dot" style="background:' + colorVar + '" aria-hidden="true"></span>' +
      '<span class="legend-class-name">' + cls.name + '</span>' +
      '<span class="legend-class-count mono">' + totalAssets + '</span>' +
      '<svg class="legend-class-chevron" viewBox="0 0 12 12" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M2 4l4 4 4-4"/></svg>';

    classHeaderEls.set(classCode, classHeader);
    classRowEls.set(classCode, classDiv);

    const classBody = document.createElement('div');
    classBody.className = 'legend-class-body';
    classBody.setAttribute('role', 'group');

    function toggleClass() {
      const collapsed = classDiv.classList.toggle('collapsed');
      classDiv.setAttribute('aria-expanded', String(!collapsed));
    }

    classHeader.addEventListener('click', toggleClass);
    classHeader.addEventListener('keydown', e => {
      if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleClass(); }
      if (e.key === 'ArrowDown') { e.preventDefault(); moveFocusDown(classHeader); }
      if (e.key === 'ArrowUp')   { e.preventDefault(); moveFocusUp(classHeader); }
    });

    // Class hover: highlight first sector row in heatmap
    classHeader.addEventListener('mouseenter', () => {
      if (cls.children && cls.children[0]) {
        emitter.emit('heatmap:highlightRow', cls.children[0].code);
      }
    });
    classHeader.addEventListener('mouseleave', () => emitter.emit('heatmap:highlightRow', null));

    classDiv.appendChild(classHeader);
    classDiv.appendChild(classBody);

    // Sector rows
    (cls.children || []).forEach(sec => {
      const sectorCode = sec.code;
      const sectorAssetCount = (sec.children || [])
        .reduce((s, ss) => s + (ss.assets || []).length, 0);

      const sectorDiv = document.createElement('div');
      sectorDiv.className = 'legend-sector collapsed'; // default collapsed
      sectorDiv.setAttribute('role', 'treeitem');
      sectorDiv.setAttribute('aria-expanded', 'false');

      const sectorHeader = document.createElement('div');
      sectorHeader.className = 'legend-sector-header';
      sectorHeader.setAttribute('tabindex', '0');
      sectorHeader.dataset.sectorCode = sectorCode;
      sectorHeader.innerHTML =
        '<span class="legend-sector-code">' + sectorCode + '</span>' +
        '<span class="legend-sector-name">' + sec.name + '</span>' +
        '<span class="legend-sector-count mono">' + sectorAssetCount + '</span>' +
        '<svg class="legend-sector-chevron" viewBox="0 0 10 10" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="M1.5 3.5l3.5 3.5 3.5-3.5"/></svg>';

      sectorHeaderEls.set(sectorCode, sectorHeader);
      sectorRowEls.set(sectorCode, sectorDiv);

      const sectorBody = document.createElement('div');
      sectorBody.className = 'legend-sector-body';
      sectorBody.setAttribute('role', 'group');

      function toggleSector() {
        const collapsed = sectorDiv.classList.toggle('collapsed');
        sectorDiv.setAttribute('aria-expanded', String(!collapsed));
      }

      sectorHeader.addEventListener('click', toggleSector);
      sectorHeader.addEventListener('keydown', e => {
        if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); toggleSector(); }
        if (e.key === 'ArrowDown') { e.preventDefault(); moveFocusDown(sectorHeader); }
        if (e.key === 'ArrowUp')   { e.preventDefault(); moveFocusUp(sectorHeader); }
        if (e.key === 'Escape')    { e.preventDefault(); classHeader.focus(); }
      });

      // Sector hover: sync heatmap row highlight
      sectorHeader.addEventListener('mouseenter', () => emitter.emit('heatmap:highlightRow', sectorCode));
      sectorHeader.addEventListener('mouseleave', () => emitter.emit('heatmap:highlightRow', null));

      // Sub-sector rows (skip empty sub-sectors)
      (sec.children || []).forEach(ss => {
        if (!ss.assets || ss.assets.length === 0) return;

        const ssDiv = document.createElement('div');
        ssDiv.className = 'legend-subsector';
        ssDiv.setAttribute('role', 'group');

        const ssNameEl = document.createElement('div');
        ssNameEl.className = 'legend-subsector-name';
        ssNameEl.innerHTML = '<span class="legend-sector-code">' + ss.code + '</span>' + ss.name;
        ssDiv.appendChild(ssNameEl);

        const assetWrap = document.createElement('div');
        assetWrap.className = 'legend-assets';

        ss.assets.forEach(asset => {
          const sym = document.createElement('button');
          sym.className = 'legend-asset-sym';
          sym.setAttribute('tabindex', '0');
          sym.setAttribute('type', 'button');
          sym.setAttribute('role', 'treeitem');
          sym.setAttribute('aria-label', asset.symbol + ' -- ' + asset.name + '. Click to inspect.');
          sym.dataset.assetId = asset.asset_id;
          sym.textContent = asset.symbol;

          sym.addEventListener('click', e => {
            e.stopPropagation();
            const fullAsset = assetById[asset.asset_id];
            if (!fullAsset) return;
            setState({ selectedAsset: fullAsset });
            emitter.emit('selectAndZoom', fullAsset);
            srAnnounce('Selected ' + fullAsset.name + ', class ' + fullAsset.class_name);
            const sb = document.getElementById('sunburst-section');
            if (sb) sb.scrollIntoView({ behavior: 'smooth', block: 'start' });
          });

          sym.addEventListener('keydown', e => {
            if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); sym.click(); }
            if (e.key === 'ArrowDown') { e.preventDefault(); moveFocusDown(sym); }
            if (e.key === 'ArrowUp')   { e.preventDefault(); moveFocusUp(sym); }
            if (e.key === 'Escape')    { e.preventDefault(); sectorHeader.focus(); }
          });

          assetSymEls.set(asset.asset_id, sym);
          assetWrap.appendChild(sym);
        });

        ssDiv.appendChild(assetWrap);
        sectorBody.appendChild(ssDiv);
      });

      sectorDiv.appendChild(sectorHeader);
      sectorDiv.appendChild(sectorBody);
      classBody.appendChild(sectorDiv);
    });

    root.appendChild(classDiv);
  });

  // ---------------------------------------------------------------------------
  // Keyboard: focus traversal helpers (arrow keys through visible items)
  // ---------------------------------------------------------------------------
  function allFocusable() {
    return Array.from(root.querySelectorAll(
      '.legend-class-header, .legend-sector-header, .legend-asset-sym'
    )).filter(el => {
      // Exclude items hidden inside collapsed ancestors
      let p = el.parentElement;
      while (p && p !== root) {
        if (p.classList.contains('legend-class-body') &&
            p.previousElementSibling &&
            p.parentElement.classList.contains('collapsed')) return false;
        if (p.classList.contains('legend-sector-body') &&
            p.parentElement.classList.contains('collapsed')) return false;
        p = p.parentElement;
      }
      return true;
    });
  }

  function moveFocusDown(current) {
    const items = allFocusable();
    const idx = items.indexOf(current);
    if (idx >= 0 && idx < items.length - 1) items[idx + 1].focus();
  }

  function moveFocusUp(current) {
    const items = allFocusable();
    const idx = items.indexOf(current);
    if (idx > 0) items[idx - 1].focus();
  }

  // (v1.1.1: legacy mobile toggle removed — <details> in index.html handles
  // collapse natively across all viewports. The disclosure is closed by
  // default so it never breaks the hero layout.)

  // When user picks an asset (from anywhere) and the legend is closed,
  // open it so they can see the highlighted row.
  const explorer = document.getElementById('legend-explorer');
  emitter.on('state:selectedAsset', asset => {
    if (asset && explorer && !explorer.open) {
      // Don't auto-open on the first selection from a sunburst click —
      // only open if the user opened it before. Comment out to NEVER auto-open.
      // explorer.open = true;
    }
  });

  // ---------------------------------------------------------------------------
  // Legend filter input: substring match on symbol + name
  // ---------------------------------------------------------------------------
  const filterInput = document.getElementById('legend-filter');
  if (filterInput) {
    filterInput.addEventListener('input', () => {
      applyFilter(filterInput.value.trim().toLowerCase());
    });
    filterInput.addEventListener('keydown', e => {
      if (e.key === 'Escape') { filterInput.value = ''; applyFilter(''); }
    });
  }

  function applyFilter(q) {
    if (!q) {
      assetSymEls.forEach(el => el.classList.remove('legend-dim', 'legend-active'));
      classRowEls.forEach(el => el.classList.remove('legend-dim'));
      sectorRowEls.forEach(el => el.classList.remove('legend-dim'));
      return;
    }
    assetSymEls.forEach((el, assetId) => {
      const a = assetById[assetId];
      const match = a && (a.symbol.toLowerCase().includes(q) || a.name.toLowerCase().includes(q));
      el.classList.toggle('legend-dim', !match);
      el.classList.toggle('legend-active', !!match);
    });
    classRowEls.forEach(el => {
      const anyMatch = Array.from(el.querySelectorAll('.legend-asset-sym'))
        .some(s => !s.classList.contains('legend-dim'));
      el.classList.toggle('legend-dim', !anyMatch);
    });
    sectorRowEls.forEach(el => {
      const anyMatch = Array.from(el.querySelectorAll('.legend-asset-sym'))
        .some(s => !s.classList.contains('legend-dim'));
      el.classList.toggle('legend-dim', !anyMatch);
    });
  }

  // ---------------------------------------------------------------------------
  // Chart -> legend sync via emitter state events
  // ---------------------------------------------------------------------------

  // Asset selected (from chart wedge click, search, or our own legend click)
  emitter.on('state:selectedAsset', asset => {
    // Clear previous active
    assetSymEls.forEach(el => el.classList.remove('legend-active'));
    classHeaderEls.forEach(el => el.classList.remove('legend-active'));
    sectorHeaderEls.forEach(el => el.classList.remove('legend-active'));

    if (!asset) return;

    const symEl = assetSymEls.get(asset.asset_id);
    if (!symEl) return;

    symEl.classList.add('legend-active');

    // Expand the sector containing this asset so the symbol is visible
    const sectorCode = asset.sector_code;
    const secEl = sectorRowEls.get(sectorCode);
    if (secEl && secEl.classList.contains('collapsed')) {
      secEl.classList.remove('collapsed');
      secEl.setAttribute('aria-expanded', 'true');
    }

    // Scroll symbol into view in the legend (delayed to let sunburst animation start)
    setTimeout(() => {
      symEl.scrollIntoView({ block: 'nearest', behavior: 'instant' });
    }, 350);
  });

  // Sunburst zoomed into a sub-sector: highlight the parent sector header
  emitter.on('state:zoomedSubSector', subSector => {
    sectorHeaderEls.forEach(el => el.classList.remove('legend-active'));
    if (!subSector || !subSector.code) return;
    // Sub-sector codes: 301010 -> sector 3010 = floor(301010 / 10)
    const derivedSectorCode = Math.floor(subSector.code / 10);
    const el = sectorHeaderEls.get(derivedSectorCode);
    if (el) {
      el.classList.add('legend-active');
      // Expand if collapsed
      const secRow = sectorRowEls.get(derivedSectorCode);
      if (secRow && secRow.classList.contains('collapsed')) {
        secRow.classList.remove('collapsed');
        secRow.setAttribute('aria-expanded', 'true');
      }
    }
  });
}
