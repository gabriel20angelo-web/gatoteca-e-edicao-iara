# Your changes to cooked.

Everything in this folder is yours. Updating the editor replaces the editor's own files, never this
folder, so what you put here keeps working after every update. The editor reads this folder first.

- `rules/*.md`: extra rules in plain words, one per line. Every edit follows them.
- `captions/<name>.json`: a caption style, like `{"size_pct": 5, "y_pct": 72, "color": "#FFFFFF"}`.
  It shows up as a tile on the style page, rendered on your own video. Pick it there, or run
  `taste.py set captions.preset <name>`.
- `templates/<type>.json`: default settings for one animation template, like `flow.json`.
- `sounds/`: your own sound effects, and which sound plays where (pick them in a video's Sounds panel).
- `prompts/judge-rubric.md`: your own version of the cut critic's rubric. Copy the editor's first.

Easiest is to tell Claude what you want changed. It writes the file here for you.
