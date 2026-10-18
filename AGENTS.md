# Agent Guidance

This is an NVIDIA AI Workbench project. `.project/spec.yaml` defines the Workbench container (Python with CUDA 12.4), its mounts, and its apps; edit it only for Workbench changes.

## Layout

- `code/`: Python modules and Streamlit apps.
- `data/`, `models/`: tracked with Git LFS (see `.gitattributes`). `data/scratch/` is gitignored.
- `requirements.txt`: Python dependencies for both Workbench and Amp orbs. Add new dependencies here.
- `apt.txt`, `preBuild.bash`, `postBuild.bash`, `onStart.bash`: Workbench container build hooks. Amp orbs do not run them.

## Amp orbs

- `.agents/setup` installs system packages, configures Git LFS, and installs `requirements.txt` into `.venv` with `uv`. When you add a dependency, run `.agents/setup` again instead of installing packages by hand.
- `.venv/bin` is on `PATH` in login shells inside the repository, so `python`, `streamlit`, and `jupyter` resolve to the virtualenv.
- Orbs have no GPU. PyTorch is the CPU build, and `torch.cuda.is_available()` is `False`. Do not assume CUDA, DCGM (`:9400`), or NVIDIA drivers are available.
- `/project/` and `/project/gmm/` are Workbench mounts that do not exist in orbs. Code that reads them, including the 6-Axis Science Calibration app, cannot run there.

## Running apps

- NVIDIA Deep Stack Bridge: `streamlit run code/nvidia_deep_stack_bridge.py --server.port 8502 --server.headless true`. In an orb, run it as a supervised service and share a portal URL instead of a localhost URL.
