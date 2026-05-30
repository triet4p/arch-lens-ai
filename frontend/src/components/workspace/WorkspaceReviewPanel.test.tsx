import { describe, expect, it } from 'vitest';
import { render, screen } from '@testing-library/react';

import { WorkspaceReviewPanel } from './WorkspaceReviewPanel';


describe('WorkspaceReviewPanel', () => {
  it('renders decision summary and recommendation data', () => {
    render(
      <WorkspaceReviewPanel
        review={{
          workspace_id: 1,
          generated_at: '2026-05-30T00:00:00Z',
          review_input: {
            workspace_id: 1,
            workspace_name: 'Alpha',
            workspace_description: null,
            constraints: {},
            artifacts: [],
          },
          findings: [{ category: 'fit', title: 'Stack alignment', detail: 'Fit is strong.', related_artifact_ids: [] }],
          conflicts: [],
          decision_summary: 'The workspace is ready for a scoped trial.',
          recommendation: { label: 'trial', rationale: 'Balanced upside with manageable risk.' },
          recommended_next_steps: ['Run a limited integration pilot.'],
          scores: {
            technical_fit_score: 80,
            risk_score: 30,
            roi_score: 72,
            confidence_score: 78,
            evidence_coverage_score: 100,
          },
          artifact_coverage: { analyzed_artifacts: 2, total_artifacts: 2, pending_artifacts: 0 },
          radar_entries: [],
        }}
        isLoading={false}
        isRefreshing={false}
        isExporting={false}
        onRefresh={() => undefined}
        onExport={() => undefined}
      />
    );

    expect(screen.getByText(/Recommendation: trial/i)).toBeInTheDocument();
    expect(screen.getByText(/The workspace is ready for a scoped trial\./i)).toBeInTheDocument();
    expect(screen.getByText(/Run a limited integration pilot\./i)).toBeInTheDocument();
  });
});
