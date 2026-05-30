import React, { useState, useRef } from 'react';
import api from '../../utils/api';

const COLORS = ['#5865f2','#3ba55c','#f0b232','#ed4245','#7289da','#00aff4','#eb459e','#faa61a'];
function getColor(name) {
  let h = 0;
  for (let c of name) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
  return COLORS[Math.abs(h) % COLORS.length];
}
function getInitials(name) {
  const p = name.trim().split(/\s+/);
  return p.length >= 2 ? (p[0][0] + p[1][0]).toUpperCase() : name.slice(0, 2).toUpperCase();
}

export default function ServerSettingsModal({ server, onClose, onUpdated }) {
  const [name, setName] = useState(server.name);
  const [iconFile, setIconFile] = useState(null);
  const [iconPreview, setIconPreview] = useState(server.icon_url || null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
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

  const handleSave = async (e) => {
    e.preventDefault();
    if (!name.trim()) { setError('Naam mag niet leeg zijn.'); return; }
    setLoading(true);
    setError('');
    try {
      const formData = new FormData();
      formData.append('name', name.trim());
      if (iconFile) formData.append('icon', iconFile);

      const res = await api.patch(`/servers/${server.id}/`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' }
      });
      onUpdated(res.data);
      onClose();
    } catch (err) {
      setError(err.response?.data?.error || 'Opslaan mislukt.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="modal-overlay" onClick={e => e.target === e.currentTarget && onClose()}>
      <div className="modal">
        <h2>Server instellingen</h2>
        <p>Pas de naam of het icoontje van je server aan.</p>

        {error && <div className="error-msg">{error}</div>}

        <form onSubmit={handleSave}>
          {/* Icon upload */}
          <div style={{ marginBottom: 20 }}>
            <label style={{ fontSize:12, fontWeight:700, textTransform:'uppercase',
              letterSpacing:'0.5px', color:'var(--text-secondary)', display:'block', marginBottom:10 }}>
              Server icoontje
            </label>
            <div className="icon-upload-area">
              <div
                className="icon-preview"
                style={{ background: !iconPreview ? getColor(name || server.name) : undefined }}
                onClick={() => fileInputRef.current?.click()}
                title="Klik om een afbeelding te kiezen"
              >
                {iconPreview
                  ? <img src={iconPreview} alt="Server icon preview" />
                  : <span style={{ color:'white', fontWeight:700 }}>{getInitials(name || server.name)}</span>
                }
              </div>
              <div className="icon-upload-info">
                <button
                  type="button"
                  className="btn-modal-confirm"
                  style={{ padding:'8px 14px', fontSize:13 }}
                  onClick={() => fileInputRef.current?.click()}
                >
                  Afbeelding kiezen
                </button>
                <p>PNG, JPG of GIF. Max 5 MB.<br />Klik op het icoontje of de knop om te uploaden.</p>
                {iconFile && (
                  <button
                    type="button"
                    onClick={() => { setIconFile(null); setIconPreview(server.icon_url || null); }}
                    style={{ marginTop:6, background:'none', color:'var(--danger)', border:'none',
                      cursor:'pointer', fontSize:12, padding:0 }}
                  >
                    ✕ Wijziging ongedaan maken
                  </button>
                )}
              </div>
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                className="file-input-hidden"
                onChange={handleIconChange}
              />
            </div>
          </div>

          {/* Name */}
          <div style={{ marginBottom: 8 }}>
            <label style={{ fontSize:12, fontWeight:700, textTransform:'uppercase',
              letterSpacing:'0.5px', color:'var(--text-secondary)', display:'block', marginBottom:8 }}>
              Servernaam
            </label>
            <input
              className="modal-input"
              type="text"
              value={name}
              onChange={e => setName(e.target.value)}
              placeholder="Servernaam"
              maxLength={100}
              autoFocus
            />
          </div>

          <div className="modal-actions">
            <button type="button" className="btn-modal-cancel" onClick={onClose}>Annuleren</button>
            <button type="submit" className="btn-modal-confirm" disabled={loading || !name.trim()}>
              {loading ? 'Opslaan...' : 'Opslaan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}