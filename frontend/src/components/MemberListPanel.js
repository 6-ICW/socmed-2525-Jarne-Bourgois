import React, { useEffect, useState, useCallback } from 'react';
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

const ROLE_LABELS = { owner: 'Eigenaar', admin: 'Admin', member: 'Lid' };

export default function MemberListPanel({ server, currentUser, currentUserRole, onMembersChange }) {
  const [members, setMembers] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMembers = useCallback(async () => {
    if (!server) return;
    try {
      const res = await api.get(`/servers/${server.id}/members/`);
      setMembers(res.data);
    } catch {}
    finally { setLoading(false); }
  }, [server]);

  useEffect(() => {
    setLoading(true);
    fetchMembers();
    const interval = setInterval(fetchMembers, 15000);
    return () => clearInterval(interval);
  }, [fetchMembers]);

  const handleToggleAdmin = async (memberId) => {
    try {
      const res = await api.patch(`/servers/${server.id}/members/${memberId}/toggle-admin/`);
      setMembers(prev => {
        const updated = prev.map(m => m.user.id === memberId ? { ...m, role: res.data.role } : m);
        return sortMembers(updated);
      });
      if (onMembersChange) onMembersChange();
    } catch (err) {
      alert(err.response?.data?.error || 'Actie mislukt.');
    }
  };

  const handleKick = async (memberId, username) => {
    if (!window.confirm(`Wil je ${username} verwijderen uit de server?`)) return;
    try {
      await api.delete(`/servers/${server.id}/members/${memberId}/kick/`);
      setMembers(prev => prev.filter(m => m.user.id !== memberId));
    } catch (err) {
      alert(err.response?.data?.error || 'Verwijderen mislukt.');
    }
  };

  function sortMembers(list) {
    const order = { owner: 0, admin: 1, member: 2 };
    return [...list].sort((a, b) => (order[a.role] || 3) - (order[b.role] || 3));
  }

  const canManage = currentUserRole === 'owner' || currentUserRole === 'admin';
//   const isOwner = currentUserRole === 'owner';

  const owners = members.filter(m => m.role === 'owner');
  const admins = members.filter(m => m.role === 'admin');
  const regularMembers = members.filter(m => m.role === 'member');

  const renderMember = (m) => {
    const isMe = m.user.id === currentUser?.id;
    const isTargetOwner = m.role === 'owner';
    const showAdminToggle = canManage && !isMe && !isTargetOwner;
    const showKick = canManage && !isMe && !isTargetOwner;
    const adminLabel = m.role === 'admin' ? 'Admin afnemen' : 'Admin maken';

    return (
      <div key={m.user.id} className="member-item">
        <div className="member-avatar-wrap">
          <div className="member-avatar" style={{ background: getColor(m.user.username) }}>
            {getInitials(m.user.username)}
          </div>
          <div className={`online-dot ${m.user.is_online ? 'online' : 'offline'}`} />
        </div>
        <div className="member-name-wrap">
          <div className="member-name">{m.user.username}{isMe ? ' (jij)' : ''}</div>
          <span className={`member-role-badge role-${m.role}`}>{ROLE_LABELS[m.role]}</span>
        </div>
        {(showAdminToggle || showKick) && (
          <div className="member-actions">
            {showAdminToggle && (
              <button
                className="member-action-btn"
                title={adminLabel}
                onClick={() => handleToggleAdmin(m.user.id)}
              >
                {m.role === 'admin' ? '⬇' : '⬆'}
              </button>
            )}
            {showKick && (
              <button
                className="member-action-btn danger"
                title={`${m.user.username} verwijderen`}
                onClick={() => handleKick(m.user.id, m.user.username)}
              >
                ✕
              </button>
            )}
          </div>
        )}
      </div>
    );
  };

  if (loading) return (
    <div className="member-list-panel">
      <div className="member-list-header">Leden laden...</div>
    </div>
  );

  return (
    <div className="member-list-panel">
      <div className="member-list-header">
        Leden — {members.length}
      </div>

      {owners.length > 0 && (
        <>
          <div className="member-section-label">Eigenaar</div>
          {owners.map(renderMember)}
        </>
      )}

      {admins.length > 0 && (
        <>
          <div className="member-section-label">Admins — {admins.length}</div>
          {admins.map(renderMember)}
        </>
      )}

      {regularMembers.length > 0 && (
        <>
          <div className="member-section-label">Leden — {regularMembers.length}</div>
          {regularMembers.map(renderMember)}
        </>
      )}
    </div>
  );
}