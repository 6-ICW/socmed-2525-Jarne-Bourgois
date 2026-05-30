import React from 'react';

const COLORS = ['#5865f2','#3ba55c','#f0b232','#ed4245','#7289da','#00aff4','#eb459e','#faa61a'];

function getColor(name) {
  let h = 0;
  for (let c of name) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
  return COLORS[Math.abs(h) % COLORS.length];
}

function serverInitials(name) {
  const words = name.trim().split(/\s+/);
  if (words.length === 1) return words[0].slice(0, 2).toUpperCase();
  return words.slice(0, 2).map(w => w[0]).join('').toUpperCase();
}

function ServerIcon({ server, isActive, onClick }) {
  const bg = isActive ? getColor(server.name) : undefined;

  return (
    <div className="tooltip-wrapper">
      <button
        className={`server-icon-btn${isActive ? ' active' : ''}`}
        onClick={onClick}
        style={{ background: bg, overflow: 'hidden', padding: 0 }}
        title={server.name}
      >
        {server.icon_url ? (
          <img src={server.icon_url} alt={server.name} className="server-icon-img" />
        ) : (
          server.is_private ? '👤' : serverInitials(server.name)
        )}
      </button>
      <span className="tooltip">{server.name}</span>
    </div>
  );
}

export default function ServerSidebar({
  publicServers, privateServers, selectedServer, showDmView,
  pendingInviteCount, onSelectServer, onToggleDmView,
  onCreateServer, onLogout, onHome, user
}) {
  return (
    <div className="server-sidebar">
      {/* Home */}
      <div className="tooltip-wrapper">
        <button className="server-icon-btn" onClick={onHome} title="Home">🏠</button>
        <span className="tooltip">Home</span>
      </div>

      <div className="server-divider" />

      {/* DM / Invite toggle */}
      <div className="tooltip-wrapper" style={{ position: 'relative' }}>
        <button
          className={`server-icon-btn dm-btn${showDmView ? ' active' : ''}`}
          onClick={onToggleDmView}
        >
          💬
        </button>
        {pendingInviteCount > 0 && (
          <span className="notif-badge">{pendingInviteCount}</span>
        )}
        <span className="tooltip">Privéberichten & Invites</span>
      </div>

      <div className="server-divider" />

      {/* Public servers */}
      {publicServers.map(server => (
        <ServerIcon
          key={server.id}
          server={server}
          isActive={selectedServer?.id === server.id && !showDmView}
          onClick={() => onSelectServer(server)}
        />
      ))}

      {/* Private/DM servers */}
      {privateServers.length > 0 && (
        <>
          <div className="server-divider" />
          {privateServers.map(server => (
            <ServerIcon
              key={server.id}
              server={server}
              isActive={selectedServer?.id === server.id && !showDmView}
              onClick={() => onSelectServer(server)}
            />
          ))}
        </>
      )}

      <div className="server-divider" />

      {/* Add server */}
      <div className="tooltip-wrapper">
        <button className="server-icon-btn add-btn" onClick={onCreateServer} title="Server aanmaken">
          +
        </button>
        <span className="tooltip">Server aanmaken</span>
      </div>

      <div style={{ flex: 1 }} />

      {/* Logout */}
      <div className="tooltip-wrapper">
        <button className="server-icon-btn" onClick={onLogout}
          style={{ fontSize: '20px', color: '#da373c' }}>↩</button>
        <span className="tooltip">Uitloggen</span>
      </div>
    </div>
  );
}