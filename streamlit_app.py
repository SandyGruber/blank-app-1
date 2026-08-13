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

# System Prompt für visuelle Aufbereitung & SVG-Zeichnungen / Matplotlib
system_prompt = f"""
Du bist ein freundlicher, geduldiger und VISUELLER Mathematik-Tutor für Schülerinnen und Schüler.

STRIKTE REGELN:
1. Beantworte AUSSCHLIESSLICH Fragen zur Mathematik.
2. FORMELN & SCHREIBWEISE:
   - Nutze für ALLE mathematischen Formeln, Brüche und Variablen sauberes LaTeX.
   - Im Text: $f(x) = x^2 - 4$ oder $\\frac{{a}}{{b}}$.
   - Freistehende Wichtige Formeln:
     $$x_{{1,2}} = \\frac{{-b \\pm \\sqrt{{b^2 - 4ac}}}}{{2a}}$$

3. VISUELLE GRAPHIKEN & SKIZZEN:
   Wenn eine Zeichnung, ein Funktionsgraph oder eine Geometrie-Skizze der Erklärung hilft (z.B. bei Parabeln, Geraden, Winkeln, Dreiecken, Koordinatensystemen), füge am Ende Deiner Antwort einen speziellen Python-Codeblock ein, der mit ```python_plot beginnt.

BEISPIEL FÜR EINEN FUNKTIONSGRAPHEN / GRAPHIK:
```python_plot
import matplotlib.pyplot as plt
import numpy as np

x = np.linspace(-5, 5, 200)
y = x**2 - 2

fig, ax = plt.subplots(figsize=(6, 4))
ax.plot(x, y, color='#1f77b4', linewidth=2, label='f(x) = x² - 2')
ax.axhline(0, color='black', linewidth=0.8)
ax.axvline(0, color='black', linewidth=0.8)
ax.grid(True, linestyle='--', alpha=0.6)
ax.legend()
ax.set_title("Funktionsgraph")
