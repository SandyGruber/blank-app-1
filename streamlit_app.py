import streamlit as st
import json
import urllib.request
import urllib.error
from datetime import date

# Page Setup
st.set_page_config(page_title="Mathematik-Zauberer", page_icon="🧙‍♂️", layout="centered")

st.title("🧙‍♂️ Dein Mathematik-Zauberer")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und passenden Medien-Tipps.")

# Maximale Anfragen pro Tag
MAX_DAILY_QUESTIONS = 12
today_str = str(date.today())

# Session State Initialisierung (Zähler & Datum)
if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"
if "last_active_date" not in st.session_state:
    st.session_state.last_active_date = today_str
if "question_count" not in st.session_state:
    st.session_state.question_count = 0

# Zähler zurücksetzen, wenn ein neuer Tag beginnt
if st.session_state.last_active_date != today_str:
    st.session_state.last_active_date = today_str
    st.session_state.question_count = 0

# Anzeige der verbleibenden Fragen
remaining_questions = MAX_DAILY_QUESTIONS - st.session_state.question_count

# Hinweis-Box zu Limit & Umwelt
st.info(
    f"💡 **Wichtiger Hinweis vorab:**\n"
    f"- **Nutzung:** Du hast heute noch **{remaining_questions} von {MAX_DAILY_QUESTIONS} Fragen** übrig.\n"
    f"- **Umwelthinweis 🌱:** Jede KI-Anfrage verbraucht Rechenleistung und Strom. Gehe deshalb bewusst und sparsam mit deinen Anfragen um!"
)

# API Key aus den Secrets laden
api_key = st.secrets.get("OPENROUTER_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte OPENROUTER_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

# System Prompt als sicherer Multi-Line String
p1 = "Du bist ein freundlicher, geduldiger und hilfsbereiter Mathematik-Zauberer für Schülerinnen und Schüler.\n\n"
p2 = (
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. ERZEUGE KEINE BILDER, BILD-LINKS ODER ASCII-ZEICHNUNGEN!\n"
    "3. FORMATIERUNG FÜR FORMELN:\n"
    "   - Nutze NIEMALS eckige Klammern wie \\[ ... \\] oder \\( ... \\) für LaTeX!\n"
    "   - Nutze für Formeln im Text IMMER einfache Dollarzeichen: $a^2 + b^2 = c^2$\n"
    "   - Nutze für freistehende Formeln IMMER doppelte Dollarzeichen:\n"
    "     $$\\frac{\\overline{ZA}}{\\overline{ZA'}} = \\frac{\\overline{ZB}}{\\overline{ZB'}}$$\n\n"
)
p3 = "4. ABSCHLUSS JEDER ANTWORT (HALTE DICH EXAKT AN DIESE STRUKTUR):\n\n---\n### 🎬 Video-Tipp (YouTube)\nErklärvideos auf YouTube sind sehr lehrreich. Hier geht es zur Seite:\n🔗 [Zu YouTube wechseln](https://www.youtube.com)\n\n👉 **Kopiere diesen Suchtext für die YouTube-Suche:**\n*(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇\n```text\n[Passendes Thema] einfach erklärt\n```\n💡 *Hinweis:* Beachte bitte, dass der Zugriff auf YouTube auf deinen Schul- oder Elterngeräten möglicherweise eingeschränkt sein kann.\n\n---\n### 📚 Nachschlagen auf Ki-Pedia.ch\nDie Seite Ki-Pedia.ch ist hervorragend zum Forschen und Nachschlagen für Schülerinnen und Schüler!\n🔗 [Zu Ki-Pedia.ch wechseln](https://ki-pedia.ch)\n\n👉 **Kopiere diesen Suchtext für Ki-Pedia.ch:**\n*(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇\n```text\n[Passendes Thema]\n```\n\n"
p4 = "Erklär-Niveau: " + str(st.session_state.level) + ".\n"

system_prompt = p1 + p2 + p3 + p4

def ask_openrouter(messages_history, key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://streamlit.io",
        "X-Title": "Mathematik-Zauberer"
    }
    
    payload_messages = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in messages_history
    ]
    
    data = {
        "model": "openrouter/auto",
        "messages": payload_messages
    }
    
    req = urllib.request.Request(url, data=json.dumps(data).encode('utf-8'), headers=headers)
    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode('utf-8'))
            return res_data["choices"][0]["message"]["content"]
    except urllib.error.HTTPError as e:
        error_detail = e.read().decode('utf-8')
        return f"⚠️ Fehler bei der Verbindung (HTTP {e.code}): {error_detail}"
    except Exception as e:
        return f"⚠️ Fehler bei der Anfrage: {e}"

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# Eingabefeld mit Zähler-Logik
if remaining_questions > 0:
    user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Wie geht der Satz des Pythagoras?')...")
else:
    st.chat_input("⛔ Tageslimit von 12 Fragen erreicht. Morgen kannst du wieder neue Fragen stellen!", disabled=True)
    st.warning("⛔ Du hast deine 12 Fragen für heute aufgebraucht. Bitte versuche es morgen wieder!")
    user_input = None

if user_input:
    st.session_state.question_count += 1
    st.session_state.messages.append({"role": "user", "content": user_input})
    
    with st.spinner("Der Mathematik-Zauberer denkt nach..."):
        bot_reply = ask_openrouter(st.session_state.messages, api_key)
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
