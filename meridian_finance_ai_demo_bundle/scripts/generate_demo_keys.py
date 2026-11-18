#!/usr/bin/env python3
"""Generate fresh demo-only Ed25519 issuer keys and re-sign the signed inputs.

The repo ships without signing keys. Run this once during setup (and again any time you
want new keys). For each signed disclosure it:

- creates a new Ed25519 key pair,
- writes demo_keys/<name>_public.pem (the issuer key Meridian verifies against),
- writes demo_keys/DEMO_ONLY_<name>_private.pem (kept local, never committed or shipped
  into the sandbox),
- signs the canonical JSON of signed_inputs/<name>.json into signed_inputs/<name>.sig.b64.

The payloads are not changed, so ATTACK_tampered_startup_metrics.json still fails against
the startup_commercial_authorized signature. These keys are for the demo only; never use
them in production.
"""

import base64
import json
import sys
from pathlib import Path

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ROOT = Path(__file__).resolve().parents[1]
KEYS = ROOT / "demo_keys"
SIGNED = ROOT / "signed_inputs"
NAMES = [
    "startup_commercial_authorized",
    "startup_ip_authorized",
    "buyer_reliability_authorized",
    "calculation_receipt",
]


def canonical_bytes(path: Path) -> bytes:
    data = json.loads(path.read_text(encoding="utf-8"))
    return json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def main() -> int:
    KEYS.mkdir(exist_ok=True)
    for name in NAMES:
        key = Ed25519PrivateKey.generate()
        private_pem = key.private_bytes(
            serialization.Encoding.PEM,
            serialization.PrivateFormat.PKCS8,
            serialization.NoEncryption(),
        )
        public_pem = key.public_key().public_bytes(
            serialization.Encoding.PEM,
            serialization.PublicFormat.SubjectPublicKeyInfo,
        )
        private_path = KEYS / f"DEMO_ONLY_{name}_private.pem"
        private_path.write_bytes(private_pem)
        private_path.chmod(0o600)
        (KEYS / f"{name}_public.pem").write_bytes(public_pem)
        signature = key.sign(canonical_bytes(SIGNED / f"{name}.json"))
        (SIGNED / f"{name}.sig.b64").write_text(base64.b64encode(signature).decode("ascii") + "\n", encoding="ascii")
        print(f"new demo key and signature: {name}")
    print("Done. Demo-only keys are in demo_keys/; never use them in production.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
