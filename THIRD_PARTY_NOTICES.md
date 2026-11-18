# Third-party notices

## Upstream project

Meridian was created by the FA team (Hsiang-Yu (Anna) Huang and Carrie (Chuqiao) Feng) in
[annaandmandy/dell_nvidia_hackathon](https://github.com/annaandmandy/dell_nvidia_hackathon). That repository has no
licence file and no copyright or licence notices, so there is no upstream notice text to reproduce here. Dell
Technologies shares this copy under the rights the authors granted Dell. Dell's changes: Copyright (c) 2026 Dell Inc.

No third-party repositories are bundled (vendored) in this repo.

## Products you install

The demo runs on the following products. None of them is included in this repo; you install each one yourself, and
each is under its own licence and terms, which you accept when you install it.

| Product | Used for | Installed by |
|---|---|---|
| NVIDIA NemoClaw | Installs and runs the agent stack and managed vLLM | `scripts/setup_nemoclaw.sh` (NVIDIA's installer; you accept its third-party software terms) |
| OpenClaw | Agent and Slack front end; Meridian ships as two OpenClaw skills | NemoClaw |
| OpenShell | Agent sandbox, network policy and audit logs | NemoClaw |
| vLLM (NVIDIA container image `nvcr.io/nvidia/vllm`) | Serves the LLM/VLM and Whisper | NemoClaw and `scripts/start_whisper.sh` |
| Qwen3.6-35B-A3B NVFP4 (`nvidia/Qwen3.6-35B-A3B-NVFP4`) | Agent LLM and vision model | You provide the weights; `scripts/stage_model_from_ssd.sh` |
| Whisper large-v3-turbo | Meeting speech-to-text | You provide the weights; `scripts/start_whisper.sh` |
| Flask | Meridian host app | `requirements.txt` |
| Slack (Socket Mode, `slack-bolt`) | Deal Q&A, links and reports | Your Slack workspace and app; `requirements.txt` |

The Python packages in `requirements.txt` (Flask, requests, python-dotenv, slack-bolt, cryptography) and the PyAV
package that `scripts/start_whisper.sh` installs into the Whisper container are each under their own licences. The
web pages load the Carlito font from Google Fonts at run time, under its own licence.

Naming a third-party product does not mean its owner endorses this demo or Dell.
