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
api_key = st.secrets.get("OPENROUTER_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte OPENROUTER_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

# System Prompt
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
    "
