#!/usr/bin/env python3
"""Add (or refresh) the "shotbird" board server in <project>/.claude/launch.json, keeping other entries.

  python3 -I ensure_launch.py <session project folder>
"""
import json
import os
import sys

ENTRY = {
    "name": "shotbird",
    "runtimeExecutable": "/usr/bin/python3",
    "runtimeArgs": ["-I", os.path.join(os.path.dirname(os.path.abspath(__file__)), "serve.py"), "--port", "8777"],
    "port": 8777,
}

proj = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.getcwd())
path = os.path.join(proj, ".claude", "launch.json")
cfg = {"version": "0.0.1", "configurations": []}
if os.path.exists(path):
    try:
        cfg = json.load(open(path, encoding="utf-8"))
    except ValueError:
        sys.exit("refusing to touch %s: it is not valid JSON" % path)
confs = [c for c in cfg.get("configurations", []) if c.get("name") != "shotbird"]
confs.append(ENTRY)
cfg["configurations"] = confs
cfg.setdefault("version", "0.0.1")
os.makedirs(os.path.dirname(path), exist_ok=True)
with open(path, "w", encoding="utf-8") as f:
    json.dump(cfg, f, indent=2)
    f.write("\n")
print(path)
