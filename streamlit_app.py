import streamlit as st
import json
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Mathematik-Zauberer", page_icon="🧙‍♂️", layout="centered")

st.title("🧙‍♂️ Dein Mathematik-Zauberer")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und passenden Medien-Tipps.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt für saubere Kopier-Hinweise
system_prompt = f"""
Du bist ein freundlicher, geduldiger und hilfsbereiter Mathematik-Zauberer für Schülerinnen und Schüler.

STRIKTE REGELN:
1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.
2. ERZEUGE KEINE BILDER, BILD-LINKS ODER ASCII-ZEICHNUNGEN!
3. Nutze für ALLE mathematischen Ausdrücke und Formeln sauberes LaTeX (z.B. $a^2 + b^2 = c^2$).

4. YOUTUBE-EMPFEHLUNG (am Ende anfügen):
   - Erwähne, dass Erklärvideos auf YouTube sehr lehrreich sind.
   - Biete einen direkten Link zu YouTube an: [Zu YouTube wechseln](https://www.youtube.com)
   - Formatiere den Suchtext exakt so, damit Schüler ihn kinderleicht kopieren können:

     👉 **Kopiere diesen Suchtext für die YouTube-Suche:**
     *(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇
     ```text
     Satz des Pythagoras einfach erklärt
     ```
   - Füge folgenden Hinweis an:
     '💡 *Hinweis:* Beachte bitte, dass der Zugriff auf YouTube auf deinen Schul- oder Elterngeräten möglicherweise eingeschränkt sein kann.'

5. KI-PEDIA.CH EMPFEHLUNG (am Ende anfügen):
   - Weise darauf hin, dass [Ki-Pedia.ch](https://ki-pedia.ch) eine hervorragende Seite zum Forschen und Nachschlagen für Schülerinnen und Schüler ist.
   - Formatiere den Suchtext für Ki-Pedia ebenfalls exakt so:

     👉 **Kopiere diesen Suchtext für Ki-Pedia.ch:**
     *(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇
     ```text
     Satz des Pythagoras
     ```

Erklär-Niveau: {st.session_state.level}.
"""

def ask_groq(messages_payload, key):
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
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
    except urllib.error.HTTPError as e:
        return f"⚠️ Fehler bei der Verbindung (HTTP {e.code}). Bitte versuche es gleich noch einmal."
    except Exception as e:
        return f"⚠️ Fehler bei der Anfrage: {e}"

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Eingabefeld
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Wie geht der Satz des Pythagoras?')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.spinner("Der Mathematik-Zauberer denkt nach..."):
        bot_reply = ask_groq(messages_payload, api_key)
        st.session_state.messages.append({"role": "assistant", "content": bot_reply})
        
    st.rerun()

# Feedback-Buttons
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
