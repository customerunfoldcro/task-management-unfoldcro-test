const API_BASE = '/api';

export async function fetchUniverse() {
  const res = await fetch(`${API_BASE}/universe/top100`);
  if (!res.ok) throw new Error('Failed to fetch universe');
  return res.json();
}

export async function fetchSignals({ label, symbol, sort, limit } = {}) {
  const params = new URLSearchParams();
  if (label) params.set('label', label);
  if (symbol) params.set('symbol', symbol);
  if (sort) params.set('sort', sort);
  if (limit) params.set('limit', limit);
  const res = await fetch(`${API_BASE}/signals?${params}`);
  if (!res.ok) throw new Error('Failed to fetch signals');
  return res.json();
}

export async function fetchSignalDetail(symbol) {
  const res = await fetch(`${API_BASE}/signals/${symbol}`);
  if (!res.ok) throw new Error('Failed to fetch signal detail');
  return res.json();
}

export async function fetchNews({ symbol, range, urgency, limit } = {}) {
  const params = new URLSearchParams();
  if (symbol) params.set('symbol', symbol);
  if (range) params.set('range', range);
  if (urgency) params.set('urgency', urgency);
  if (limit) params.set('limit', limit);
  const res = await fetch(`${API_BASE}/news?${params}`);
  if (!res.ok) throw new Error('Failed to fetch news');
  return res.json();
}

export async function fetchMarketStatus() {
  const res = await fetch(`${API_BASE}/market-status`);
  if (!res.ok) throw new Error('Failed to fetch market status');
  return res.json();
}

export async function triggerRefresh(type) {
  const res = await fetch(`${API_BASE}/refresh/${type}`, { method: 'POST' });
  return res.json();
}

export function createSSEConnection(onMessage) {
  const eventSource = new EventSource(`${API_BASE}/alerts/stream`);

  eventSource.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      onMessage(data);
    } catch (e) {
      // ignore parse errors
    }
  };

  eventSource.onerror = () => {
    // Will auto-reconnect
  };

  return eventSource;
}
