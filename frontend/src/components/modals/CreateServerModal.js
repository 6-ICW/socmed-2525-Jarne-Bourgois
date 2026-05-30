import React, { useState, useRef } from 'react';

const COLORS = ['#5865f2','#3ba55c','#f0b232','#ed4245','#7289da','#00aff4','#eb459e','#faa61a'];
function getColor(name) {
  let h = 0;
  for (let c of (name || 'a')) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
  return COLORS[Math.abs(h) % COLORS.length];
}
function getInitials(name) {
  const p = (name || '?').trim().split(/\s+/);
  return p.length >= 2 ? (p[0][0] + p[1][0]).toUpperCase() : (name || '?').slice(0, 2).toUpperCase();
}

export default function CreateServerModal({ onClose, onCreate }) {
  const [name, setName] = useState('');
  const [iconFile, setIconFile] = useState(null);
  const [iconPreview, setIconPreview] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const fileInputRef = useRef();

  const handleIconChange = (e) => {
    const file = e.target.files[0];
    if (!file) return;
    if (file.size > 5 * 1024 * 1024) { setError('Afbeelding mag maximaal 5 MB zijn.'); return; }
    setIconFile(file);
    const reader = new FileReader();
    reader.onloadend = () => setIconPreview(reader.result);
    reader.readAsDataURL(file);
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Geef de server een naam.'); return; }
    setLoading(true);
    try {
      await onCreate(name.trim(), iconFile);
    } catch (err) {
      setError(err.response?.data?.error || 'Server aanmaken mislukt.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>Server aanmaken</h2>
        <p>Geef je server een naam en optioneel een icoontje.</p>
        {error && <div className="error-msg">{error}</div>}

        {/* Icon preview */}
        <div style={{ display: 'flex', justifyContent: 'center', marginBottom: 20 }}>
          <div
            className="icon-preview"
            style={{ background: !iconPreview ? getColor(name) : undefined }}
            onClick={() => fileInputRef.current?.click()}
            title="Klik om een icoontje te kiezen"
          >
            {iconPreview
              ? <img src={iconPreview} alt="Preview" />
              : <span style={{ color: 'white', fontWeight: 700, fontSize: 22 }}>
                  {name ? getInitials(name) : '📷'}
                </span>
            }
          </div>
          <input
            ref={fileInputRef}
            type="file"
            accept="image/*"
            className="file-input-hidden"
            onChange={handleIconChange}
          />
        </div>
        <p style={{ textAlign: 'center', fontSize: 12, color: 'var(--text-muted)', marginBottom: 16, marginTop: -12 }}>
          Klik op het icoontje om een foto te kiezen (optioneel)
        </p>

        <form onSubmit={handleSubmit}>
          <label style={{ fontSize: 12, fontWeight: 700, textTransform: 'uppercase',
            letterSpacing: '0.5px', color: 'var(--text-secondary)', display: 'block', marginBottom: 8 }}>
            Servernaam
          </label>
          <input
            className="modal-input"
            type="text"
            value={name}
            onChange={e => setName(e.target.value)}
            placeholder="Mijn geweldige server"
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