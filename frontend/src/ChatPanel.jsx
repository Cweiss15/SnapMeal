import { useState, useRef, useEffect } from "react";
import { apiFetch } from "./api";

export default function ChatPanel({ ingredients, recipes, onRecipesUpdate }) {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [sending, setSending] = useState(false);
  const bottomRef = useRef(null);

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    const text = input.trim();
    if (!text || sending) return;

    const userMsg = { role: "user", content: text };
    const updated = [...messages, userMsg];
    setMessages(updated);
    setInput("");
    setSending(true);

    try {
      const res = await apiFetch("/chat", {
        method: "POST",
        body: JSON.stringify({
          messages: updated,
          ingredients: ingredients.map((i) => i.name || i),
          recipes: recipes,
        }),
      });

      if (!res.ok) throw new Error(`Server error ${res.status}`);

      const data = await res.json();

      if (data.updated_recipes && onRecipesUpdate) {
        onRecipesUpdate(data.updated_recipes, data.updated_shopping_list);
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply || "✨ Recipes updated above!" },
        ]);
      } else {
        setMessages((prev) => [
          ...prev,
          { role: "assistant", content: data.reply },
        ]);
      }
    } catch {
      setMessages((prev) => [
        ...prev,
        { role: "assistant", content: "Sorry, something went wrong. Try again." },
      ]);
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <>
      <button
        className="chat-fab"
        onClick={() => setOpen((o) => !o)}
        title="Chat with AI"
      >
        {open ? "✕" : "💬"}
      </button>

      {open && (
        <div className="chat-panel">
          <div className="chat-header">
            <span>🤖 Recipe Assistant</span>
            <button className="chat-close" onClick={() => setOpen(false)}>
              ✕
            </button>
          </div>

          <div className="chat-messages">
            {messages.length === 0 && (
              <div className="chat-empty">
                <p>
                  {ingredients.length > 0
                    ? "Tell me how to adjust your recipes!"
                    : "Ask me anything about cooking!"}
                </p>
                <div className="chat-suggestions">
                  {(ingredients.length > 0
                    ? [
                        "I don't have eggs",
                        "Make it vegetarian",
                        "Quick 15-min meals only",
                        "I also have pasta and garlic",
                      ]
                    : [
                        "What can I make with chicken and rice?",
                        "Give me a quick pasta recipe",
                        "Suggest a healthy dinner",
                        "What's a good dessert with chocolate?",
                      ]
                  ).map((s) => (
                    <button
                      key={s}
                      className="chat-suggestion"
                      onClick={() => {
                        setInput(s);
                      }}
                    >
                      {s}
                    </button>
                  ))}
                </div>
              </div>
            )}

            {messages.map((msg, i) => (
              <div
                key={i}
                className={`chat-bubble ${msg.role === "user" ? "user" : "assistant"}`}
              >
                {msg.content}
              </div>
            ))}

            {sending && (
              <div className="chat-bubble assistant">
                <span className="chat-typing">
                  <span></span><span></span><span></span>
                </span>
              </div>
            )}

            <div ref={bottomRef} />
          </div>

          <div className="chat-input-area">
            <textarea
              className="chat-input"
              placeholder="e.g. I don't have milk, suggest Italian recipes..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              rows={1}
            />
            <button
              className="chat-send"
              onClick={sendMessage}
              disabled={!input.trim() || sending}
            >
              ➤
            </button>
          </div>
        </div>
      )}
    </>
  );
}
