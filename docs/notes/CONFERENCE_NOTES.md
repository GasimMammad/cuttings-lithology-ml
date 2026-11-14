# Conference notes: the machine-learning part of "Looking for Sinkites"

Working notes for the talk in early December 2026. Not a slide deck. Every
number comes from V2-V10 results files in this repository; the consolidated
tables are in THESIS_NOTES.md (sections 1 and 7).

## 1. One-sentence message

Photographs of drill-cuttings bags carry a weak but repeatable chemical
signal that transfers to wells the model has never seen; they do not
identify sand beds, and they cannot test the origin of the sands.

## 2. Abstract (about 250 words, draft)

Using 11 northern North Sea wells, 5,038 photographed cuttings bags and
handheld-XRF analyses of the same bags, we asked what a model can learn
from cuttings photographs. Each question was fixed in a written plan before
it was run, with one well held out at a time.

Classifying sand against clay from gamma-ray labels did not transfer
between wells at first; with more labels it worked at the scale of zones
(median AUC 0.73), but no better than depth within the well. The
photographs do predict the chemistry of the bag: the local variation of Si/Al is weakly predicted
in all 11 held-out wells (median rank correlation +0.32), and Fe, Ca and Ti
ratios carry further signal, mostly through colour. Agreement is highest
where the chemistry varies most, consistent with the one well where it
fails (measurement noise predicts the same pattern). Against wellsite sand
percentages digitised from 1980s mud logs, the model agrees only weakly in
the clay-rich Tertiary (+0.13, six wells). Below the Cretaceous, where
sandstone is common, the pre-Tertiary photo model agrees at +0.50 (5 of 5
locations; an exploratory test whose eligibility rule was amended after
the labels were read), about as well as measured Si/Al. A detector for
glauconite pellets failed its specificity test, fine-tuning a network gave
no detectable gain over frozen features, and the photographs placed
stratigraphic tops less well than an offset well.

The cuttings add no evidence for a sinkite origin of the
Oligocene sands, and none that tests it; the decisive data, sidewall cores, do not exist. The
practical result is a cheap, bag-scale chemical log from photographs, with a known limit on what
it resolves.

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
5. **Skill follows the spread of the chemistry** (between wells +0.78,
   p 0.003; within wells p 0.014). Noise attenuation predicts the same
   pattern. Within wells, intervals where the prediction moves more agree
   better (p 0.003); between wells this is weaker (p 0.07). It ranks
   intervals; it certifies none.
6. **Against wellsite sand percentages it depends on the section.** In
   the clay-rich Tertiary: +0.13 (p 0.047, six wells), no better than
   colour, and two mud logs of the same well agree at only +0.42. Below the
   Cretaceous, where sandstone is 35-81 % of the cuttings: +0.50 with the
   twin wells held out together (5 of 5 locations, p 0.031; +0.52 leaving
   one well out), as good as measured Si/Al (+0.51). This exploratory number comes
   from a test whose eligibility rule was amended before the photographs
   were joined: say so. It also uses a different (pre-Tertiary) model;
   colour features alone give +0.47; the partial given Si/Al is +0.15, an
   upper bound. The digitised labels there follow wireline gamma ray
   (-0.26, 6 of 6 wells); the Tertiary labels (-0.14) do not meet the
   pre-declared bar. An instrument key, not a human key.
7. **Things that did not work, stated as such.** Glauconite-pellet detector
   (22 % false positives in the Lista Formation); fine-tuning (no
   detectable gain); stratigraphic tops (photo error 65 m against 43 m for
   an offset well; worse in 8 of 10 locations); the vertical resolution of
   cuttings (could not be measured).
8. **Sinkites.** The cuttings add no evidence for them; limited
   compositional evidence against a glauconitic Utsira source; the age
   test is impossible without sidewall cores. The case for sinking is the
   thesis's seismic and log evidence at the Visund SE mound, which this
   work does not test and does not contradict.

## 4. Talk outline (12 slides; what each must show)

| # | slide | must show | source |
|---|---|---|---|
| 1 | Title, question | cuttings photo, one sentence: what can a model learn from these? | - |
| 2 | Data | map or list of 11 wells; one bag photo; bag = 3-10 m of hole; XRF on the same bag | THESIS_NOTES 4 |
| 3 | How each test was run | plan committed -> code committed -> run once -> reviewed; one well held out | V2-V10 plans |
| 4 | Sand/clay from GR labels | v1 negative; v2 AUC 0.73 but equal to depth-in-well | THESIS_NOTES 1a, results/v3 figures |
| 5 | Chemistry: the main figure | overview figure, 11 wells, measured vs predicted Si/Al | results/v8/fig_v8_overview.png |
| 6 | Best, middle, worst | detail figure with gamma ray and mud-log sand | results/v8/fig_v8_detail.png |
| 7 | More elements | table of five ratios; which survive the Si-and-Al and mud controls | V8_RESULTS A |
| 8 | Where it works | scatter: per-well rho against spread of Si/Al (11 points) | results/v8/fig_v8_where.png |
| 9 | Mud logs as labels | one tile, the two-reader design; Tertiary +0.13 against Jurassic-Triassic +0.50 (five locations; amended, exploratory; different models; measured Si/Al +0.18 against +0.51); two logs of one well +0.42; gamma-ray key -0.26 below base Cretaceous | V7_RESULTS step 3, X2; V8_RESULTS D; V9_RESULTS K2b, K3 |
| 10 | What failed | glauconite detector on Lista; fine-tuning; stratigraphic tops against an offset well | V7_RESULTS step 2, X1; V8_RESULTS C; V10_RESULTS S |
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
  bentonite cannot be separated. For Fe-Ti: the mud-materials tables of
  ten wells list barite as the only solid weighting material; 24/9-3 has no materials list, so an iron-titanium weighting agent is not excluded there.
- **"Why not sand?"** Si/Al is quartz plus biogenic silica against clay. In
  the Hordaland Group opal, tuff and glauconite move it. Against gamma-ray
  sand labels the Si/Al prediction is no better than the earlier model.
  Below the Cretaceous, where Si/Al does follow sand (+0.51), the model
  follows the wellsite sand fraction (+0.50, five locations; amended, exploratory test).
- **"Only 11 wells?"** Yes, and all were used in earlier rounds. Each test
  was fixed beforehand, but none is a fresh hold-out. With 11 wells the
  smallest possible p is 0.0005; with six, 0.016.
- **"Who read the mud logs?"** Two AI models, on tiles made by a
  script, blind to photographs and chemistry. They agree
  with each other; there is no human key. Say this before being asked.
  An instrument check exists: below the Cretaceous the digitised sand
  fraction follows wireline gamma ray (-0.26, 6 of 6 wells), as well as measured Si/Al does; the Tertiary labels do not meet
  the bar (-0.14). It is not a human key. None of the eight sheets prints a gamma-ray track.
- **"Why does 34/8-3 fail?"** Its Si/Al is nearly flat (second-smallest
  spread of the 11 wells), and the frozen model finds nothing there. A
  fine-tuned network gave +0.21 to +0.41 there in three runs with
  different seeds, so it may not be all noise. It still gave +0.17 to
  +0.40 with its sidetrack taken out of training. Three seeds cannot
  exclude a contribution of the sidetrack of up to about 0.2. One well, singled out
  after the first run: an observation, not a result.
- **"Does deep learning help?"** Frozen ImageNet features plus ridge
  regression is the model of record. Fine-tuning gave no detectable gain
  over frozen features of the same network in three runs (+0.38 against
  +0.33 medians; higher in 4 of 11 wells, p 0.52). The median moved from
  +0.31 to +0.46 between seeds: quote +0.38, never the best run.
- **"Can it pick formation tops?"** No. Tested against the official
  tops in 10 locations, the photo picks were 65 m off in the median against
  43 m for the nearest well, and worse in 8 of 10 locations. The bag
  chemistry did no better per location. At the base Cretaceous unconformity alone the median error was 25 m
  (5 of 8 within 30 m; two misses of about 200 and 250 m); singled out
  afterwards, descriptive.
- **"What is the vertical resolution?"** Not measured. A test at sharp
  gamma-ray steps had too few steps to give a number.
- **"So where are the sinkites?"** The cuttings cannot say. The thesis argues for
  sinking at the Visund SE mound from seismic volumetrics and logs. The
  photographs cannot date a sand, and no sidewall cores exist in the
  target sands of these eleven wells, so the cuttings neither support nor
  contradict it. The term is from Rudjord and Huuse (2025), as cited in
  the thesis (section 1.3); Løseth et al. (2013) is the injection model.
- **"The thesis says the colour index detects glauconite."** The
  follow-up withdrew that: it is a green-hue index and fires on green
  mudstones. The thesis used it in 4.7 and 5.4 to
  explain a glauconitic Utsira; that sentence no longer stands. Its
  numbered conclusions do not use it (THESIS_CHECK.md).
- **"How was AI used?"** More than in the thesis. The code was written with
  an AI coding assistant; the mud-log tiles, core photographs and well-report
  pages were analysed by AI models; AI checked the plans and numbers and helped draft the text. Say so
  before being asked; the statement is in THESIS_NOTES.md section 5.

## 7. Do not claim

- "Sand detector", "lithology classifier", or anything at bed scale.
- "Glauconite detector", for the new detector or for the thesis's colour
  index.
- That the cuttings work argues against sinkites: it cannot test their age.
- That the photographs add beyond chemistry below the Cretaceous: +0.15 is
  an upper bound.
- That the Tertiary mud-log result validates the photographs: it narrowly met its
  criterion, no better than colour, and adds nothing once Si/Al is known.
- That the seven-well mud-log number (+0.17) is a result: it depends on a
  deviation from the plan.
- That the readers are accurate: they are consistent.
- That the Jurassic-Triassic mud-log result (+0.50) is a pre-registered
  test: it is an amended, exploratory one. Six wells (five locations), one area, twin
  wells; it depends in part on the twin being in training.
- That photographs pick formation tops or beat a depth prognosis.
- Any number for the vertical resolution of cuttings.
- That the gamma-ray check is a human key, or that the Tertiary mud-log
  labels passed it.
- That casing or mud changes are shown to steer the top picks: at top
  Cretaceous the two cannot be separated.
