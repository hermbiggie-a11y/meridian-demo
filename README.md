# Meridian: a neutral M&A agent on the Dell Pro Precision GB10

**Topic: private, local AI for M&A due diligence** · runs entirely on a **Dell Pro Precision GB10** · built on **NVIDIA NemoClaw, OpenClaw and OpenShell**

Two companies want to do a deal, but neither will hand its private data to the other. Meridian sits in the middle: both
sides upload signed data into a local clean room, ask questions in Slack and meet on video, all on one Dell Pro Precision
GB10 with no data, model call or transcript leaving it. A deterministic policy engine, not the model, decides what each
side may see, and only the party that owns the data can release it.

## Watch it first

The overview video is under [Releases](../../releases).

## The stages

| Stage | What happens | Check or human gate |
|---|---|---|
| **1. Deal room** | `@Meridian new deal`: each person gets a personal upload link by Slack DM and each side uploads one Ed25519-signed disclosure | Identity comes from Slack; every upload is signature-checked, and a tampered file (ARR edited 11.8 → 15.8) is rejected as INVALID |
| **2. Clean room** | Once both sides are verified, Meridian recomputes valuation, ARR, synergies and funding coverage from both sides' private data and posts the joint reports and the list of assets to verify | Runs only after both signatures are VALID; the recompute must match the signed calculation receipt; only approved aggregates leave |
| **3. Slack Q&A** | Each side asks about the other's report | The policy engine answers ALLOW or DENY by who asks and where (shared channel or own DM); the 10 bundled attack prompts are blocked |
| **4. Live meeting** | `@Meridian new meeting`: both join a Meridian-hosted WebRTC room; every transcript line is attributed to a verified speaker; "joint statement" opens the Joint Summary on both screens; the seller shows its assets to the camera | Human gate: material is released only on a spoken "yes" from the party that owns it; the local VLM checks each asset on camera |
| **5. Close** | End meeting: a neutral report with releases, denials, verified assets, next steps and the next meeting date, posted to Slack | Both sides review the report; every release and denial is in the audit trail |

How it works in detail (architecture, the NVIDIA stack, the security model and sample results):
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Hardware

**Built and run on**

| Component | Built and run on |
|---|---|
| System | Dell Pro Precision GB10 |
| GPU (with memory) | NVIDIA GB10 Grace Blackwell superchip, 128 GB unified LPDDR5x (shared by CPU and GPU) |
| CPU | 20-core NVIDIA Grace Arm CPU |
| Memory (RAM) | 128 GB unified LPDDR5x |
| Storage | 4 TB NVMe SSD |
| OS | NVIDIA DGX OS |
| Software | NVIDIA NemoClaw, OpenClaw, OpenShell; vLLM serving Qwen3.6-35B-A3B NVFP4 (LLM + VLM) and Whisper large-v3-turbo; Flask host app; Slack (Socket Mode); WebRTC |

GPU requirement: 128 GB of unified memory for the LLM, VLM, speech-to-text, sandbox and app together.

A Slack workspace is required, with a Slack app in Socket Mode and its bot and app tokens.

## What's in this repo

| Path | What |
|---|---|
| `app.py` | Meridian engine: policy, clean room, signatures, owner disclosure, deal room, meeting room (WebRTC signaling, attributed speech, consent, asset checks), reports, host API |
| `ed25519_verify.py` | Pure-Python Ed25519 verifier (RFC 8032), usable inside the sandbox |
| `meridian_format.py` | Slack rendering of decisions and evidence sections |
| `slack_bot.py` | Standalone Socket Mode bot for laptop testing (do not run it alongside OpenClaw) |
| `skills/meridian/` | OpenClaw skill: Slack sender → party/channel context → engine; bridges to the host app |
| `skills/mergeops-identity/` | OpenClaw identity skill and the team directory (`roles.json`) |
| `skills/install_*.sh` | Install the two skills into the NemoClaw sandbox |
| `policies/meridian-host.yaml` | OpenShell preset: sandbox → host, `python3` only, four paths |
| `scripts/` | NemoClaw setup, model staging, Whisper on vLLM, huddle capture, acceptance checks |
| `meridian_finance_ai_demo_bundle/` | Synthetic deal data: registry, policy rules, signed disclosures, private A/B data, attack tests, meeting script, demo documents, deal model workbook, system prompt, and `DEMO_RUNBOOK_CN.md` (a scenario walkthrough in Chinese with example lines) |
| `meridian_finance_ai_demo_bundle/scripts/generate_demo_keys.py` | Generates fresh demo-only signing keys and re-signs the disclosures (run once in setup) |
| `data/meridian/visual_criteria.json` | Default asset checklist for the camera check |
| `DEMO_SCRIPT.md` | Step-by-step run with exact lines and keywords, reset and troubleshooting |
| `docs/ARCHITECTURE.md` | Architecture, NVIDIA stack, security model, sample results |
| `docs/DEVELOPMENT.md` | Detailed run notes, laptop mode and debugging pages |

## Setup

Linux, on the Dell Pro Precision GB10 with NVIDIA DGX OS. Commands run from the repo folder.

1. Install the prerequisites: Docker with NVIDIA CDI, Python 3 with `venv`, Node.js (`scripts/setup_nemoclaw.sh` uses
   `node` to read `data/roles.json`) and `rsync`.
2. Create a Slack app with Socket Mode in your Slack workspace (an example manifest is in
   `meridian_finance_ai_demo_bundle/config/slack_app_manifest.example.yaml`) and note its bot token (`SLACK_BOT_TOKEN`)
   and app token (`SLACK_APP_TOKEN`).
3. Copy the settings file and add the Slack tokens:
   ```bash
   cp .env.example .env
   ```
4. Create the team directory and put the Slack user IDs of your two demo participants in it:
   ```bash
   cp skills/mergeops-identity/roles.json data/roles.json
   ```
5. Install the Python packages and generate fresh demo-only signing keys (the repo ships without keys; the keys are
   for the demo only):
   ```bash
   python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
   .venv/bin/python meridian_finance_ai_demo_bundle/scripts/generate_demo_keys.py
   ```
6. Stage the model weights from a local copy of `nvidia/Qwen3.6-35B-A3B-NVFP4` into the Hugging Face cache:
   ```bash
   scripts/stage_model_from_ssd.sh <folder holding the Qwen3.6-35B-A3B-NVFP4 weights>
   ```
7. Install NVIDIA NemoClaw (with OpenClaw, OpenShell and managed vLLM), connect Slack, and install both skills and the
   host policy:
   ```bash
   scripts/setup_nemoclaw.sh
   ```
8. Start speech-to-text (Whisper large-v3-turbo on vLLM; set `WHISPER_SRC` to a local copy of the model the first
   time) and the Meridian host app:
   ```bash
   WHISPER_SRC=<folder holding whisper-large-v3-turbo> scripts/start_whisper.sh
   .venv/bin/python app.py         # :5050 (deal room, reports) · :5443 HTTPS (meeting room)
   ```
9. Run the acceptance checks:
   ```bash
   .venv/bin/python scripts/check_expected_results.py
   .venv/bin/python meridian_finance_ai_demo_bundle/scripts/check_expected_results.py
   ```
10. The full checklist (pre-flight, the run step by step, reset between runs and fixes) is in
    [`DEMO_SCRIPT.md`](DEMO_SCRIPT.md); detailed notes are in [`docs/DEVELOPMENT.md`](docs/DEVELOPMENT.md).

## Known limits

- **Slack is required.** You need a Slack workspace and a Slack app with its bot and app tokens; the demo uses one
  workspace. In production the two companies would be separate workspaces sharing a channel through Slack Connect
  (identity = `team_id + user_id`).
- **Synthetic data, not investment advice.** All company names, figures, documents and findings are fictional and
  created for this demo. Nothing in it is legal, accounting or investment advice.
- **Demo-only keys.** Setup generates new demo-only Ed25519 keys and re-signs the disclosures; never use them in
  production. `meridian_finance_ai_demo_bundle/SHA256SUMS.txt` does not list the keys or signatures, since they are
  generated on each install.
- **Device-to-device networking.** Peer-to-peer video needs device-to-device traffic. If the network blocks it,
  transcript, policy and asset checks still work, and a TURN server would fix it.
- **Self-signed certificate.** The meeting room uses HTTPS on :5443 with a local certificate; browsers warn on the first
  visit.
- **Intent detection** is keyword-based by design (predictable in a live demo). An LLM intent classifier behind the same
  policy gate is the next step.
- **Trusting the neutral host:** whoever runs the Dell Pro Precision GB10 can see both sides. Confidential computing or attested hosting is
  the production answer.

## Credits

- **Created by the FA team: Hsiang-Yu (Anna) Huang and Carrie (Chuqiao) Feng.** The original project is
  [annaandmandy/dell_nvidia_hackathon](https://github.com/annaandmandy/dell_nvidia_hackathon). If Meridian is useful
  to you, please star their repo.
- **Partner:** NVIDIA (NemoClaw, OpenClaw, OpenShell, the NVIDIA GB10 Grace Blackwell superchip).
- **What Dell changed:** this README and `docs/ARCHITECTURE.md` (reorganised from the original README), product naming
  (Dell Pro Precision GB10), setup steps that work outside the original environment (model and Whisper folders as
  arguments), a key generator in place of the original demo signing keys, and removal of personal paths and
  environment-specific notes. No dependency repos are bundled: NVIDIA NemoClaw, OpenClaw, OpenShell, vLLM, the models,
  Flask and Slack are products you install, each under its own licence (see
  [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md)).
- **Upstream licence:** the original repository has no licence file; Dell shares this copy under the rights the authors
  granted Dell. See [`LICENSE`](LICENSE).
- **Demo data:** the synthetic deal data, demo documents and deal model workbook in
  `meridian_finance_ai_demo_bundle/` were created for this demo; every company, figure and finding in them is fictional.
- **AI-generated assets:** the overview video under Releases is narrated with an AI-generated voice.
- **Trademarks:** Dell, Dell Technologies and Dell Pro Precision are trademarks of Dell Inc. or its subsidiaries. NVIDIA,
  DGX, Grace and Blackwell are trademarks of NVIDIA Corporation. Slack is a trademark of Slack Technologies, LLC.
  NemoClaw, OpenClaw, OpenShell, vLLM, Qwen, Whisper, Flask, Chrome and other names belong to their owners. HarborStone Financial Group and QuantaShield AI are fictional. Naming a third-party
  product or project does not mean its owner endorses this demo or Dell.

## Support

Logan Lawler, Dell Technologies: [logan.lawler@dell.com](mailto:logan.lawler@dell.com)

## License

The original work by the FA team has no licence file; Dell shares it under the rights the authors granted Dell. Dell's
changes are Copyright (c) 2026 Dell Inc. See [`LICENSE`](LICENSE) and [`THIRD_PARTY_NOTICES.md`](THIRD_PARTY_NOTICES.md).
