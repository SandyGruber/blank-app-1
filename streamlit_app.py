import streamlit as st
import json
import re
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und anschaulichen Bildern.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System-Prompt für hochwertige visuelle Bilder & schöne Graphen
system_prompt = (
    "Du bist ein freundlicher, geduldiger und hochvisueller Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "DEINE WICHTIGSTE AUFGABE - ANSCHAULICHE BILDER:\n"
    "1. Bei bekannten Mathe-Themen (z.B. Satz des Pythagoras, Geometrie, Bruchrechnung, Trigonometrie, Dreiecke, Kreise) sollst Du ein ECHTES, SCHÖNES BILD aus dem Internet einbinden!\n"
    "   Verwende dazu das Standard-Markdown-Bildformat: ![Titel](URL)\n"
    "   Nutze verlässliche Bild-URLs aus Wikimedia Commons, z.B.:\n"
    "   - Pythagoras: https://upload.wikimedia.org/wikipedia/commons/thumb/d/d2/Pythagorean.svg/600px-Pythagorean.svg.png\n"
    "   - Einheitskreis: https://upload.wikimedia.org/wikipedia/commons/thumb/7/72/Sinus_und_Kosinus_am_Einheitskreis_1.svg/600px-Sinus_und_Kosinus_am_Einheitskreis_1.svg.png\n"
    "   - Strahlensatz: https://upload.wikimedia.org/wikipedia/commons/thumb/1/11/Strahlensatz_1.svg/600px-Strahlensatz_1.svg.png\n\n"
    "2. Bei SCHUL-FUNKTIONEN (Parabeln, Geraden): Verwende einen sauberen, hochauflösenden `python_plot` Block mit modernem Design (Grid, schöne Farben, dicke Linien).\n\n"
    "3. FORMELN: Nutze sauberes LaTeX im Text (z.B. $a^2 + b^2 = c^2$).\n"
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

def display_response(text):
    pattern = r"```python_plot\n(.*?)\n```"
    match = re.search(pattern, text, re.DOTALL)
    
    if match:
        clean_text = re.sub(pattern, "", text, flags=re.DOTALL)
        st.markdown(clean_text)
        
        plot_code = match.group(1)
        try:
            import matplotlib.pyplot as plt
            import matplotlib.patches as patches
            import numpy as np
            
            # Schöneres Design für Matplotlib aktivieren
            plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
            
            local_scope = {"plt": plt, "np": np, "patches": patches}
            exec(plot_code, local_scope)
            
            if "fig" in local_scope:
                st.pyplot(local_scope["fig"])
            else:
                st.pyplot(plt.gcf())
            plt.close('all')
        except Exception:
            pass
    else:
        st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"])

# Eingabe
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Erkläre mir den Satz des Pythagoras mit Bild')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Ich suche das passende Bild und erkläre..."):
            bot_reply = ask_groq(messages_payload, api_key)
            display_response(bot_reply)
            st.session_state.messages.append({"role": "assistant", "content": bot_reply})

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
