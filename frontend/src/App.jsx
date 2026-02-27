import { useState, useMemo, useCallback } from 'react';
import TopBar from './components/TopBar';
import FilterBar from './components/FilterBar';
import StockTable from './components/StockTable';
import DetailDrawer from './components/DetailDrawer';
import { useUniverseData, useNewsData, useSignalDetail, useSSE } from './hooks/useData';

const styles = {
  app: {
    height: '100vh',
    display: 'flex',
    flexDirection: 'column',
    backgroundColor: '#0d1117',
    color: '#e5e7eb',
    fontFamily: '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif',
  },
  main: {
    display: 'flex',
    flex: 1,
    overflow: 'hidden',
  },
  tableArea: {
    flex: 1,
    overflow: 'auto',
  },
  loading: {
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center',
    height: '100vh',
    flexDirection: 'column',
    gap: '16px',
  },
  toast: {
    position: 'fixed',
    bottom: '20px',
    right: '20px',
    padding: '12px 20px',
    borderRadius: '8px',
    fontSize: '13px',
    fontWeight: '500',
    zIndex: 1000,
    transition: 'all 0.3s',
    maxWidth: '350px',
  },
};

function App() {
  const { data, loading, error, refresh } = useUniverseData(60000);
  const { news } = useNewsData(null, 90000);
  const [selectedSymbol, setSelectedSymbol] = useState(null);
  const { detail, loading: detailLoading } = useSignalDetail(selectedSymbol);
  const [filters, setFilters] = useState({
    signal: null,
    sort: 'score_desc',
    sector: null,
    search: '',
  });
  const [toasts, setToasts] = useState([]);

  // SSE handler
  const handleSSE = useCallback((event) => {
    if (event.type === 'signal_change') {
      setToasts(prev => [...prev.slice(-4), {
        id: Date.now(),
        message: `${event.data.symbol}: ${event.data.old_label} → ${event.data.new_label} (Score: ${event.data.score})`,
        color: event.data.new_label?.includes('Buy') ? '#16a34a' : '#dc2626',
      }]);
      setTimeout(() => {
        setToasts(prev => prev.slice(1));
      }, 8000);
    } else if (event.type === 'urgent_news') {
      setToasts(prev => [...prev.slice(-4), {
        id: Date.now(),
        message: `Breaking: ${event.data.items?.[0]?.title || 'New alert'}`,
        color: '#dc2626',
      }]);
      setTimeout(() => {
        setToasts(prev => prev.slice(1));
      }, 10000);
    }
  }, []);

  useSSE(handleSSE);

  // Filter and sort symbols
  const filteredSymbols = useMemo(() => {
    if (!data?.symbols) return [];

    let symbols = [...data.symbols];

    if (filters.signal) {
      symbols = symbols.filter(s => s.signal?.label === filters.signal);
    }

    if (filters.sector) {
      symbols = symbols.filter(s => s.sector === filters.sector);
    }

    if (filters.search) {
      const q = filters.search.toLowerCase();
      symbols = symbols.filter(s =>
        s.symbol.toLowerCase().includes(q) ||
        s.name?.toLowerCase().includes(q)
      );
    }

    switch (filters.sort) {
      case 'score_desc':
        symbols.sort((a, b) => (b.signal?.score ?? 0) - (a.signal?.score ?? 0));
        break;
      case 'score_asc':
        symbols.sort((a, b) => (a.signal?.score ?? 0) - (b.signal?.score ?? 0));
        break;
      case 'pct_1d':
        symbols.sort((a, b) => Math.abs(b.pct_1d || 0) - Math.abs(a.pct_1d || 0));
        break;
      case 'vol_ratio':
        symbols.sort((a, b) => (b.vol_ratio || 0) - (a.vol_ratio || 0));
        break;
      case 'symbol':
        symbols.sort((a, b) => a.symbol.localeCompare(b.symbol));
        break;
    }

    return symbols;
  }, [data, filters]);

  if (error) {
    return (
      <div style={styles.loading}>
        <div style={{ color: '#ef4444', fontSize: '16px' }}>Error: {error}</div>
        <div style={{ color: '#9ca3af', fontSize: '13px' }}>
          Make sure the backend is running on port 8000
        </div>
        <button
          onClick={refresh}
          style={{
            padding: '8px 20px',
            borderRadius: '6px',
            backgroundColor: '#2563eb',
            color: '#fff',
            border: 'none',
            cursor: 'pointer',
            fontSize: '13px',
          }}
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div style={styles.app}>
      <TopBar
        marketStatus={data?.market_status}
        breadth={data?.breadth}
        lastPriceUpdate={data?.last_price_update}
        lastNewsUpdate={data?.last_news_update}
      />

      <FilterBar filters={filters} onFilterChange={setFilters} />

      <div style={styles.main}>
        <div style={styles.tableArea}>
          <StockTable
            symbols={filteredSymbols}
            news={news}
            onSelectSymbol={setSelectedSymbol}
            selectedSymbol={selectedSymbol}
          />
        </div>

        <DetailDrawer
          symbol={selectedSymbol}
          detail={detail}
          news={news}
          loading={detailLoading}
          onClose={() => setSelectedSymbol(null)}
        />
      </div>

      {toasts.map((toast, i) => (
        <div
          key={toast.id}
          style={{
            ...styles.toast,
            backgroundColor: toast.color + '20',
            color: toast.color,
            border: `1px solid ${toast.color}40`,
            bottom: `${20 + i * 60}px`,
          }}
        >
          {toast.message}
        </div>
      ))}
    </div>
  );
}

export default App;
