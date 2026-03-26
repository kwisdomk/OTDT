import { useState, useEffect, useRef } from 'react';

export function useWebSocket(url) {
  const [data, setData] = useState(null);
  const [status, setStatus] = useState('connecting');
  const wsRef = useRef(null);

  useEffect(() => {
    const connect = () => {
      const ws = new WebSocket(url);
      wsRef.current = ws;
      ws.onopen = () => setStatus('connected');
      ws.onclose = () => {
        setStatus('reconnecting');
        setTimeout(connect, 2000);
      };
      ws.onerror = (e) => console.error('[WS]', e);
      ws.onmessage = (e) => setData(JSON.parse(e.data));
    };
    connect();
    return () => wsRef.current?.close();
  }, [url]);

  return { data, status };
}
