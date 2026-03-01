'use client';

import { useState } from 'react';

export default function ReplayPage({ params }: { params: { id: string } }) {
  const [result, setResult] = useState<string>('');

  async function triggerReplay() {
    const res = await fetch(`http://localhost:8000/v1/replay/${params.id}`, {
      method: 'POST',
      headers: { 'x-api-key': 'dev-api-key', 'content-type': 'application/json' },
      body: JSON.stringify({ mode: 'exact' }),
    });
    const json = await res.json();
    setResult(json.replay_run_id || JSON.stringify(json));
  }

  return (
    <div>
      <h2>Replay Run {params.id}</h2>
      <button onClick={triggerReplay}>Trigger exact replay</button>
      {result && <pre>{result}</pre>}
    </div>
  );
}
