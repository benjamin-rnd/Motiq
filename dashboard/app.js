/* ─── Theme ──────────────────────────────────────────────── */
(function () {
  const saved = localStorage.getItem('motiq-theme') ?? 'light';
  document.documentElement.dataset.theme = saved;
})();

document.addEventListener('DOMContentLoaded', () => {

  // ── Theme toggle ────────────────────────────────────────
  const themeToggle = document.getElementById('theme-toggle');
  themeToggle.addEventListener('click', () => {
    const isDark = document.documentElement.dataset.theme === 'dark';
    const next = isDark ? 'light' : 'dark';
    document.documentElement.dataset.theme = next;
    localStorage.setItem('motiq-theme', next);
  });

  // ── Sidebar collapse ────────────────────────────────────
  const sidebar = document.getElementById('sidebar');
  const sidebarToggle = document.getElementById('sidebar-toggle');
  sidebarToggle.addEventListener('click', () => {
    sidebar.classList.toggle('collapsed');
  });

  // ── API helpers ─────────────────────────────────────────
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

  // ── Chart defaults ───────────────────────────────────────
  const COLORS = {
    new:       '#f5c842',
    returning: '#4a90d9',
  };

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

  // ── Donut chart ──────────────────────────────────────────
  function renderDonut(canvasId, legendId, newPct, returningPct, newAbs, returningAbs) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    // HTML legend
    const legend = document.getElementById(legendId);
    if (legend) {
      const returningAbsStr = returningAbs != null ? ` (${returningAbs})` : '';
      const newAbsStr       = newAbs != null       ? ` (${newAbs})`       : '';
      legend.innerHTML = `
        <div class="donut-legend-item">
          <span class="donut-legend-dot" style="background:${COLORS.returning}"></span>
          Returning: ${returningPct}%${returningAbsStr}
        </div>
        <div class="donut-legend-item">
          <span class="donut-legend-dot" style="background:${COLORS.new}"></span>
          New: ${newPct}%${newAbsStr}
        </div>
      `;
    }

    return new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Returning', 'New'],
        datasets: [{
          data: [returningPct, newPct],
          backgroundColor: [COLORS.returning, COLORS.new],
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

  // ── Bar chart (devices) ──────────────────────────────────
  function renderDeviceChart(labels, values, absolutes = []) {
    const barHeight = 28;
    const padding = 40;
    const totalHeight = labels.length * barHeight + padding;
    const wrap = document.querySelector('.chart-wrap');
    if (wrap) wrap.style.height = `${totalHeight}px`;

    const ctx = document.getElementById('chart-devices').getContext('2d');
    return new Chart(ctx, {
      type: 'bar',
      data: {
        labels,
        datasets: [{
          data: values,
          backgroundColor: COLORS.returning,
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

  // ── Load data ────────────────────────────────────────────
  async function loadOverview() {
    try {
      const [users, sessions, nvr7, nvr30, devices] = await Promise.all([
        apiFetch('/analytics/users/active'),
        apiFetch('/analytics/sessions/summary'),
        apiFetch('/analytics/users/new-vs-returning?days=7'),
        apiFetch('/analytics/users/new-vs-returning?days=30'),
        apiFetch('/analytics/devices/breakdown'),
      ]);

      // /analytics/users/active → { dau, mau }
      setValue('stat-dau', formatNumber(users.dau));
      setValue('stat-mau', formatNumber(users.mau));

      // /analytics/sessions/summary → { sessions_today, avg_sessions_last_7d, avg_sessions_last_30d, avg_duration_per_session }
      setValue('stat-sessions', formatNumber(sessions.sessions_today));
      setValue('stat-spd-7d',   sessions.avg_sessions_last_7d?.toFixed(1) ?? '—');
      setValue('stat-spd-30d',  sessions.avg_sessions_last_30d?.toFixed(1) ?? '—');
      setValue('stat-duration', formatDuration(sessions.avg_duration_per_session));

      // /analytics/users/new-vs-returning?days=N → { absolute: {...}, percentage: { new_users, returning_users } }
      renderDonut('chart-nvr-7d',  'legend-nvr-7d',  nvr7.percentage.new_users,  nvr7.percentage.returning_users,  nvr7.absolute.new_users,  nvr7.absolute.returning_users);
      renderDonut('chart-nvr-30d', 'legend-nvr-30d', nvr30.percentage.new_users, nvr30.percentage.returning_users, nvr30.absolute.new_users, nvr30.absolute.returning_users);

      // /analytics/devices/breakdown → { absolute: {...}, percentage: { "iPhone X": 20.0, ... } }
      const sorted = sortDescending(
        Object.keys(devices.percentage),
        Object.values(devices.percentage),
        Object.values(devices.absolute)
      );
      renderDeviceChart(sorted.labels, sorted.values, sorted.absolutes);

    } catch (err) {
      console.error('Failed to load overview data:', err);
    }
  }

  loadOverview();
});
