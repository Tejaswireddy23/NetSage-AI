# Packet Tracer Lab Workspace

This directory deliberately contains **no generated `.pkt` files**. Cisco Packet
Tracer owns that binary format; an instructor or lab author must create each
working topology in Packet Tracer, introduce exactly one documented fault, and
save it at the path declared in `data/case_metadata.csv`.

Run `python scripts/create_lab_specs.py` after changing case data to create or
refresh documentation-only `README.md` and `expected.json` files for every case.
The command never creates, overwrites, or simulates a `.pkt` file.

For every lab, demonstrate: **WORKING → introduce one fault → BROKEN →
DIAGNOSE → human review → FIX → VERIFY → record result**. Use the case's supplied
show output as pre-fix evidence; post-fix output and screenshots are human/PT
artefacts and must be recorded as `NOT VERIFIED` until collected.
