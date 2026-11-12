# Conference notes: the machine-learning part of "Looking for Sinkites"

Working notes for the talk in early December 2026. Not a slide deck. Every
number comes from V2-V8 results files in this repository; the consolidated
tables are in THESIS_NOTES.md (sections 1 and 7). Lines marked PENDING wait
for v8 parts C and D.

## 1. One-sentence message

Photographs of drill-cuttings bags carry a weak but repeatable chemical
signal that transfers to wells the model has never seen; they do not
identify sand beds, and they do not find sinkites.

## 2. Abstract (about 250 words, draft)

Cuttings photographs exist for thousands of samples in released Norwegian
wells, but it is unclear what a model can learn from them. Using 11 wells
from the northern North Sea (Tampen area and block 24/9), about 5,000
photographed cuttings bags and handheld-XRF analyses of the same bags, we
tested a series of questions, each fixed in a written plan before it was
run, with one well held out at a time.

A first attempt to classify sand against clay from gamma-ray labels did not
transfer between wells. With more labels and per-well standardisation, the
photographs separated sand-prone from clay-prone intervals (median AUC
0.73), but no better than depth within the well. The same photographs do
predict the chemistry of the bag: the local variation of Si/Al is recovered
in all 11 held-out wells (median rank correlation +0.32), and Fe, Ca and Ti
ratios carry further signal, mostly through colour. Agreement is highest
where the chemistry varies most, which explains the one well where it
fails. Against wellsite sand percentages digitised from 1980s mud logs the
same model agrees only weakly in the clay-rich Tertiary (+0.13 in six
wells) but clearly in the sandstone-rich Jurassic-Triassic (+0.52 in six of
six wells); two mud logs of one well agree with each other at only +0.42. A detector for glauconite pellets
failed its specificity test: it responds to green claystone. Fine-tuning a
network gave no detectable gain over frozen features.

For the geological question, the photographs and XRF give no evidence for
sinkites in the Oligocene sands; the decisive data (sidewall cores in the
sands) do not exist. The practical result is a cheap, bag-scale chemical
log from photographs, with a known limit on what it can resolve.

## 3. Key messages (in the order to say them)

1. **Negative first.** Sand/clay classification from photographs did not
   transfer between wells (v1: every confidence interval contained 0.50).
2. **Interval scale, not bed scale.** With ten labelled wells it works at
   the scale of zones (AUC 0.73, p 0.039) but does not beat depth within
   the well (p 0.15).
3. **Chemistry transfers.** Photo -> Si/Al of the same bag: +0.32, 11 of 11
   held-out wells, p 0.0005. This is the solid result.
4. **More than one element.** K, Fe, Ca, Ti and Zr over Al are all
   predicted (+0.10 to +0.28). Robustly two axes beyond Si and Al: Fe(-Ti)
   and Ca. It is mostly colour.
5. **You can tell where to trust it.** Agreement follows the spread of the
   chemistry (between wells +0.78, p 0.003; within wells p 0.014). The
   model's own output varies more where it is more right.
6. **Against wellsite sand percentages it depends on the section.** In
   the clay-rich Tertiary: +0.13 (p 0.047, six wells), no better than
   colour, and two mud logs of the same well agree at only +0.42. Below the
   Cretaceous, where sandstone is 40-75 % of the cuttings: +0.52 in six of
   six wells (p 0.016), as good as measured Si/Al (+0.51). The second
   number comes from a test whose eligibility rule was amended before the
   photographs were joined: say so.
7. **Things that did not work, stated as such.** Glauconite-pellet detector
   (22 % false positives in the Lista Formation); fine-tuning (no gain).
8. **Sinkites.** No evidence for them; limited compositional evidence
   against a glauconitic Utsira source; the age test is impossible without
   sidewall cores.

## 4. Talk outline (12 slides; what each must show)

| # | slide | must show | source |
|---|---|---|---|
| 1 | Title, question | cuttings photo, one sentence: what can a model learn from these? | - |
| 2 | Data | map or list of 11 wells; one bag photo; bag = 3-10 m of hole; XRF on the same bag | THESIS_NOTES 4 |
| 3 | How each test was run | plan committed -> code committed -> run once -> reviewed; one well held out | V2-V8 plans |
| 4 | Sand/clay from GR labels | v1 negative; v2 AUC 0.73 but equal to depth-in-well | THESIS_NOTES 1a, results/v3 figures |
| 5 | Chemistry: the main figure | overview figure, 11 wells, measured vs predicted Si/Al | results/v8/fig_v8_overview.png |
| 6 | Best, middle, worst | detail figure with gamma ray and mud-log sand | results/v8/fig_v8_detail.png |
| 7 | More elements | table of five ratios; which survive the Si-and-Al and mud controls | V8_RESULTS A |
| 8 | Where it works | scatter: per-well rho against spread of Si/Al (11 points) | results/v8/fig_v8_where.png |
| 9 | Mud logs as labels | one tile, the two-reader design; Tertiary +0.13 against Jurassic-Triassic +0.52; two logs of one well +0.42 | V7_RESULTS step 3, X2; V8_RESULTS D |
| 10 | What failed | glauconite detector on Lista; fine-tuning | V7_RESULTS step 2, X1 |
| 11 | Sinkites | three alternatives, what the data can and cannot decide | V6_RESULTS |
| 12 | Take-home and limits | the one-sentence message; 11 wells; bag scale; mud residue; no human key | THESIS_NOTES 7c |

## 5. Figures available now

- results/v8/fig_v8_overview.png / .pdf: measured and photo-predicted Si/Al
  against depth, 11 wells, ordered by agreement.
- results/v8/fig_v8_detail.png / .pdf: best (34/7-9), middle (34/7-6) and
  worst (34/8-3) well with gamma ray and mud-log sand.
- results/v3/v3_fig1_baselines.png, v3_fig2_xrf_shallow.png: sand/clay AUC
  against the depth and bag-weight baselines; the first XRF test.
- results/v8/fig_v8_where.png / .pdf: per-well agreement against the spread of
  Si/Al, 11 points (slide 8).
- Still to make if wanted:
  one annotated mud-log tile (slide 9).

## 6. Questions to expect

- **"Is it just colour?"** Largely, yes. Mean colour alone gives +0.24 for
  Si/Al against +0.32 for the embeddings, and for Fe, Ca and Ti simple
  colour and texture features do as well as the network. Colour is a
  legitimate carrier: it is what a geologist uses too.
- **"Is it drilling mud?"** Partly possible. The photographs also predict
  barite (+0.31). Partialling out Ba, Ca and Cl leaves Si/Al at +0.33, but
  bentonite cannot be separated, and an ilmenite weighting agent has not
  been ruled out for Fe-Ti.
- **"Why not sand?"** Si/Al is quartz plus biogenic silica against clay. In
  the Hordaland Group opal, tuff and glauconite move it. Against gamma-ray
  sand labels the Si/Al prediction is no better than the earlier model.
- **"Only 11 wells?"** Yes, and all were used in earlier rounds. Each test
  was fixed beforehand, but none is a fresh hold-out. With 11 wells the
  smallest possible p is 0.0005; with six, 0.016.
- **"Who read the mud logs?"** Two AI readers of different models, on
  tiles made by a script, blind to photographs and chemistry. They agree
  with each other; there is no human key. Say this before being asked.
- **"Why does 34/8-3 fail?"** Its Si/Al is nearly flat (second-smallest
  spread of the 11 wells), so there is little to predict. A fine-tuned
  network reached +0.31 there in one run. PENDING: whether that repeats
  with other seeds (v8 C).
- **"Does deep learning help?"** Frozen ImageNet features plus ridge
  regression is the model of record. Fine-tuning gave no detectable gain.
- **"So where are the sinkites?"** Not shown. The photographs cannot date a
  sand, and no sidewall cores exist in the target sands. Use the
  supervisor's definition of "sinkite"; do not attribute it to a paper
  without reading it.

## 7. Do not claim

- "Sand detector", "lithology classifier", or anything at bed scale.
- "Glauconite detector".
- That the mud-log result validates the photographs: it narrowly met its
  criterion, no better than colour, and adds nothing once Si/Al is known.
- That the seven-well mud-log number (+0.17) is a result: it depends on a
  deviation from the plan.
- That the readers are accurate: they are consistent.
- That the Jurassic-Triassic mud-log result (+0.52) is a pre-registered
  test: it is an amended, exploratory one. Six wells, one area, twin wells.
