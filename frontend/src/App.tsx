import React, { useState, useRef, useEffect } from 'react';
import './App.css';

interface Message {
  type: 'user' | 'agent' | 'error';
  text: string;
}

function App() {
  const [query, setQuery] = useState('');
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(scrollToBottom, [messages]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;

    const userMessage: Message = { type: 'user', text: query };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setQuery('');
    setLoading(true);

    try {
      const res = await fetch('/predict', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ query }),
      });

      const data = await res.json();

      if (res.ok) {
        const agentMessage: Message = { type: 'agent', text: data.response };
        setMessages((prevMessages) => [...prevMessages, agentMessage]);
      } else {
        const errorMessage: Message = { type: 'error', text: data.error || 'An unknown error occurred.' };
        setMessages((prevMessages) => [...prevMessages, errorMessage]);
      }
    } catch (err) {
      const errorMessage: Message = { type: 'error', text: 'Failed to connect to the backend server.' };
      setMessages((prevMessages) => [...prevMessages, errorMessage]);
      console.error('Fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>Job Search AI Assistant</h1>
        <div className="chat-window">
          <div className="messages-container">
            {messages.map((msg, index) => (
              <div key={index} className={`message ${msg.type}`}>
                <p>{msg.text}</p>
              </div>
            ))}
            {loading && <div className="message agent loading"><p>Agent is typing...</p></div>}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={handleSubmit} className="input-area">
            <textarea
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              placeholder="Enter your job search query..."
              disabled={loading}
              rows={3}
            />
            <button type="submit" disabled={loading}>
              {loading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </header>
    </div>
  );
}

export default App;
