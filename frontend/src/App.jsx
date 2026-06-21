import { useState, useCallback } from "react";
import "./App.css";

const API_URL = "http://localhost:8000";

function App() {
  const [files, setFiles] = useState([]);
  const [previews, setPreviews] = useState([]);
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragActive, setDragActive] = useState(false);

  const handleFiles = useCallback((incoming) => {
    const valid = Array.from(incoming).filter((f) =>
      ["image/jpeg", "image/png", "image/webp"].includes(f.type)
    );
    setFiles((prev) => {
      const next = [...prev, ...valid].slice(0, 20);
      setPreviews(next.map((f) => URL.createObjectURL(f)));
      return next;
    });
    setError(null);
  }, []);

  const handleDrop = useCallback(
    (e) => {
      e.preventDefault();
      setDragActive(false);
      if (e.dataTransfer.files.length) handleFiles(e.dataTransfer.files);
    },
    [handleFiles]
  );

  const removeFile = (index) => {
    setFiles((prev) => {
      const next = prev.filter((_, i) => i !== index);
      setPreviews(next.map((f) => URL.createObjectURL(f)));
      return next;
    });
  };

  const analyze = async () => {
    if (!files.length) return;
    setLoading(true);
    setError(null);
    setResult(null);

    const formData = new FormData();
    files.forEach((f) => formData.append("files", f));

    try {
      const res = await fetch(`${API_URL}/analyze`, {
        method: "POST",
        body: formData,
      });
      if (!res.ok) {
        const body = await res.json().catch(() => null);
        throw new Error(body?.detail || `Server error ${res.status}`);
      }
      setResult(await res.json());
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const reset = () => {
    setFiles([]);
    setPreviews([]);
    setResult(null);
    setError(null);
  };

  return (
    <div className="app">
      <header className="header">
        <div className="logo">🍳</div>
        <h1>Fridge Recipe AI</h1>
        <p className="subtitle">Snap your fridge, get recipes instantly</p>
      </header>

      {!result ? (
        <main className="upload-section">
          <div
            className={`dropzone ${dragActive ? "active" : ""}`}
            onDragOver={(e) => {
              e.preventDefault();
              setDragActive(true);
            }}
            onDragLeave={() => setDragActive(false)}
            onDrop={handleDrop}
            onClick={() => document.getElementById("file-input").click()}
          >
            <div className="dropzone-icon">📷</div>
            <p className="dropzone-text">
              Drop images here or <span className="link">browse</span>
            </p>
            <p className="dropzone-hint">
              JPEG, PNG, or WebP &middot; up to 20 images
            </p>
            <input
              id="file-input"
              type="file"
              multiple
              accept="image/jpeg,image/png,image/webp"
              hidden
              onChange={(e) => handleFiles(e.target.files)}
            />
          </div>

          {previews.length > 0 && (
            <div className="preview-grid">
              {previews.map((src, i) => (
                <div key={i} className="preview-card">
                  <img src={src} alt={`Upload ${i + 1}`} />
                  <button
                    className="remove-btn"
                    onClick={(e) => {
                      e.stopPropagation();
                      removeFile(i);
                    }}
                  >
                    ×
                  </button>
                  <span className="preview-badge">{i + 1}</span>
                </div>
              ))}
            </div>
          )}

          {files.length > 0 && (
            <div className="actions">
              <span className="file-count">
                {files.length} / 20 image{files.length !== 1 ? "s" : ""}
              </span>
              <button className="btn secondary" onClick={reset}>
                Clear
              </button>
              <button
                className="btn primary"
                onClick={analyze}
                disabled={loading}
              >
                {loading ? <span className="spinner" /> : "Analyze"}
              </button>
            </div>
          )}

          {loading && (
            <div className="loading-overlay">
              <div className="loading-card">
                <span className="spinner large" />
                <p>Analyzing your fridge...</p>
                <p className="loading-hint">This may take a moment</p>
              </div>
            </div>
          )}

          {error && <div className="error-banner">{error}</div>}
        </main>
      ) : (
        <main className="results-section">
          <button className="btn secondary back-btn" onClick={reset}>
            ← New Analysis
          </button>

          <section className="card ingredients-card">
            <h2>🥬 Ingredients Found</h2>
            <div className="ingredient-tags">
              {result.ingredients.map((ing, i) => (
                <span key={i} className="tag">
                  {ing.name}
                </span>
              ))}
            </div>
          </section>

          <section className="recipes-grid">
            {result.recipes.map((recipe, i) => (
              <div key={i} className="card recipe-card">
                <h3>
                  <span className="recipe-num">#{i + 1}</span> {recipe.name}
                </h3>
                <div className="recipe-ingredients">
                  <h4>Ingredients</h4>
                  <ul>
                    {recipe.ingredients.map((ing, j) => (
                      <li key={j}>{ing}</li>
                    ))}
                  </ul>
                </div>
                <div className="recipe-steps">
                  <h4>Instructions</h4>
                  <ol>
                    {recipe.instructions.map((step, j) => (
                      <li key={j}>{step}</li>
                    ))}
                  </ol>
                </div>
              </div>
            ))}
          </section>

          {result.shopping_list.length > 0 && (
            <section className="card shopping-card">
              <h2>🛒 Shopping List</h2>
              <ul className="shopping-list">
                {result.shopping_list.map((item, i) => (
                  <li key={i}>{item}</li>
                ))}
              </ul>
            </section>
          )}
        </main>
      )}
    </div>
  );
}

export default App;
