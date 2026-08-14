import streamlit as st
import json
import urllib.request
import urllib.error

# Page Setup
st.set_page_config(page_title="Mathematik-Zauberer", page_icon="🧙‍♂️", layout="centered")

st.title("🧙‍♂️ Dein Mathematik-Zauberer")
st.write("Stelle mir eine Frage zur Mathematik! Ich helfe dir mit Erklärungen, Formeln und passenden Medien-Tipps.")

# Hinweis-Box zu Limit & Umwelt zu Beginn der Session
st.info(
    "💡 **Wichtiger Hinweis vorab:**\n"
    "- **Nutzung:** Dir stehen pro Tag etwa **12 Fragen** zur Verfügung. Überlege dir deine Fragen also gut!\n"
    "- **Umwelthinweis 🌱:** Jede KI-Anfrage verbraucht Rechenleistung und Strom. Gehe deshalb bewusst und sparsam mit deinen Anfragen um!"
)

# API Key
api_key = st.secrets.get("GROQ_API_KEY", None)

if not api_key:
    st.error("⚠️ Bitte GROQ_API_KEY in den Streamlit Secrets hinterlegen!")
    st.stop()

if "messages" not in st.session_state:
    st.session_state.messages = []
if "level" not in st.session_state:
    st.session_state.level = "normal"

# System Prompt mit exakter Strukturierung für die Links
system_prompt = f"""
Du bist ein freundlicher, geduldiger und hilfsbereiter Mathematik-Zauberer für Schülerinnen und Schüler.

STRIKTE REGELN:
1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.
2. ERZEUGE KEINE BILDER, BILD-LINKS ODER ASCII-ZEICHNUNGEN!
3. Nutze für ALLE mathematischen Ausdrücke und Formeln sauberes LaTeX (z.B. $a^2 + b^2 = c^2$).

4. ABSCHLUSS JEDER ANTWORT (HALTE DICH EXAKT AN DIESE STRUKTUR):

---
### 🎬 Video-Tipp (YouTube)
Erklärvideos auf YouTube sind sehr lehrreich. Hier geht es zur Seite: 
🔗 [Zu YouTube wechseln](https://www.youtube.com)

👉 **Kopiere diesen Suchtext für die YouTube-Suche:**
*(Fahre mit der Maus über das graue Feld und klicke oben rechts auf das kleine Klemmbrett-Symbol zum Kopieren!)* 👇
```text
[THEMA] einfach erklärt
