export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html>
      <body style={{ fontFamily: 'sans-serif', margin: 20 }}>
        <h1>AgentOps Dashboard</h1>
        <nav style={{ display: 'flex', gap: 12 }}>
          <a href="/runs">Runs</a>
          <a href="/evals">Evals</a>
        </nav>
        <hr />
        {children}
      </body>
    </html>
  );
}
