import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:8001";

export default function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(e) {
    e.preventDefault();
    const question = input.trim();
    if (!question || loading) return;
    setInput("");
    setMessages((m) => [...m, { role: "user", text: question }]);
    setLoading(true);
    try {
      const res = await fetch(`${API_URL}/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ question }),
      });

      if (!res.ok) {
        const detail = await res.json().then((d) => d.detail).catch(() => null);
        throw new Error(detail || `API error ${res.status}`);
      }

      const data = await res.json();
      setMessages((m) => [...m, { role: "assistant", text: data.answer }]);
    } catch (err) {
      setMessages((m) => [...m, { role: "error", text: `Request failed: ${err.message}` }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app">
      <h1>Batch Plant Assistant</h1>
      <div className="chat">
        {messages.length === 0 && (
          <p className="hint">Try: “Can we produce 3 batches of Product A?”</p>
        )}
        {messages.map((msg, i) => (
          <div key={i} className={`msg ${msg.role}`}>{msg.text}</div>
        ))}
        {loading && <div className="msg assistant">Thinking…</div>}
      </div>
      <form onSubmit={send} className="composer">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          placeholder="Ask about production, tanks, or maintenance…"
          autoFocus
        />
        <button disabled={loading}>Send</button>
      </form>
    </div>
  );
}
