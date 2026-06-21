# SnapMeal

A full-stack recipe app that identifies ingredients from fridge photos and generates personalized recipes using a three-stage GPT-4o pipeline.

---

## What it does

1. **Upload** up to 20 fridge/pantry photos
2. **GPT-4o Vision** extracts every ingredient it can identify across all images
3. **GPT-4o** generates 3 personalized recipes with exact measurements, step-by-step instructions, and a shopping list for missing items — respecting your dietary preferences
4. **Refine** via a context-aware chat endpoint: remove ingredients, request a cuisine type, ask for substitutions, or regenerate recipes entirely

---

## Tech stack

| Layer      | Technology                              |
|------------|-----------------------------------------|
| Backend    | Python / FastAPI (async)                |
| Database   | PostgreSQL / SQLAlchemy                 |
| Auth       | JWT (7-day tokens) + bcrypt             |
| AI         | OpenAI GPT-4o (vision + chat)           |
| Frontend   | React / Vite / Tailwind CSS             |
| Storage    | Local filesystem (configurable)         |

---

## API overview

### Auth
| Method | Endpoint        | Description              |
|--------|-----------------|--------------------------|
| POST   | `/auth/register`| Register with email + password |
| POST   | `/auth/login`   | Login, receive JWT token |
| GET    | `/auth/me`      | Get current user info    |

### Core
| Method | Endpoint    | Description                                              |
|--------|-------------|----------------------------------------------------------|
| POST   | `/analyze`  | Upload images → get ingredients + recipes + shopping list |
| POST   | `/recipes`  | Regenerate recipes from an updated ingredient list       |
| POST   | `/chat`     | Refine recipes via conversation                          |

### User
| Method | Endpoint            | Description                        |
|--------|---------------------|------------------------------------|
| GET/POST/DELETE | `/preferences` | Manage dietary preferences    |
| GET/POST/DELETE | `/favorites`   | Save and retrieve favorite recipes |

---

## Local setup

**Prerequisites:** Python 3.11+, Node.js 18+, PostgreSQL

### Backend

```bash
git clone https://github.com/Cweiss15/SnapMeal.git
cd SnapMeal
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

Copy the environment file and fill in your values:

```bash
cp .env.example .env
```

Run the backend:

```bash
python main.py
# → http://localhost:8000
# → Docs at http://localhost:8000/docs
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# → http://localhost:5173
```

---

## Environment variables

| Variable        | Description                          |
|-----------------|--------------------------------------|
| `OPENAI_API_KEY`| OpenAI API key (GPT-4o access required) |
| `DATABASE_URL`  | PostgreSQL connection string         |
| `JWT_SECRET`    | Secret key for signing JWT tokens    |

---

## Project structure

```
SnapMeal/
├── app/
│   ├── main.py               # FastAPI app, middleware, router registration
│   ├── config.py             # Settings loaded from environment
│   ├── database.py           # SQLAlchemy engine and session
│   ├── models/
│   │   ├── user.py           # User model
│   │   ├── image.py          # Uploaded image tracking
│   │   ├── recipe.py         # Saved/favorite recipes
│   │   └── food_preference.py# User dietary preferences
│   ├── routers/
│   │   ├── upload.py         # /analyze, /recipes, /chat endpoints
│   │   ├── auth.py           # /auth/* endpoints
│   │   ├── preferences.py    # /preferences endpoints
│   │   └── favorites.py      # /favorites endpoints
│   ├── services/
│   │   ├── vision.py         # GPT-4o image analysis
│   │   ├── recipes.py        # GPT-4o recipe generation
│   │   ├── chat.py           # GPT-4o context-aware chat
│   │   └── auth.py           # JWT creation, bcrypt hashing
│   ├── schemas/              # Pydantic request/response models
│   └── storage/              # File upload handling
├── frontend/                 # React + Vite + Tailwind
├── main.py                   # Entrypoint (runs uvicorn)
└── requirements.txt
```
