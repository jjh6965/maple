import RealtimeChatPanel from "../components/RealtimeChatPanel";
import "./RealtimeChatPage.css";

export default function RealtimeChatPage() {
  return (
    <main className="chat-page">
      <section className="chat-page-card">
        <h2>메이플 길드 실시간 채팅</h2>
        <p>로그인한 길드원끼리 실시간으로 대화할 수 있습니다.</p>
        <RealtimeChatPanel />
      </section>
    </main>
  );
}
