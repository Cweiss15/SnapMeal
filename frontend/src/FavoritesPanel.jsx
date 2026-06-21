import { useState, useEffect } from "react";
import { apiFetch } from "./api";

export default function FavoritesPanel({ open, onClose }) {
  const [favorites, setFavorites] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (open) loadFavorites();
  }, [open]);

  const loadFavorites = async () => {
    setLoading(true);
    try {
      const res = await apiFetch("/favorites/");
      if (res.ok) setFavorites(await res.json());
    } catch {}
    setLoading(false);
  };

  const deleteFavorite = async (id) => {
    try {
      await apiFetch(`/favorites/${id}`, { method: "DELETE" });
      setFavorites((prev) => prev.filter((f) => f.id !== id));
    } catch {}
  };

  if (!open) return null;

  return (
    <div className="panel-overlay" onClick={onClose}>
      <div className="panel-content wide" onClick={(e) => e.stopPropagation()}>
        <div className="panel-header">
          <h2>❤️ Favorite Recipes</h2>
          <button className="chat-close" onClick={onClose}>✕</button>
        </div>

        {loading && <div className="panel-loading"><span className="spinner" /></div>}

        {!loading && favorites.length === 0 && (
          <p className="pref-empty">No favorites yet. Save recipes you like from the results!</p>
        )}

        <div className="favorites-grid">
          {favorites.map((recipe) => (
            <div key={recipe.id} className="card recipe-card">
              <div className="fav-card-header">
                <h3>{recipe.name}</h3>
                <button className="remove-btn" onClick={() => deleteFavorite(recipe.id)} title="Remove">×</button>
              </div>
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
        </div>
      </div>
    </div>
  );
}
