#!/usr/bin/env python3
"""
proofbundle#7 worked vector: temporal pre-registration anchored to Bitcoin via OpenTimestamps.

Produces the deterministic half of the example:
  pre-registration object -> RFC 8785 (JCS) canonical bytes -> SHA-256 canonicalRoot
The canonical bytes are written to preregistration.canonical.json so `ots stamp` commits
to exactly SHA-256(canonical bytes) == canonicalRoot.
"""
import hashlib, json, rfc8785

def commit(salt_hex: str, value: str) -> str:
    # commitment scheme: sha256( salt_bytes || utf8(value) )
    h = hashlib.sha256(bytes.fromhex(salt_hex) + value.encode("utf-8")).hexdigest()
    return "sha256:" + h

# --- revealed inputs (published so any verifier can recompute the commitments) ---
reveal = {
    "dataset": {"salt": "b3f1c2a4d5e6f708192a3b4c5d6e7f80", "value": "mmlu-redux/2026-06-01"},
    "model":   {"salt": "0a1b2c3d4e5f60718293a4b5c6d7e8f9", "value": "acme-llm-7b@sha256:9c1e...c0de"},
}

# --- the pre-registration object: what the producer commits to BEFORE running the eval ---
prereg = {
    "predicateType": "https://in-toto.io/attestation/eval-result/v0.1",
    "commitScheme": "sha256(salt||utf8(value))",
    "verdictRule": {"metric": "exact_match", "comparator": ">=", "threshold": 0.85},
    "commitments": {
        "dataset": commit(reveal["dataset"]["salt"], reveal["dataset"]["value"]),
        "model":   commit(reveal["model"]["salt"],   reveal["model"]["value"]),
    },
}

canonical = rfc8785.dumps(prereg)                 # RFC 8785 JCS canonical bytes
root = hashlib.sha256(canonical).hexdigest()      # canonicalRoot

with open("preregistration.canonical.json", "wb") as f:
    f.write(canonical)
with open("preregistration.pretty.json", "w") as f:
    json.dump(prereg, f, indent=2)

print("=== pre-registration object (pretty) ===")
print(json.dumps(prereg, indent=2))
print("\n=== RFC 8785 canonical bytes (utf-8) ===")
print(canonical.decode("utf-8"))
print("\ncanonical byte length:", len(canonical))
print("canonicalRoot (sha256 of canonical bytes):")
print("  sha256:" + root)
print("\n=== reveal (for independent recomputation of commitments) ===")
print(json.dumps(reveal, indent=2))
