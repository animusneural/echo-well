import os, sqlite3
from datetime import datetime
import sounddevice as sd
import soundfile as sf
import streamlit as st

# — CONFIG —
CLIPS_DIR    = "clips"
DB_FILE      = "echo_well.db"
SAMPLE_RATE  = 16000
DURATION_SEC = 5.0  # match CLI duration

os.makedirs(CLIPS_DIR, exist_ok=True)
conn = sqlite3.connect(DB_FILE, check_same_thread=False)
c = conn.cursor()
c.execute("""
CREATE TABLE IF NOT EXISTS EchoClips (
  ClipID      INTEGER PRIMARY KEY AUTOINCREMENT,
  Filename    TEXT    NOT NULL,
  Timestamp   TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP),
  ContextTag  TEXT    NOT NULL
)""")
conn.commit()

def log_clip(filepath, tag):
    ts = datetime.now().isoformat()
    c.execute(
        "INSERT INTO EchoClips (Filename,Timestamp,ContextTag) VALUES (?,?,?)",
        (filepath, ts, tag)
    )
    conn.commit()

st.title("Ecoul Fântânii – Echo Well Dashboard")

# — Sidebar controls —
with st.sidebar:
    st.header("Actions")
    tag = st.text_input("Context tag:", value="play")
    if st.button("🔴 Record New Clip"):
        st.info(f"Recording {DURATION_SEC}s…")
        data = sd.rec(int(DURATION_SEC * SAMPLE_RATE), SAMPLE_RATE, 1)
        sd.wait()
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        fn = os.path.join(CLIPS_DIR, f"{ts}.wav")
        sf.write(fn, data, SAMPLE_RATE)
        log_clip(fn, tag)
        st.success(f"Saved & logged {fn}")

    # load existing clips
    clips = c.execute(
        "SELECT ClipID, Filename, Timestamp, ContextTag "
        "FROM EchoClips ORDER BY Timestamp DESC"
    ).fetchall()
    if clips:
        ids = [str(r[0]) for r in clips]
        sel = st.selectbox("Select ClipID:", ids)
        clip = next(r for r in clips if str(r[0]) == sel)
        st.write("**Selected:**", clip)
        if st.button("▶️ Play Selected"):
            # use simple unpack without .T
            data, fs = sf.read(clip[1])
            st.audio(data, sample_rate=fs)
        if st.button("🗑️ Delete Selected"):
            try:
                os.remove(clip[1])
            except FileNotFoundError:
                pass
            c.execute("DELETE FROM EchoClips WHERE ClipID = ?", (clip[0],))
            conn.commit()
            st.warning(f"Deleted clip {clip[0]}")
            st.experimental_rerun()

# — Main table view —
st.subheader("All Recorded Clips")
# Display using st.dataframe
if clips:
    import pandas as pd
    df = pd.DataFrame(clips, columns=["ClipID", "Filename", "Timestamp", "ContextTag"])
    st.dataframe(df)
else:
    st.write("_No clips recorded yet._")
