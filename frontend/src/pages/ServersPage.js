import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import api from '../utils/api';
import ServerSidebar from '../components/ServerSidebar';
import ChannelPanel from '../components/ChannelPanel';
import ChatArea from '../components/ChatArea';
import MemberListPanel from '../components/MemberListPanel';
import DmPanel from '../components/DmPanel';
import CreateServerModal from '../components/modals/CreateServerModal';
import CreateChannelModal from '../components/modals/CreateChannelModal';
import InviteModal from '../components/modals/InviteModal';
import ServerSettingsModal from '../components/modals/ServerSettingsModal';

export default function ServersPage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  const [servers, setServers] = useState([]);
  const [selectedServer, setSelectedServer] = useState(null);
  const [selectedChannel, setSelectedChannel] = useState(null);
  const [showDmView, setShowDmView] = useState(false);
  const [pendingInvites, setPendingInvites] = useState([]);

  const [showCreateServer, setShowCreateServer] = useState(false);
  const [showCreateChannel, setShowCreateChannel] = useState(false);
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [showServerSettings, setShowServerSettings] = useState(false);

  const fetchServers = useCallback(async () => {
    try {
      const res = await api.get('/servers/');
      setServers(res.data);
    } catch {}
  }, []);

  const fetchPendingInvites = useCallback(async () => {
    try {
      const res = await api.get('/invites/');
      setPendingInvites(res.data);
    } catch {}
  }, []);

  // Heartbeat for online status
  useEffect(() => {
    const interval = setInterval(() => {
      api.post('/auth/heartbeat/').catch(() => {});
    }, 60000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    fetchServers();
    fetchPendingInvites();
    const interval = setInterval(fetchPendingInvites, 10000);
    return () => clearInterval(interval);
  }, [fetchServers, fetchPendingInvites]);

  const handleSelectServer = (server) => {
    setSelectedServer(server);
    setShowDmView(false);
    const firstText = server.channels?.find(c => c.channel_type === 'text');
    setSelectedChannel(firstText || null);
  };

  const handleSelectChannel = (channel) => {
    if (channel.channel_type === 'voice') return;
    setSelectedChannel(channel);
  };

  const handleLogout = async () => {
    await logout();
    navigate('/login');
  };

  const handleCreateServer = async (name) => {
    const res = await api.post('/servers/', { name });
    const newServer = res.data;
    setServers(prev => [...prev, newServer]);
    handleSelectServer(newServer);
    setShowCreateServer(false);
  };

  const handleCreateChannel = async (name, channelType) => {
    if (!selectedServer) return;
    const res = await api.post(`/servers/${selectedServer.id}/channels/`, { name, channel_type: channelType });
    const newChannel = res.data;
    const updatedServer = { ...selectedServer, channels: [...(selectedServer.channels || []), newChannel] };
    setServers(prev => prev.map(s => s.id === selectedServer.id ? updatedServer : s));
    setSelectedServer(updatedServer);
    if (newChannel.channel_type === 'text') setSelectedChannel(newChannel);
    setShowCreateChannel(false);
  };

  const handleDeleteServer = async (serverId) => {
    if (!window.confirm('Weet je zeker dat je deze server wilt verwijderen?')) return;
    try {
      await api.delete(`/servers/${serverId}/`);
      setServers(prev => prev.filter(s => s.id !== serverId));
      if (selectedServer?.id === serverId) { setSelectedServer(null); setSelectedChannel(null); }
    } catch {}
  };

  const handleServerUpdated = (updatedServer) => {
    setServers(prev => prev.map(s => s.id === updatedServer.id ? updatedServer : s));
    setSelectedServer(updatedServer);
    // Keep selected channel if still exists
    if (selectedChannel) {
      const stillExists = updatedServer.channels?.find(c => c.id === selectedChannel.id);
      if (!stillExists) setSelectedChannel(null);
    }
  };

  const handleAcceptInvite = async (code) => {
    try {
      const res = await api.post(`/invites/${code}/accept/`);
      const newServer = res.data;
      setServers(prev => prev.find(s => s.id === newServer.id) ? prev : [...prev, newServer]);
      setPendingInvites(prev => prev.filter(i => i.code !== code));
      handleSelectServer(newServer);
    } catch (err) {
      alert(err.response?.data?.error || 'Invite accepteren mislukt.');
    }
  };

  const handleDmCreated = (server) => {
    setServers(prev => prev.find(s => s.id === server.id) ? prev : [...prev, server]);
    setShowDmView(false);
    handleSelectServer(server);
  };

  const publicServers = servers.filter(s => !s.is_private);
  const privateServers = servers.filter(s => s.is_private);
  const currentUserRole = selectedServer?.current_user_role;

  return (
    <div className="app-layout">
      <ServerSidebar
        publicServers={publicServers}
        privateServers={privateServers}
        selectedServer={selectedServer}
        showDmView={showDmView}
        pendingInviteCount={pendingInvites.length}
        onSelectServer={handleSelectServer}
        onToggleDmView={() => {
          setShowDmView(v => !v);
          if (!showDmView) { setSelectedServer(null); setSelectedChannel(null); }
        }}
        onCreateServer={() => setShowCreateServer(true)}
        onLogout={handleLogout}
        onHome={() => navigate('/home')}
        user={user}
      />

      {showDmView ? (
        <DmPanel
          pendingInvites={pendingInvites}
          onAcceptInvite={handleAcceptInvite}
          onDmCreated={handleDmCreated}
          onRefreshInvites={fetchPendingInvites}
        />
      ) : selectedServer ? (
        <>
          <ChannelPanel
            server={selectedServer}
            selectedChannel={selectedChannel}
            user={user}
            currentUserRole={currentUserRole}
            onSelectChannel={handleSelectChannel}
            onCreateChannel={() => setShowCreateChannel(true)}
            onInvite={() => setShowInviteModal(true)}
            onOpenSettings={() => setShowServerSettings(true)}
            onDeleteServer={() => handleDeleteServer(selectedServer.id)}
            onLogout={handleLogout}
          />

          {selectedChannel ? (
            <ChatArea
              key={selectedChannel.id}
              channel={selectedChannel}
              user={user}
              currentUserRole={currentUserRole}
            />
          ) : (
            <div className="chat-area">
              <div className="empty-state">
                <div className="empty-icon">💬</div>
                <h3>Selecteer een kanaal</h3>
                <p>Kies een kanaal in de lijst om te beginnen met chatten.</p>
              </div>
            </div>
          )}

          {!selectedServer.is_private && (
            <MemberListPanel
              server={selectedServer}
              currentUser={user}
              currentUserRole={currentUserRole}
              onMembersChange={fetchServers}
            />
          )}
        </>
      ) : (
        <div className="chat-area">
          <div className="empty-state">
            <div className="empty-icon">🚀</div>
            <h3>Welkom bij Discord Clone</h3>
            <p>Selecteer een server in de zijbalk, of maak een nieuwe aan via de + knop.<br /><br />Gebruik het 💬 icoon voor privéberichten en invites.</p>
          </div>
        </div>
      )}

      {showCreateServer && (
        <CreateServerModal onClose={() => setShowCreateServer(false)} onCreate={handleCreateServer} />
      )}
      {showCreateChannel && selectedServer && (
        <CreateChannelModal
          serverName={selectedServer.name}
          onClose={() => setShowCreateChannel(false)}
          onCreate={handleCreateChannel}
        />
      )}
      {showInviteModal && selectedServer && (
        <InviteModal server={selectedServer} onClose={() => setShowInviteModal(false)} />
      )}
      {showServerSettings && selectedServer && (
        <ServerSettingsModal
          server={selectedServer}
          onClose={() => setShowServerSettings(false)}
          onUpdated={handleServerUpdated}
        />
      )}
    </div>
  );
}