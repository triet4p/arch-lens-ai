import { useEffect, useRef } from 'react';
import { useAppStore, hasActiveOperations } from './stores/useAppStore';
import { apiClient } from './lib/axios';
import { StartupOverlay } from './components/layout/StartupOverlay';
import { Layout } from './components/layout/Layout';
import { invoke } from '@tauri-apps/api/core';

function App() {
  const { isDarkMode, isBackendReady, setBackendReady, minDisplayTimeReached, setMinDisplayTimeReached, setConnectionError, t } = useAppStore();
  const retryCountRef = useRef(0);

  useEffect(() => {
    const displayTimer = setTimeout(() => setMinDisplayTimeReached(true), 2500);
    const sidecarTimer = setTimeout(async () => {
      try { await invoke('start_sidecar'); } catch (err) { console.error(err); }
    }, 1000);
    return () => { clearTimeout(displayTimer); clearTimeout(sidecarTimer); };
  }, [setMinDisplayTimeReached]);

  useEffect(() => {
    const checkConnection = async () => {
      if (hasActiveOperations()) return;
      try {
        await apiClient.get('/health', { timeout: 3000 });
        if (!isBackendReady) { setBackendReady(true); setConnectionError(null); }
      } catch (e) {
        if (!isBackendReady) {
          retryCountRef.current += 1;
          if (retryCountRef.current >= 30) setConnectionError("Sidecar connection timeout. Check port 14201.");
        }
      }
    };
    const interval = setInterval(checkConnection, isBackendReady ? 8000 : 1500);
    return () => clearInterval(interval);
  },[isBackendReady, setBackendReady, setConnectionError]);

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
  }, [isDarkMode]);

  const canEnterApp = isBackendReady && minDisplayTimeReached;

  return (
    <>
      <StartupOverlay canEnter={canEnterApp} />
      {canEnterApp && (
        <Layout>
          <div className="flex flex-col items-center justify-center h-full text-center space-y-4 animate-in fade-in zoom-in-95">
            <h1 className="text-4xl font-black tracking-tight">{t.welcome} <span className="text-blue-600">Arch Lens AI</span></h1>
            <p className="text-slate-500 max-w-lg">{t.subtitle}</p>
          </div>
        </Layout>
      )}
    </>
  );
}

export default App;