import streamlit as st
import json
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln, Medien-Tipps und Modellen.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt mit den neuen Vorgaben für YouTube-Suchtexte, Bild-Links und Ki-Pedia / Wikipedia
system_prompt = (
    "Du bist ein freundlicher, geduldiger und visuleller Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. Nutze für ALLE mathematischen Ausdrücke und Formeln sauberes LaTeX (z.B. $a^2 + b^2 = c^2$).\n\n"
    "3. YOUTUBE-VIDEOS & SUCHTEXT:\n"
    "   - Gib KEINE direkten YouTube-Links an, da diese oft veralten oder fehlerhaft sind.\n"
    "   - Erwähne stattdessen IMMER, dass Erklärvideos auf YouTube sehr lehrreich sind, und liefere den EXAKTEN Suchtext, den die Schüler kopieren und in die YouTube-Suchmaske einfügen können (z.B. `Suchtext: Satz des Pythagoras einfach erklärt Daniel Jung`).\n"
    "   - Setze direkt darunter stets folgenden Hinweis:\n"
    "     '💡 *Hinweis:* Beachte bitte, dass der Zugriff auf YouTube auf deinen Schul- oder Elterngeräten möglicherweise eingeschränkt ist.'\n\n"
    "4. LINKS ZU BILDERN:\n"
    "   - Füge funktionierende Links zu anschaulichen Grafiken/Diagrammen ein.\n"
    "   - Format: '🖼️ *Link zu einer Grafik:* [Name der Grafik](URL) – *Dieses Bild liefert dir weitere Erklärungen zum Thema.*'\n\n"
    "5. KI-PEDIA / WIKIPEDIA LINK:\n"
    "   - Verlinke IMMER am Ende der Erklärung die thematisch passende Seite von Kipedia / Wikipedia / Klexikon, da diese für Schülerinnen und Schüler sehr wertvoll ist.\n"
    "   - Format: '📚 *Mehr zum Thema auf Kipedia / Wikipedia:* [Thema im Kinderlexikon / Wikipedia](URL)' (z.B. https://de.wikipedia.org/wiki/Satz_des_Pythagoras oder https://klexikon.zum.de/wiki/Mathematik).\n\n"
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
    
    # 1. GeoGebra Modell laden, falls Thema passt
    for keyword, vis_info in VISUALS.items():
        if keyword in query_lower:
            st.subheader(vis_info["title"])
            st.components.v1.iframe(vis_info["url"], height=460)
            break

    # 2. Text der KI anzeigen
    st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"], msg.get("user_query", ""))

# Eingabe
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Erkläre mir den Satz des Pythagoras')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "user_query": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Ich erkläre und erstelle dir die passenden Hinweise..."):
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
