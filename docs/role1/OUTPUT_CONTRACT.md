# Contract A: what the vision module hands to Roles 2, 3 and 4

This is the output of Role 1. Every call returns **either** a damage report (Contract A) **or** a `VisionError`, never both and never an exception. The source of truth is `src/vision/schema.py`; the machine-readable schema is `schemas/contract_a.schema.json` (CI fails if it drifts from the code).

## How to call it

```python
from src.vision import assess_damage, load_image, make_provider

result = assess_damage(
    images=[load_image("front.jpg"), load_image("side.jpg")],    # 1 to 5 photos
    vehicle={"make": "Maruti Suzuki", "model": "Swift", "year": 2021, "fuel": "petrol"},
    provider=make_provider("gemini"),                              # or "groq"
    user_description="Hit a pole while reversing",
    claim_id="CLM-20261020-001",                                   # Role 4 should pass this
)

if result.ok:
    contract_a = result.report.model_dump()     # dict, shape below
else:
    error = result.error.model_dump()           # dict, shape below
```

Run from the repo root. Keys come from `.env` (`GEMINI_API_KEY`, `GROQ_API_KEY`). No key is needed to build against the contract: use the files in `mocks/`.

## Contract A (success)

```json
{
  "claim_id": "CLM-20261020-001",
  "vehicle": {"make": "Maruti Suzuki", "model": "Swift", "year": 2021, "fuel": "petrol"},
  "user_description": "Scraped a parking pillar while turning out of the basement",
  "damages": [
    {
      "part": "front_bumper",
      "damage_type": "scratch",
      "severity": "moderate",
      "confidence": 0.9,
      "image_index": 0,
      "notes": "Paint scraped through to black primer on the right side, roughly 20 cm"
    }
  ],
  "image_quality_flags": [],
  "model_used": "gemini-3.5-flash-lite",
  "prompt_strategy": "v4_best"
}
```

| Field | Type | Rules |
|---|---|---|
| `claim_id` | string | `CLM-YYYYMMDD-NNN`. Generated only if the caller passes none; Role 4 should own ids. |
| `vehicle` | object | Copied from the user form, never filled by the model. `year` is 1980 to 2100. |
| `user_description` | string | Copied from the input. Can be empty. |
| `damages` | list | Can be empty (no damage seen). One entry per (`part`, `damage_type`), see merging below. |
| `damages[].part` | enum | One of the 26 parts below. |
| `damages[].damage_type` | enum | `dent`, `scratch`, `crack`, `glass_shatter`, `lamp_broken`, `tire_flat` (the 6 CarDD classes). |
| `damages[].severity` | enum | `minor`, `moderate`, `severe`. Meaning: [SEVERITY_RUBRIC.md](SEVERITY_RUBRIC.md). |
| `damages[].confidence` | number | 0.0 to 1.0, the model's own estimate. Not calibrated; use it for ordering, not as a probability. |
| `damages[].image_index` | int | 0-based index of the photo the damage was seen in. |
| `damages[].notes` | string | Free text. Approximate size (cm) goes here when the model gives one. Can be empty. |
| `image_quality_flags` | list of strings | `image_<index>_<issue>`, same 0-based index as `image_index`. Sorted, no duplicates. |
| `model_used` | string | Exact model id, e.g. `gemini-3.5-flash-lite` or `qwen/qwen3.8-27b`. |
| `prompt_strategy` | string | Prompt file id, with `+schema` when API schema enforcement was on, e.g. `v1_structured+schema`. |

**Parts (26):** `front_bumper`, `rear_bumper`, `bonnet`, `boot_lid`, `grille`, `roof`, `windshield`, `rear_windshield`, `left_headlamp`, `right_headlamp`, `left_taillamp`, `right_taillamp`, `left_orvm`, `right_orvm`, `front_left_door`, `front_right_door`, `rear_left_door`, `rear_right_door`, `front_left_fender`, `front_right_fender`, `left_quarter_panel`, `right_quarter_panel`, `front_left_tyre`, `front_right_tyre`, `rear_left_tyre`, `rear_right_tyre`.

Left and right are the **vehicle's own** sides, as seen by a driver sitting inside facing forward.

**Quality issues (8):** `blurry`, `too_dark`, `overexposed`, `low_resolution`, `too_far`, `partial_view`, `obstructed`, `no_vehicle`.

## VisionError (failure)

```json
{
  "claim_id": "CLM-20261020-006",
  "error_code": "invalid_model_output",
  "message": "The reply contained no JSON object. Return exactly one JSON object.",
  "attempts": 3,
  "last_raw_output": "I'm sorry, I can't tell what this photo shows.",
  "model_used": "gemini-3.5-flash-lite",
  "prompt_strategy": "v4_best"
}
```

| `error_code` | Meaning | What the UI should do |
|---|---|---|
| `bad_input` | Fewer than 1 or more than 5 photos. No model call was made. | Ask for 1 to 5 photos. |
| `invalid_model_output` | The model's reply failed validation even after 2 repair retries. | Ask for clearer photos, or retry. |
| `provider_error` | The API call failed (network, 5xx, bad request). | Retry later. |
| `quota_exhausted` | The free-tier daily quota ran out. | Switch provider or retry tomorrow. |

`attempts` counts model calls (first try plus repairs). `last_raw_output` is for debugging only; do not show it to users.

## Guarantees

- Every enum value is from the lists above. The reply is validated with Pydantic before a report is built; anything else becomes a `VisionError`.
- **Merging across photos:** the same (`part`, `damage_type`) seen in several photos is kept once, with the higher severity and the highest confidence. Different damage types on one part stay separate (a bumper with a dent and a crack gives 2 entries), so Role 2 can apply repair-or-replace per damage.
- `damages: []` with no flags means "no damage seen". `damages: []` with flags means "could not judge, ask for better photos".
- Role 1 never estimates prices or decides repair vs replace. That is Role 2.

## Notes per role

- **Role 2 (cost engine):** key repair-or-replace on (`part`, `damage_type`, `severity`). If you need one severity per part, take the worst across its entries.
- **Role 3 (RAG / policy):** `user_description` and `notes` are free text and may help retrieval; enums are stable and safe to filter on.
- **Role 4 (app):** pass your own `claim_id`. Show `image_quality_flags` as "Photo 2 is blurry" (`image_index + 1`); `src/vision/demo_app.py` has a `describe_flag` helper. Build the UI against `mocks/` before keys are set up.

## Mocks

5 real Contract A reports produced by the pipeline (Gemini 3.5 Flash-Lite, `v4_best`), plus one failure. Regenerate with `python -m scripts.make_mocks`.

| File | Car | What it covers |
|---|---|---|
| `contract_a_001_dev_01.json` | Maruti Suzuki Swift 2021, petrol | 3 damages; two on the front bumper (scratch + dent) kept as separate entries |
| `contract_a_002_eval_18.json` | Hyundai Creta 2022, diesel | **No damage**: `damages: []`, no flags |
| `contract_a_003_dev_04.json` | Tata Nexon 2023, petrol | 1 damage (windshield `glass_shatter`) |
| `contract_a_004_dev_05.json` | Honda City 2019, petrol | 4 damages: dent + scratch on each of the two left doors |
| `contract_a_005_dev_09.json` | Maruti Suzuki Baleno 2020, CNG | 1 damage plus **image quality flags** (blurry, low resolution, too dark) |
| `vision_error_example.json` | none | `VisionError` with `invalid_model_output` |

## Open proposals (need team sign-off, not in the contract yet)

1. **`needs_more_photos: bool`**: the task brief had it. It can be derived today as `len(image_quality_flags) > 0`, so it was left out to avoid changing Contract A alone.
2. **`approx_size_cm`**: the task brief had it as a number. It sits in `notes` as text for now. A number field would help Role 2 tell a 5 cm dent from a 30 cm one.
3. **Door glass part name**: there is no part for side windows, so door-glass photos were dropped from the eval set. Proposal: add `front_left_door_glass` and the other 3 sides.
4. **Merge key and flag index** (DECISIONS D19, D20): merge on (`part`, `damage_type`), and 0-based flag index matching `image_index`.

Any change to this contract goes to the whole group first.
