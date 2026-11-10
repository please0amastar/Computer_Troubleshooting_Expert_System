import json
import sqlite3

# 1. Connect to SQLite (this creates a file named troubleshooting.db automatically)
conn = sqlite3.connect('troubleshooting.db')
cur = conn.cursor()

# 2. Create the tables
cur.execute("DROP TABLE IF EXISTS problems")
cur.execute("DROP TABLE IF EXISTS devices")

cur.execute("""
    CREATE TABLE devices (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL UNIQUE
    )
""")

cur.execute("""
    CREATE TABLE problems (
        id INTEGER PRIMARY KEY,
        device_id INTEGER NOT NULL,
        problem TEXT NOT NULL,
        symptoms TEXT,
        possible_cause TEXT,
        solution TEXT,
        follow_up_group TEXT,
        FOREIGN KEY (device_id) REFERENCES devices(id)
    )
""")

# 3. Insert devices
devices = ['PC/Laptop', 'Smartphone/iPad', 'Monitor', 'Printer', 'Router / Wi-Fi']
for name in devices:
    cur.execute("INSERT INTO devices (name) VALUES (?)", (name,))

cur.execute("SELECT id, name FROM devices")
device_ids = {name: id for id, name in cur.fetchall()}

# 4. Load JSON and insert problems
with open("knowledge_base.json", "r", encoding="utf-8") as f:
    data = json.load(f)

DEVICE_ID_RANGES = {
    "PC/Laptop":        range(1, 31),
    "Smartphone/iPad":  range(31, 54),
    "Monitor":          range(54, 61),
    "Printer":          range(61, 64),
    "Router / Wi-Fi":   range(64, 70),
}

def get_device_name(problem_id):
    for name, id_range in DEVICE_ID_RANGES.items():
        if problem_id in id_range:
            return name
    return None

inserted = 0
for entry in data:
    problem_id = int(entry.get("id", 0))
    device_name = get_device_name(problem_id)
    
    if device_name:
        cur.execute("""
            INSERT INTO problems 
            (id, device_id, problem, symptoms, possible_cause, solution, follow_up_group)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            problem_id,
            device_ids[device_name],
            entry.get("problem", ""),
            entry.get("symptoms", ""),
            entry.get("possible_cause", ""),
            entry.get("solution", ""),
            entry.get("follow_up_group", "")
        ))
        inserted += 1

conn.commit()

# 5. Verify
cur.execute("SELECT COUNT(*) FROM problems")
count = cur.fetchone()[0]

print(f"\n✅ Processed {inserted} records")
print(f"Rows in problems table: {count}")

conn.close()