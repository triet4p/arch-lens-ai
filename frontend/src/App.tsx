import { useEffect, useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import axios from 'axios';

function App() {
  const [status, setStatus] = useState<string>("Initializing...");

  useEffect(() => {
    const initSidecar = async () => {
      try {
        console.log("[System] Triggering Sidecar...");
        await invoke('start_sidecar');
        
        // Polling để check khi nào sidecar thực sự up
        let retries = 0;
        const checkHealth = async () => {
          try {
            const res = await axios.get("http://127.0.0.1:14201/health");
            if (res.data.status === "ok") {
              setStatus("Connected to Sidecar! PydanticAI & MarkItDown Ready.");
            }
          } catch (e) {
            if (retries < 10) {
              retries++;
              setTimeout(checkHealth, 1000);
            } else {
              setStatus("Sidecar connection timeout.");
            }
          }
        };
        checkHealth();
      } catch (err) {
        setStatus("Failed to start sidecar.");
      }
    };

    initSidecar();
  }, []);

  return (
    <div className="h-screen bg-slate-950 text-white flex flex-col items-center justify-center gap-4">
      <h1 className="text-4xl font-black italic">ARCH LENS AI</h1>
      <div className="px-4 py-2 bg-slate-800 rounded-full text-xs font-mono text-blue-400 border border-blue-900/30">
        Status: {status}
      </div>
    </div>
  );
}

export default App;