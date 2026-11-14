# Thesis check: where the follow-up work changes what the thesis says about cuttings

Checked 2026-11-12 against the submitted dissertation, "Looking for
Sinkites" (GasimMammadov_MScThesis2026.pdf, 4 September 2026, 51 pages).
Page numbers are the printed ones. The thesis file was read only; nothing
in it was changed.

**Scope.** The thesis is a seismic and petrophysical study of the Visund SE
mound. Its cuttings work sits in section 3.6 (one paragraph), section 4.7
(one sentence), section 6.6 with Table 6, and Appendix A. The follow-up
(v2 to v10 in this repository, November 2026) concerns only that part.

**Bottom line.** Five of the six observations make no use of the cuttings. P6 rests
on the photoelectric factor and spectroscopy, but sections 4.7 and 5.4 use
the colour analysis to remove an apparent contradiction. That support is
withdrawn (item 1). The numbered conclusions in section 7 stand as worded.
The follow-up changes four statements in the cuttings part.

## Statements the follow-up changes

| # | Thesis says | Where | Follow-up found | What to say now |
|---|---|---|---|---|
| 1 | The colour index "did produce usable results, detecting glauconite in control intervals at 27 to 239 times background"; it "detected glauconite reliably in control intervals"; "Regional colour analysis of drill cuttings shows that the Utsira is not uniformly glauconitic across the area, which removes the apparent contradiction" | 6.6 p. 33; 8 p. 37; 4.7 p. 27 and 5.4 p. 31; A.2, A.3 | The index is a green-hue index, not a glauconite index: it fires 25 to 100 times background in green-grey Lista, Jorsalfare and Lunde mudstones, and its chroma gate removes almost nothing. The Utsira positive control was over-counted: the original README's "five of seven wells" becomes about 1 to 2 of 6 independent wells (one is the calibration well, three rest on single photographs). A second, pre-registered detector fired on 22 % of Lista Formation bags and failed its criterion (GLAUCONITE_CORRECTIONS.md; V6_RESULTS.md A; V7_RESULTS.md step 2) | The colour index does not show where the Utsira is or is not glauconitic. The sentence in 4.7 and 5.4 loses that support. P6 itself rests on the photoelectric factor and elemental spectroscopy at the two Visund wells, which the follow-up does not touch, and P6 was already scored "in part" for inversion (Table 5). The exploratory XRF index found glauconite in the Utsira in 4 of 5 wells (V6_RESULTS.md D), so the apparent contradiction is not removed |
| 2 | Portable XRF "failed" as a label source: Si/Al against shale volume has Spearman -0.28 to +0.30, changing sign between wells; "the instrument is weak on precisely the light elements that ratio depends on" | 6.6 p. 34; Table 6; A.4 | The numbers stand as measured (whole wells, raw correlation). Table 6's "No gamma-ray agreement" does not: Si/Al separates the gamma-ray sand and clay labels at median AUC 0.81 in 6 of 7 held-out wells (V3_RESULTS.md). Within a well, after a +/-50 m trend is removed, Si/Al behaves as a usable relative signal: the photographs predict it in 11 of 11 held-out wells (+0.32), it follows the wellsite sand fraction below the Cretaceous (+0.51), and it follows gamma ray (Tertiary -0.21, below the Cretaceous -0.26, each 6 of 6; reference rows, descriptive) (V7_RESULTS.md step 1; V8_RESULTS.md D; V9_RESULTS.md K3) | XRF failed as an absolute sand/clay label across wells. It did not fail as a measurement: Si/Al works as a relative, within-well signal. "Weak on light elements" is too strong as the explanation |
| 3 | Figure A6 shows held-out predictions against barium and depth, "confirming that model outputs are free from contamination-driven leakage" | A.5 p. 40 | The four classifiers were at chance, so the absence of a barium relation says little. With a working target the photographs do see mud: they predict barium itself (+0.31, 11 of 11 wells). The chemistry result survives partialling barium, carbonate and chloride (+0.33), but bentonite cannot be separated (V7_RESULTS.md step 1) | Photographs see barite. Mud residue contributes an unknown part of every photo result |
| 4 | "Four classifiers were trained and the balanced-accuracy confidence interval of every one includes 0.50, so none is distinguishable from chance" (three folds) | 6.6 p. 33; Table 6; A.6 | Stands for the thesis data. With ten labelled wells the classifier separates sand from clay at the scale of zones (median held-out AUC 0.73, p 0.039) but no better than depth within the well (p 0.15) (V3_RESULTS.md) | The thesis negative stays the first finding. The follow-up adds: more wells give zone-scale skill only |

## Points that are consistent, or that the thesis settles

- **Composition of the sand.** The thesis reads the mound sand as clean
  quartz, with glauconite below 2.4 % (4.7). The follow-up found, in other
  wells, that the Oligocene target sands carry little or no glauconite
  (cuttings XRF in three wells, logs in 34/7-6; V6_RESULTS.md). The two
  agree: both argue against a glauconitic source and neither identifies the
  parent.
- **The word "sinkite".** The thesis attributes the term to Rudjord and
  Huuse (2025), who call the sunken sand bodies sinkites and the uplifted
  rafts floatites (1.3, p. 3). Løseth et al. (2013) is the injection model.
  The follow-up notes carried a caution not to attribute the term without a
  source; the source is Rudjord and Huuse (2025), cited in the thesis.
- **Future work named in the thesis.** "Consolidating the underlying
  analysis into a single reproducible script prior to archiving" (8, p. 37):
  the repository now maps every result to its script and pins the package
  versions (README.md), though it is a set of numbered scripts, not one
  script. "A training set drawn from wells with comparable barite loading":
  not tested as such; the barium control of item 3 is the nearest thing.

## Two things to keep apart when presenting

1. **Evidence for sinking comes from the thesis, not from the cuttings.**
   The thesis concludes that the Visund SE mound formed by buoyancy-driven
   inversion, from seismic volumetrics and logs at wells 34/8-A-14 H and
   34/8-A-33 H. The follow-up works on photographs and XRF of cuttings from
   eleven other wells. It found no evidence on the origin of the sands in
   either direction, and it could not: the decisive test there is age, and
   no sidewall cores exist. "No evidence for sinkites" in the follow-up
   files means "the cuttings add none"; it does not contradict the thesis.
   CONFERENCE_NOTES.md now says this in those words.
2. **The AI declaration in the thesis does not cover the follow-up.** The
   thesis states that generative AI was used only for writing and debugging
   Python code and for correcting grammar (p. iii). It covers the dissertation. In the follow-up AI was also used to analyse the
   mud-log tiles, core photographs and well-report pages, and to check the
   plans and numbers. Anything presented from the follow-up needs the
   statement in THESIS_NOTES.md (section 5), adapted to the rules of the
   venue.

## Not checked

- The seismic, volumetric and petrophysical chapters (outside this work).
- The appendix figures A1 to A8 themselves (the PDF text was read, not the
  images).
- The September presentation deck (GasimMammadov_2026_MSc_conference.pptx)
  was scanned for cuttings claims: it repeats only item 4 and the
  photoelectric-factor result, and needs no change.
