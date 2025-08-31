from __future__ import annotations
import os
from datetime import datetime
from typing import Optional, List
from fastapi import FastAPI, Depends, HTTPException, Header, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlmodel import SQLModel, Field as SQLField, Session, create_engine, select, Relationship
import aiofiles

ADMIN_API_KEY = os.getenv("ADMIN_API_KEY", "changeme")
DB_URL = os.getenv("DATABASE_URL", "sqlite:///./stats.db")
UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

engine = create_engine(DB_URL, echo=False)
app = FastAPI(title="NHL26 Stats API")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")

class Team(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    name: str
    short: str
    players: List["Player"] = Relationship(back_populates="team")
    team_stats: List["TeamStat"] = Relationship(back_populates="team")

class Player(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    handle: str
    position: str
    number: Optional[int] = None
    team_id: Optional[int] = SQLField(foreign_key="team.id")
    skater_stats: List["SkaterStat"] = Relationship(back_populates="player")
    goalie_stats: List["GoalieStat"] = Relationship(back_populates="player")

class Game(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    date: datetime
    home_team_id: int = SQLField(foreign_key="team.id")
    away_team_id: int = SQLField(foreign_key="team.id")
    home_score: int = 0
    away_score: int = 0
    round: Optional[str] = None
    screenshot_path: Optional[str] = None

class SkaterStat(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    game_id: int = SQLField(foreign_key="game.id")
    player_id: int = SQLField(foreign_key="player.id")
    goals: int = 0
    assists: int = 0
    shots: int = 0
    ppg: int = 0
    ppa: int = 0
    shg: int = 0
    sha: int = 0
    gwg: int = 0
    otg: int = 0
    plus_minus: int = 0
    hits: int = 0
    blocked: int = 0
    giveaways: int = 0
    takeaways: int = 0
    faceoff_wins: int = 0
    faceoff_losses: int = 0
    toi_seconds: int = 0
    pp_toi_seconds: int = 0
    pk_toi_seconds: int = 0
    pim: int = 0
    majors: int = 0
    misconducts: int = 0
    player: Optional[Player] = Relationship(back_populates="skater_stats")

class GoalieStat(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    game_id: int = SQLField(foreign_key="game.id")
    player_id: int = SQLField(foreign_key="player.id")
    gp: int = 0
    wins: int = 0
    losses: int = 0
    ot: int = 0
    shots_against: int = 0
    saves: int = 0
    goals_against: int = 0
    shutout: int = 0
    toi_seconds: int = 0
    player: Optional[Player] = Relationship(back_populates="goalie_stats")

class TeamStat(SQLModel, table=True):
    id: Optional[int] = SQLField(default=None, primary_key=True)
    game_id: int = SQLField(foreign_key="game.id")
    team_id: int = SQLField(foreign_key="team.id")
    goals: int = 0
    shots: int = 0
    pp_goals: int = 0
    pp_attempts: int = 0
    pk_goals_against: int = 0
    pk_attempts_against: int = 0
    faceoff_wins: int = 0
    faceoff_losses: int = 0
    saves: int = 0
    shots_against: int = 0
    team: Optional[Team] = Relationship(back_populates="team_stats")

class TeamIn(BaseModel):
    name: str
    short: str

class PlayerIn(BaseModel):
    handle: str
    position: str
    number: Optional[int] = None
    team_id: Optional[int] = None

class GameIn(BaseModel):
    date: datetime
    home_team_id: int
    away_team_id: int
    round: Optional[str] = None

class SkaterStatIn(BaseModel):
    goals: int = 0
    assists: int = 0
    shots: int = 0
    ppg: int = 0
    ppa: int = 0
    shg: int = 0
    sha: int = 0
    gwg: int = 0
    otg: int = 0
    plus_minus: int = 0
    hits: int = 0
    blocked: int = 0
    giveaways: int = 0
    takeaways: int = 0
    faceoff_wins: int = 0
    faceoff_losses: int = 0
    toi_seconds: int = 0
    pp_toi_seconds: int = 0
    pk_toi_seconds: int = 0
    pim: int = 0
    majors: int = 0
    misconducts: int = 0

class GoalieStatIn(BaseModel):
    gp: int = 1
    wins: int = 0
    losses: int = 0
    ot: int = 0
    shots_against: int = 0
    saves: int = 0
    goals_against: int = 0
    shutout: int = 0
    toi_seconds: int = 0

class TeamStatIn(BaseModel):
    goals: int = 0
    shots: int = 0
    pp_goals: int = 0
    pp_attempts: int = 0
    pk_goals_against: int = 0
    pk_attempts_against: int = 0
    faceoff_wins: int = 0
    faceoff_losses: int = 0
    saves: int = 0
    shots_against: int = 0

@app.on_event("startup")
def on_startup():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def require_api_key(x_api_key: str = Header(..., alias="X-API-Key")):
    if x_api_key != ADMIN_API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")

@app.post("/teams", dependencies=[Depends(require_api_key)])
def create_team(payload: TeamIn, session: Session = Depends(get_session)):
    t = Team(name=payload.name, short=payload.short)
    session.add(t); session.commit(); session.refresh(t)
    return t

@app.get("/teams")
def list_teams(session: Session = Depends(get_session)):
    return session.exec(select(Team)).all()

@app.post("/players", dependencies=[Depends(require_api_key)])
def create_player(payload: PlayerIn, session: Session = Depends(get_session)):
    if payload.team_id and not session.get(Team, payload.team_id):
        raise HTTPException(404, "Team not found")
    p = Player(handle=payload.handle, position=payload.position, number=payload.number, team_id=payload.team_id)
    session.add(p); session.commit(); session.refresh(p)
    return p

@app.get("/players")
def list_players(team_id: Optional[int] = None, session: Session = Depends(get_session)):
    q = select(Player)
    if team_id:
        q = q.where(Player.team_id == team_id)
    return session.exec(q).all()

@app.post("/games", dependencies=[Depends(require_api_key)])
def create_game(payload: GameIn, session: Session = Depends(get_session)):
    for tid in (payload.home_team_id, payload.away_team_id):
        if not session.get(Team, tid):
            raise HTTPException(404, f"Team {tid} not found")
    g = Game(date=payload.date, home_team_id=payload.home_team_id, away_team_id=payload.away_team_id, round=payload.round)
    session.add(g); session.commit(); session.refresh(g)
    return g

@app.get("/games")
def list_games(session: Session = Depends(get_session)):
    return session.exec(select(Game)).all()

@app.post("/games/{game_id}/players/{player_id}/skater", dependencies=[Depends(require_api_key)])
def enter_skater_stat(game_id: int, player_id: int, payload: SkaterStatIn, session: Session = Depends(get_session)):
    if not session.get(Game, game_id):
        raise HTTPException(404, "Game not found")
    if not session.get(Player, player_id):
        raise HTTPException(404, "Player not found")
    stat = SkaterStat(game_id=game_id, player_id=player_id, **payload.model_dump())
    session.add(stat); session.commit(); session.refresh(stat)
    return stat

@app.post("/games/{game_id}/players/{player_id}/goalie", dependencies=[Depends(require_api_key)])
def enter_goalie_stat(game_id: int, player_id: int, payload: GoalieStatIn, session: Session = Depends(get_session)):
    if not session.get(Game, game_id):
        raise HTTPException(404, "Game not found")
    if not session.get(Player, player_id):
        raise HTTPException(404, "Player not found")
    stat = GoalieStat(game_id=game_id, player_id=player_id, **payload.model_dump())
    session.add(stat); session.commit(); session.refresh(stat)
    return stat

@app.post("/games/{game_id}/teamstats", dependencies=[Depends(require_api_key)])
def enter_team_stats(game_id: int, payload: TeamStatIn, team_id: int, session: Session = Depends(get_session)):
    if not session.get(Game, game_id):
        raise HTTPException(404, "Game not found")
    if not session.get(Team, team_id):
        raise HTTPException(404, "Team not found")
    ts = TeamStat(game_id=game_id, team_id=team_id, **payload.model_dump())
    session.add(ts); session.commit(); session.refresh(ts)
    return ts

@app.post("/games/{game_id}/screenshot", dependencies=[Depends(require_api_key)])
async def upload_screenshot(game_id: int, file: UploadFile = File(...), session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")
    ext = os.path.splitext(file.filename)[1]
    fname = f"game_{game_id}_{int(datetime.utcnow().timestamp())}{ext}"
    path = os.path.join(UPLOAD_DIR, fname)
    async with aiofiles.open(path, 'wb') as out_file:
        content = await file.read()
        await out_file.write(content)
    game.screenshot_path = f"/uploads/{fname}"
    session.add(game); session.commit(); session.refresh(game)
    return {"path": game.screenshot_path}

@app.get("/games/{game_id}/boxscore")
def boxscore(game_id: int, session: Session = Depends(get_session)):
    game = session.get(Game, game_id)
    if not game:
        raise HTTPException(404, "Game not found")
    skaters = session.exec(select(SkaterStat).where(SkaterStat.game_id == game_id)).all()
    goalies = session.exec(select(GoalieStat).where(GoalieStat.game_id == game_id)).all()
    return {"game": game, "skaters": skaters, "goalies": goalies}

def aggregate_player_totals(session: Session):
    players = session.exec(select(Player)).all()
    totals = {}
    for p in players:
        sk = session.exec(select(SkaterStat).where(SkaterStat.player_id == p.id)).all()
        gl = session.exec(select(GoalieStat).where(GoalieStat.player_id == p.id)).all()
        s = {
            "player": p.handle,
            "team_id": p.team_id,
            "goals": sum(x.goals for x in sk),
            "assists": sum(x.assists for x in sk),
            "points": sum(x.goals + x.assists for x in sk),
            "shots": sum(x.shots for x in sk),
            "hits": sum(x.hits for x in sk),
            "blocked": sum(x.blocked for x in sk),
            "pim": sum(x.pim for x in sk),
            "toi_seconds": sum(x.toi_seconds for x in sk)
        }
        g = {
            "gp": sum(x.gp for x in gl),
            "wins": sum(x.wins for x in gl),
            "losses": sum(x.losses for x in gl),
            "shots_against": sum(x.shots_against for x in gl),
            "saves": sum(x.saves for x in gl),
            "goals_against": sum(x.goals_against for x in gl),
            "toi_seconds": sum(x.toi_seconds for x in gl)
        }
        totals[p.id] = {**s, **{"goalie": g}}
    return totals

@app.get("/leaders/{stat}")
def leaders(stat: str, limit: int = 20, session: Session = Depends(get_session)):
    totals = aggregate_player_totals(session)
    arr = []
    for pid, t in totals.items():
        arr.append(t)
    if stat == "goals":
        arr.sort(key=lambda x: x["goals"], reverse=True)
    elif stat == "points":
        arr.sort(key=lambda x: x["points"], reverse=True)
    elif stat == "shots":
        arr.sort(key=lambda x: x["shots"], reverse=True)
    elif stat == "savepct":
        arr = [x for x in arr if x["goalie"]["shots_against"]>0]
        for x in arr:
            ga = x["goalie"]["goals_against"]
            sa = x["goalie"]["saves"]
            sa_total = sa + ga
            x["savepct"] = sa / sa_total if sa_total>0 else 0
        arr.sort(key=lambda x: x.get("savepct",0), reverse=True)
    else:
        raise HTTPException(400, "Unknown stat")
    return arr[:limit]

@app.get("/standings")
def standings(session: Session = Depends(get_session)):
    teams = session.exec(select(Team)).all()
    standings = []
    for t in teams:
        team_stats = session.exec(select(TeamStat).where(TeamStat.team_id == t.id)).all()
        gf = sum(ts.goals for ts in team_stats)
        ga = sum(ts.shots_against for ts in team_stats) if team_stats else 0
        wins=losses=ot=0
        for g in session.exec(select(Game)).all():
            if g.home_team_id==t.id or g.away_team_id==t.id:
                if g.home_score is None or g.away_score is None:
                    continue
                if g.home_score==g.away_score:
                    ot += 1
                else:
                    is_win = (g.home_team_id==t.id and g.home_score>g.away_score) or (g.away_team_id==t.id and g.away_score>g.home_score)
                    if is_win:
                        wins += 1
                    else:
                        losses += 1
        standings.append({"team": t.name, "team_id": t.id, "wins": wins, "losses": losses, "ot": ot, "gf": gf, "ga": ga})
    standings.sort(key=lambda x: (x["wins"]*2 + x["ot"]), reverse=True)
    return standings

@app.get("/awards/mvp")
def award_mvp(session: Session = Depends(get_session)):
    totals = aggregate_player_totals(session)
    arr = list(totals.values())
    arr.sort(key=lambda x: x["points"], reverse=True)
    return arr[0] if arr else {}

@app.get("/awards/vezina")
def award_vezina(session: Session = Depends(get_session)):
    totals = aggregate_player_totals(session)
    candidates = []
    for t in totals.values():
        g = t["goalie"]
        sa = g["shots_against"]
        if sa>0 and g["gp"]>0:
            savepct = g["saves"] / (g["saves"]+g["goals_against"]) if (g["saves"]+g["goals_against"])>0 else 0
            candidates.append({"player": t["player"], "team_id": t["team_id"], "savepct": savepct, "wins": g["wins"]})
    candidates.sort(key=lambda x: (x["savepct"], x["wins"]), reverse=True)
    return candidates[0] if candidates else {}

@app.get("/awards/norris")
def award_norris(session: Session = Depends(get_session)):
    totals = aggregate_player_totals(session)
    arr = [t for t in totals.values()]
    arr.sort(key=lambda x: (x.get("points",0), x.get("plus_minus",0)), reverse=True)
    return arr[0] if arr else {}

@app.get("/awards/calder")
def award_calder(session: Session = Depends(get_session)):
    totals = aggregate_player_totals(session)
    arr = list(totals.values())
    arr.sort(key=lambda x: x["points"], reverse=True)
    return arr[0] if arr else {}

@app.get("/health")
def health():
    return {"ok": True}
