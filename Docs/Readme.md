# examples/

Reference tooling for external auditors and curious engineers. Nothing in this directory should be deployed to production without adaptation.

## `verify_chain.py`

A standalone verifier for FoundLab evidence chains. Given a sequence of recibos and the public keys that signed them, the script validates four properties:

1. **Sequence continuity.** Records appear with consecutive `seq` values starting from 1.
2. **Chain linkage.** Each record's `prev_hash` matches the previous record's `this_hash`. The first record's `prev_hash` is 64 hex zeros (genesis).
3. **Hash recomputation.** Each record's `this_hash` equals `SHA-256(prev_hash || payload_hash)`.
4. **Signature validity.** Each record's `kms_signature` verifies against the public key declared in `kms_key_version`, over the bytes of `this_hash`.

If all four hold for every record, the script exits 0. If any record fails any check, the script exits 1 and prints the failing records to stderr.

### Sample data

Two files are provided as a self-contained demo:

- `sample_recibos.jsonl` — a five-record chain with synthetic payloads.
- `sample_public_keys.pem` — the matching ECDSA P-256 public key.

The sample key was generated locally for this demo. Real signing keys live in Cloud KMS HSM and never leave the HSM. The sample exists so an auditor can run the verifier end-to-end without any FoundLab infrastructure access.

### Running it

```bash
pip install cryptography

python verify_chain.py \
  --recibos sample_recibos.jsonl \
  --keys sample_public_keys.pem
```

Expected output (to stderr):

```
chain summary: 5/5 records valid, 0 failed
```

### Demonstrating tamper detection

To see the verifier fail on a modified chain, alter one byte of any field:

```bash
# Flip the last hex character of seq 3's payload_hash.
python -c "
import json
with open('sample_recibos.jsonl') as f:
    lines = f.readlines()
r = json.loads(lines[2])
ph = r['payload_hash']
r['payload_hash'] = ph[:-1] + ('0' if ph[-1] != '0' else '1')
lines[2] = json.dumps(r) + '\n'
with open('tampered.jsonl', 'w') as f:
    f.writelines(lines)
"

python verify_chain.py --recibos tampered.jsonl --keys sample_public_keys.pem
```

Expected: exit code 1, with a message indicating the `this_hash` mismatch at `seq=3`.

### What this script does *not* do

- It does not connect to BigQuery, Cloud KMS, or any FoundLab service. Adapting it to read from BigQuery is straightforward (`google-cloud-bigquery` plus a `SELECT * ORDER BY seq`); we leave that to the auditor's own environment.
- It does not validate **semantic correctness** of the recorded decision. If the recibo says "Gemini approved this transaction," the verifier confirms the recibo is intact and signed; it does not opine on whether the approval was right.
- It does not check **TrueTime monotonicity**. In production, recibos must have strictly non-decreasing `truetime_ts`. The check is straightforward to add and was omitted here to keep the reference small.
- It does not validate the **public key chain of trust**. In production, the `kms_key_version` should be cross-checked against Google's transparency log or an attestation report. The script trusts the PEM file the operator provides.

These omissions are deliberate. Adding them inflates the script past the point where an auditor will read every line — and reading every line is the point.

### License

`verify_chain.py` is licensed under Apache 2.0. See `../LICENSE-CODE`. Reuse it, fork it, ship it under a different name. We only ask that if you find a flaw, you open an issue.
