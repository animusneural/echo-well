import os
import sqlite3
import argparse
from datetime import datetime
import sounddevice as sd
import soundfile as sf

# — CONFIG —
CLIPS_DIR    = "clips"
DB_FILE      = "echo_well.db"
SAMPLE_RATE  = 16000
DURATION_SEC = 5.0

# Ensure clips folder exists
os.makedirs(CLIPS_DIR, exist_ok=True)

# Connect to SQLite and ensure table exists
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

def echo_and_save(tag: str):
    print(f"⏺  Recording {DURATION_SEC}s…")
    data = sd.rec(int(DURATION_SEC * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=1)
    sd.wait()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = os.path.join(CLIPS_DIR, f"{timestamp}.wav")
    sf.write(filename, data, SAMPLE_RATE)
    print(f"💾  Saved clip: {filename}")

    sd.play(data, SAMPLE_RATE)
    sd.wait()
    print("🔊  Echo complete")

    log_clip(filename, tag)
    print(f"✅  Logged clip with tag='{tag}'\n")
    return filename, data   #make sure to return the filename and data for further use

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Echo Well CLI")
    parser.add_argument("-t", "--tag", type=str, default="play", help="Context tag for this clip")
    args = parser.parse_args()

    #from here: we'll ask user if wants to continue, stop or record another clip
#First recording
print("Welcome to the Echo Well CLI!")
print("This tool allows you to record audio clips and tag them for later reference.")
print("You can record multiple clips, and each will be saved with a timestamp and context tag.")
print("Let's start with your first recording.\n")
current_filepath, current_data = echo_and_save(args.tag)

while True:
    print("\nWhat next?")
    print("1.Play again?")
    print("2.Record another clip?")
    print("3.Don't like it? Delete it!")
    print("4.Stop recording and exit?")
    choice = input("Enter your choice (1, 2, 3 or 4): ").strip()

    if choice == "1":
        # replay the last recorded clip
        sd.play(current_data, SAMPLE_RATE)
        sd.wait()
    elif choice == "2":
        # record another clip
        current_filepath, current_data = echo_and_save(args.tag)
    elif choice == "3":
        # delete the last recorded clip
        try:
            os.remove(current_filepath)
            print(f"🗑️  Deleted clip: {current_filepath}")
        except FileNotFoundError:
            print(f"❌  File already gone!")

        #db ask if keep or delete
        db_choice = input("Do you want to delete this clip from the database as well? (yes/no): ").strip().lower()
        if db_choice == "yes":
            #delete the DB row
            c.execute("DELETE FROM EchoClips WHERE Filename = ?", (current_filepath,))
            conn.commit()
            print("✅  Deleted clip from database as well.")
        else:
            print("❗  Keeping clip in database for audit.")

        #prompt to record a new clip
        current_filepath, current_data = echo_and_save(args.tag)
    elif choice == "3":
        #delete the DB row
        c.execute("DELETE FROM EchoClips WHERE Filename = ?", (current_filepath,))
        conn.commit()
        print("✅  Deleted clip from database as well.")

        #After deletion, we don't have a 'current' clips-ask to record a new one:
        print("You've deleted the last clip. Let's record a new one.")
        current_filepath, current_data = echo_and_save(args.tag)
    elif choice == "4":
        print("Exiting Echo Well CLI. Goodbye!")
        break
    else:
        print("Invalid choice. Please enter 1, 2, or 3.")
   