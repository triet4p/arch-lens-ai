import { useEffect, useRef } from 'react';
import { useAppStore, hasActiveOperations } from './stores/useAppStore';
import { apiClient } from './lib/axios';
import { StartupOverlay } from './components/layout/StartupOverlay';
import { Layout } from './components/layout/Layout';
import { invoke } from '@tauri-apps/api/core';
import { WorkspaceList } from './views/WorkspaceList';
import { WorkspaceDetail } from './views/WorkspaceDetail';

function App() {
  const { isDarkMode, isBackendReady, setBackendReady, minDisplayTimeReached, 
    setMinDisplayTimeReached, setConnectionError, currentView, selectedWorkspaceId } = useAppStore();
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
          {selectedWorkspaceId ? (
            <WorkspaceDetail />
          ) : (
            <>
              {currentView === 'workspaces' && <WorkspaceList />}
              {currentView === 'tech_radar' && (
                <div className="flex flex-col items-center justify-center h-full text-center space-y-4">
                  <h2 className="text-2xl font-black opacity-20 uppercase tracking-widest">Tech Radar Coming Soon</h2>
                </div>
              )}
            </>
          )}
        </Layout>
      )}
    </>
  );
}

export default App;