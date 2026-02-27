import { formatPrice, formatPct, formatVolume, formatNumber, getSignalColor, getSignalBg, getPctColor } from '../utils/format';

const styles = {
  wrapper: {
    overflowX: 'auto',
    flex: 1,
  },
  table: {
    width: '100%',
    borderCollapse: 'collapse',
    fontSize: '12px',
  },
  th: {
    position: 'sticky',
    top: 0,
    backgroundColor: '#111827',
    color: '#9ca3af',
    fontWeight: '600',
    padding: '8px 10px',
    textAlign: 'left',
    borderBottom: '2px solid #374151',
    whiteSpace: 'nowrap',
    fontSize: '11px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
    cursor: 'pointer',
    userSelect: 'none',
  },
  thRight: {
    textAlign: 'right',
  },
  td: {
    padding: '7px 10px',
    borderBottom: '1px solid #1f2937',
    whiteSpace: 'nowrap',
  },
  tdRight: {
    textAlign: 'right',
  },
  row: {
    cursor: 'pointer',
    transition: 'background-color 0.1s',
  },
  symbol: {
    fontWeight: '700',
    color: '#f9fafb',
    fontSize: '13px',
  },
  name: {
    color: '#9ca3af',
    fontSize: '11px',
    display: 'block',
    maxWidth: '140px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
  },
  sector: {
    color: '#6b7280',
    fontSize: '11px',
  },
  signalBadge: {
    display: 'inline-block',
    padding: '2px 8px',
    borderRadius: '4px',
    fontWeight: '700',
    fontSize: '11px',
    textAlign: 'center',
    minWidth: '80px',
  },
  score: {
    fontWeight: '600',
    fontSize: '13px',
  },
  trendStack: {
    display: 'flex',
    gap: '3px',
    alignItems: 'center',
  },
  trendDot: {
    width: '6px',
    height: '6px',
    borderRadius: '50%',
  },
  riskChip: {
    display: 'inline-block',
    padding: '1px 6px',
    borderRadius: '3px',
    fontSize: '10px',
    fontWeight: '500',
    marginRight: '3px',
    backgroundColor: '#7f1d1d',
    color: '#fca5a5',
  },
  newsChip: {
    fontSize: '10px',
    color: '#93c5fd',
    maxWidth: '150px',
    overflow: 'hidden',
    textOverflow: 'ellipsis',
    whiteSpace: 'nowrap',
    display: 'block',
  },
  empty: {
    textAlign: 'center',
    padding: '40px',
    color: '#6b7280',
    fontSize: '14px',
  },
};

function TrendStack({ ema20, ema50, ema200, price }) {
  const short = ema20 > ema50;
  const long = ema50 > ema200;
  const aboveEma = price > ema20;

  return (
    <div style={styles.trendStack} title={`EMA20/50: ${short ? 'Bull' : 'Bear'}, EMA50/200: ${long ? 'Bull' : 'Bear'}`}>
      <span style={{ ...styles.trendDot, backgroundColor: aboveEma ? '#22c55e' : '#ef4444' }} title={`Price ${aboveEma ? 'above' : 'below'} EMA20`} />
      <span style={{ ...styles.trendDot, backgroundColor: short ? '#22c55e' : '#ef4444' }} title={`EMA20 ${short ? '>' : '<'} EMA50`} />
      <span style={{ ...styles.trendDot, backgroundColor: long ? '#22c55e' : '#ef4444' }} title={`EMA50 ${long ? '>' : '<'} EMA200`} />
    </div>
  );
}

function getRiskFlags(sym) {
  const flags = [];
  if (sym.vol_ratio > 2) flags.push('High Vol');
  if (Math.abs(sym.gap_pct || 0) > 2) flags.push('Gap');
  if (sym.atr_pct > 4) flags.push('Volatile');
  if (sym.events?.some(e => e.event_type === 'earnings')) flags.push('Earnings');
  return flags;
}

export default function StockTable({ symbols, news, onSelectSymbol, selectedSymbol }) {
  if (!symbols || symbols.length === 0) {
    return <div style={styles.empty}>Loading universe data... This may take a minute on first load.</div>;
  }

  // Build a quick lookup for latest news per symbol
  const newsMap = {};
  if (news) {
    for (const item of news) {
      if (item.symbol && !newsMap[item.symbol]) {
        newsMap[item.symbol] = item;
      }
    }
  }

  return (
    <div style={styles.wrapper}>
      <table style={styles.table}>
        <thead>
          <tr>
            <th style={styles.th}>#</th>
            <th style={styles.th}>Symbol</th>
            <th style={styles.th}>Sector</th>
            <th style={{ ...styles.th, ...styles.thRight }}>Price</th>
            <th style={{ ...styles.th, ...styles.thRight }}>1D %</th>
            <th style={{ ...styles.th, ...styles.thRight }}>5D %</th>
            <th style={{ ...styles.th, ...styles.thRight }}>20D %</th>
            <th style={{ ...styles.th, ...styles.thRight }}>Vol Ratio</th>
            <th style={{ ...styles.th, ...styles.thRight }}>ATR %</th>
            <th style={{ ...styles.th, ...styles.thRight }}>Gap %</th>
            <th style={styles.th}>Trend</th>
            <th style={{ ...styles.th, ...styles.thRight }}>RSI</th>
            <th style={{ ...styles.th, ...styles.thRight }}>MACD H</th>
            <th style={styles.th}>Signal</th>
            <th style={{ ...styles.th, ...styles.thRight }}>Score</th>
            <th style={styles.th}>Risks</th>
            <th style={styles.th}>News</th>
          </tr>
        </thead>
        <tbody>
          {symbols.map((sym, i) => {
            const signal = sym.signal || {};
            const riskFlags = getRiskFlags(sym);
            const latestNews = newsMap[sym.symbol];
            const isSelected = selectedSymbol === sym.symbol;

            return (
              <tr
                key={sym.symbol}
                style={{
                  ...styles.row,
                  backgroundColor: isSelected ? '#1e3a5f' : (i % 2 === 0 ? '#0d1117' : '#111827'),
                }}
                onClick={() => onSelectSymbol(sym.symbol)}
                onMouseEnter={(e) => { if (!isSelected) e.currentTarget.style.backgroundColor = '#1a1f2e'; }}
                onMouseLeave={(e) => { if (!isSelected) e.currentTarget.style.backgroundColor = i % 2 === 0 ? '#0d1117' : '#111827'; }}
              >
                <td style={{ ...styles.td, color: '#6b7280' }}>{i + 1}</td>
                <td style={styles.td}>
                  <span style={styles.symbol}>{sym.symbol}</span>
                  <span style={styles.name}>{sym.name}</span>
                </td>
                <td style={styles.td}>
                  <span style={styles.sector}>{sym.sector}</span>
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: '#f9fafb', fontWeight: '600' }}>
                  {formatPrice(sym.price)}
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: getPctColor(sym.pct_1d), fontWeight: '600' }}>
                  {formatPct(sym.pct_1d)}
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: getPctColor(sym.pct_5d) }}>
                  {formatPct(sym.pct_5d)}
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: getPctColor(sym.pct_20d) }}>
                  {formatPct(sym.pct_20d)}
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: sym.vol_ratio > 1.5 ? '#22c55e' : '#9ca3af' }}>
                  {formatNumber(sym.vol_ratio, 1)}x
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: '#d1d5db' }}>
                  {formatNumber(sym.atr_pct, 1)}%
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: getPctColor(sym.gap_pct) }}>
                  {formatPct(sym.gap_pct)}
                </td>
                <td style={styles.td}>
                  <TrendStack ema20={sym.ema20} ema50={sym.ema50} ema200={sym.ema200} price={sym.price} />
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: sym.rsi14 > 70 ? '#ef4444' : sym.rsi14 < 30 ? '#22c55e' : '#d1d5db' }}>
                  {formatNumber(sym.rsi14, 1)}
                </td>
                <td style={{ ...styles.td, ...styles.tdRight, color: sym.macd_hist > 0 ? '#22c55e' : '#ef4444' }}>
                  {formatNumber(sym.macd_hist, 2)}
                </td>
                <td style={styles.td}>
                  <span style={{
                    ...styles.signalBadge,
                    backgroundColor: getSignalBg(signal.label),
                    color: getSignalColor(signal.label),
                    border: `1px solid ${getSignalColor(signal.label)}40`,
                  }}>
                    {signal.label || 'N/A'}
                  </span>
                </td>
                <td style={{ ...styles.td, ...styles.tdRight }}>
                  <span style={{ ...styles.score, color: getSignalColor(signal.label) }}>
                    {signal.score ?? '—'}
                  </span>
                </td>
                <td style={styles.td}>
                  {riskFlags.map(flag => (
                    <span key={flag} style={styles.riskChip}>{flag}</span>
                  ))}
                </td>
                <td style={styles.td}>
                  {latestNews && (
                    <span style={styles.newsChip} title={latestNews.title}>
                      {latestNews.title}
                    </span>
                  )}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
