import React, { useState, useEffect } from 'react'

const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export default function App(){
  const [apiKey, setApiKey] = useState(localStorage.getItem('apiKey')||'changeme')
  const [teams, setTeams] = useState([])
  const [players, setPlayers] = useState([])
  const [games, setGames] = useState([])
  const [selectedGame, setSelectedGame] = useState(null)
  const [screenshotFile, setScreenshotFile] = useState(null)

  useEffect(()=>{ fetchAll() }, [])

  async function fetchAll(){
    try{
      const t = await fetch(`${API_BASE}/teams`).then(r=>r.json())
      setTeams(t)
      const p = await fetch(`${API_BASE}/players`).then(r=>r.json())
      setPlayers(p)
      const g = await fetch(`${API_BASE}/games`).then(r=>r.json())
      setGames(g)
    }catch(e){console.error(e)}
  }

  function authHeaders(){ return { 'X-API-Key': apiKey, 'Content-Type': 'application/json' } }

  async function createTeam(e){
    e.preventDefault()
    const name = e.target.name.value, short = e.target.short.value
    await fetch(`${API_BASE}/teams`, { method:'POST', headers: authHeaders(), body: JSON.stringify({name, short}) })
    await fetchAll()
  }

  async function createPlayer(e){
    e.preventDefault()
    const handle=e.target.handle.value, pos=e.target.position.value, num=+e.target.number.value, team_id=+e.target.team_id.value
    await fetch(`${API_BASE}/players`, { method:'POST', headers: authHeaders(), body: JSON.stringify({handle,pos,number:num,team_id}) })
    await fetchAll()
  }

  async function createGame(e){
    e.preventDefault()
    const date=e.target.date.value, home=+e.target.home.value, away=+e.target.away.value, round=e.target.round.value
    await fetch(`${API_BASE}/games`, { method:'POST', headers: authHeaders(), body: JSON.stringify({date,home_team_id:home,away_team_id:away,round}) })
    await fetchAll()
  }

  async function uploadScreenshot(){
    if(!selectedGame || !screenshotFile) return alert('Select game and file')
    const fd = new FormData(); fd.append('file', screenshotFile)
    const res = await fetch(`${API_BASE}/games/${selectedGame}/screenshot`, { method:'POST', headers: {'X-API-Key': apiKey}, body: fd })
    const j = await res.json(); alert('Uploaded: '+j.path)
    await fetchAll()
  }

  async function enterSkaterStat(e){
    e.preventDefault()
    const game_id = +e.target.game_id.value
    const player_id = +e.target.player_id.value
    const body = { goals:+e.target.goals.value, assists:+e.target.assists.value, shots:+e.target.shots.value, plus_minus:+e.target.plus_minus.value, hits:+e.target.hits.value, blocked:+e.target.blocked.value, pim:+e.target.pim.value, toi_seconds:+e.target.toi_seconds.value }
    await fetch(`${API_BASE}/games/${game_id}/players/${player_id}/skater`, { method:'POST', headers: {'X-API-Key': apiKey, 'Content-Type':'application/json'}, body: JSON.stringify(body) })
    alert('Saved')
  }

  return (
    <div style={{fontFamily:'Arial', padding:20}}>
      <h1>NHL26 League Admin</h1>
      <div style={{display:'flex', gap:20}}>
        <div style={{flex:1}}>
          <h2>Auth</h2>
          <input value={apiKey} onChange={e=>{setApiKey(e.target.value); localStorage.setItem('apiKey', e.target.value)}} />

          <h2>Create Team</h2>
          <form onSubmit={createTeam}><input name='name' placeholder='Team Name'/> <input name='short' placeholder='Short'/> <button>Create</button></form>

          <h2>Create Player</h2>
          <form onSubmit={createPlayer}>
            <input name='handle' placeholder='@handle'/> <input name='position' placeholder='F/D/G'/> <input name='number' placeholder='99'/> 
            <select name='team_id'>{teams.map(t=> <option key={t.id} value={t.id}>{t.name}</option>)}</select>
            <button>Create</button>
          </form>

          <h2>Create Game</h2>
          <form onSubmit={createGame}><input name='date' placeholder='2025-08-31T20:00:00'/> <select name='home'>{teams.map(t=> <option key={t.id} value={t.id}>{t.name}</option>)}</select> <select name='away'>{teams.map(t=> <option key={t.id} value={t.id}>{t.name}</option>)}</select> <input name='round' placeholder='Round'/><button>Create</button></form>

          <h2>Games</h2>
          <select onChange={e=>setSelectedGame(e.target.value)}>
            <option value=''>Select game</option>
            {games.map(g=> <option key={g.id} value={g.id}>{g.id} - {g.round || ''} - {g.home_team_id} vs {g.away_team_id}</option>)}
          </select>

          <h3>Upload Screenshot</h3>
          <input type='file' onChange={e=>setScreenshotFile(e.target.files[0])} />
          <button onClick={uploadScreenshot}>Upload Screenshot</button>

        </div>

        <div style={{flex:1}}>
          <h2>Enter Skater Stat</h2>
          <form onSubmit={enterSkaterStat}>
            <input name='game_id' placeholder='Game ID'/> <input name='player_id' placeholder='Player ID'/> <input name='goals' placeholder='Goals'/> <input name='assists' placeholder='Assists'/> <input name='shots' placeholder='Shots'/> <input name='plus_minus' placeholder='+/-'/> <input name='hits' placeholder='Hits'/> <input name='blocked' placeholder='Blocked'/> <input name='pim' placeholder='PIM'/> <input name='toi_seconds' placeholder='TOI (sec)'/> <button>Save Skater</button>
          </form>

          <h2>Quick Leaders</h2>
          <button onClick={async ()=>{ const d = await fetch(`${API_BASE}/leaders/goals`).then(r=>r.json()); alert(JSON.stringify(d.slice(0,5),null,2))}}>Top Goals</button>
          <button onClick={async ()=>{ const d = await fetch(`${API_BASE}/leaders/points`).then(r=>r.json()); alert(JSON.stringify(d.slice(0,5),null,2))}}>Top Points</button>

          <h2>Standings</h2>
          <button onClick={async ()=>{ const d = await fetch(`${API_BASE}/standings`).then(r=>r.json()); alert(JSON.stringify(d,null,2))}}>Show Standings</button>

          <h2>Awards</h2>
          <button onClick={async ()=>{ const d = await fetch(`${API_BASE}/awards/mvp`).then(r=>r.json()); alert(JSON.stringify(d,null,2))}}>MVP</button>
          <button onClick={async ()=>{ const d = await fetch(`${API_BASE}/awards/vezina`).then(r=>r.json()); alert(JSON.stringify(d,null,2))}}>Vezina</button>
        </div>
      </div>

    </div>
  )
}