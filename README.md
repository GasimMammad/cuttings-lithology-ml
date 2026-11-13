# What can a model learn from photographs of drill cuttings?

Code and results for the drill-cuttings part of my MSc dissertation,
*Looking for Sinkites* (University of Manchester, September 2026), and for
the follow-up work done after submission (November 2026).

The data are released Norwegian North Sea wells: photographs of washed
cuttings bags, handheld XRF on the same bags, wireline logs, mud logs and
well reports for 11 wells. **The data are not in this repository.**

- The tag `v1-dissertation` marks the code as it stood for the dissertation.
- `main` now also holds the follow-up, v2 to v10. The follow-up scripts start
  at number 25. Five v1 files were extended for it (`config.py`,
  `features.py`, `03_make_labels.py`, `04_prepare_patches.py`,
  `12_glauconite_test.py`); the tag keeps them as they were.

## What came out of it

Every question was written down, with its pass rule, before it was run.
Models were always tested on wells they had not seen. Negative results are
reported as such.

| Question | Answer | Where |
|---|---|---|
| Can photographs separate sand from clay, with labels from gamma ray? | Not with three labelled wells (v1: at chance). With ten wells, only at the scale of zones (median held-out AUC 0.73), and no better than depth within the well | `V3_RESULTS.md` |
| Can photographs predict the chemistry of the same bag? | **Yes, weakly, in every well.** Si/Al: median rank correlation +0.32 in 11 of 11 held-out wells. K, Fe, Ca, Ti and Zr over Al also pass (+0.10 to +0.28); Fe, Ca and Ti count as signal beyond Si/Al and mud (robustly two axes, Fe-Ti and Ca), mostly through colour | `V7_RESULTS.md` step 1, `V8_RESULTS.md` A |
| When does it work? | Where the chemistry varies. Agreement follows the spread of Si/Al between wells (+0.78) and within wells (not separated from measurement noise) | `V8_RESULTS.md` B |
| Does the prediction follow the wellsite geologist's sand percentage? | Weakly in the clay-rich Tertiary (+0.13). Below the Cretaceous, where sandstone is common, +0.50 (five locations; an amended, exploratory test) | `V7_RESULTS.md` step 3, `V8_RESULTS.md` D, `V9_RESULTS.md` K2b |
| Does fine-tuning a network help? | No detectable gain over frozen features (three seeds) | `V8_RESULTS.md` C |
| Can a colour or pellet detector find glauconite? | No. The colour index of the dissertation is a green-hue index; a new detector fired on 22 % of Lista Formation bags | `GLAUCONITE_CORRECTIONS.md`, `V7_RESULTS.md` step 2 |
| Can photographs place stratigraphic tops in an unseen well? | No. Median error 65 m against 43 m for the nearest offset well | `V10_RESULTS.md` S |
| What is the vertical resolution of cuttings? | Could not be measured with these wells | `V10_RESULTS.md` R |
| Do the cuttings say anything about the origin of the sands (sinkites)? | No evidence for; limited compositional evidence against a glauconitic Utsira source. The decisive test is age, and no sidewall cores exist | `V6_RESULTS.md` |

The consolidated tables, methods text and limitations are in
`THESIS_NOTES.md`. `THESIS_CHECK.md` lists the four statements in the
dissertation that the follow-up changes. `CONFERENCE_NOTES.md` holds the
talk outline.

**Limits that apply to everything here.** Eleven wells from two areas, all
used in every round, so no result is a fresh hold-out. A bag mixes 3 to
10 m of hole and includes cavings. Photographs also see drilling mud (they
predict barium). The mud-log labels were read by AI readers; there is no
human key.

## How the work was run

1. A plan with the test, the statistic and the pass rule was committed.
2. A reviewer criticised the plan; amendments were committed.
3. The code was committed before the run.
4. Each test was run once. Deviations are written into the results file.
5. The reviewer checked every number against the saved result files.

The reviewer was an AI agent, not a person. The plans are `V2_PLAN.md` to
`V10_PLAN.md`; the results are `V3_RESULTS.md` to `V10_RESULTS.md`;
`PROJECT_LOG.md` is the day-by-day record with commit hashes.

## Which script produces which result

All paths and parameters are in `config.py`. Scripts write to `WORK_DIR`
(`~/sinkite_ml_work_v2`); the tables and figures that the results files
quote are copied to `results/`.

| Stage | Scripts | Output |
|---|---|---|
| v1 (dissertation) | `01` to `24` | see the README at the tag `v1-dissertation` |
| v2 inputs | `25_v2_index`, `26_v2_tiles`, `27_v2_embed`, `28_v2_features` | photo index, tiles, ResNet-50 embeddings, 15 colour and texture features |
| v2 sand/clay, ten wells | `29_v2_evaluate`, `30_v2_figures`, `31_v2_cnn`, `32_v2_report` | `results/summary.json`, `results/v2_fig*` |
| v3 baselines and first XRF test | `33` to `41` | `results/v3/` |
| v4 core photographs (stopped at a reliability gate) | `42` to `49` | `results/v4/` |
| v5 adjudication by a panel of AI agents | `50_v5_unseal` | `results/v5/` |
| v6 glauconite and the sinkite question | `51_v6_xrf_glauconite` | `results/v6/` |
| v7 step 1, photo to chemistry | `52_v7_photo_to_xrf`, `52a`, `52b` | `results/v7/step1_*` |
| v7 step 2, pellet detector | `53_v7_pellet_blobs`, `53b_v7_pellet_eval` | `results/v7/step2*` |
| v7 step 3, Tertiary mud logs | `54` to `58`, extras `60` to `62` | `results/v7/step3/` |
| v7 X1 and v8 C, fine-tuning | `59_v7_cnn_sial` (`train`, `eval`, `evalseeds`, `trainx`) | `results/v7/x1/`, `results/v8/x1_seeds_results.json` |
| v8 A and B, more elements and where it works | `63_v8_elements_when` (`A`, `B`, `preT`) | `results/v8/A_*`, `B_*` |
| v8 D, mud logs below the Cretaceous | `64_v8_jt_tiles`, `66_v8_jt_readers`, `67_v8_jt_score` | `results/v8/jt_*` |
| v8 E figures | `65_v8_figures` | `results/v8/fig_v8_*` |
| v9 checks | `68_v9_checks` (`k2b`, `k2c`, `k3`), `69_v9_k1_ocr` | `results/v9/` |
| v10 tops and step response | `70_v10_strat`, `71_v10_step` | `results/v10/` |
| v9 and v10 figures | `72_v10_figures` | `results/v10/fig_v10_tops`, `results/v9/fig_v9_mudlog_tile` |

## Running it

Python 3.13. On Apple Silicon, PyTorch uses the MPS backend.

```bash
pip install -r requirements-lock.txt     # exact versions used for the results
# or: pip install -r requirements.txt    # unpinned
```

Set `SSD_ROOT` and `WORK_DIR` at the top of `config.py`. The data drive is
only read. Then, for the main result:

```bash
python 25_v2_index.py && python 26_v2_tiles.py && python 27_v2_embed.py && python 28_v2_features.py
python 52_v7_photo_to_xrf.py             # photo -> Si/Al, leave one well out
python 63_v8_elements_when.py A          # more elements
python 65_v8_figures.py
```

Two steps cannot be rerun from code alone. The mud-log tiles were read by
AI agents (their raw readings are saved in `results/v7/step3/readers/` and
`results/v8/readers/`), and the report search in `69_v9_k1_ocr.py` needs
PyMuPDF and the macOS text recogniser in `tools/ocr.swift`.

## Use of AI

In the follow-up (v2 to v10) an AI assistant (Anthropic Claude, through
Claude Code) drafted the plans, wrote and ran the code, read the mud-log
tiles and the well reports, and acted as reviewer, under my direction. The
full statement is in `THESIS_NOTES.md`, sections 5 and 7e. The dissertation
itself (v1) carries its own, narrower declaration.

## Status

Research code for one dataset. Well names, depth zones and file layouts in
`config.py` are specific to it.

---

Gasim Mammadov · PhD candidate, The University of Manchester · Supervisor: Prof. Mads Huuse
