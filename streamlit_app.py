import streamlit as st
import json
import urllib.request
import urllib.error
import urllib.parse

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln, Medien-Tipps und passenden Links.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt mit strikten Regeln für Ki-Pedia.ch Links & YouTube
system_prompt = (
    "Du bist ein freundlicher, geduldiger und visuleller Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. Nutze für ALLE mathematischen Ausdrücke und Formeln sauberes LaTeX (z.B. $a^2 + b^2 = c^2$).\n\n"
    "3. YOUTUBE-VIDEOS & SUCHTEXT:\n"
    "   - Gib KEINE direkten YouTube-Links an.\n"
    "   - Liefere stattdessen den EXAKTEN Suchtext zum Kopieren für die YouTube-Suchmaske (z.B. `Suchtext: Satz des Pythagoras einfach erklärt`).\n"
    "   - Setze direkt darunter stets folgenden Hinweis:\n"
    "     '💡 *Hinweis:* Beachte bitte, dass der Zugriff auf YouTube auf deinen Schul- oder Elterngeräten möglicherweise eingeschränkt sein kann.'\n\n"
    "4. KI-PEDIA.CH LINK (PFLICHT):\n"
    "   - Füge am Ende Deiner Antwort IMMER einen direkten Link zur passenden Artikelseite von Ki-Pedia.ch ein!\n"
    "   - Format: '📚 *Mehr zum Thema auf Ki-Pedia:* [Thema auf Ki-Pedia.ch lesen](https://ki-pedia.ch/wiki/THEMA)' (Ersetze THEMA durch den passenden Begriff, z.B. https://ki-pedia.ch/wiki/Satz_des_Pythagoras oder nutze die Suche https://ki-pedia.ch/?s=THEMA).\n\n"
    "5. LINKS ZU BILDERN:\n"
    "   - Wenn du Links zu vertiefenden Grafiken anfügst, nutze: '🖼️ *Link zu einer Grafik:* [Name der Grafik](URL) – *Dieses Bild liefert weitere Erklärungen.*'\n\n"
    f"Erklär-Niveau: {st.session_state.level}.\n"
)

# Zuverlässige Schul-Grafiken ohne weiße Ladeflächen
VISUALS = {
    "pythagoras": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Pythagorean.svg/800px-Pythagorean.svg.png",
        "title": "📐 Der Satz des Pythagoras (Katheten- und Hypotenusenquadrate)",
        "kipedia": "https://ki-pedia.ch/?s=Pythagoras"
    },
    "einheitskreis": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Sinus_und_Kosinus_am_Einheitskreis_1.svg/800px-Sinus_und_Kosinus_am_Einheitskreis_1.svg.png",
        "title": "⭕ Sinus und Kosinus am Einheitskreis",
        "kipedia": "https://ki-pedia.ch/?s=Einheitskreis"
    },
    "strahlensatz": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Strahlensatz_1.svg/800px-Strahlensatz_1.svg.png",
        "title": "📐 Der erste Strahlensatz",
        "kipedia": "https://ki-pedia.ch/?s=Strahlensatz"
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
    
    # 1. Zuverlässige Grafik direkt über st.image laden (kein weißer iframe mehr!)
    for keyword, vis_info in VISUALS.items():
        if keyword in query_lower:
            st.subheader(vis_info["title"])
            st.image(vis_info["url"], use_container_width=True)
            break

    # 2. Text der KI anzeigen
    st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"], msg.get("user_query", ""))

# Eingabe
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Wie geht Pythagoras?')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input, "user_query": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Ich antworte und lade die Infos..."):
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
