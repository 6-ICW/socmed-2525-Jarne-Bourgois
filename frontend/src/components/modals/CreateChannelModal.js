import React, { useState } from 'react';

export default function CreateChannelModal({ serverName, onClose, onCreate }) {
  const [name, setName] = useState('');
  const [channelType, setChannelType] = useState('text');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Geef het kanaal een naam.'); return; }
    setLoading(true);
    try {
      await onCreate(name.trim().toLowerCase().replace(/\s+/g, '-'), channelType);
    } catch (err) {
      setError(err.response?.data?.error || 'Kanaal aanmaken mislukt.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>Kanaal aanmaken</h2>
        <p>In <strong style={{ color:'var(--text-primary)' }}>{serverName}</strong></p>
        {error && <div className="error-msg">{error}</div>}

        <div style={{ marginBottom:16 }}>
          <label style={{ fontSize:12, fontWeight:700, textTransform:'uppercase',
            letterSpacing:'0.5px', color:'var(--text-secondary)', display:'block', marginBottom:8 }}>
            Kanaaltype
          </label>
          <div className="channel-type-select">
            <div
              className={`type-option${channelType === 'text' ? ' selected' : ''}`}
              onClick={() => setChannelType('text')}
            >
              <div className="type-icon">#</div>
              <div style={{ fontWeight:600 }}>Tekst</div>
              <div style={{ fontSize:12, color:'var(--text-muted)', marginTop:2 }}>Berichten sturen</div>
            </div>
            <div
              className={`type-option${channelType === 'voice' ? ' selected' : ''}`}
              onClick={() => setChannelType('voice')}
            >
              <div className="type-icon">🔊</div>
              <div style={{ fontWeight:600 }}>Spraak</div>
              <div style={{ fontSize:12, color:'var(--text-muted)', marginTop:2 }}>Placeholder</div>
            </div>
          </div>
        </div>

        <form onSubmit={handleSubmit}>
          <label style={{ fontSize:12, fontWeight:700, textTransform:'uppercase',
            letterSpacing:'0.5px', color:'var(--text-secondary)', display:'block', marginBottom:8 }}>
            Kanaalnaam
          </label>
          <input
            className="modal-input"
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder={channelType === 'text' ? 'nieuw-kanaal' : 'spraakkanaal'}
            autoFocus
            maxLength={100}
          />
          <div className="modal-actions">
            <button type="button" className="btn-modal-cancel" onClick={onClose}>Annuleren</button>
            <button type="submit" className="btn-modal-confirm" disabled={loading || !name.trim()}>
              {loading ? 'Aanmaken...' : 'Aanmaken'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
