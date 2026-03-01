const API_BASE = process.env.AGENTOPS_API_URL || 'http://server:8000';
const API_KEY = process.env.AGENTOPS_API_KEY || 'dev-api-key';

export async function apiFetch(path: string, init?: RequestInit) {
  const res = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: {
      'x-api-key': API_KEY,
      'content-type': 'application/json',
      ...(init?.headers || {}),
    },
    cache: 'no-store',
  });
  return res.json();
}
