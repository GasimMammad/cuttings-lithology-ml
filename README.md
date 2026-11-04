# Lithology from drill-cuttings photographs

Code from the drill-cuttings part of my MSc thesis, *Looking for Sinkites* (University of Manchester, 2026). It asks a simple question: can photographs of drill cuttings tell you whether a depth interval is sand or clay, in the shallow overburden where operators rarely run wireline logs?

The pipeline has two parts:

1. **Supervised classification.** Labels come from wireline gamma ray (shale volume), and models are trained on cuttings photographs and tested on wells they have never seen.
2. **A CIELAB "green index" for glauconite.** This is a fixed colour test calibrated on one well, then applied unchanged to ten others to see whether it picks out the glauconitic Utsira Formation.

Data are released Norwegian North Sea wells (cuttings photographs, LAS logs, XRF and mud logs). The data are not included here.

## What came out of it

The negative results are as much the point as the positive ones.

- **Image classifiers did not generalise between wells.** Four models (CNN on colour, CNN on greyscale, and logistic regression on 15 engineered features with and without colour) were tested with leave-one-well-out cross-validation. The 95% confidence interval on balanced accuracy spans 0.50 for every model, so none can be told apart from chance.
- **XRF could not be used as an independent label.** SiO₂/Al₂O₃ against shale volume changed sign between wells (Spearman ρ from −0.28 to +0.30), because of instrument sensitivity and barite from the drilling mud.
- **Barite turned out to be useful as a contamination covariate.** Predictions were checked against Ba (ppm) and against depth, to make sure models were not learning mud additives or depth trends instead of lithology.
- **The green index works as a positive-only test.** With thresholds frozen on 34/4-6, it fired on the Utsira Formation in five of the seven wells that have photographs inside the Utsira interval, and missed two at 3.6 to 3.7 times background.

## How the pipeline is organised

The scripts are numbered in the order they run. Every path and parameter lives in `config.py`.

| Step | Script | What it does |
|---|---|---|
| 1 | `01_inventory.py` | Lists what is on the data drive: wells, folders, file names, image sizes |
| 2 | `02_build_index.py` | Parses well and depth from every photo filename (dry run first, then `--commit`) |
| 3 | `03_make_labels.py` | Converts gamma ray to shale volume with geologically anchored end members per zone, and keeps a label only if every log sample within ±3 m falls in the same class |
| 4 | `04_prepare_patches.py` | Crops each photo to a fixed geometry and cuts it into 224 px patches |
| 5 | `05_train.py` | Trains a ResNet-18 (ImageNet weights) with a two-tier validation: within-well and leave-one-well-out |
| 6 | `06_predict_log.py` | Turns predictions into a sand-fraction curve against depth |
| 7 to 10 | `07_extract_features.py` to `10_tier1_balanced.py` | Engineered features (`features.py`), a three-way model comparison on identical folds, leakage checks and the report |
| 11 | `11_biostrat_compile.py` | Compiles the NPD Bulletin 10 age framework for the Tampen wells |
| 12 and 14 to 19 | `12_glauconite_test.py`, `15_` to `19_` | Green index: calibration, colour comparability across wells, all-well run, statistics, figures and a photo montage for visual checks |
| 20 to 24 | `20_controls_34_7_6.py` to `24_figures_34_7_6.py` | Pre-registered controls, diagnostic and target run for well 34/7-6 |

`13_a14h_lithology.py` is a separate plot of the 34/8-A-14 H mud log. `run_final.sh` and `run_final2.sh` chain steps 7 to 10 together.

## Design choices worth knowing about

- **Thresholds are frozen before evaluation.** The green index gate (a* < −5.0, C* ≥ 12.0, 15 < L* < 80) was calibrated only on 34/4-6, using the Utsira at 1210 to 1250 m as the positive control and the Upper Pliocene diamicton as background. The feature list in `features.py` was also fixed before any model was scored.
- **Validation splits by well, not at random.** Patches from one well are not independent samples, so a random split would leak.
- **Shale volume instead of raw gamma ray.** Absolute GR is not comparable between these wells (different tool vintages and contractors), so each zone uses named sand and shale intervals as end members.

## Running it

Python 3.11 or later. On Apple Silicon, PyTorch uses the MPS backend.

```bash
pip install -r requirements.txt
```

Set `SSD_ROOT`, `WELL_ROOTS` and `WORK_DIR` at the top of `config.py`, then:

```bash
python 01_inventory.py
python 02_build_index.py            # check the parsed depths, then:
python 02_build_index.py --commit
python 03_make_labels.py
python 04_prepare_patches.py
python 05_train.py
python 06_predict_log.py --well 34_4-6
```

Outputs (tables, models and figures) are written to `WORK_DIR`, not to the data drive.

## Status

This is research code written for one thesis and one dataset. It is not a general-purpose package, and the well names, depth zones and file layouts in `config.py` are specific to that data.

---

Gasim Mammadov · PhD candidate, The University of Manchester · Supervisor: Prof. Mads Huuse
