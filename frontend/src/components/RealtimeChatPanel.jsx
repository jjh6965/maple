import { useEffect, useState } from "react";
import { io } from "socket.io-client";

import { API_ORIGIN } from "../config/api";

import "./RealtimeChatPanel.css";

export default function RealtimeChatPanel() {
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState([]);
  const [text, setText] = useState("");

  const sessionToken = localStorage.getItem("session_token");
  const userDbId = localStorage.getItem("userDbId");

  useEffect(() => {
    if (!sessionToken || !userDbId) return;

    const client = io(API_ORIGIN, {
      path: "/socket.io",
      transports: ["websocket", "polling"],
      auth: { session_token: sessionToken },
    });

    client.on("connect", () => setConnected(true));
    client.on("disconnect", () => setConnected(false));
    client.on("receiveMessage", (msg) => {
      setMessages((prev) => [...prev.slice(-119), msg]);
    });

    setSocket(client);

    return () => {
      client.disconnect();
    };
  }, [sessionToken, userDbId]);

  const send = (e) => {
    e.preventDefault();
    if (!socket || !text.trim()) return;
    socket.emit("sendMessage", { content: text.trim(), userId: userDbId });
    setText("");
  };

  if (!sessionToken) return null;

  return (
    <section className="realtime-chat">
      <div className="realtime-chat-head">
        <h3>채팅</h3>
        <span className={connected ? "on" : "off"}>
          {connected ? "ON" : "OFF"}
        </span>
      </div>
      <div className="realtime-chat-body">
        {messages.map((m, i) => (
          <p key={`${m.timestamp || i}-${i}`}>
            <strong>{m.senderName || m.senderId || "길드원"}</strong>{" "}
            {m.content}
          </p>
        ))}
        {messages.length === 0 && (
          <p className="empty">채팅이 비어 있습니다.</p>
        )}
      </div>
      <form className="realtime-chat-form" onSubmit={send}>
        <input
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="메시지를 입력하세요"
        />
        <button type="submit">전송</button>
      </form>
    </section>
  );
}
