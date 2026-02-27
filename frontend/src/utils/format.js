export function formatPrice(price) {
  if (!price && price !== 0) return '—';
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(price);
}

export function formatPct(pct) {
  if (!pct && pct !== 0) return '—';
  const sign = pct >= 0 ? '+' : '';
  return `${sign}${pct.toFixed(2)}%`;
}

export function formatVolume(vol) {
  if (!vol) return '—';
  if (vol >= 10000000) return `${(vol / 10000000).toFixed(1)}Cr`;
  if (vol >= 100000) return `${(vol / 100000).toFixed(1)}L`;
  if (vol >= 1000) return `${(vol / 1000).toFixed(1)}K`;
  return vol.toString();
}

export function formatNumber(num, decimals = 2) {
  if (!num && num !== 0) return '—';
  return Number(num).toFixed(decimals);
}

export function timeAgo(dateStr) {
  if (!dateStr) return '';
  const date = new Date(dateStr);
  const now = new Date();
  const diffMs = now - date;
  const diffMins = Math.floor(diffMs / 60000);
  const diffHours = Math.floor(diffMins / 60);
  const diffDays = Math.floor(diffHours / 24);

  if (diffMins < 1) return 'just now';
  if (diffMins < 60) return `${diffMins}m ago`;
  if (diffHours < 24) return `${diffHours}h ago`;
  return `${diffDays}d ago`;
}

export function getSignalColor(label) {
  switch (label) {
    case 'Strong Buy': return '#16a34a';
    case 'Buy': return '#22c55e';
    case 'Neutral': return '#9ca3af';
    case 'Sell': return '#f97316';
    case 'Strong Sell': return '#dc2626';
    default: return '#9ca3af';
  }
}

export function getSignalBg(label) {
  switch (label) {
    case 'Strong Buy': return '#052e16';
    case 'Buy': return '#14532d';
    case 'Neutral': return '#1f2937';
    case 'Sell': return '#431407';
    case 'Strong Sell': return '#450a0a';
    default: return '#1f2937';
  }
}

export function getPctColor(pct) {
  if (!pct) return '#9ca3af';
  if (pct > 0) return '#22c55e';
  if (pct < 0) return '#ef4444';
  return '#9ca3af';
}

export function getSentimentColor(sentiment) {
  if (!sentiment && sentiment !== 0) return '#9ca3af';
  if (sentiment > 0.2) return '#22c55e';
  if (sentiment < -0.2) return '#ef4444';
  return '#eab308';
}

export function getUrgencyColor(urgency) {
  switch (urgency) {
    case 'high': return '#ef4444';
    case 'medium': return '#eab308';
    case 'low': return '#9ca3af';
    default: return '#9ca3af';
  }
}
