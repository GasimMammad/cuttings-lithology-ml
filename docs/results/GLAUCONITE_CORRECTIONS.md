# Corrections to the green-index (glauconite) part (v6 A; reviewer rounds 11-12)

The original repository is left untouched. These corrections apply to the
thesis text and README wording.

1. **The Utsira positive control was over-counted.**
   - The README says "it fired on the Utsira Formation in five of the seven
     wells that have photographs inside the Utsira interval". That does not
     hold up.
   - 34/4-6 is the calibration well (circular).
   - 34/7-4 (28.9x) and 34/7-10 (26.9x) each rest on one photograph; the
     34/7-10 one lies outside the NPD Utsira window.
   - 34/7-1 rests on a single 239x photograph that needs a visual check
     (possible artefact).
   - Repeated firing is seen only in 34/8-3 A.
   - Honest count: about 1-2 of 6 independent wells.
2. **The index is not glauconite-specific.**
   - It fires 25-100x background in green-grey Lista, Jorsalfare and Lunde
     mudstones.
   - The chroma gate removes almost nothing (93% of hue-passing pixels
     survive), so the index is effectively a single hue threshold
     (a* < -5).
   - Call it a "green index", not a "glauconite index".
3. **"Fire = above background" is a noise-level criterion.** Backgrounds are
   0.0002-0.0015, so fractions such as 7/26 firing carry little meaning. Use a
   high percentile of each well's own background and correct for the number
   of photographs tested.
4. **Firing concentrated 0-30 m below THGU does not discriminate.** Caving
   from the Utsira and sinkites hanging just below the unconformity both
   predict it.
5. **The STAGE3lite GR/AI "glauconite" labels are not specific.**
   - "Vsh says shale, AI says sand => glauconite" ignores other causes:
     opal-A to opal-CT diagenesis in biosiliceous ooze, silty or compacted
     mudstone.
   - The strong-negative statement for the 34/7-6 target sand still
     stands, but it needs:
     - a clean-sand end member from an independent interval;
     - an explicit detection limit (an excess of ~1 API corresponds to under
       ~2-3% glauconite at 5-8% K2O).
6. **The calibration is not reproducible.**
   - `12_glauconite_test.py` contains the Fig. A7 plotting code; the
     original calibration script is lost (single-commit repository).
   - The frozen thresholds (a* < -5.0, C* >= 12.0, 15 < L* < 80) are
     reproducible; how they were chosen is not.
7. **Spectral GR was considered and is not possible.** The valid NGT
   POTA/THOR intervals are 34/4-6 2499-2776 m, 34/7-1 1831-2913 m and
   34/8-3 2572-3331 m; none covers the Utsira or the Oligocene.
