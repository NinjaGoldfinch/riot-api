# Riot API

FastAPI service for fetching League of Legends data through the Riot Games API with
[Pulsefire](https://pulsefire.ianhco.dev/).

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env
```

Add your Riot development key to `.env`.

## Run

```bash
uvicorn app.main:app --reload
```

Open:

- API docs: <http://127.0.0.1:8000/docs>
- Health check: <http://127.0.0.1:8000/health>

## Initial Endpoints

- `GET /health`
- `GET /api/v1/account/{region}/{game_name}/{tag_line}`
- `GET /api/v1/summoner/{platform}/{puuid}`
- `GET /api/v1/ranked/{platform}/{summoner_id}`
- `GET /api/v1/matches/{region}/{puuid}`
- `GET /api/v1/matches/{region}/detail/{match_id}`

The Riot-backed endpoints are scaffolded through a thin internal client wrapper so route and
service code do not depend directly on Pulsefire.
