// MARK: Theme
(function () {
  const saved = localStorage.getItem('motiq-theme') ?? 'light';
  document.documentElement.dataset.theme = saved;
})();

document.addEventListener('DOMContentLoaded', () => {

  // MARK: Theme toggle
  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.dataset.theme === 'dark';
    const next = isDark ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('motiq-theme', next);
  });

  // MARK: Sidebar collapse
  const sidebar = document.getElementById('sidebar');
  const mainWrapper = document.getElementById('main-wrapper');
  const sidebarToggle = document.getElementById('sidebar-toggle');

  function updateMainMargin() {
    const collapsed = sidebar.classList.contains('collapsed');
    const width = getComputedStyle(document.documentElement)
      .getPropertyValue(collapsed ? '--sidebar-width-collapsed' : '--sidebar-width').trim();
    mainWrapper.style.marginLeft = width;
  }

  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
    updateMainMargin();
  });

  // MARK: API helpers
  async function apiFetch(path) {
    let baseUrl = CONFIG.baseUrl;
    if (baseUrl.endsWith('/')) {
      baseUrl = baseUrl.slice(0, -1);
    }
    const res = await fetch(`${baseUrl}${path}`, {
      headers: { 'X-API-Key': CONFIG.apiKey }
    });
    if (!res.ok) throw new Error(`API error: ${res.status}`);
    return res.json();
  }

  function setValue(id, value) {
    const el = document.getElementById(id);
    if (el) el.textContent = value;
  }

  function formatNumber(n) {
    if (n == null) return '—';
    return Number(n).toLocaleString('en-US');
  }

  function formatDuration(seconds) {
    if (seconds == null) return '—';
    const m = Math.round(seconds / 60);
    return `${m} min`;
  }

  // MARK: Color palette
  // Charts pick colors from the front of this array in order.
  // A chart needing 1 color gets palette[0], 2 colors get [0,1] etc.
  const PALETTE = [
    '#4a90d9',
    '#f5c842',
    '#5cbd8a',
    '#e8734a',
    '#a06cd5',
    '#e05c7a',
    '#4bbfc9',
  ];

  function paletteColors(n) {
    return Array.from({ length: n }, (_, i) => PALETTE[i % PALETTE.length]);
  }

  Chart.defaults.font.family = "'Inter', system-ui, -apple-system, sans-serif";

  function getTextColor() {
    return getComputedStyle(document.documentElement)
      .getPropertyValue('--text-secondary').trim();
  }

  function getGridColor() {
    return getComputedStyle(document.documentElement)
      .getPropertyValue('--border').trim();
  }

  function sortDescending(labels, values, absolutes = []) {
    const paired = labels.map((label, i) => ({ label, value: values[i], absolute: absolutes[i] ?? null }));
    paired.sort((a, b) => b.value - a.value);
    return {
      labels:    paired.map(p => p.label),
      values:    paired.map(p => p.value),
      absolutes: paired.map(p => p.absolute),
    };
  }

  // MARK: Generic donut chart
  // labels, pcts, abs are parallel arrays; colors picked from palette in order.
  function renderDonut(canvasId, legendId, labels, pcts, abs = []) {
    const colors = paletteColors(labels.length);
    const ctx = document.getElementById(canvasId).getContext('2d');

    const legend = document.getElementById(legendId);
    if (legend) {
      legend.innerHTML = labels.map((label, i) => {
        const absStr = abs[i] != null ? ` (${abs[i]})` : '';
        return `
          <div class="donut-legend-item">
            <span class="donut-legend-dot" style="background:${colors[i]}"></span>
            ${label}: ${pcts[i]}%${absStr}
          </div>`;
      }).join('');
    }

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels,
        datasets: [{
          data: pcts,
          backgroundColor: colors,
          borderWidth: 0,
          hoverOffset: 4,
        }]
      },
      options: {
        cutout: '68%',
        plugins: {
          legend: { display: false },
          tooltip: { enabled: false }
        }
      }
    });
  }

  // MARK: Generic bar chart
  function renderBarChart(canvasId, labels, values, absolutes = []) {
    const barHeight = 28;
    const padding = 40;
    const totalHeight = labels.length * barHeight + padding;
    const canvas = document.getElementById(canvasId);
    const wrap = canvas?.closest('.chart-wrap');
    if (wrap) wrap.style.height = `${totalHeight}px`;

    const ctx = canvas.getContext('2d');
    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: PALETTE[0],
          borderRadius: 4,
          borderSkipped: false,
        }]
      },
      options: {
        indexAxis: 'y',
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            callbacks: {
              label: (ctx) => {
                const abs = absolutes[ctx.dataIndex];
                return abs != null ? ` ${ctx.raw}% (${abs})` : ` ${ctx.raw}%`;
              }
            }
          }
        },
        scales: {
          x: {
            grid: { color: getGridColor() },
            ticks: {
              color: getTextColor(),
              font: { family: "'Inter', system-ui, -apple-system, sans-serif", size: 11 },
              callback: (v) => `${v}%`
            },
            max: 100,
          },
          y: {
            grid: { display: false },
            ticks: {
              color: getTextColor(),
              font: { family: "'Inter', system-ui, -apple-system, sans-serif", size: 12 },
            }
          }
        }
      }
    });
  }

  // MARK: Load data
  async function loadOverview() {
    try {
      const [users, sessions, nvr7, nvr30, devices, environment] = await Promise.all([
        apiFetch('/analytics/users/active'),
        apiFetch('/analytics/sessions/summary'),
        apiFetch('/analytics/users/new-vs-returning?days=7'),
        apiFetch('/analytics/users/new-vs-returning?days=30'),
        apiFetch('/analytics/devices/breakdown'),
        apiFetch('/analytics/environment/breakdown'),
      ]);

      // MARK: Usage
      setValue('stat-dau',      formatNumber(users.dau));
      setValue('stat-mau',      formatNumber(users.mau));
      setValue('stat-sessions', formatNumber(sessions.sessions_today));
      setValue('stat-spd-7d',   sessions.avg_sessions_last_7d?.toFixed(1) ?? '—');
      setValue('stat-spd-30d',  sessions.avg_sessions_last_30d?.toFixed(1) ?? '—');
      setValue('stat-duration', formatDuration(sessions.avg_duration_per_session_30d));

      // New vs. Returning (7d)
      renderDonut(
        'chart-nvr-7d', 'legend-nvr-7d',
        ['Returning', 'New'],
        [nvr7.percentage.returning_users, nvr7.percentage.new_users],
        [nvr7.absolute.returning_users,   nvr7.absolute.new_users]
      );
      // New vs. Returning (30d)
      renderDonut(
        'chart-nvr-30d', 'legend-nvr-30d',
        ['Returning', 'New'],
        [nvr30.percentage.returning_users, nvr30.percentage.new_users],
        [nvr30.absolute.returning_users,   nvr30.absolute.new_users]
      );

      // MARK: Devices
      const devSorted = sortDescending(
        Object.keys(devices.percentage),
        Object.values(devices.percentage),
        Object.values(devices.absolute)
      );
      renderBarChart('chart-devices', devSorted.labels, devSorted.values, devSorted.absolutes);

      // MARK: Environment
      // OS Version
      const osKeys = Object.keys(environment.os_version.percentage);
      renderDonut(
        'chart-os', 'legend-os',
        osKeys,
        osKeys.map(k => environment.os_version.percentage[k]),
        osKeys.map(k => environment.os_version.absolute[k])
      );

      // Color Scheme
      const csKeys = Object.keys(environment.color_scheme.percentage);
      renderDonut(
        'chart-color-scheme', 'legend-color-scheme',
        csKeys.map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        csKeys.map(k => environment.color_scheme.percentage[k]),
        csKeys.map(k => environment.color_scheme.absolute[k])
      );

      // Orientation
      const orKeys = Object.keys(environment.orientation.percentage);
      renderDonut(
        'chart-orientation', 'legend-orientation',
        orKeys.map(k => k.charAt(0).toUpperCase() + k.slice(1)),
        orKeys.map(k => environment.orientation.percentage[k]),
        orKeys.map(k => environment.orientation.absolute[k])
      );

      // Connectivity
      const conKeys = Object.keys(environment.connectivity.percentage);
      renderDonut(
        'chart-connectivity', 'legend-connectivity',
        conKeys.map(k => k === 'wifi' ? 'WiFi' : k.charAt(0).toUpperCase() + k.slice(1)),
        conKeys.map(k => environment.connectivity.percentage[k]),
        conKeys.map(k => environment.connectivity.absolute[k])
      );

      // Accessibility Features
      const accSorted = sortDescending(
        Object.keys(environment.accessibility_features.percentage).map(k =>
          k.replace(/_/g, ' ').replace(/\b\w/g, c => c.toUpperCase())
        ),
        Object.values(environment.accessibility_features.percentage),
        Object.values(environment.accessibility_features.absolute)
      );
      renderBarChart('chart-accessibility', accSorted.labels, accSorted.values, accSorted.absolutes);

    } catch (err) {
      console.error('Failed to load overview data:', err);
    }
  }

  loadOverview();
});