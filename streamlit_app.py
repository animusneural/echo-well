import os
import sqlite3
from datetime import datetime
import sounddevice as sd
import soundfile as sf
import streamlit as st

# — CONFIG —
CLIPS_DIR    = "clips"
DB_FILE      = "echo_well.db"
SAMPLE_RATE  = 16000
DURATION_SEC = 1.0

os.makedirs(CLIPS_DIR, exist_ok=True)

conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS EchoClips (
  ClipID      INTEGER PRIMARY KEY AUTOINCREMENT,
  Filename    TEXT    NOT NULL,
  Timestamp   TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  ContextTag  TEXT    NOT NULL
)
""")
conn.commit()

def log_clip(filepath: str, tag: str):
    ts = datetime.now().isoformat()
    c.execute(
        "INSERT INTO EchoClips (Filename, Timestamp, ContextTag) VALUES (?, ?, ?)",
        (filepath, ts, tag)
    )
    conn.commit()

st.title("Ecoul Fântânii – Echo Well")

tag = st.text_input("Context tag:", value="play")
if st.button("Capture & Echo"):
    st.write(f"⏺  Recording {DURATION_SEC}s…")
    data = sd.rec(int(DURATION_SEC * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(CLIPS_DIR, f"{timestamp}.wav")
    sf.write(filename, data, SAMPLE_RATE)

    st.audio(data, sample_rate=SAMPLE_RATE)
    log_clip(filename, tag)
    st.success(f"💾  Saved & echoed clip with tag '{tag}'")