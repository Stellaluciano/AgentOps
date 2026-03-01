import { apiFetch } from '@/lib/api';

export default async function EvalsPage() {
  const evals = await apiFetch('/v1/evals');
  return (
    <div>
      <h2>Eval Runs</h2>
      <ul>
        {(evals || []).map((ev: any) => (
          <li key={ev.id}>{ev.dataset_name} ({ev.agent_version}) pass_rate={ev.summary?.pass_rate}</li>
        ))}
      </ul>
    </div>
  );
}
