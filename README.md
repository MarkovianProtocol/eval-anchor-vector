# Worked vector: temporal pre-registration anchored to Bitcoin (OpenTimestamps)

This is the minimal, fully checkable example promised on in-toto/attestation#565: a
`committed-before-you-ran` proof that needs no trusted authority and no trust in the
producer's clock. It fleshes out the optional `anchors[]` field discussed there.

The claim an anchor makes is narrow and precise: *the pre-registration object existed by
time T*. It says nothing about the eval result itself, which the existing signature and
salted commitments already cover. It only makes the temporal ordering (committed, then ran)
verifiable by a third party.

---

## 1. The pre-registration object

What the producer fixes **before** running the eval: the verdict rule and salted
commitments to the dataset and model. Salts hide the identities while binding them.

```json
{
  "predicateType": "https://in-toto.io/attestation/eval-result/v0.1",
  "commitScheme": "sha256(salt||utf8(value))",
  "verdictRule": { "metric": "exact_match", "comparator": ">=", "threshold": 0.85 },
  "commitments": {
    "dataset": "sha256:d7c378231a1003f1a60f39b7a32a05e8e8d6e17f8d369d8fe98202974deca2cd",
    "model":   "sha256:9629760f251b473da0864d1f88b6c1919a9033877016935adf77713064d59680"
  }
}
```

### Reveal (so anyone can recompute the commitments)

```json
{
  "dataset": { "salt": "b3f1c2a4d5e6f708192a3b4c5d6e7f80", "value": "mmlu-redux/2026-06-01" },
  "model":   { "salt": "0a1b2c3d4e5f60718293a4b5c6d7e8f9", "value": "acme-llm-7b@sha256:9c1e...c0de" }
}
```

Check: `sha256( bytes.fromhex(salt) + utf8(value) )` reproduces each commitment above.

---

## 2. Canonical form and root (RFC 8785 / JCS)

Canonicalizing the object with RFC 8785 gives one byte string every implementation agrees
on (keys sorted, no insignificant whitespace, canonical number form):

```
{"commitScheme":"sha256(salt||utf8(value))","commitments":{"dataset":"sha256:d7c378231a1003f1a60f39b7a32a05e8e8d6e17f8d369d8fe98202974deca2cd","model":"sha256:9629760f251b473da0864d1f88b6c1919a9033877016935adf77713064d59680"},"predicateType":"https://in-toto.io/attestation/eval-result/v0.1","verdictRule":{"comparator":">=","metric":"exact_match","threshold":0.85}}
```

- canonical byte length: **366**
- **canonicalRoot = `sha256:5afa72991e876da463eb691749eac3424b992406b21cb0e21321d05ee9cc94aa`**

This root is the single value the anchor commits to. It is invariant for the life of the
object.

---

## 3. The `anchors[]` entry

An optional array on the predicate. Each entry binds the same `canonicalRoot`, so multiple
anchors are interchangeable evidence for the one "committed by time T" claim, and a relying
party picks the trust model it accepts.

```json
"anchors": [
  {
    "type": "ots",
    "canonicalRoot": "sha256:5afa72991e876da463eb691749eac3424b992406b21cb0e21321d05ee9cc94aa",
    "proof": "<base64 OpenTimestamps receipt, see section 4>"
  }
]
```

(An `rfc3161` entry over the identical root could sit alongside it for parties who prefer a
TSA. Same root, different trust model.)

---

## 4. The OpenTimestamps receipt

Produced by stamping the canonical bytes, so the receipt commits to exactly
`sha256(canonical bytes) == canonicalRoot`.

- receipt size: 1529 bytes (Bitcoin-confirmed, self-contained)
- receipt sha256: `848e2615d82da6dc37187a0986b1988d56cf0c4e3ab408b3f685fe0e5c59bf03`
- **Bitcoin attestation:** block **956857**, header time **2026-07-06 01:26:17 UTC** (unix 1783301177), block merkle root `bbe2b9a3952ef1e9236e377ddf9993f74a4cf0b77eaf7a807dec6984fee373a5`. The committed root provably existed by that block time.
- `proof` (base64, upgraded):

```
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
```

---

## 5. The pending -> confirmed workflow (the detail worth pinning in the spec)

This is where a naive verifier goes wrong, so state it explicitly.

At stamp time the receipt is **calendar-only (pending)**: the calendars have accepted the
root but no Bitcoin block commits to it yet. Right after stamping:

```
$ ots upgrade preregistration.canonical.json.ots
Calendar https://btc.calendar.catallaxy.com: Pending confirmation in Bitcoin blockchain
...
Failed! Timestamp not complete
```

After the calendars aggregate and the commitment lands in a Bitcoin block, the same command
succeeds and rewrites the receipt to be self-contained. For this vector it confirmed in
**block 956857**:

```
$ ots upgrade preregistration.canonical.json.ots     # succeeded
$ ots info  preregistration.canonical.json.ots
   ... verify BitcoinBlockHeaderAttestation(956857)
   # Bitcoin block merkle root bbe2b9a3952ef1e9236e377ddf9993f74a4cf0b77eaf7a807dec6984fee373a5
# committed root anchored in block 956857, header time 2026-07-06 01:26:17 UTC
```

Rules for implementers:

1. `canonicalRoot` is invariant across the upgrade. **Only the `proof` bytes change** when
   the Bitcoin attestation is grafted in.
2. A verifier **MUST** treat an un-upgraded (calendar-only) receipt as *the absence of a
   temporal anchor*, not a weaker one. A `PendingAttestation` proves nothing about Bitcoin
   time.
3. So the producer's upgrade step is a precondition for the anchor to count. The relying
   party should carry only upgraded receipts in a published attestation.

---

## 6. Verifier algorithm (offline, given a Bitcoin block-header source)

1. Recompute `sha256( RFC8785(prereg_object) )`; require it equals `anchors[i].canonicalRoot`.
2. Decode `anchors[i].proof`; require its committed digest equals that same root.
3. Walk the OTS proof to its `BitcoinBlockHeaderAttestation`; require the referenced block
   header is on the chain the verifier trusts (header source, no full node required).
4. Read the block's time `T`. The anchor establishes: the object existed by `T`.
5. Accept the pre-registration as `committed-before` iff `T <= run_start_time` recorded in
   the eval attestation.

No calendar, TSA, or producer clock is trusted in steps 1 to 5.

---

## 7. Reproduce

```bash
python3 -m venv pbenv
./pbenv/bin/pip install rfc8785 opentimestamps-client
./pbenv/bin/python build_vector.py                       # object -> canonical -> root
./pbenv/bin/ots stamp preregistration.canonical.json     # writes .ots (pending)
./pbenv/bin/ots upgrade preregistration.canonical.json.ots   # later, once Bitcoin confirms
./pbenv/bin/ots verify  preregistration.canonical.json.ots
```

Files in this directory: `build_vector.py`, `preregistration.pretty.json`,
`preregistration.canonical.json`, `preregistration.canonical.json.ots`.
