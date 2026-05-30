import React, { useState } from 'react';
import api from '../../utils/api';

export default function InviteModal({ server, onClose }) {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [inviting, setInviting] = useState(null);
  const [successMsg, setSuccessMsg] = useState('');
  const [error, setError] = useState('');

  const handleSearch = async (e) => {
    e.preventDefault();
    if (query.trim().length < 2) return;
    setSearching(true);
    setResults([]);
    setError('');
    setSuccessMsg('');
    try {
      const res = await api.get(`/users/search/?q=${encodeURIComponent(query.trim())}`);
      setResults(res.data);
      if (res.data.length === 0) setError(`Geen gebruikers gevonden voor "${query}".`);
    } catch {
      setError('Zoeken mislukt.');
    } finally {
      setSearching(false);
    }
  };

  const handleInvite = async (username) => {
    setInviting(username);
    setError('');
    setSuccessMsg('');
    try {
      await api.post(`/servers/${server.id}/invite/`, { username });
      setSuccessMsg(`✓ Uitnodiging verstuurd naar ${username}! Ze zien de invite in hun DM-paneel.`);
      setResults([]);
      setQuery('');
    } catch (err) {
      setError(err.response?.data?.error || 'Uitnodigen mislukt.');
    } finally {
      setInviting(null);
    }
  };

  const COLORS = ['#5865f2','#3ba55c','#f0b232','#ed4245','#7289da','#00aff4'];
  function getColor(name) {
    let h = 0;
    for (let c of name) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
    return COLORS[Math.abs(h) % COLORS.length];
  }

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>Gebruiker uitnodigen</h2>
        <p>Nodig iemand uit voor <strong style={{ color:'var(--text-primary)' }}>{server.name}</strong>. Ze ontvangen de invite in hun DM-paneel.</p>

        {error && <div className="error-msg">{error}</div>}
        {successMsg && (
          <div style={{ background:'rgba(35,165,90,0.15)', border:'1px solid #23a55a',
            borderRadius:4, padding:'10px 12px', color:'#23a55a', fontSize:13, marginBottom:16 }}>
            {successMsg}
          </div>
        )}

        <form onSubmit={handleSearch}>
          <label style={{ fontSize:12, fontWeight:700, textTransform:'uppercase',
            letterSpacing:'0.5px', color:'var(--text-secondary)', display:'block', marginBottom:8 }}>
            Gebruikersnaam zoeken
          </label>
          <div style={{ display:'flex', gap:8 }}>
            <input
              className="modal-input"
              style={{ marginTop:0, flex:1 }}
              type="text"
              value={query}
              onChange={e => { setQuery(e.target.value); setResults([]); setError(''); setSuccessMsg(''); }}
              placeholder="Gebruikersnaam..."
              autoFocus
            />
            <button
              type="submit"
              className="btn-modal-confirm"
              disabled={searching || query.trim().length < 2}
              style={{ whiteSpace:'nowrap' }}
            >
              {searching ? '...' : 'Zoeken'}
            </button>
          </div>
        </form>

        {results.map(u => (
          <div key={u.id} style={{ display:'flex', alignItems:'center', gap:12,
            padding:'10px 12px', background:'var(--bg-input)', borderRadius:8, marginTop:12 }}>
            <div style={{ width:36, height:36, borderRadius:'50%', background:getColor(u.username),
              display:'flex', alignItems:'center', justifyContent:'center',
              fontSize:13, fontWeight:700, color:'white', flexShrink:0 }}>
              {u.username.slice(0,2).toUpperCase()}
            </div>
            <span style={{ flex:1, fontSize:15, fontWeight:600 }}>{u.username}</span>
            <button
              className="btn-modal-confirm"
              style={{ padding:'8px 14px', fontSize:13 }}
              onClick={() => handleInvite(u.username)}
              disabled={inviting === u.username}
            >
              {inviting === u.username ? 'Uitnodigen...' : 'Uitnodigen'}
            </button>
          </div>
        ))}

        <div className="modal-actions">
          <button className="btn-modal-cancel" onClick={onClose}>Sluiten</button>
        </div>
      </div>
    </div>
  );
}
