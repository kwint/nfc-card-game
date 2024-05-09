from pathlib import Path
from itertools import batched

SPLIT_LINES= 50
FILE = "sc20-nfc-card.csv"

with Path(FILE).open("r") as fp:
    lines = fp.readlines()

chunked_lines = list(batched(lines, SPLIT_LINES))

base_filename, ext = FILE.split(".")

for i, chunk in enumerate(chunked_lines):
    with Path(f"{base_filename}_{i}.{ext}").open("w") as fp:
        fp.writelines(chunk)


