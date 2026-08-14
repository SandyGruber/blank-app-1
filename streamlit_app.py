import streamlit as st
import json
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln, Modellen und nützlichen Links.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt mit klaren Regeln für YouTube- und Bild-Links
system_prompt = (
    "Du bist ein freundlicher, geduldiger und visuleller Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. ERZEUGE KEINE EMBEDDED MARKDOWN BILDER (kein '![...](url)'), sondern nutze reine Text-Links!\n"
    "3. Nutze für ALLE mathematischen Ausdrücke und Formeln sauberes LaTeX (z.B. $a^2 + b^2 = c^2$).\n\n"
    "4. YOUTUBE-VIDEOS & HINWEIS:\n"
    "   Wenn Du passende YouTube-Videos zur Vertiefung empfiehlst, setze DIREKT unter den Video-Link zwingend folgenden Hinweis:\n"
    "   '💡 *Hinweis:* Dieses Video ist sehr lehrreich! Beachte jedoch, dass der Zugriff auf YouTube auf deinen Schul- oder Elterngeräten möglicherweise eingeschränkt ist.'\n\n"
    "5. LINKS ZU BILDERN & GRAFIKEN:\n"
    "   Wenn Du Links zu externen Bildern oder Infografiken anfügst, deklariere sie klar so:\n"
    "   '🖼️ *Link zu einer Grafik:* [Name der Grafik](URL) – *Dieses Bild liefert dir weitere Erklärungen zum Thema.*'\n\n"
    f"Erklär-Niveau: {st.session_state.level}.\n"
)

# Interaktive GeoGebra-Graphen & Modelle
VISUALS = {
    "pythagoras": {
        "url": "https://www.geogebra.org/material/iframe/id/M8vS4D3U/width/600/height/450/border/888888/sfsb/true/smb/false/stb/false/stbh/false/ai/true/asb/false/sri/true/rc/false/ld/false/sdz/true/ctl/false",
        "title": "📐 Interaktives Modell: Satz des Pythagoras"
    },
    "einheitskreis": {
        "url": "https://www.geogebra.org/material/iframe/id/vx9M396z/width/600/height/450/border/888888/sfsb/true/smb/false/stb/false/stbh/false/ai/true/asb/false/sri/true/rc/false/ld/false/sdz/true/ctl/false",
        "title": "⭕ Sinus und Kosinus am Einheitskreis"
    },
    "parabel": {
        "url": "https://www.geogebra.org/material/iframe/id/v89vyfze/width/600/height/400/border/888888/sfsb/true/smb/false/stb/false/stbh/false/ai/true/asb/false/sri/true/rc/false/ld/false/sdz/true/ctl/false",
        "title": "📈 Interaktiver Funktionsgraph (Parabel)"
    }
}

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
    except Exception as e:
        return f"Fehler bei der Anfrage: {e}"

def display_response(text, user_query=""):
    query_lower = user_query.lower()
    
    # 1. GeoGebra Modell laden, falls passend
    for keyword, vis_info in VISUALS.items():
        if keyword in query_lower:
            st.subheader(vis_info["title"])
            st.components.v1.iframe(vis_info["url"], height=460)
            break

    # 2. Text-Antwort der KI darstellen
    st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"], msg.get("user_query", ""))

# Eingabe
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Erkläre mir den Satz des Pythagoras mit Video-Tipp')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "user_query": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Ich antworte und suche nützliche Links..."):
            bot_reply = ask_groq(messages_payload, api_key)
            display_response(bot_reply, user_input)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply, "user_query": user_input})

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
