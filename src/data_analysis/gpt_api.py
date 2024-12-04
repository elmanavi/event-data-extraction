import os
import json
from openai import OpenAI
import streamlit as st

client = OpenAI(api_key=st.secrets["open_ai"]["api_key"])


def classify_text(content: str):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": 'Sei ein Textklassifizierungsmodell'},
                  {"role": "user",
                   "content": 'Klassifiziere den folgenden Text in einer der 2 Klassen: "Event", "None". "Event" enthält Informationen (Name und Datum der Veranstaltung) zu mindestens einer Veranstaltung. "None" enthält keine Details zu einem spezifischen Event. Gebe die Klasse in JSON Format (Kein Markdown) zurück: z.B.: {"class": "Event"} \n' + content}],

    )
    return json.loads(response.choices[0].message.content)