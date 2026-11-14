# v7 step 2: mineralogical check of the pellet-detector spec, 2026-11-10
AI check (see Use of AI in the README); "I" in this file is that check. No photograph was viewed. No gate was changed on the basis of labelled data.

## Verdict
The gates in A3–A5 are mineralogically reasonable for fresh, evolved Utsira/Hordaland glaucony in washed, dried cuttings. Freeze them as written. There are three required changes, all to wording or diagnostics, none to gates.

1. **Fix the meaning of the detection limit relative to G (B3 text).**
   - In a two-end-member mixing model, G > 0.2 needs about 12–15 wt% evolved glaucony (K2O about 7%, Fe2O3t about 25%) in a Hordaland-mudstone or quartz-sand host. Nascent glaucony (K2O about 4%) needs about 17–28 wt%.
   - The high-G bags themselves imply about 40–60% glaucony:
     - 34/4-6 at 1230–1240 m: Fe 10.2–13.0 wt%, Al 2.3–3.3 wt%.
     - 34/8-3_A at 1120–1130 m: Fe 11.5 wt%.
     - 34/7-10 at 1110 m: Fe 9.2 wt%.
   - Glaucony density (2.4–2.95) is close to quartz and clay, so vol% ≈ wt%.
   - The 105 µm wash retains loose pellets in both the XRF aliquot and the photo, so both see the same material.
   - So a detection limit of about 1–few % area sits an order of magnitude below G > 0.2. **Sensitivity is not the limiting factor; specificity is.** State this.
2. **Define the negatives as "G ≤ 0.2", not "glauconite-free".**
   - Window bags with G ≤ 0.2 can hold up to about 10% pellets, and caving moves real pellets into neighbouring bags.
   - Detector hits there are expected and are not all false positives.
   - Lista (G 0/125) is the only near-clean negative, and is correctly the specificity set (A10).
3. **Add diagnostics only (written, not tested):**
   - Per photo, histograms of accepted-blob size and hue.
   - The count of "brown rounded blobs": same shape gates, hue 40–95° and a* > 0. This is an oxidised-glaucony monitor.
   - A descriptive false-positive row for Balder Fm bags (tuff) alongside Lista.

## (a) Gates
- **Hue 95–200° with a* ≤ −1.5:** right for 5GY–10G glaucony under the warm cast.
  - Excludes oxidised or limonitised (yellow-brown, olive-brown) pellets. Thirty-five years of bag storage can oxidise pellet surfaces.
- **C* 4–30, L* 15–50, blob C* ≥ 5, blob L* ≤ 45:** right for dark-green, moderately saturated grains.
  - Excludes near-black, highly evolved pellets (5G 2/1, C* about 3) and pale nascent glaucony.
  - Both exclusions are acceptable because G favours K-rich, evolved glaucony.
- **Size 0.10–0.51 mm:** matches the Utsira fine-to-medium sand mode and the 105 µm wash cut-off.
  - Coarse pellets (0.5–1 mm, typical of condensed lags at THGU) are lost.
- **Solidity ≥ 0.8, circularity ≥ 0.5, axis ratio ≥ 0.4:** acceptable for ovoid and lobate pellets.
  - Drying-shrinkage cracks reaching the rim, and multi-chamber foram-infill moulds, will fail some pellets.
  - The 30 px hole-fill helps only with internal cracks.

## (c) Errors named in advance
- **False negatives:**
  - Oxidised brown or olive pellets.
  - Near-black pellets.
  - Pellets larger than 0.51 mm or smaller than 0.10 mm.
  - Cracked, fragmented or vermiform pellets.
  - Pellets inside mudstone chips.
  - Pellets coated by barite or mud (desaturated).
  - Pale nascent glaucony.
- **False positives:**
  - Rounded green-grey claystone granules of 0.1–0.5 mm (Lista, Hordaland, Lunde).
  - Balder tuff grains (smectitic, green-grey).
  - Chlorite or chloritised-biotite flakes seen face-on, in micaceous sands.
  - Green paint flakes or dyed lost-circulation material from the rig.
  - Dark green-grey siltstone granules.
- **Low risk:**
  - Verdine and chamosite/berthierine ooids are absent from the North Sea Neogene; they occur in the Jurassic, outside the Tertiary scope.
  - Shells: a* is rarely negative.
  - Pyrite-filled forams: these are black, not green.
- **Label noise, not detector error:**
  - Real pellets caved into bags with G ≤ 0.2.
  - Siderite, Fe-smectite or biotite raising G without pellets (2 of 10 high-G bags were not pellet-confirmed).

## (d) Is G > 0.2 the right label?
- **Keep G > 0.2 as the frozen primary positive label.** It flags greensand-level abundance (about 12% or more glaucony, typically 40–60%), and it is chemically independent of the photo.
- **It is a poor negative label** (see change 2). The within-well ranking test (A9) tolerates this. A false-positive count inside the window does not.
- **The pellet-check result should NOT be the training or test label:**
  - It exists for only 10 bags.
  - It is visual, so it would partly make the test circular.
  - Use it as a validation layer, reporting concordance.
- **Add as descriptive:** the within-window Spearman of S against continuous G (the review's exploratory no-Al-floor G). This uses the graded information that the binary label throws away.
