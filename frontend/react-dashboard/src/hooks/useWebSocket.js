import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState('connecting');

  const wsRef = useRef(null);
  const reconnectTimerRef = useRef(null);
  const reconnectAttemptsRef = useRef(0);
  const mountedRef = useRef(false);

  useEffect(() => {
    mountedRef.current = true;

    // Reset state when URL changes
    setStatus('connecting');
    setData(null);

    const clearTimers = () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    const connect = () => {
      if (!mountedRef.current) return;

      clearTimers();

      const ws = new WebSocket(url);
      wsRef.current = ws;

      ws.onopen = () => {
        reconnectAttemptsRef.current = 0;
        setStatus('connected');
        // No app-level heartbeat needed: server pushes every 2s which keeps
        // the connection alive through proxies and load balancers.
      };

      ws.onmessage = (e) => {
        try {
          setData(JSON.parse(e.data));
        } catch (err) {
          console.error('[WS] Failed to parse message', err);
        }
      };

      ws.onerror = () => {
        // Close will trigger reconnection; keep status as reconnecting to reduce UI flicker.
        if (mountedRef.current) setStatus((prev) => (prev === 'connected' ? 'reconnecting' : prev));
      };

      ws.onclose = () => {
        if (!mountedRef.current) return;

        setStatus('reconnecting');
        clearTimers();

        reconnectAttemptsRef.current += 1;
        const attempt = reconnectAttemptsRef.current;

        const baseDelay = 2000;
        const delay = Math.min(30000, baseDelay * Math.pow(2, attempt - 1));
        const jitter = Math.random() * 250;

        reconnectTimerRef.current = setTimeout(connect, delay + jitter);
      };
    };

    connect();

    return () => {
      mountedRef.current = false;
      clearTimers();
      try {
        wsRef.current?.close();
      } catch (_) {
        // ignore
      }
      wsRef.current = null;
    };
  }, [url]);

  return { data, status };
}