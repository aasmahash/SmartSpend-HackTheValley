import pandas as pd
import glob
from pathlib import Path
import csv
current_dir = Path.cwd()

# Match files like:
files = sorted(current_dir.glob("accountactivity (*).csv"))

if not files:
    raise FileNotFoundError("No files matched pattern: accountactivity*.csv")

out_path = current_dir / "accountactivity-complete.csv"
        
# Option A: fast & simple — read all then save once
first = True
for p in files:
    df = pd.read_csv(p)
    df.to_csv(out_path, mode="a", header=first, index=False)
    first = False
# df_all = pd.concat((pd.read_csv(p) for p in files), ignore_index=True)

print(f"Merged {len(files)} files → {out_path}")

with open('accountactivity-complete.csv', 'r') as file:
    with open('accountactivity-cleaned.csv','w') as file2:
        reader = csv.reader(file)
        writer = csv.writer(file2)
        for row in reader:
            if '' in row:
                row.remove('')
            for s in row[:]:
                if s == '' or 'unnamed' in s.lower():
                    row.remove(s)
            writer.writerow(row)