import React, { useState } from 'react';
import api from '../utils/api';

export default function DmPanel({ pendingInvites, onAcceptInvite, onDmCreated, onRefreshInvites }) {
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [dmLoading, setDmLoading] = useState(null);

  const handleSearch = async (e) => {
    e.preventDefault();
    if (searchQuery.trim().length < 2) return;
    setSearching(true);
    try {
      const res = await api.get(`/users/search/?q=${encodeURIComponent(searchQuery.trim())}`);
      setSearchResults(res.data);
    } catch {}
    finally { setSearching(false); }
  };

  const handleStartDm = async (username) => {
    setDmLoading(username);
    try {
      const res = await api.post('/dm/create/', { username });
      onDmCreated(res.data);
    } catch (err) {
      alert(err.response?.data?.error || 'DM aanmaken mislukt.');
    } finally {
      setDmLoading(null);
    }
  };

  function getInitials(username) {
    return username.slice(0, 2).toUpperCase();
  }

  const COLORS = ['#5865f2','#3ba55c','#f0b232','#ed4245','#7289da','#00aff4'];
  function getColor(name) {
    let h = 0;
    for (let c of name) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
    return COLORS[Math.abs(h) % COLORS.length];
  }

  return (
    <div className="dm-panel">
      <div className="dm-topbar">
        <span style={{ fontSize:20 }}>💬</span>
        <h3>Privéberichten & Invites</h3>
      </div>

      <div className="dm-content">
        {/* User search for DMs */}
        <div className="dm-search-box">
          <h3>Nieuw privégesprek</h3>
          <p>Zoek een gebruiker op naam om een privégesprek te starten.</p>
          <form onSubmit={handleSearch} className="dm-search-input-wrapper">
            <input
              type="text"
              value={searchQuery}
              onChange={e => { setSearchQuery(e.target.value); setSearchResults([]); }}
              placeholder="Gebruikersnaam zoeken..."
              autoFocus
            />
            <button
              type="submit"
              style={{ padding:'10px 16px', background:'#5865f2', color:'white', borderRadius:4,
                fontWeight:600, fontSize:14, cursor:'pointer', border:'none', whiteSpace:'nowrap' }}
              disabled={searching || searchQuery.trim().length < 2}
            >
              {searching ? '...' : 'Zoeken'}
            </button>
          </form>

          {searchResults.length === 0 && searchQuery.length >= 2 && !searching && (
            <p style={{ color:'var(--text-muted)', fontSize:13, marginTop:12 }}>
              Geen gebruikers gevonden voor "{searchQuery}".
            </p>
          )}

          {searchResults.map(u => (
            <div
              key={u.id}
              className="user-result"
              onClick={() => handleStartDm(u.username)}
              title={`Privégesprek starten met ${u.username}`}
            >
              <div className="user-avatar-sm" style={{ background: getColor(u.username) }}>
                {getInitials(u.username)}
              </div>
              <div style={{ flex:1 }}>
                <div style={{ fontSize:15, fontWeight:600 }}>{u.username}</div>
                <div style={{ fontSize:12, color:'var(--text-muted)' }}>Klik om gesprek te starten</div>
              </div>
              {dmLoading === u.username ? (
                <span style={{ fontSize:12, color:'var(--text-muted)' }}>Laden...</span>
              ) : (
                <span style={{ fontSize:20 }}>→</span>
              )}
            </div>
          ))}
        </div>

        {/* Pending invites */}
        <div className="invite-section">
          <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:12 }}>
            <h3>
              Openstaande uitnodigingen
              {pendingInvites.length > 0 && (
                <span style={{ marginLeft:8, background:'#da373c', color:'white',
                  borderRadius:10, padding:'2px 7px', fontSize:11, fontWeight:700 }}>
                  {pendingInvites.length}
                </span>
              )}
            </h3>
            <button
              onClick={onRefreshInvites}
              style={{ background:'none', color:'var(--text-muted)', fontSize:18,
                cursor:'pointer', border:'none', padding:4 }}
              title="Vernieuwen"
            >
              ↻
            </button>
          </div>

          {pendingInvites.length === 0 && (
            <div style={{ textAlign:'center', padding:24, color:'var(--text-muted)', fontSize:14,
              background:'var(--bg-secondary)', borderRadius:8 }}>
              <div style={{ fontSize:32, marginBottom:8 }}>📭</div>
              Geen openstaande uitnodigingen
            </div>
          )}

          {pendingInvites.map(invite => (
            <div key={invite.id} className="invite-card">
              <div className="invite-card-info">
                <h4>{invite.server?.name}</h4>
                <p>Uitgenodigd door <strong>{invite.created_by?.username}</strong></p>
              </div>
              <button
                className="btn-accept"
                onClick={() => onAcceptInvite(invite.code)}
              >
                ✓ Accepteren
              </button>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
