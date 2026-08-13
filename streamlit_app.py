import streamlit as st
import json
import re
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Visueller Mathe-Tutor", page_icon="🧮", layout="centered")

st.title("🧮 Dein interaktiver & visueller Mathe-Tutor")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und Zeichnungen.")

# Get API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt für verlässliche Grafiken
system_prompt = (
    "Du bist ein freundlicher, geduldiger und VISUELLER Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. FORMELN: Nutze sauberes LaTeX im Text (z.B. $a^2 + b^2 = c^2$).\n"
    "3. ZEICHNUNGEN & GRAPHIKEN:\n"
    "   WANN IMMER nach einer Grafik, Zeichnung, Funktion oder Geometrie (z.B. Pythagoras, Dreieck, Parabel) gefragt wird, MÜSSTE am Ende ein Codeblock mit ```python_plot eingefügt werden.\n\n"
    "   REGELN FÜR DEN PLOT-CODE:\n"
    "   - Nutze NUR matplotlib.pyplot (als plt), numpy (als np) und matplotlib.patches (als patches).\n"
    "   - Erstelle ein klares Bild ohne unnötigen Schnickschnack.\n"
    "   - Beende den Codeblock immer mit plt.plot(...) oder ax.add_patch(...).\n\n"
    "BEISPIEL PYTHAGORAS DREIECK:\n"
    "```python_plot\n"
    "import matplotlib.pyplot as plt\n"
    "import matplotlib.patches as patches\n\n"
    "fig, ax = plt.subplots(figsize=(5, 5))\n"
    "ax.plot([0, 4, 0, 0], [0, 0, 3, 0], 'b-', linewidth=2)\n"
    "ax.add_patch(patches.Rectangle((0, 0), 4, -4, alpha=0.3, color='red'))\n"
    "ax.add_patch(patches.Rectangle((-3, 0), 3, 3, alpha=0.3, color='green'))\n"
    "ax.set_xlim(-4, 6)\n"
    "ax.set_ylim(-5, 5)\n"
    "ax.set_aspect('equal')\n"
    "ax.grid(True, linestyle='--')\n"
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

# Hilfsfunktion zum Rendern von Text + dynamischen Diagrammen
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
            
            # Ausführungsumgebung mit allen wichtigen Mathe-Modulen ausstatten
            local_scope = {"plt": plt, "np": np, "patches": patches}
            exec(plot_code, local_scope)
            
            if "fig" in local_scope:
                st.pyplot(local_scope["fig"])
            else:
                st.pyplot(plt.gcf())
            plt.close('all')
        except Exception as err:
            st.warning(f"⚠️ Die Grafik konnte nicht gerendert werden. Fehler: {err}")
    else:
        st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"])

# Eingabefeld
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Zeichne mir ein rechtwinkliges Dreieck')...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    messages_payload = [{"role": "system", "content": system_prompt}] + [
        {"role": m["role"], "content": m["content"]} for m in st.session_state.messages
    ]

    with st.chat_message("assistant"):
        with st.spinner("Ich erkläre und zeichne für dich..."):
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
