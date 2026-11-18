# Testing - what was actually run

| Area | How | Result |
|---|---|---|
| Language detection (Hindi, Hinglish, English, Tamil, Spanish, explicit override, short follow-up) | pytest `test_core.py` | PASS |
| Registration, login, duplicate email, wrong password, protected route | pytest | PASS |
| Chat saves language; other user cannot read the conversation | pytest (Ollama mocked) | PASS |
| TXT upload, invalid type rejected, library privacy, summarize/ask/generate (language passed to model, source parts returned) | pytest `test_modules.py` (Ollama mocked) | PASS |
| Planner CRUD, other user cannot edit task, analytics values, profile/theme update, delete document | pytest | PASS |
| Frontend TypeScript check + production build | `npm run build` | PASS |
| Server serves the built app; Ollama-unavailable error returned cleanly | live smoke test | PASS |

Total: 3 backend tests pass.

## Not tested here (please test on your PC)
- Real Ollama answers and real Hindi/Hinglish quality (depends on your model; Llama 3.2 3B is weaker in Indian languages than larger models).
- Microphone input, speech output and voice quality in your browser.
- PDF/DOCX extraction on your own files, and the visual layout in a real browser at all screen sizes.
- Long-document speed (summaries run chunk by chunk, synchronously).
