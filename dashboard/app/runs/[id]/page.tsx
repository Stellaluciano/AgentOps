import { apiFetch } from '@/lib/api';

export default async function RunDetailPage({ params }: { params: { id: string } }) {
  const data = await apiFetch(`/v1/runs/${params.id}`);
  return (
    <div>
      <h2>Run: {data.run?.name}</h2>
      <a href={`/replay/${params.id}`}>Replay this run</a>
      <h3>Timeline</h3>
      <ol>
        {(data.spans || []).map((span: any) => (
          <li key={span.id}>
            [{span.type}] {span.name} - {span.status}
          </li>
        ))}
      </ol>
    </div>
  );
}
