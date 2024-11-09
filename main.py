from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
import httpx
import os
from dotenv import load_dotenv
from fastapi.responses import JSONResponse

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Real-Time Sports Analytics Platform",
    description="An API for ingesting, querying, and fetching volleyball data",
    version="1.1.0"
)

# In-memory storage for player stats (replace with DB later)
stats_data: Dict[int, "PlayerStats"] = {}

# Base URL for API-Sports Volleyball API
BASE_URL = "https://api-volleyball.p.rapidapi.com"
API_KEY = os.getenv("API_SPORTS_KEY")
HEADERS = {"x-rapidapi-key": API_KEY, 'x-rapidapi-host': "api-volleyball.p.rapidapi.com"}

# Models
class PlayerStats(BaseModel):
    player_id: int
    name: str
    team: str
    spikes: int
    blocks: int
    digs: int
    errors: int

class League(BaseModel):
    id: int
    name: str
    country: str

@app.get("/rtsa")
async def root():
    return {"message": "Welcome to the Real-Time Sports Analytics API!"}

# Add player stats
@app.post("/stats/", response_model=PlayerStats)
async def add_player_stats(stats: PlayerStats):
    if stats.player_id in stats_data:
        raise HTTPException(status_code=400, detail="Player stats already exist.")
    stats_data[stats.player_id] = stats
    return stats

# Get stats for a specific player
@app.get("/stats/{player_id}", response_model=PlayerStats)
async def get_player_stats(player_id: int):
    if player_id not in stats_data:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    return stats_data[player_id]

# Get stats for all players
@app.get("/stats/", response_model=List[PlayerStats])
async def get_all_stats():
    return list(stats_data.values())

# Update player stats
@app.put("/stats/{player_id}", response_model=PlayerStats)
async def update_player_stats(player_id: int, updated_stats: PlayerStats):
    if player_id not in stats_data:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    stats_data[player_id] = updated_stats
    return updated_stats

# Delete player stats
@app.delete("/stats/{player_id}")
async def delete_player_stats(player_id: int):
    if player_id not in stats_data:
        raise HTTPException(status_code=404, detail="Player stats not found.")
    del stats_data[player_id]
    return {"message": f"Player stats for ID {player_id} have been deleted."}

# Fetch volleyball leagues from API-Sports-Volleyball
@app.get("/leagues/", response_model=List[League])
async def get_volleyball_leagues():
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{BASE_URL}/leagues", headers=HEADERS)

            # Check for a successful response
            if response.status_code != 200:
                raise HTTPException(
                    status_code=response.status_code,
                    detail=f"Error fetching leagues: {response.text}"
                )

            # Parse the JSON response
            leagues_data = response.json().get("response", [])
            print("Extracted Leagues Data:", leagues_data)  # Debugging

            # Transform the data into the desired format
            transformed_leagues = [
                {
                    "id": league["id"],
                    "name": league["name"],
                    "type": league["type"],
                    "country": league["country"]["name"],
                    "logo": league["logo"],
                    "flag": league["country"]["flag"],
                }
                for league in leagues_data
            ]

            # Return a pretty-printed JSON response
            return JSONResponse(content=transformed_leagues, media_type="application/json")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {str(e)}")


# TODO: Change Volleyball-API to sportsdevs Volleyball API
# TODO: reduce scope of platform to follow only Brazilian and Italian Men's Volleyball SuperLega/Liga
# TODO: related to above  - come up with scaleable way to add more leagues if necessary (something involving airflow here..)


# reminder jeff: every time you make changes to your FastAPI app, rebuild the Docker image:

# docker build -t fastapi-app .
# Then, stop and remove the old container, and run a new one:

# docker stop <container-id>
# docker rm <container-id>
# docker run -p 8000:80 fastapi-app
