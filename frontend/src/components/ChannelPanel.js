import React, { useState } from 'react';

function getInitials(username) {
  return username.slice(0, 2).toUpperCase();
}

export default function ChannelPanel({
  server, selectedChannel, user, currentUserRole,
  onSelectChannel, onCreateChannel, onInvite,
  onDeleteServer, onOpenSettings, onLogout
}) {
  const [showMenu, setShowMenu] = useState(false);

  const textChannels = server.channels?.filter(c => c.channel_type === 'text') || [];
  const voiceChannels = server.channels?.filter(c => c.channel_type === 'voice') || [];
  const isOwner = currentUserRole === 'owner';
  const isAdmin = currentUserRole === 'admin' || isOwner;

  return (
    <div className="channel-panel">
      <div className="channel-panel-header">
        <h2 title={server.name}>{server.name}</h2>
        {isAdmin && !server.is_private && (
          <div style={{ position: 'relative' }}>
            <button className="icon-btn" onClick={() => setShowMenu(v => !v)} title="Serveropties">
              ⚙️
            </button>
            {showMenu && (
              <div style={{
                position: 'absolute', right: 0, top: '100%', background: '#111214',
                border: '1px solid #1e1f22', borderRadius: 6, padding: '4px 0', zIndex: 50,
                minWidth: 190, boxShadow: '0 4px 16px rgba(0,0,0,0.6)'
              }} onClick={() => setShowMenu(false)}>
                <MenuItem icon="⚙️" label="Server instellingen" onClick={onOpenSettings} />
                <MenuItem icon="👤" label="Gebruiker uitnodigen" onClick={onInvite} />
                {isOwner && (
                  <>
                    <div style={{ height: 1, background: '#1e1f22', margin: '4px 0' }} />
                    <MenuItem icon="🗑️" label="Server verwijderen" onClick={onDeleteServer} danger />
                  </>
                )}
              </div>
            )}
          </div>
        )}
      </div>

      <div className="channel-list" onClick={() => showMenu && setShowMenu(false)}>
        {/* Text channels */}
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <span className="channel-section-label">Tekstkanalen</span>
          {isAdmin && !server.is_private && (
            <button className="channel-add-btn" onClick={onCreateChannel} title="Kanaal aanmaken">+</button>
          )}
        </div>

        {textChannels.map(ch => (
          <ChannelButton
            key={ch.id}
            channel={ch}
            isActive={selectedChannel?.id === ch.id}
            icon="#"
            onClick={() => onSelectChannel(ch)}
          />
        ))}
        {textChannels.length === 0 && (
          <p style={{ fontSize: 12, color: 'var(--text-muted)', padding: '4px 8px' }}>Geen tekstkanalen</p>
        )}

        {/* Voice channels */}
        {!server.is_private && (
          <>
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginTop: 8 }}>
              <span className="channel-section-label">Spraakkanalen</span>
              {isAdmin && (
                <button className="channel-add-btn" onClick={onCreateChannel} title="Kanaal aanmaken">+</button>
              )}
            </div>
            {voiceChannels.map(ch => (
              <ChannelButton
                key={ch.id}
                channel={ch}
                isActive={false}
                icon="🔊"
                isVoice
                onClick={() => {}}
              />
            ))}
            {voiceChannels.length === 0 && (
              <p style={{ fontSize: 12, color: 'var(--text-muted)', padding: '4px 8px' }}>Geen spraakkanalen</p>
            )}
          </>
        )}
      </div>

      {/* Footer */}
      <div className="channel-panel-footer">
        <div className="user-info-footer">
          <div style={{
            width: 32, height: 32, borderRadius: '50%', background: '#5865f2',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: 12, fontWeight: 700, color: 'white', flexShrink: 0
          }}>
            {getInitials(user?.username || '?')}
          </div>
          <span className="username" title={user?.username}>{user?.username}</span>
          {currentUserRole && currentUserRole !== 'member' && (
            <span className={`member-role-badge role-${currentUserRole}`} style={{ marginLeft: 4 }}>
              {currentUserRole === 'owner' ? 'Eigenaar' : 'Admin'}
            </span>
          )}
        </div>
        <button className="icon-btn danger" onClick={onLogout} title="Uitloggen">↩</button>
      </div>
    </div>
  );
}

function MenuItem({ icon, label, onClick, danger }) {
  const [hover, setHover] = useState(false);
  return (
    <button
      onClick={onClick}
      onMouseOver={() => setHover(true)}
      onMouseOut={() => setHover(false)}
      style={{
        display: 'block', width: '100%', padding: '8px 16px',
        background: hover ? (danger ? 'rgba(218,55,60,0.1)' : '#35373c') : 'none',
        color: danger ? '#da373c' : '#b5bac1',
        fontSize: 14, textAlign: 'left', cursor: 'pointer', border: 'none',
        fontFamily: 'inherit'
      }}
    >
      {icon} {label}
    </button>
  );
}

function ChannelButton({ channel, isActive, icon, isVoice, onClick }) {
  return (
    <button
      className={`channel-item${isActive ? ' active' : ''}`}
      onClick={onClick}
      style={isVoice ? { opacity: 0.6, cursor: 'default' } : {}}
      title={isVoice ? 'Spraakkanalen zijn een placeholder' : channel.name}
    >
      <span className="channel-icon">{icon}</span>
      {channel.name}
      {isVoice && (
        <span style={{ marginLeft: 'auto', fontSize: 10, color: 'var(--text-muted)', fontStyle: 'italic' }}>
          binnenkort
        </span>
      )}
    </button>
  );
}