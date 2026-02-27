import { timeAgo } from '../utils/format';

const styles = {
  bar: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'space-between',
    padding: '12px 24px',
    backgroundColor: '#111827',
    borderBottom: '1px solid #374151',
    flexWrap: 'wrap',
    gap: '12px',
  },
  title: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
  },
  h1: {
    fontSize: '18px',
    fontWeight: '700',
    color: '#f9fafb',
    margin: 0,
  },
  subtitle: {
    fontSize: '11px',
    color: '#9ca3af',
    margin: 0,
  },
  section: {
    display: 'flex',
    alignItems: 'center',
    gap: '20px',
  },
  chip: {
    display: 'inline-flex',
    alignItems: 'center',
    gap: '6px',
    padding: '4px 10px',
    borderRadius: '6px',
    fontSize: '12px',
    fontWeight: '600',
  },
  dot: {
    width: '8px',
    height: '8px',
    borderRadius: '50%',
    display: 'inline-block',
  },
  meta: {
    fontSize: '11px',
    color: '#6b7280',
  },
  breadth: {
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
    fontSize: '12px',
  },
};

function getStatusColor(status) {
  switch (status) {
    case 'Open': return '#22c55e';
    case 'Pre-Open': return '#eab308';
    case 'Closed': return '#ef4444';
    default: return '#9ca3af';
  }
}

export default function TopBar({ marketStatus, breadth, lastPriceUpdate, lastNewsUpdate }) {
  const status = marketStatus?.status || 'Unknown';
  const statusColor = getStatusColor(status);

  return (
    <div style={styles.bar}>
      <div style={styles.title}>
        <div>
          <h1 style={styles.h1}>India Swing Tracker</h1>
          <p style={styles.subtitle}>Top 100 | NIFTY 50 + NEXT 50 | Strong Buy / Strong Sell</p>
        </div>
      </div>

      <div style={styles.section}>
        {/* Market Status */}
        <div style={{ ...styles.chip, backgroundColor: statusColor + '20', color: statusColor, border: `1px solid ${statusColor}40` }}>
          <span style={{ ...styles.dot, backgroundColor: statusColor }} />
          {status}
        </div>

        {/* Breadth */}
        {breadth && (
          <div style={styles.breadth}>
            <span style={{ color: '#22c55e' }}>{breadth.advancers} adv</span>
            <span style={{ color: '#6b7280' }}>|</span>
            <span style={{ color: '#ef4444' }}>{breadth.decliners} dec</span>
            <span style={{ color: '#6b7280' }}>|</span>
            <span style={{ color: '#9ca3af' }}>{breadth.unchanged} unch</span>
          </div>
        )}

        {/* Freshness */}
        <div>
          <div style={styles.meta}>
            Prices: {lastPriceUpdate ? timeAgo(lastPriceUpdate) : 'loading...'}
          </div>
          <div style={styles.meta}>
            News: {lastNewsUpdate ? timeAgo(lastNewsUpdate) : 'loading...'}
          </div>
        </div>
      </div>
    </div>
  );
}
