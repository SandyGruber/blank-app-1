import streamlit as st
import json
import urllib.request

# Seiteneinstellungen
st.set_page_config(page_title="Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir Schritt für Schritt.")

# API Key aus den Streamlit Secrets holen
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
   st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
   st.stop()

# Speicher für Nachrichten und Erklärungs-Niveau
if "messages" not in st.session_state:
   st.session_state.messages = []
if "level" not in st.session_state:
   st.session_state.level = "normal"

# System-Prompt für die Mathe-KI
system_prompt = f"""
Du bist ein freundlicher und geduldiger Mathematik-Tutor für Schülerinnen und Schüler.

STRIKTE REGELN:
1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.
  Wenn die Frage NICHTS mit Mathematik zu tun hat (z.B. Biologie, Geschichte, Tiere, Deutsch), antworte höflich:
  "Ich bin dein Mathe-Tutor und darf nur Mathematikfragen beantworten. Stelle mir gerne eine Matheaufgabe!"

2. Aktuelles Erklär-Niveau: {st.session_state.level}.
  - Wenn level='einfach': Erkläre sehr einfach mit bildhaften Vergleichen, Alltagsbeispielen und kurzer Schritt-für-Schritt-Anleitung.
  - Wenn level='schwer': Gib tiefere mathematische Hintergründe, formale Begriffe und eine kleine Zusatzaufgabe.

3. Gib nicht nur sofort die Endlösung, sondern erkläre den Rechenweg klar und verständlich.
"""

# Funktion zur Kommunikation mit Groq (ohne externe Module!)
def ask_groq(messages_payload, key):
   url = "https://api.groq.com/openai/v1/chat/completions"
   headers = {
       "Authorization": f"Bearer {key}",
       "Content-Type": "application/json"
   }
   data = {
       "model": "llama-3.3-70b-versatile",
       "messages": messages_payload
   }
   req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
   try:
       with urllib.request.urlopen(req) as response:
           res_data = json.loads(response.read().decode('utf-8'))
           return res_data["choices"][0]["message"]["content"]
   except Exception as e:
       return f"Fehler bei der Anfrage: {e}"

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
   with st.chat_message(msg["role"]):
       st.markdown(msg["content"])

# Eingabefeld für Schüler
user_input = st.chat_input("Deine Mathe-Frage hier eingeben...")

if user_input:
   # Benutzereingabe anzeigen
   st.session_state.messages.append({"role": "user", "content": user_input})
   with st.chat_message("user"):
       st.markdown(user_input)

   # Payload vorbereiten
   messages_payload = [{"role": "system", "content": system_prompt}] + [
       {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
   ]

   # KI um Antwort bitten
   with st.chat_message("assistant"):
       with st.spinner("Ich denke nach..."):
           bot_reply = ask_groq(messages_payload, api_key)
           st.markdown(bot_reply)
           st.session_state.messages.append({"role": "assistant", "content": bot_reply})

# Feedback-Buttons für Schüler
st.divider()
st.write("**Wie war die Erklärung?**")
col1, col2 = st.columns(2)

with col1:
   if st.button("🔴 Zu schwer (Einfacher erklären)"):
       st.session_state.level = "einfach"
       st.toast("Alles klar! Die nächsten Erklärungen werden einfacher.")

with col2:
   if st.button("🟢 Zu einfach (Mehr Details)"):
       st.session_state.level = "schwer"
       st.toast("Super! Ich erkläre es dir beim nächsten Mal genauer.")
