import streamlit as st
import json
import re
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und Grafiken.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# Wörterbuch mit perfekten, vorgeprüften Lehrbuch-Grafiken
STATIC_IMAGES = {
    "pythagoras": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Pythagorean.svg/600px-Pythagorean.svg.png",
        "title": "📐 Der Satz des Pythagoras (Katheten- und Hypotenusenquadrate)"
    },
    "einheitskreis": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Sinus_und_Kosinus_am_Einheitskreis_1.svg/600px-Sinus_und_Kosinus_am_Einheitskreis_1.svg.png",
        "title": "⭕ Sinus und Kosinus am Einheitskreis"
    },
    "strahlensatz": {
        "url": "https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Strahlensatz_1.svg/600px-Strahlensatz_1.svg.png",
        "title": "📐 Der erste Strahlensatz"
    }
}

system_prompt = (
    "Du bist ein freundlicher, geduldiger und VISUELLER Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. FORMELN: Nutze sauberes LaTeX im Text (z.B. $a^2 + b^2 = c^2$).\n"
    "3. GRAPHIKEN:\n"
    "   - Erzeuge KEINE fehlerhaften Python-Zeichnungen für Geometrie oder Pythagoras!\n"
    "   - Für Funktionsgraphen (z.B. Parabeln wie f(x) = x^2) darfst Du einen sauberen `python_plot` Codeblock erzeugen.\n"
    f"Erklär-Niveau: {st.session_state.level}.\n"
)

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
    # 1. Automatische Prüfung auf Standard-Geometrie-Themen für perfekte Lehrbuchbilder
    query_lower = user_query.lower()
    shown_image = False
    
    for key, img_info in STATIC_IMAGES.items():
        if key in query_lower:
            st.image(img_info["url"], caption=img_info["title"], use_container_width=True)
            shown_image = True
            break

    # 2. Falls ein Python-Plot für Funktionen generiert wurde
    pattern = r"```python_plot\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    
    clean_text = re.sub(pattern, "", text, flags=re.DOTALL)
    st.markdown(clean_text)

    if match and not shown_image:
        plot_code = match.group(1)
        try:
            import matplotlib.pyplot as plt
            import numpy as np
            
            plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
            local_scope = {"plt": plt, "np": np}
            exec(plot_code, local_scope)
            
            if "fig" in local_scope:
                st.pyplot(local_scope["fig"])
            else:
                st.pyplot(plt.gcf())
            plt.close('all')
        except Exception:
            pass

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
        with st.spinner("Ich antworte und zeige die passende Grafik..."):
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
