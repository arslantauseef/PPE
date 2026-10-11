# Offline CCTV SOP Monitor (POC)

This repository contains the first offline vertical slice for employee SOP monitoring. It intentionally separates **observed video facts** from **SOP decisions** and requires human review for possible noncompliance.

## Current capability

- Ingests structured observations from a detector/tracker adapter.
- Evaluates configurable zone policies for PPE/SOP requirements.
- Debounces alerts so one unclear frame does not create an incident.
- Emits one review event only after the configured number of consecutive clear noncompliance observations; compliant/unknown observations reset the debounce state.
- Stores observations and review events in local SQLite.
- Exports review events to CSV.
- Uses `UNKNOWN` when visibility or evidence is insufficient.

The detector, tracker, and Windows SmartPSS capture adapters are intentionally interfaces at this stage. No identity is inferred from a track ID, and no real employee biometrics are required.

## Setup and demo

```bash
python -m venv .venv
python -m pip install -e .[dev]
python -m cctv_monitor demo --database demo.sqlite3 --csv events.csv
python -m pytest
```

For a recorded MP4, run the local CPU detector and write an annotated video plus local reports:

```bash
python -m cctv_monitor video input.mp4 --output annotated.mp4 --database events.sqlite3 --csv events.csv
```

The built-in OpenCV HOG detector identifies people only. PPE classes are not inferred by this detector and must not be represented as detected; a PPE model adapter is a separate milestone.

To inspect locally stored events in a browser or integrate them with a future frontend:

```bash
python -m cctv_monitor dashboard --database events.sqlite3
```

The local page is available at `http://127.0.0.1:8765/`; JSON events are at `/api/events`.

The demo uses synthetic observations only. It creates a local SQLite database and CSV report.

## Status vocabulary

`COMPLIANT`, `POSSIBLE_NONCOMPLIANCE`, `UNKNOWN`, and `NOT_EVALUATED` are evidence states, not disciplinary outcomes. A real deployment must add consent, retention/deletion controls, access restrictions, model/license review, and authorized Windows screen capture testing.

