import React, { useEffect, useMemo, useState } from 'react';
import { KeyRound, Loader2, Save, ShieldCheck, SlidersHorizontal } from 'lucide-react';

import { useAISettings } from '../hooks/useAISettings';


const providers = ['ollama', 'openai', 'anthropic'] as const;
const tasks = ['default', 'summary', 'chat', 'trend', 'code'] as const;


export const AISettingsView: React.FC = () => {
    const { settingsQuery, updateSettings } = useAISettings();
    const [activeProvider, setActiveProvider] = useState<'ollama' | 'openai' | 'anthropic'>('ollama');
    const [providerConfigs, setProviderConfigs] = useState<Record<string, Record<string, any>>>({});
    const [taskRouting, setTaskRouting] = useState<Record<string, string>>({});
    const [apiKeys, setApiKeys] = useState<Record<string, string>>({});
    const [keysToDelete, setKeysToDelete] = useState<string[]>([]);

    useEffect(() => {
        const data = settingsQuery.data;
        if (!data) return;
        setActiveProvider(data.active_provider as 'ollama' | 'openai' | 'anthropic');
        setProviderConfigs(data.provider_configs);
        setTaskRouting(data.task_routing);
    }, [settingsQuery.data]);

    const settings = settingsQuery.data;
    const activeConfig = useMemo(() => providerConfigs[activeProvider] ?? {}, [activeProvider, providerConfigs]);

    if (settingsQuery.isLoading && !settings) {
        return (
            <div className="flex h-full items-center justify-center text-slate-400">
                <div className="flex items-center gap-3 text-sm font-bold">
                    <Loader2 size={18} className="animate-spin text-blue-600" />
                    Loading AI settings...
                </div>
            </div>
        );
    }

    const handleConfigChange = (provider: string, field: string, value: string) => {
        setProviderConfigs((current) => ({
            ...current,
            [provider]: {
                ...(current[provider] ?? {}),
                [field]: field === 'temperature' ? Number(value) : value,
            },
        }));
    };

    const submit = () => {
        updateSettings.mutate({
            active_provider: activeProvider,
            config_update: providerConfigs,
            api_key_update: Object.fromEntries(Object.entries(apiKeys).filter(([, value]) => value.trim().length > 0)),
            keys_to_delete: keysToDelete,
            task_routing_update: taskRouting,
        });
        setApiKeys({});
        setKeysToDelete([]);
    };

    return (
        <div className="mx-auto max-w-6xl space-y-8 pb-16">
            <div className="flex flex-col gap-3 lg:flex-row lg:items-end lg:justify-between">
                <div>
                    <div className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
                        <SlidersHorizontal size={18} />
                        <span className="text-[11px] font-black uppercase tracking-[0.24em]">Provider Control Plane</span>
                    </div>
                    <h2 className="mt-2 text-3xl font-black tracking-tight">AI Settings</h2>
                    <p className="mt-2 max-w-3xl text-sm text-slate-500 dark:text-slate-300">
                        Configure local and hosted providers, decide which one is active, and control task routing before deeper agent workflows land.
                    </p>
                </div>
                <button
                    onClick={submit}
                    disabled={updateSettings.isPending}
                    className="inline-flex items-center gap-2 rounded-2xl bg-slate-900 px-5 py-3 text-xs font-black uppercase tracking-wide text-white disabled:opacity-60 dark:bg-white dark:text-slate-900"
                >
                    {updateSettings.isPending ? <Loader2 size={16} className="animate-spin" /> : <Save size={16} />}
                    Save Settings
                </button>
            </div>

            <section className="grid grid-cols-1 gap-6 xl:grid-cols-[1.1fr_1.3fr]">
                <div className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                    <div className="flex items-center gap-2 text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">
                        <ShieldCheck size={16} className="text-blue-500" />
                        Provider Selection
                    </div>

                    <div className="mt-5 grid gap-3">
                        {providers.map((provider) => {
                            const hasKey = settings?.keys_status?.[provider];
                            return (
                                <button
                                    key={provider}
                                    onClick={() => setActiveProvider(provider)}
                                    className={`rounded-2xl border px-4 py-4 text-left transition ${
                                        activeProvider === provider
                                            ? 'border-blue-500 bg-blue-50 dark:border-blue-400 dark:bg-blue-950/40'
                                            : 'border-slate-200 bg-slate-50 hover:border-slate-300 dark:border-slate-800 dark:bg-slate-950/40'
                                    }`}
                                >
                                    <div className="flex items-center justify-between gap-3">
                                        <div>
                                            <div className="text-sm font-black uppercase tracking-wide">{provider}</div>
                                            <div className="mt-1 text-xs text-slate-500 dark:text-slate-400">
                                                {providerConfigs[provider]?.default_model || 'No default model set'}
                                            </div>
                                        </div>
                                        <div className="text-[10px] font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">
                                            {hasKey ? 'key saved' : 'no key'}
                                        </div>
                                    </div>
                                </button>
                            );
                        })}
                    </div>

                    <div className="mt-6 space-y-4">
                        <div>
                            <label className="mb-2 block text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">Active provider</label>
                            <select
                                value={activeProvider}
                                onChange={(event) => setActiveProvider(event.target.value as 'ollama' | 'openai' | 'anthropic')}
                                className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold outline-none dark:border-slate-800 dark:bg-slate-950"
                            >
                                {providers.map((provider) => (
                                    <option key={provider} value={provider}>{provider}</option>
                                ))}
                            </select>
                        </div>

                        <div>
                            <label className="mb-2 block text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">API key</label>
                            <div className="flex gap-2">
                                <div className="relative flex-1">
                                    <KeyRound size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                                    <input
                                        value={apiKeys[activeProvider] ?? ''}
                                        onChange={(event) => setApiKeys((current) => ({ ...current, [activeProvider]: event.target.value }))}
                                        type="password"
                                        placeholder={settings?.keys_status?.[activeProvider] ? 'Stored in keyring. Enter to replace.' : 'Paste API key'}
                                        className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 text-sm font-bold outline-none dark:border-slate-800 dark:bg-slate-950"
                                    />
                                </div>
                                {settings?.keys_status?.[activeProvider] && (
                                    <button
                                        onClick={() => setKeysToDelete((current) => Array.from(new Set([...current, activeProvider])))}
                                        className="rounded-xl border border-red-200 px-4 text-xs font-black uppercase tracking-wide text-red-600 dark:border-red-900/50 dark:text-red-300"
                                    >
                                        Clear
                                    </button>
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                <div className="space-y-6">
                    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                        <div className="text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">Provider Config</div>
                        <div className="mt-5 grid grid-cols-1 gap-4 md:grid-cols-2">
                            <div>
                                <label className="mb-2 block text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">Base URL</label>
                                <input
                                    value={activeConfig.base_url ?? ''}
                                    onChange={(event) => handleConfigChange(activeProvider, 'base_url', event.target.value)}
                                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold outline-none dark:border-slate-800 dark:bg-slate-950"
                                />
                            </div>
                            <div>
                                <label className="mb-2 block text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">Default model</label>
                                <input
                                    value={activeConfig.default_model ?? ''}
                                    onChange={(event) => handleConfigChange(activeProvider, 'default_model', event.target.value)}
                                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold outline-none dark:border-slate-800 dark:bg-slate-950"
                                />
                            </div>
                            <div>
                                <label className="mb-2 block text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">Temperature</label>
                                <input
                                    value={activeConfig.temperature ?? 0}
                                    onChange={(event) => handleConfigChange(activeProvider, 'temperature', event.target.value)}
                                    type="number"
                                    min="0"
                                    max="2"
                                    step="0.1"
                                    className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold outline-none dark:border-slate-800 dark:bg-slate-950"
                                />
                            </div>
                        </div>
                    </section>

                    <section className="rounded-[2rem] border border-slate-200 bg-white p-6 shadow-sm dark:border-slate-800 dark:bg-slate-900">
                        <div className="text-sm font-black uppercase tracking-wide text-slate-500 dark:text-slate-400">Task Routing</div>
                        <div className="mt-5 grid gap-4 md:grid-cols-2">
                            {tasks.map((task) => (
                                <div key={task}>
                                    <label className="mb-2 block text-[10px] font-black uppercase tracking-[0.18em] text-slate-400">{task}</label>
                                    <select
                                        value={taskRouting[task] ?? 'ollama'}
                                        onChange={(event) => setTaskRouting((current) => ({ ...current, [task]: event.target.value }))}
                                        className="w-full rounded-xl border border-slate-200 bg-white px-4 py-3 text-sm font-bold outline-none dark:border-slate-800 dark:bg-slate-950"
                                    >
                                        {providers.map((provider) => (
                                            <option key={provider} value={provider}>{provider}</option>
                                        ))}
                                    </select>
                                </div>
                            ))}
                        </div>
                    </section>
                </div>
            </section>
        </div>
    );
};
