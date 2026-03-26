"""Team management routes."""

from ....core.src.database import db
from ....core.src.helpers import generate_id, timestamp_iso
from ....core.src.validators import validate_required


def register(router):
    """Register team routes."""
    router.add_route("GET", "/api/teams", list_teams)
    router.add_route("POST", "/api/teams", create_team)
    router.add_route("GET", "/api/teams/{team_id}", get_team)


def list_teams(request: dict) -> dict:
    """GET /api/teams — list all teams."""
    teams = db.get_all("teams")
    return {"status": 200, "data": teams, "count": len(teams)}


def create_team(request: dict) -> dict:
    """POST /api/teams — create a new team."""
    body = request.get("body", {})
    errors = validate_required(body, ["name"])
    if errors:
        return {"status": 400, "errors": errors}
    team = {
        "id": generate_id(),
        "name": body["name"],
        "description": body.get("description", ""),
        "created_at": timestamp_iso(),
    }
    db.insert("teams", team["id"], team)
    return {"status": 201, "data": team}


def get_team(request: dict) -> dict:
    """GET /api/teams/:id — get a single team."""
    team_id = request["params"]["team_id"]
    team = db.get("teams", team_id)
    if team is None:
        return {"status": 404, "error": "Team not found"}
    return {"status": 200, "data": team}
