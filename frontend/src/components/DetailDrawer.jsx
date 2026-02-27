import { useState } from 'react';
import { formatPrice, formatPct, formatNumber, getSignalColor, getSignalBg, getPctColor, getSentimentColor, getUrgencyColor, timeAgo } from '../utils/format';

const styles = {
  drawer: {
    width: '420px',
    minWidth: '420px',
    backgroundColor: '#111827',
    borderLeft: '1px solid #374151',
    overflowY: 'auto',
    display: 'flex',
    flexDirection: 'column',
  },
  header: {
    padding: '16px 20px',
    borderBottom: '1px solid #1f2937',
  },
  symbolRow: {
    display: 'flex',
    justifyContent: 'space-between',
    alignItems: 'center',
  },
  symbolName: {
    fontSize: '18px',
    fontWeight: '700',
    color: '#f9fafb',
  },
  closeBtn: {
    background: 'none',
    border: 'none',
    color: '#9ca3af',
    fontSize: '20px',
    cursor: 'pointer',
    padding: '4px',
  },
  meta: {
    fontSize: '12px',
    color: '#9ca3af',
    marginTop: '4px',
  },
  priceSection: {
    display: 'flex',
    alignItems: 'baseline',
    gap: '12px',
    marginTop: '8px',
  },
  price: {
    fontSize: '24px',
    fontWeight: '700',
    color: '#f9fafb',
  },
  tabs: {
    display: 'flex',
    borderBottom: '1px solid #1f2937',
  },
  tab: {
    flex: 1,
    padding: '10px',
    textAlign: 'center',
    fontSize: '12px',
    fontWeight: '600',
    cursor: 'pointer',
    color: '#9ca3af',
    backgroundColor: 'transparent',
    border: 'none',
    borderBottom: '2px solid transparent',
    transition: 'all 0.15s',
  },
  tabActive: {
    color: '#3b82f6',
    borderBottom: '2px solid #3b82f6',
  },
  content: {
    padding: '16px 20px',
    flex: 1,
    overflowY: 'auto',
  },
  section: {
    marginBottom: '20px',
  },
  sectionTitle: {
    fontSize: '13px',
    fontWeight: '700',
    color: '#d1d5db',
    marginBottom: '10px',
    textTransform: 'uppercase',
    letterSpacing: '0.5px',
  },
  signalBox: {
    padding: '14px',
    borderRadius: '8px',
    textAlign: 'center',
  },
  signalLabel: {
    fontSize: '20px',
    fontWeight: '800',
    marginBottom: '4px',
  },
  scoreText: {
    fontSize: '14px',
    color: '#d1d5db',
  },
  reasonList: {
    listStyle: 'none',
    padding: 0,
    margin: 0,
  },
  reasonItem: {
    padding: '6px 0',
    fontSize: '12px',
    color: '#d1d5db',
    borderBottom: '1px solid #1f2937',
    display: 'flex',
    alignItems: 'flex-start',
    gap: '6px',
  },
  bullet: {
    display: 'inline-block',
    minWidth: '6px',
    height: '6px',
    borderRadius: '50%',
    marginTop: '5px',
  },
  levelRow: {
    display: 'flex',
    justifyContent: 'space-between',
    padding: '6px 0',
    fontSize: '12px',
    borderBottom: '1px solid #1f2937',
  },
  levelLabel: {
    color: '#9ca3af',
  },
  levelValue: {
    fontWeight: '600',
    color: '#f9fafb',
  },
  newsItem: {
    padding: '10px 0',
    borderBottom: '1px solid #1f2937',
  },
  newsTitle: {
    fontSize: '12px',
    color: '#e5e7eb',
    lineHeight: '1.4',
    marginBottom: '4px',
  },
  newsMeta: {
    fontSize: '10px',
    color: '#6b7280',
    display: 'flex',
    gap: '8px',
    alignItems: 'center',
  },
  auditItem: {
    padding: '6px 0',
    fontSize: '11px',
    borderBottom: '1px solid #1f2937',
    display: 'flex',
    justifyContent: 'space-between',
  },
  indicatorGrid: {
    display: 'grid',
    gridTemplateColumns: '1fr 1fr',
    gap: '8px',
  },
  indicatorCard: {
    backgroundColor: '#0d1117',
    padding: '10px',
    borderRadius: '6px',
    border: '1px solid #1f2937',
  },
  indicatorLabel: {
    fontSize: '10px',
    color: '#6b7280',
    textTransform: 'uppercase',
  },
  indicatorValue: {
    fontSize: '14px',
    fontWeight: '600',
    color: '#f9fafb',
    marginTop: '2px',
  },
  placeholder: {
    textAlign: 'center',
    padding: '60px 20px',
    color: '#6b7280',
  },
};

const TABS = ['Signal', 'News', 'Indicators', 'Levels'];

export default function DetailDrawer({ symbol, detail, news, onClose, loading }) {
  const [activeTab, setActiveTab] = useState('Signal');

  if (!symbol) {
    return (
      <div style={styles.drawer}>
        <div style={styles.placeholder}>
          <p style={{ fontSize: '14px', marginBottom: '8px' }}>Select a stock to view details</p>
          <p style={{ fontSize: '12px' }}>Click any row in the table</p>
        </div>
      </div>
    );
  }

  const symData = detail?.symbol_data || {};
  const signal = detail?.signal || symData.signal || {};
  const reasons = detail?.reasons || [];
  const risks = detail?.risks || [];
  const levels = detail?.levels;
  const audits = detail?.audit_trail || [];
  const events = detail?.events || [];

  const symbolNews = (news || []).filter(n => n.symbol === symbol).slice(0, 20);

  return (
    <div style={styles.drawer}>
      {/* Header */}
      <div style={styles.header}>
        <div style={styles.symbolRow}>
          <span style={styles.symbolName}>{symbol}</span>
          <button style={styles.closeBtn} onClick={onClose}>&times;</button>
        </div>
        <div style={styles.meta}>
          {symData.name} &middot; {symData.sector} &middot; {symData.universe}
        </div>
        <div style={styles.priceSection}>
          <span style={styles.price}>{formatPrice(symData.price)}</span>
          <span style={{ fontSize: '16px', fontWeight: '600', color: getPctColor(symData.pct_1d) }}>
            {formatPct(symData.pct_1d)}
          </span>
        </div>
      </div>

      {/* Tabs */}
      <div style={styles.tabs}>
        {TABS.map(tab => (
          <button
            key={tab}
            style={{ ...styles.tab, ...(activeTab === tab ? styles.tabActive : {}) }}
            onClick={() => setActiveTab(tab)}
          >
            {tab}
          </button>
        ))}
      </div>

      {/* Content */}
      <div style={styles.content}>
        {loading && <div style={{ color: '#9ca3af', textAlign: 'center', padding: '20px' }}>Loading...</div>}

        {!loading && activeTab === 'Signal' && (
          <>
            {/* Signal box */}
            <div style={styles.section}>
              <div style={{
                ...styles.signalBox,
                backgroundColor: getSignalBg(signal.label),
                border: `1px solid ${getSignalColor(signal.label)}40`,
              }}>
                <div style={{ ...styles.signalLabel, color: getSignalColor(signal.label) }}>
                  {signal.label || 'N/A'}
                </div>
                <div style={styles.scoreText}>
                  Confidence: {signal.score ?? '—'}/100
                  {signal.swing_suitable === false && <span style={{ color: '#eab308' }}> (Not swing suitable)</span>}
                </div>
              </div>
            </div>

            {/* Score breakdown */}
            <div style={styles.section}>
              <div style={styles.sectionTitle}>Score Breakdown</div>
              <div style={styles.indicatorGrid}>
                <div style={styles.indicatorCard}>
                  <div style={styles.indicatorLabel}>Trend</div>
                  <div style={styles.indicatorValue}>{signal.trend_score ?? 0}/40</div>
                </div>
                <div style={styles.indicatorCard}>
                  <div style={styles.indicatorLabel}>Momentum</div>
                  <div style={styles.indicatorValue}>{signal.momentum_score ?? 0}/25</div>
                </div>
                <div style={styles.indicatorCard}>
                  <div style={styles.indicatorLabel}>Volume</div>
                  <div style={styles.indicatorValue}>{signal.volume_score ?? 0}/20</div>
                </div>
                <div style={styles.indicatorCard}>
                  <div style={styles.indicatorLabel}>Risk Penalty</div>
                  <div style={{ ...styles.indicatorValue, color: '#ef4444' }}>-{signal.risk_penalty ?? 0}</div>
                </div>
              </div>
            </div>

            {/* Reasons */}
            {reasons.length > 0 && (
              <div style={styles.section}>
                <div style={styles.sectionTitle}>Reasons ({reasons.length})</div>
                <ul style={styles.reasonList}>
                  {reasons.map((r, i) => (
                    <li key={i} style={styles.reasonItem}>
                      <span style={{ ...styles.bullet, backgroundColor: '#22c55e' }} />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Risks */}
            {risks.length > 0 && (
              <div style={styles.section}>
                <div style={styles.sectionTitle}>Risks ({risks.length})</div>
                <ul style={styles.reasonList}>
                  {risks.map((r, i) => (
                    <li key={i} style={styles.reasonItem}>
                      <span style={{ ...styles.bullet, backgroundColor: '#ef4444' }} />
                      {r}
                    </li>
                  ))}
                </ul>
              </div>
            )}

            {/* Audit trail */}
            {audits.length > 0 && (
              <div style={styles.section}>
                <div style={styles.sectionTitle}>Signal History</div>
                {audits.map((a, i) => (
                  <div key={i} style={styles.auditItem}>
                    <span style={{ color: '#9ca3af' }}>{timeAgo(a.ts)}</span>
                    <span>
                      <span style={{ color: getSignalColor(a.old_label) }}>{a.old_label}</span>
                      <span style={{ color: '#6b7280' }}> → </span>
                      <span style={{ color: getSignalColor(a.new_label) }}>{a.new_label}</span>
                    </span>
                  </div>
                ))}
              </div>
            )}

            {/* Events */}
            {events.length > 0 && (
              <div style={styles.section}>
                <div style={styles.sectionTitle}>Upcoming Events</div>
                {events.map((e, i) => (
                  <div key={i} style={styles.levelRow}>
                    <span style={styles.levelLabel}>{e.type}</span>
                    <span style={styles.levelValue}>{e.date ? new Date(e.date).toLocaleDateString() : '—'}</span>
                  </div>
                ))}
              </div>
            )}
          </>
        )}

        {!loading && activeTab === 'News' && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>News Timeline (72h)</div>
            {symbolNews.length === 0 ? (
              <div style={{ color: '#6b7280', fontSize: '12px' }}>No recent news for {symbol}</div>
            ) : (
              symbolNews.map((n, i) => (
                <div key={i} style={styles.newsItem}>
                  <div style={styles.newsTitle}>
                    {n.url ? (
                      <a href={n.url} target="_blank" rel="noopener noreferrer" style={{ color: '#93c5fd', textDecoration: 'none' }}>
                        {n.title}
                      </a>
                    ) : n.title}
                  </div>
                  <div style={styles.newsMeta}>
                    <span>{n.source}</span>
                    <span>{timeAgo(n.ts)}</span>
                    <span style={{ color: getSentimentColor(n.sentiment) }}>
                      {n.sentiment_label}
                    </span>
                    <span style={{ color: getUrgencyColor(n.urgency), fontWeight: '600' }}>
                      {n.urgency}
                    </span>
                  </div>
                </div>
              ))
            )}
          </div>
        )}

        {!loading && activeTab === 'Indicators' && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Technical Indicators</div>
            <div style={styles.indicatorGrid}>
              {[
                { label: 'EMA 20', value: formatPrice(symData.ema20) },
                { label: 'EMA 50', value: formatPrice(symData.ema50) },
                { label: 'EMA 200', value: formatPrice(symData.ema200) },
                { label: 'RSI (14)', value: formatNumber(symData.rsi14, 1) },
                { label: 'MACD', value: formatNumber(symData.macd, 2) },
                { label: 'MACD Hist', value: formatNumber(symData.macd_hist, 2) },
                { label: 'ATR (14)', value: formatNumber(symData.atr14, 2) },
                { label: 'ATR %', value: formatNumber(symData.atr_pct, 1) + '%' },
                { label: 'BB Width', value: formatNumber(symData.bb_width, 1) + '%' },
                { label: 'Vol Ratio', value: formatNumber(symData.vol_ratio, 1) + 'x' },
                { label: '20D High', value: formatPrice(symData.high_20d) },
                { label: '20D Low', value: formatPrice(symData.low_20d) },
              ].map((ind, i) => (
                <div key={i} style={styles.indicatorCard}>
                  <div style={styles.indicatorLabel}>{ind.label}</div>
                  <div style={styles.indicatorValue}>{ind.value}</div>
                </div>
              ))}
            </div>
          </div>
        )}

        {!loading && activeTab === 'Levels' && (
          <div style={styles.section}>
            <div style={styles.sectionTitle}>Swing Levels</div>
            {levels ? (
              <>
                {[
                  { label: 'Entry', value: formatPrice(levels.entry), color: '#3b82f6' },
                  { label: 'Stop Loss', value: formatPrice(levels.stop_loss), color: '#ef4444' },
                  { label: 'Target 1 (2x ATR)', value: formatPrice(levels.target_1), color: '#22c55e' },
                  { label: 'Target 2 (3x ATR)', value: formatPrice(levels.target_2), color: '#16a34a' },
                  { label: 'Risk:Reward', value: levels.risk_reward, color: '#d1d5db' },
                ].map((l, i) => (
                  <div key={i} style={styles.levelRow}>
                    <span style={styles.levelLabel}>{l.label}</span>
                    <span style={{ ...styles.levelValue, color: l.color }}>{l.value}</span>
                  </div>
                ))}
              </>
            ) : (
              <div style={{ color: '#6b7280', fontSize: '12px' }}>
                Swing levels available for Buy/Sell signals only
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
}
