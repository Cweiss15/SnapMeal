import { useState, useEffect } from "react";
import { apiFetch } from "./api";

export default function PreferencesPanel({ open, onClose }) {
  const [preferences, setPreferences] = useState([]);
  const [type, setType] = useState("allergy");
  const [value, setValue] = useState("");
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) loadPreferences();
  }, [open]);

  const loadPreferences = async () => {
    try {
      const res = await apiFetch("/preferences/");
      if (res.ok) setPreferences(await res.json());
    } catch {}
  };

  const addPreference = async (e) => {
    e.preventDefault();
    if (!value.trim()) return;
    setLoading(true);
    try {
      const res = await apiFetch("/preferences/", {
        method: "POST",
        body: JSON.stringify({ preference_type: type, value: value.trim() }),
      });
      if (res.ok) {
        setValue("");
        loadPreferences();
      }
    } catch {}
    setLoading(false);
  };

  const deletePreference = async (id) => {
    try {
      await apiFetch(`/preferences/${id}`, { method: "DELETE" });
      setPreferences((prev) => prev.filter((p) => p.id !== id));
    } catch {}
  };

  if (!open) return null;

  const typeLabels = {
    allergy: "🚫 Allergy",
    dislike: "👎 Dislike",
    diet: "🥗 Diet",
    cuisine_preference: "🍽️ Cuisine",
  };

  const grouped = preferences.reduce((acc, p) => {
    if (!acc[p.preference_type]) acc[p.preference_type] = [];
    acc[p.preference_type].push(p);
    return acc;
  }, {});

  return (
    <div className="panel-overlay" onClick={onClose}>
      <div className="panel-content" onClick={(e) => e.stopPropagation()}>
        <div className="panel-header">
          <h2>🍽️ Food Preferences</h2>
          <button className="chat-close" onClick={onClose}>✕</button>
        </div>

        <form className="pref-form" onSubmit={addPreference}>
          <select value={type} onChange={(e) => setType(e.target.value)} className="pref-select">
            <option value="allergy">Allergy</option>
            <option value="dislike">Dislike</option>
            <option value="diet">Diet (e.g. vegetarian)</option>
            <option value="cuisine_preference">Cuisine preference</option>
          </select>
          <input
            type="text"
            placeholder="e.g. peanuts, gluten, vegan..."
            value={value}
            onChange={(e) => setValue(e.target.value)}
            className="pref-input"
          />
          <button type="submit" className="btn primary" disabled={loading || !value.trim()}>
            Add
          </button>
        </form>

        <div className="pref-list">
          {Object.entries(grouped).map(([key, items]) => (
            <div key={key} className="pref-group">
              <h4>{typeLabels[key] || key}</h4>
              <div className="pref-tags">
                {items.map((p) => (
                  <span key={p.id} className="pref-tag">
                    {p.value}
                    <button onClick={() => deletePreference(p.id)}>×</button>
                  </span>
                ))}
              </div>
            </div>
          ))}
          {preferences.length === 0 && (
            <p className="pref-empty">No preferences set. Add some so recipes respect your dietary needs!</p>
          )}
        </div>
      </div>
    </div>
  );
}
