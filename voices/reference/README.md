# Permanent production voice reference assets

This directory is **permanent**. Its approved reference audio files are never temporary build outputs.

- `english_af_heart_096.wav` is the approved Kokoro `af_heart` / speed 0.96 baseline. The Kokoro smoke-test workflow creates it only after audible synthesis QA; it must never overwrite an existing approved baseline automatically.
- Keep generated per-video WAV files in temporary Actions artifacts separately. Those may expire after seven days; the permanent baseline must not.
- Cleanup/retention scripts MUST explicitly exclude `voices/reference/**`, `config/approved_voices.json`, and `scripts/approved_voice.py`. No age-based cleanup is permitted for these assets.
- New reference voices require human approval and a distinct filename/version. Do not replace or delete a baseline without explicit approval.
- The sample is a regression/reference audio clip, not the entire synthesis model. New narration still uses the locked Kokoro engine and `af_heart`.
- Periodically check that the committed file exists and matches the stored checksum. Git history retains old versions but is not a substitute for an independent backup.

- `korean_sarah_f1_110.wav`: permanent reference extracted from the verified audible Korean Supertonic 3 Sarah/F1 1.1-speed draft. The Korean draft workflow creates it if missing, NEVER overwrites it; temporary output retention never applies. Its creation must be verified separately before claiming the file exists.
