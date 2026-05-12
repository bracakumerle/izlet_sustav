import Link from "next/link";

export default function Home() {
  return (
    <main style={{ padding: 40, fontFamily: "monospace" }}>
      <h1>iZLET_sustav v2</h1>

      <p>Entity Infrastructure Layer Active</p>

      <hr style={{ margin: "20px 0" }} />

      <h2>Core Modules</h2>

      <ul>
        <li><Link href="/debug/entity-check">Entity Debug</Link></li>
        <li><Link href="/works">Works (if implemented)</Link></li>
        <li><Link href="/events">Events (if implemented)</Link></li>
        <li><Link href="/izlet">iZLET Entity</Link></li>
        <li><Link href="/about">About Layer</Link></li>
      </ul>

      <hr style={{ margin: "20px 0" }} />

      <h3>System Status</h3>
      <p>Frontend: OK</p>
      <p>Routing: OK</p>
      <p>Entity layer: pending runtime verification</p>
    </main>
  );
}