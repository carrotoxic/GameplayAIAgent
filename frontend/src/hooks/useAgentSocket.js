import { useState, useEffect, useRef } from 'react';

const WEBSOCKET_URL = `ws://${window.location.host}/ws/agent`;

export const useAgentSocket = () => {
  const [isConnected, setIsConnected] = useState(false);
  const [lastMessage, setLastMessage] = useState(null);
  const [isAgentReady, setIsAgentReady] = useState(false);
  const socketRef = useRef(null);
  const reconnectTimerRef = useRef(null);

  const connect = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      return;
    }

    socketRef.current = new WebSocket(WEBSOCKET_URL);
    
    socketRef.current.onopen = () => {
      console.log('WebSocket connected');
      setIsConnected(true);
      setIsAgentReady(true);
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
    };

    socketRef.current.onmessage = (event) => {
      const message = JSON.parse(event.data);
      setLastMessage(message);
    };

    socketRef.current.onclose = () => {
      console.log('WebSocket disconnected');
      setIsConnected(false);
      setIsAgentReady(false);

      if (!reconnectTimerRef.current) {
        reconnectTimerRef.current = setTimeout(() => {
          console.log('Reconnecting WebSocket...');
          connect();
        }, 3000);
      }
    };

    socketRef.current.onerror = (error) => {
      console.error('WebSocket error:', error);
      socketRef.current.close();
    };
  };

  useEffect(() => {
    connect();

    return () => {
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
      }
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, []);

  return { isConnected, lastMessage, isAgentReady };
}; 