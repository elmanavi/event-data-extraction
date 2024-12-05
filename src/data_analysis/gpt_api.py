import os
import json
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["open_ai"]["api_key"])


def classify_text(content: str):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "system", "content": 'Sei ein Textklassifizierungsmodell'},
                  {"role": "user",
                   "content": 'Klassifiziere den folgenden Text in einer der 3 Klassen: "EventDetail", "EventOverview", "None". "EventDetail" enthält detallierte Informationen zu einer Veranstaltung, wobei Werbung / Vorschau für weitere Veranstaltungen auf der Seite enthalten sein können. "EventOverview" enthält eine Liste mehrerer Events so wie einen Link pro Event für weitere Informationen. "None" enthält keine Informationen über spezifische Veranstaltungen. Gebe die Klasse in JSON Format (Kein Markdown) zurück: z.B.: {"class": "EventDetail"} \n' + content}],

    )
    return json.loads(response.choices[0].message.content)