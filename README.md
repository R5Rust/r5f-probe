# r5f-probe

Ground truth for R5Rust: plays scripted inputs and camera poses in the **real game** (a local R5Flowstate server +
client) and records what happens, so R5Rust's movement and rendering can be diffed against Apex 1:1.

- `mod/Kainz-R5RustProbe`: a Flowstate script mod (arms only on `+hostname r5rust_probe`). The client plays a
  schedule through the engine's own `+forward` / `+jump` / `+backward` commands (no window focus needed); the server
  and client log position + velocity every tick; it can teleport/noclip to poses, hide the HUD, swap legend (Lifeline
  can't lurch, so it records on Octane) and dump live convars.
- `plan.py`: writes the schedule. Movement runs (walk, sprint, crouch, jumps, lurches at several timings, null inputs,
  wheel spam, slides, bhop, LiTTle's Forward RAS) by default; `--shots` makes a screenshot plan from `poses.json`.
- `run.ps1`: installs the mod, starts a dedicated server + windowed client, waits for the plan, saves `out\r5f.log`
  (server samples) and `out\r5f_client.log` (client prediction, per frame), screenshots each pose with `-Shots`
  (`snap.py`, PrintWindow by PID), then stops both and removes the mod. `-Stop` kills a stuck run.

```powershell
python plan.py; .\run.ps1              # movement
python plan.py --shots; .\run.ps1 -Shots   # renders at the poses in poses.json
```

Compare in the R5Rust repo: `cargo run --release -p shared --example probecmp` (replays the same schedule through
R5Rust's sim on the real collision) and `r5rust.exe --screenshot out.png --pos x,y,z --yaw Y --pitch P --fov 100 --fly`.
Leave the PC alone while it runs: the probe client is a real game window.
