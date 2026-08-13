import streamlit as st
import json
import re
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und Zeichnungen.")

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt für hochwertige, farbige Lehrbuch-Grafiken
system_prompt = (
    "Du bist ein freundlicher, geduldiger und VISUELLER Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. ERZEUGE KEINE EXTERNEN BILD-URLS (KEINE Markdown-Links zu Bildern)!\n"
    "3. ZEICHNUNGEN & GRAFIKEN:\n"
    "   Wenn nach einer Grafik oder Visualisierung gefragt wird (z.B. Pythagoras, Geometrie, Parabeln), erstelle IMMER einen fehlerfreien `python_plot` Codeblock.\n"
    "   - Bilde geometrische Formen SCHÖN und FARBIG ab (z.B. mit matplotip.patches.Rectangle oder Polygon).\n"
    "   - Fülle Flächen mit passender Transparenz (alpha=0.4), wähle schöne Farben (Blau, Rot, Grün) und beschrifte die Seiten/Winkel direkt im Bild mit ax.text().\n\n"
    "BEISPIEL PYTHAGORAS LEHRBUCH-GRAFIK:\n"
    "```python_plot\n"
    "import matplotlib.pyplot as plt\n"
    "import matplotlib.patches as patches\n\n"
    "fig, ax = plt.subplots(figsize=(6, 6))\n"
    "# Dreieck\n"
    "ax.plot([0, 4, 0, 0], [0, 0, 3, 0], 'k-', linewidth=2.5)\n"
    "# Kathetenquadrat a^2 (rot)\n"
    "ax.add_patch(patches.Rectangle((0, 0), -3, 3, facecolor='#ff6b6b', edgecolor='red', alpha=0.5, label='a² = 9'))\n"
    "# Kathetenquadrat b^2 (blau)\n"
    "ax.add_patch(patches.Rectangle((0, 0), 4, -4, facecolor='#4d96ff', edgecolor='blue', alpha=0.5, label='b² = 16'))\n"
    "# Beschriftungen\n"
    "ax.text(2, 0.3, 'b = 4', fontsize=12, fontweight='bold')\n"
    "ax.text(-0.8, 1.5, 'a = 3', fontsize=12, fontweight='bold')\n"
    "ax.text(2.2, 1.8, 'c = 5', fontsize=12, fontweight='bold', color='purple')\n"
    "ax.set_xlim(-4, 6)\n"
    "ax.set_ylim(-5, 5)\n"
    "ax.set_aspect('equal')\n"
    "ax.axis('off')\n"
    "ax.legend(loc='upper right')\n"
    "ax.set_title('Satz des Pythagoras: a² + b² = c²', fontsize=14)\n"
    "```\n\n"
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
            
            plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
            
            local_scope = {"plt": plt, "np": np, "patches": patches}
            exec(plot_code, local_scope)
            
            if "fig" in local_scope:
                st.pyplot(local_scope["fig"])
            else:
                st.pyplot(plt.gcf())
            plt.close('all')
        except Exception as e:
            st.error(f"Fehler beim Erstellen der Grafik: {e}")
    else:
        st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"])

# Eingabe
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Zeige mir den Satz des Pythagoras anschaulich')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Ich erstelle eine farbige Grafik und erkläre..."):
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
