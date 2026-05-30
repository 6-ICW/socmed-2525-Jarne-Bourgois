import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';

const COLORS = ['#5865f2','#3ba55c','#f0b232','#ed4245','#7289da','#00aff4','#eb459e','#faa61a'];

function getColor(name) {
  let h = 0;
  for (let c of name) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
  return COLORS[Math.abs(h) % COLORS.length];
}

function getInitials(username) {
  const p = username.split(/\s+/);
  return p.length >= 2 ? (p[0][0] + p[1][0]).toUpperCase() : username.slice(0, 2).toUpperCase();
}

function Avatar({ username, size = 40 }) {
  return (
    <div style={{
      width: size, height: size, borderRadius: '50%', background: getColor(username),
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: size * 0.35, fontWeight: 700, color: 'white', flexShrink: 0
    }}>
      {getInitials(username)}
    </div>
  );
}

export default function HomePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [tab, setTab] = useState('online'); // 'online' | 'all' | 'requests'
  const [friends, setFriends] = useState([]);
  const [friendRequests, setFriendRequests] = useState([]);
  const [addInput, setAddInput] = useState('');
  const [addLoading, setAddLoading] = useState(false);
  const [addMsg, setAddMsg] = useState(null); // {type: 'success'|'error', text}

  const fetchFriends = useCallback(async () => {
    try {
      const res = await api.get('/friends/');
      setFriends(res.data);
    } catch {}
  }, []);

  const fetchRequests = useCallback(async () => {
    try {
      const res = await api.get('/friends/requests/');
      setFriendRequests(res.data);
    } catch {}
  }, []);

  useEffect(() => {
    fetchFriends();
    fetchRequests();
    // Heartbeat
    api.post('/auth/heartbeat/').catch(() => {});
    const interval = setInterval(() => {
      fetchFriends();
      fetchRequests();
    }, 30000);
    return () => clearInterval(interval);
  }, [fetchFriends, fetchRequests]);

  const handleAddFriend = async (e) => {
    e.preventDefault();
    if (!addInput.trim()) return;
    setAddLoading(true);
    setAddMsg(null);
    try {
      await api.post('/friends/add/', { username: addInput.trim() });
      setAddMsg({ type: 'success', text: `Vriendschapsverzoek verstuurd naar ${addInput.trim()}!` });
      setAddInput('');
    } catch (err) {
      setAddMsg({ type: 'error', text: err.response?.data?.error || 'Toevoegen mislukt.' });
    } finally {
      setAddLoading(false);
    }
  };

  const handleAcceptRequest = async (id) => {
    try {
      await api.post(`/friends/${id}/accept/`);
      setFriendRequests(prev => prev.filter(r => r.id !== id));
      fetchFriends();
    } catch {}
  };

  const handleDeclineRequest = async (id) => {
    try {
      await api.delete(`/friends/${id}/remove/`);
      setFriendRequests(prev => prev.filter(r => r.id !== id));
    } catch {}
  };

  const handleRemoveFriend = async (id) => {
    if (!window.confirm('Weet je zeker dat je deze vriend wilt verwijderen?')) return;
    try {
      await api.delete(`/friends/${id}/remove/`);
      setFriends(prev => prev.filter(f => f.friendship_id !== id));
    } catch {}
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  if (!user) return null;

  const onlineFriends = friends.filter(f => f.user.is_online);
  const displayedFriends = tab === 'online' ? onlineFriends : friends;

  return (
    <div className="home-page-v2">
      {/* Left panel: friends */}
      <div className="home-side">
        <div className="home-side-header">
          <h2>👥 Vrienden</h2>
          <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{friends.length} vrienden</span>
        </div>

        <div className="friends-tabs">
          <button
            className={`friends-tab${tab === 'online' ? ' active' : ''}`}
            onClick={() => setTab('online')}
          >
            Online
            {onlineFriends.length > 0 && (
              <span style={{ marginLeft: 6, background: '#23a55a', color: 'white',
                borderRadius: 10, padding: '1px 6px', fontSize: 10, fontWeight: 700 }}>
                {onlineFriends.length}
              </span>
            )}
          </button>
          <button
            className={`friends-tab${tab === 'all' ? ' active' : ''}`}
            onClick={() => setTab('all')}
          >
            Alle vrienden
          </button>
          <button
            className={`friends-tab${tab === 'requests' ? ' active' : ''}`}
            onClick={() => setTab('requests')}
          >
            Verzoeken
            {friendRequests.length > 0 && (
              <span className="tab-badge">{friendRequests.length}</span>
            )}
          </button>
        </div>

        <div className="friends-list">
          {tab === 'requests' ? (
            <>
              {friendRequests.length === 0 && (
                <div className="empty-friends">
                  <div className="empty-icon-sm">📭</div>
                  <p>Geen openstaande vriendschapsverzoeken.</p>
                </div>
              )}
              {friendRequests.map(req => (
                <div key={req.id} className="friend-request-item">
                  <div className="friend-avatar-wrap">
                    <Avatar username={req.from_user.username} size={40} />
                    <div className={`online-dot ${req.from_user.is_online ? 'online' : 'offline'}`} />
                  </div>
                  <div className="request-info">
                    <h4>{req.from_user.username}</h4>
                    <p>Wil je vriend zijn</p>
                  </div>
                  <div className="friend-request-actions">
                    <button className="btn-friend-accept" onClick={() => handleAcceptRequest(req.id)}>✓</button>
                    <button className="btn-friend-decline" onClick={() => handleDeclineRequest(req.id)}>✕</button>
                  </div>
                </div>
              ))}
            </>
          ) : (
            <>
              {displayedFriends.length === 0 && (
                <div className="empty-friends">
                  <div className="empty-icon-sm">{tab === 'online' ? '😴' : '👋'}</div>
                  <p>
                    {tab === 'online'
                      ? 'Geen vrienden zijn momenteel online.'
                      : 'Nog geen vrienden. Voeg iemand toe!'}
                  </p>
                </div>
              )}
              {displayedFriends.map(f => (
                <div key={f.friendship_id} className="friend-item">
                  <div className="friend-avatar-wrap">
                    <div className="friend-avatar" style={{ background: getColor(f.user.username) }}>
                      {getInitials(f.user.username)}
                    </div>
                    <div className={`online-dot ${f.user.is_online ? 'online' : 'offline'}`} />
                  </div>
                  <div className="friend-info">
                    <div className="friend-name">{f.user.username}</div>
                    <div className={`friend-status ${f.user.is_online ? 'online' : ''}`}>
                      {f.user.is_online ? '🟢 Online' : '⚫ Offline'}
                    </div>
                  </div>
                  <div className="friend-actions">
                    <button
                      className="friend-action-btn"
                      title="Vriend verwijderen"
                      onClick={() => handleRemoveFriend(f.friendship_id)}
                    >
                      ✕
                    </button>
                  </div>
                </div>
              ))}
            </>
          )}
        </div>

        {/* Add friend */}
        <div className="add-friend-form">
          {addMsg && (
            <div style={{
              padding: '8px 10px', marginBottom: 8, borderRadius: 4, fontSize: 12,
              background: addMsg.type === 'success' ? 'rgba(35,165,90,0.15)' : 'rgba(218,55,60,0.15)',
              color: addMsg.type === 'success' ? '#23a55a' : '#f38ba8',
              border: `1px solid ${addMsg.type === 'success' ? '#23a55a' : '#da373c'}`,
            }}>
              {addMsg.text}
            </div>
          )}
          <form onSubmit={handleAddFriend} className="input-row">
            <input
              value={addInput}
              onChange={e => { setAddInput(e.target.value); setAddMsg(null); }}
              placeholder="Vriend toevoegen op naam..."
            />
            <button type="submit" disabled={addLoading || !addInput.trim()}>
              {addLoading ? '...' : 'Toevoegen'}
            </button>
          </form>
        </div>
      </div>

      {/* Right: main welcome */}
      <div className="home-main">
        <div className="home-welcome-card">
          <div style={{
            width: 80, height: 80, borderRadius: '50%', background: getColor(user.username),
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 28, fontWeight: 700, color: 'white', margin: '0 auto 20px'
          }}>
            {getInitials(user.username)}
          </div>
          <h1>Hallo, {user.username}!</h1>
          <p>
            Welkom op je Discord clone.
            {friends.length > 0
              ? ` Je hebt ${onlineFriends.length} van ${friends.length} vrienden online.`
              : ' Voeg vrienden toe via het paneel links.'}
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12, marginTop: 8 }}>
            <button className="btn-primary" onClick={() => navigate('/servers')}>
              🚀 Ga naar Servers
            </button>
            <button className="btn-danger" onClick={handleLogout}>
              Uitloggen
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}