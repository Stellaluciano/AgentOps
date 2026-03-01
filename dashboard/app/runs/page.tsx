import { apiFetch } from '@/lib/api';

export default async function RunsPage() {
  const runs = await apiFetch('/v1/runs');
  return (
    <div>
      <h2>Runs</h2>
      <ul>
        {(runs || []).map((run: any) => (
          <li key={run.id}>
            <a href={`/runs/${run.id}`}>{run.name}</a> — {run.status}
          </li>
        ))}
      </ul>
    </div>
  );
}
