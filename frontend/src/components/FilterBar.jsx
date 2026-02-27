import { useState } from 'react';

const styles = {
  bar: {
    display: 'flex',
    alignItems: 'center',
    gap: '12px',
    padding: '10px 24px',
    backgroundColor: '#0d1117',
    borderBottom: '1px solid #1f2937',
    flexWrap: 'wrap',
  },
  label: {
    fontSize: '12px',
    color: '#9ca3af',
    fontWeight: '600',
  },
  btnGroup: {
    display: 'flex',
    gap: '4px',
  },
  btn: {
    padding: '4px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    fontWeight: '500',
    cursor: 'pointer',
    border: '1px solid #374151',
    backgroundColor: '#1f2937',
    color: '#d1d5db',
    transition: 'all 0.15s',
  },
  btnActive: {
    backgroundColor: '#2563eb',
    color: '#ffffff',
    borderColor: '#2563eb',
  },
  search: {
    padding: '5px 12px',
    borderRadius: '4px',
    fontSize: '12px',
    border: '1px solid #374151',
    backgroundColor: '#1f2937',
    color: '#f9fafb',
    outline: 'none',
    width: '160px',
  },
  select: {
    padding: '5px 10px',
    borderRadius: '4px',
    fontSize: '12px',
    border: '1px solid #374151',
    backgroundColor: '#1f2937',
    color: '#f9fafb',
    outline: 'none',
    cursor: 'pointer',
  },
};

const SIGNAL_FILTERS = [
  { label: 'All', value: null },
  { label: 'Strong Buy', value: 'Strong Buy' },
  { label: 'Buy', value: 'Buy' },
  { label: 'Neutral', value: 'Neutral' },
  { label: 'Sell', value: 'Sell' },
  { label: 'Strong Sell', value: 'Strong Sell' },
];

const SORT_OPTIONS = [
  { label: 'Confidence (High)', value: 'score_desc' },
  { label: 'Confidence (Low)', value: 'score_asc' },
  { label: 'Day Change', value: 'pct_1d' },
  { label: 'Volume Ratio', value: 'vol_ratio' },
  { label: 'Symbol', value: 'symbol' },
];

const SECTOR_OPTIONS = [
  'All', 'Technology', 'Financials', 'Energy', 'Materials',
  'Consumer Staples', 'Consumer Discretionary', 'Healthcare',
  'Industrials', 'Utilities', 'Telecom', 'Real Estate',
];

export default function FilterBar({ filters, onFilterChange }) {
  return (
    <div style={styles.bar}>
      {/* Signal filter */}
      <span style={styles.label}>Signal:</span>
      <div style={styles.btnGroup}>
        {SIGNAL_FILTERS.map(f => (
          <button
            key={f.label}
            style={{
              ...styles.btn,
              ...(filters.signal === f.value ? styles.btnActive : {}),
            }}
            onClick={() => onFilterChange({ ...filters, signal: f.value })}
          >
            {f.label}
          </button>
        ))}
      </div>

      {/* Sort */}
      <span style={styles.label}>Sort:</span>
      <select
        style={styles.select}
        value={filters.sort || 'score_desc'}
        onChange={(e) => onFilterChange({ ...filters, sort: e.target.value })}
      >
        {SORT_OPTIONS.map(o => (
          <option key={o.value} value={o.value}>{o.label}</option>
        ))}
      </select>

      {/* Sector */}
      <span style={styles.label}>Sector:</span>
      <select
        style={styles.select}
        value={filters.sector || 'All'}
        onChange={(e) => onFilterChange({ ...filters, sector: e.target.value === 'All' ? null : e.target.value })}
      >
        {SECTOR_OPTIONS.map(s => (
          <option key={s} value={s}>{s}</option>
        ))}
      </select>

      {/* Search */}
      <input
        type="text"
        placeholder="Search symbol..."
        style={styles.search}
        value={filters.search || ''}
        onChange={(e) => onFilterChange({ ...filters, search: e.target.value })}
      />
    </div>
  );
}
