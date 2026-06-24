const form = document.getElementById("chat-form");
const input = document.getElementById("question-input");
const messages = document.getElementById("messages");

const history = [];

function addMessage(text, role) {
  const el = document.createElement("div");
  el.className = `message message-${role}`;
  el.textContent = text;
  messages.appendChild(el);
  messages.scrollTop = messages.scrollHeight;
  return el;
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  const question = input.value.trim();
  if (!question) return;

  addMessage(question, "user");
  input.value = "";

  const pending = addMessage("Thinking...", "assistant");

  try {
    const response = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, history }),
    });
    const data = await response.json();

    if (!response.ok) {
      pending.textContent = data.error || "Something went wrong.";
      return;
    }

    pending.textContent = data.answer;
    history.push({ role: "user", content: question });
    history.push({ role: "assistant", content: data.answer });
  } catch (err) {
    pending.textContent = "Could not reach the server. Try again.";
  }
});

input.addEventListener("input", () => {
  input.style.height = "auto";
  input.style.height = `${Math.min(input.scrollHeight, 160)}px`;
});
