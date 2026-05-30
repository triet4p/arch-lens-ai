import { describe, expect, it, vi } from 'vitest';
import { render, screen } from '@testing-library/react';

import { AISettingsView } from './AISettingsView';

const mockedSettings = {
  active_provider: 'ollama',
  provider_configs: {
    ollama: { base_url: 'http://127.0.0.1:11434', default_model: 'qwen3:8b', temperature: 0.1 },
    openai: { base_url: 'https://api.openai.com/v1', default_model: 'gpt-5-mini', temperature: 0.1 },
    anthropic: { base_url: 'https://api.anthropic.com', default_model: 'claude-3-7-sonnet-latest', temperature: 0.1 },
  },
  keys_status: { ollama: false, openai: true, anthropic: false },
  task_routing: { default: 'ollama', summary: 'ollama', chat: 'ollama', trend: 'openai', code: 'openai' },
};

vi.mock('../hooks/useAISettings', () => ({
  useAISettings: () => ({
    settingsQuery: {
      isLoading: false,
      data: mockedSettings,
    },
    updateSettings: {
      mutate: vi.fn(),
      isPending: false,
    },
  }),
}));


describe('AISettingsView', () => {
  it('renders provider settings and task routing sections', () => {
    render(<AISettingsView />);

    expect(screen.getByText(/AI Settings/i)).toBeInTheDocument();
    expect(screen.getByText(/Provider Selection/i)).toBeInTheDocument();
    expect(screen.getByText(/^Task Routing$/i)).toBeInTheDocument();
    expect(screen.getByDisplayValue('qwen3:8b')).toBeInTheDocument();
  });
});
