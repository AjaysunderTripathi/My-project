import React, { useState } from "react";
import { sendMessage, uploadPDF } from "./api";

function App() {
  const [message, setMessage] = useState("");
  const [chat, setChat] = useState([]);
  const [file, setFile] = useState(null);

  const handleSend = async () => {
    if (!message.trim()) return;
    const response = await sendMessage(message);
    setChat([...chat, { role: "user", text: message }, { role: "bot", text: response.answer }]);
    setMessage("");
  };

  const handleUpload = async () => {
    if (!file) return;
    await uploadPDF(file);
    alert("PDF uploaded successfully!");
  };

  return (
    <div style={{ padding: "20px" }}>
      <h2>Chatbot</h2>
      <div style={{ border: "1px solid #ccc", padding: "10px", height: "300px", overflowY: "auto" }}>
        {chat.map((msg, i) => (
          <div key={i} style={{ margin: "5px 0" }}>
            <b>{msg.role === "user" ? "You" : "Bot"}:</b> {msg.text}
          </div>
        ))}
      </div>
      <div>
        <input
          type="text"
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Type your message..."
          style={{ width: "80%" }}
        />
        <button onClick={handleSend}>Send</button>
        <hr />
        <h3>Upload PDF</h3>
        <input type="file" accept="application/pdf" onChange={(e) => setFile(e.target.files[0])} />
        <button onClick={handleUpload}>Upload</button>
      </div>
    </div>
  );
}

export default App;
