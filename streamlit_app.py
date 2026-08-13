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

# System Prompt für visuelle Aufbereitung & Matplotlib
system_prompt = (
    "Du bist ein freundlicher, geduldiger und VISUELLER Mathematik-Tutor für Schülerinnen und Schüler.\n\n"
    "STRIKTE REGELN:\n"
    "1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.\n"
    "2. FORMELN & SCHREIBWEISE:\n"
    "   - Nutze für ALLE mathematischen Formeln, Brüche und Variablen sauberes LaTeX.\n"
    "   - Im Text: $f(x) = x^2 - 4$ oder $\\frac{a}{b}$.\n"
    "   - Freistehende Wichtige Formeln:\n"
    "     $$x_{1,2} = \\frac{-b \\pm \\sqrt{b^2 - 4ac}}{2a}$$\n\n"
    "3. VISUELLE GRAPHIKEN & SKIZZEN:\n"
    "Wenn eine Zeichnung, ein Funktionsgraph oder eine Geometrie-Skizze der Erklärung hilft (z.B. bei Parabeln, Geraden, Winkeln, Dreiecken, Koordinatensystemen), füge am Ende Deiner Antwort einen speziellen Python-Codeblock ein, der mit ```python_plot beginnt.\n\n"
    "BEISPIEL FÜR EINEN FUNKTIONSGRAPHEN / GRAPHIK:\n"
    "```python_plot\n"
    "import matplotlib.pyplot as plt\n"
    "import numpy as np\n\n"
    "x = np.linspace(-5, 5, 200)\n"
    "y = x**2 - 2\n\n"
    "fig, ax = plt.subplots(figsize=(6, 4))\n"
    "ax.plot(x, y, color='#1f77b4', linewidth=2, label='f(x) = x² - 2')\n"
    "ax.axhline(0, color='black', linewidth=0.8)\n"
    "ax.axvline(0, color='black', linewidth=0.8)\n"
    "ax.grid(True, linestyle='--', alpha=0.6)\n"
    "ax.legend()\n"
    "ax.set_title('Funktionsgraph')\n"
    "```\n\n"
    f"Erklär-Niveau: {st.session_state.level}.\n"
)

def ask_groq(messages_payload, key):
    url = "[https://api.groq.com/openai/v1/chat/completions](https://api.groq.com/openai/v1/chat/completions)"
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
            import numpy as np
            
            local_scope = {"plt": plt, "np": np}
            exec(plot_code, local_scope)
            
            if "fig" in local_scope:
                st.pyplot(local_scope["fig"])
            else:
                st.pyplot(plt.gcf())
            plt.close('all')
        except Exception:
            st.info("💡 *(Hinweis: Für diesen Aufgabentyp kann die Grafik direkt im Text nachvollzogen werden)*")
    else:
        st.markdown(text)

# Bisherige Nachrichten anzeigen
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        display_response(msg["content"])

# Eingabefeld
user_input = st.chat_input("Deine Mathe-Frage (z.B. 'Zeichne mir die Funktion f(x) = x^2 - 3')...")

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
