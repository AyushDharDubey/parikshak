# Parikshak

A console-based mock exam simulator. Records your answers, flags and time spent per question while you solve a paper.

- Live countdown and elapsed clock
- Per-question time tracking across visits
- Arrow-key navigation, A/B/C/D or custom text answers, flags for review
- Autosave with resume after a crash or quit
- Summary table and CSV report on submit

Requires Python 3.8+ on Linux or macOS. No dependencies.

## Run

```bash
python -m parikshak                 # from the repo root
# or install it as a command
pip install .
parikshak -n 120 -m 120             # 120 questions, 120 minutes
```

Options: `-n` questions, `-m` minutes, `--state FILE` save file (default `exam_state.json`), `--no-color`.

## Controls

| Key | Action |
| --- | --- |
| `a` `b` `c` `d` | Answer and go to next |
| `t <text>` | Custom answer |
| `f` | Toggle flag |
| `x` | Clear answer |
| `<number>` | Jump to question |
| Arrows / `n` `p` | Move |
| `s` | Submit |
| `q` / Ctrl-C | Save and quit |
