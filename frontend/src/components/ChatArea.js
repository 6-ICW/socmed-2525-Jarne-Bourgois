import React, { useState, useEffect, useRef, useCallback } from "react";
import api, { getWsUrl } from "../utils/api";

const COLORS = [
  "#5865f2",
  "#3ba55c",
  "#f0b232",
  "#ed4245",
  "#7289da",
  "#00aff4",
  "#eb459e",
  "#faa61a",
];

function getColor(username) {
  let h = 0;
  for (let c of username) h = (h * 31 + c.charCodeAt(0)) % COLORS.length;
  return COLORS[Math.abs(h) % COLORS.length];
}

function getInitials(username) {
  const p = username.split(/\s+/);
  return p.length >= 2
    ? (p[0][0] + p[1][0]).toUpperCase()
    : username.slice(0, 2).toUpperCase();
}

function formatTime(isoString) {
  return new Date(isoString).toLocaleString("nl-BE", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function MessageItem({
  msg,
  currentUser,
  isAdmin,
  onDelete,
  onEdit,
  onRestore,
}) {
  const [editing, setEditing] = useState(false);
  const [editContent, setEditContent] = useState(msg.content);
  const isMine = msg.author?.id === currentUser?.id;

  const handleEditSubmit = () => {
    if (editContent.trim() && editContent.trim() !== msg.content) {
      onEdit(msg.id, editContent.trim());
    }
    setEditing(false);
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleEditSubmit();
    }
    if (e.key === "Escape") {
      setEditing(false);
      setEditContent(msg.content);
    }
  };

  const canEdit = isMine;
  const canDelete = isMine || isAdmin;

  if (msg.is_deleted && !isMine) {
    return null;
  }

  return (
    <div className="message-row">
      <div
        className="message-avatar"
        style={{ background: getColor(msg.author?.username || "?") }}
      >
        {getInitials(msg.author?.username || "?")}
      </div>
      <div className="message-body">
        <div className="message-header">
          <span className="message-author">{msg.author?.username}</span>
          <span className="message-time">{formatTime(msg.created_at)}</span>
          {msg.is_edited && (
            <span className="message-edited-tag">(bewerkt)</span>
          )}
        </div>
        {editing ? (
          <div className="edit-input-area">
            <textarea
              className="edit-input"
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              onKeyDown={handleKeyDown}
              autoFocus
              rows={Math.min(4, editContent.split("\n").length)}
            />
            <div className="edit-actions">
              <span onClick={handleEditSubmit}>Opslaan</span>
              {" · "}
              <span
                onClick={() => {
                  setEditing(false);
                  setEditContent(msg.content);
                }}
              >
                Annuleren
              </span>
            </div>
          </div>
        ) : msg.is_deleted ? (
          <div className="message-content">
            <i>Bericht verwijderd</i>

            {isMine && (
              <button
                style={{ marginLeft: 10 }}
                onClick={() => onRestore(msg.id)}
              >
                Herstellen
              </button>
            )}
          </div>
        ) : (
          <div className="message-content">{msg.content}</div>
        )}
      </div>

      {(canEdit || canDelete) && !editing && (
        <div className="message-actions">
          {canEdit && (
            <button
              className="msg-action-btn"
              onClick={() => setEditing(true)}
              title="Bewerken"
            >
              ✏️
            </button>
          )}
          {canDelete && (
            <button
              className={`msg-action-btn delete${
                isAdmin && !isMine ? " admin-delete-btn" : ""
              }`}
              onClick={() => onDelete(msg.id)}
              title={
                isAdmin && !isMine
                  ? "Admin: bericht verwijderen"
                  : "Verwijderen"
              }
            >
              🗑️
            </button>
          )}
        </div>
      )}
    </div>
  );
}

export default function ChatArea({ channel, user, currentUserRole }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [connected, setConnected] = useState(false);
  const [loading, setLoading] = useState(true);
  const wsRef = useRef(null);
  const bottomRef = useRef(null);
  const inputRef = useRef(null);

  const isAdmin = currentUserRole === "admin" || currentUserRole === "owner";

  const scrollToBottom = useCallback(() => {
    setTimeout(
      () => bottomRef.current?.scrollIntoView({ behavior: "smooth" }),
      50
    );
  }, []);

  useEffect(() => {
    setLoading(true);
    setMessages([]);
    api
      .get(`/channels/${channel.id}/messages/`)
      .then((res) => setMessages(res.data))
      .catch(() => {})
      .finally(() => setLoading(false));
  }, [channel.id]);

  useEffect(() => {
    if (!loading) scrollToBottom();
  }, [loading, scrollToBottom]);

  useEffect(() => {
    const ws = new WebSocket(getWsUrl(channel.id));
    wsRef.current = ws;
    ws.onopen = () => setConnected(true);
    ws.onclose = () => setConnected(false);
    ws.onerror = () => setConnected(false);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === "message") {
        setMessages((prev) =>
          prev.find((m) => m.id === data.message.id)
            ? prev
            : [...prev, data.message]
        );
        scrollToBottom();
      } else if (data.type === "message_edited") {
        setMessages((prev) =>
          prev.map((m) => (m.id === data.message.id ? data.message : m))
        );
      } else if (data.type === "message_deleted") {
        setMessages((prev) =>
          prev.map((m) =>
            m.id === data.message_id ? { ...m, is_deleted: true } : m
          )
        );
      } else if (data.type === "message_restored") {
        setMessages((prev) =>
          prev.map((m) => (m.id === data.message.id ? data.message : m))
        );
      }
    };

    // Heartbeat every 60s to keep online status fresh
    const heartbeat = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ action: "heartbeat" }));
      }
    }, 60000);

    return () => {
      ws.close();
      clearInterval(heartbeat);
    };
  }, [channel.id, scrollToBottom]);

  const sendMessage = () => {
    const content = input.trim();
    if (
      !content ||
      !wsRef.current ||
      wsRef.current.readyState !== WebSocket.OPEN
    )
      return;
    wsRef.current.send(JSON.stringify({ action: "send_message", content }));
    setInput("");
    inputRef.current?.focus();
  };

  const deleteMessage = (messageId) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({ action: "delete_message", message_id: messageId })
      );
    }
  };

  const editMessage = (messageId, content) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "edit_message",
          message_id: messageId,
          content,
        })
      );
    }
  };
  const restoreMessage = (messageId) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      wsRef.current.send(
        JSON.stringify({
          action: "restore_message",
          message_id: messageId,
        })
      );
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="chat-area">
      <div className="chat-topbar">
        <span className="channel-icon">#</span>
        <h3>{channel.name}</h3>
        <div
          style={{
            marginLeft: "auto",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          <div
            style={{
              width: 8,
              height: 8,
              borderRadius: "50%",
              background: connected ? "#23a55a" : "#80848e",
            }}
          />
          <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
            {connected ? "Verbonden" : "Verbinden..."}
          </span>
        </div>
      </div>

      <div className="chat-messages">
        {loading && (
          <div
            style={{
              textAlign: "center",
              color: "var(--text-muted)",
              padding: 32,
            }}
          >
            Berichten laden...
          </div>
        )}
        {!loading && messages.length === 0 && (
          <div className="empty-state">
            <div className="empty-icon">#</div>
            <h3>Welkom in #{channel.name}!</h3>
            <p>Dit is het begin van het kanaal. Stuur het eerste bericht.</p>
          </div>
        )}
        {messages.map((msg) => (
          <MessageItem
            key={msg.id}
            msg={msg}
            currentUser={user}
            isAdmin={isAdmin}
            onDelete={deleteMessage}
            onEdit={editMessage}
            onRestore={restoreMessage}
          />
        ))}
        <div ref={bottomRef} />
      </div>

      <div className="chat-input-area">
        <div className="chat-input-wrapper">
          <textarea
            ref={inputRef}
            className="chat-input"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={`Bericht naar #${channel.name}`}
            rows={1}
            onInput={(e) => {
              e.target.style.height = "auto";
              e.target.style.height =
                Math.min(e.target.scrollHeight, 200) + "px";
            }}
          />
          <button
            className="send-btn"
            onClick={sendMessage}
            disabled={!input.trim() || !connected}
          >
            ➤
          </button>
        </div>
      </div>
    </div>
  );
}
