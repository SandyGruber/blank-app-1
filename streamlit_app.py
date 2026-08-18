import streamlit as st
import json
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Mathematik-Zauberer", page_icon="🧙‍♂️", layout="centered")

st.title("🧙‍♂️ Dein Mathematik-Zauberer")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und passenden Medien-Tipps.")

# Session State Initialisierung
if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# Hinweis-Box zu Limit & Umwelt nur zu Beginn anzeigen
if len(st.session_state.messages) == 0:
    st.info(
        "💡 **Wichtiger Hinweis vorab:**\n"
        "- **Nutzung:** Dir stehen pro Tag etwa **12 Fragen** zur Verfügung. Überlege dir deine Fragen also gut!\n"
        "- **Umwelthinweis 🌱:** Jede KI-Anfrage verbraucht Rechenleistung und Strom. Gehe deshalb bewusst und sparsam mit deinen Anfragen um!"
    )

# API Key aus den Secrets laden
api_key = st.secrets.get("GEMINI_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GEMINI_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

# System Prompt mit exakter Strukturierung für die Links
system_prompt = (
    "Du bist ein freundlicher, geduldiger und hilfsbereiter Mathematik-Zauberer für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. ERZEUGE KEINE BILDER, BILD-LINKS ODER ASCII-ZEICHNUNGEN!\n"
    "3. Nutze für ALLE mathematischen Ausdrücke und Formeln sauberes LaTeX (z.B. $a^2 + b^2 = c^2$).\n\n"
    "4. ABSCHLUSS JEDER ANTWORT (HALTE DICH EXAKT AN DIESE STRUKTUR):\n\n"
    "---\n"
    "### 🎬 Video-Tipp (YouTube)\n"
    "Erklärvideos auf YouTube sind sehr lehrreich. Hier geht es zur Seite:\n"
    "🔗 [Zu YouTube wechseln](https://www.youtube.com)\n\n"
    "👉 **Kopiere diesen Suchtext für die YouTube-Suche:**\n"
    "*(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇\n"
    "```text\n"
    "[Passendes Thema] einfach erklärt\n"
    "```\n"
    "💡 *Hinweis:* Beachte bitte, dass der Zugriff auf YouTube auf deinen Schul- oder Elterngeräten möglicherweise eingeschränkt sein kann.\n\n"
    "---\n"
    "### 📚 Nachschlagen auf Ki-Pedia.ch\n"
    "Die Seite Ki-Pedia.ch ist hervorragend zum Forschen und Nachschlagen für Schülerinnen und Schüler!\n"
    "🔗 [Zu Ki-Pedia.ch wechseln](https://ki-pedia.ch)\n\n"
    "👉 **Kopiere diesen Suchtext für Ki-Pedia.ch:**\n"
    "*(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇\n"
    "```text\n"
    "[Passendes Thema]\n"
    "```\n\n"
    f"Erklär-Niveau: {st.session_state.level}.\n"
)

def ask_gemini(messages_history, key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={key}"
    headers = {"Content-Type": "application/json"}
    
    # Konvertieren des Verlaufs für die Google Gemini API
    contents = []
    for msg in messages_history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({"role": role, "parts": [{"text": msg["content"]}]})
        
    data = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data["candidates"][0]["content"]["parts"][0]["text"]
    except urllib.error.HTTPError as e:
        return f"⚠️ Fehler bei der Verbindung (HTTP {e.code}). Bitte versuche es gleich noch einmal."
    except Exception as e:
        return f"⚠️ Fehler bei der Anfrage: {e}"

# Bisherige Nachrichten im Chat anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Eingabefeld
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Wie geht der Satz des Pythagoras?')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Der Mathematik-Zauberer denkt nach..."):
        bot_reply = ask_gemini(st.session_state.messages, api_key)
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
