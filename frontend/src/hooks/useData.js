import { useState, useEffect, useCallback, useRef } from 'react';
import { fetchUniverse, fetchNews, fetchSignalDetail, createSSEConnection } from '../utils/api';

export function useUniverseData(refreshInterval = 60000) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const load = useCallback(async () => {
    try {
      const result = await fetchUniverse();
      setData(result);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const interval = setInterval(load, refreshInterval);
    return () => clearInterval(interval);
  }, [load, refreshInterval]);

  return { data, loading, error, refresh: load };
}

export function useNewsData(symbol = null, refreshInterval = 90000) {
  const [news, setNews] = useState([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    try {
      const result = await fetchNews({ symbol, range: 72, limit: 100 });
      setNews(result.news || []);
    } catch {
      // silent
    } finally {
      setLoading(false);
    }
  }, [symbol]);

  useEffect(() => {
    load();
    const interval = setInterval(load, refreshInterval);
    return () => clearInterval(interval);
  }, [load, refreshInterval]);

  return { news, loading, refresh: load };
}

export function useSignalDetail(symbol) {
  const [detail, setDetail] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!symbol) {
      setDetail(null);
      return;
    }
    setLoading(true);
    fetchSignalDetail(symbol)
      .then(setDetail)
      .catch(() => setDetail(null))
      .finally(() => setLoading(false));
  }, [symbol]);

  return { detail, loading };
}

export function useSSE(onEvent) {
  const callbackRef = useRef(onEvent);
  callbackRef.current = onEvent;

  useEffect(() => {
    const es = createSSEConnection((data) => {
      callbackRef.current?.(data);
    });
    return () => es.close();
  }, []);
}
