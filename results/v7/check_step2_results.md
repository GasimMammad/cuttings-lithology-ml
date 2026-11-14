# v7 step 2: geochemical reading of the detector failure, 2026-11-10
A check of the result (see Use of AI in the README). EXPLORATORY, post hoc. Nothing was re-fitted or changed. The data are results/v7/g_scores_joined.csv joined to results/v6/D_xrf_glauconite_bags.csv. Thresholds tau_w are taken from step2_results.json.

## Main points
1. **The flagged Lista bags are green clay, not glaucony.** Their chemistry equals the unflagged Lista bags and the well's own Hordaland baseline (G ≈ 0). The mixing model puts an upper bound of about 2–3% glaucony on them.
2. **S tracks the overall greenness of the chip population, not pellets.**
   - Within Lista, S correlates with the photo's median a* at rho −0.96 (34/8-3) and −0.92 (34/8-3 A).
   - It also correlates with depth at rho +0.90 and +0.71.
   - In 34/8-3 it has no relation to any XRF variable.
3. **The 34/8 excess is partly colour, partly barite.**
   - The 34/8-3 Lista is the greenest-rendered Lista in the set: median a* −0.12, against +1.5 to +1.7 in 34/7-4, 34/7-9 and 34/4-6. Its large green-chip fraction is 3–14 times higher.
   - The Lista in the cleanest wells carries the least barite. In 34/7-4, Ba is about 22,500 ppm and the false-positive count is 0/24.
   - In 34/8-3 A, the flagged Lista bags have less Ba than the unflagged ones (Mann-Whitney p = 0.04). This is barite masking.
4. **The five out-of-window positives are not glauconite.** They are marginal G values (0.20–0.29) in Nordland glacigenic mud, caused by a mineralogy that differs from the baseline and by salt matrix effects. The detector was right not to flag them.

## Q1. What green rounded dark grains are expected in Lista? (literature from memory; verify before citing)
- **Lista Fm:** grey to green-grey, often variegated (green, red-brown), non-calcareous, bioturbated hemipelagic claystone. It is smectite-dominated, largely from altered Paleocene volcanic ash, and the green colour comes from Fe-smectite.
  - Sources: Isaksen & Tonstad 1989, NPD Bulletin 5; Knox & Holloway 1992, BGS Lithostratigraphic Nomenclature vol. 1; Huggett & Knox 2006, Clay Minerals 41, 5–46.
- **Glauconite** is reported locally in the Våle–Lista and in their sandstone members. It is a minor component in the claystone, as far as I know.
- **The expected false positive is drilling-rounded claystone granules.** Smectitic claystone hydrates in water-based mud and is ground into rounded "clay balls". The mud log describes this ("rounded to sub-blocky, hydrated, sticky"). Granules of 0.1–0.5 mm survive the 105 µm wash and dry dark green-grey.
- **Other possibilities:**
  - Chlorite and verdine are unlikely.
  - Tuff is a Balder/Sele issue, and Balder scored only 1/34 above the Lunde p99.
  - Glauconite at trace level is possible but chemically capped at about 2–3% (see Q2).

## Q2. XRF of the 34/8 Lista bags (medians)
| set | n | K/Al | Fe/Al | Mg/Al | Si/Al | Ba ppm | G | S |
|---|---|---|---|---|---|---|---|---|
| 34/8-3 Lista, flagged | 18 | 0.49 | 1.22 | 0.12 | 4.38 | 2,268 | −0.01 | 73 |
| 34/8-3 Lista, unflagged | 12 | 0.51 | 1.20 | 0.12 | 4.25 | 2,898 | +0.01 | 22 |
| 34/8-3 A Lista, flagged | 8 | 0.61 | 1.30 | 0.16 | 4.00 | 3,608 | −0.05 | 48 |
| 34/8-3 A Lista, unflagged | 26 | 0.65 | 1.32 | 0.14 | 4.15 | 11,315 | −0.03 | 18 |
| Lista, other 5 wells | 61 | 0.23 | 1.14 | 0.19 | 3.34 | 1,365 | −0.01 | 14 |
| G > 0.2 bags, ±80 m window | 22 | 1.08 | 2.19 | 0.18 | 9.09 | 4,033 | +0.33 | 11 |

- Flagged and unflagged bags do not differ chemically. Mann-Whitney p for K/Al, Fe/Al, G, Si/Al and Cl is 0.09–0.89. The only exception is Ba in 34/8-3 A (p 0.04, lower in the flagged bags).
- **The 34/8 K/Al is high in every interval of those wells,** including the Oligocene baseline (0.61 and 0.88). So it is a whole-well offset (analytical batch, or siltier and more illitic sediment with Si/Al 4.0–4.4), not glaucony.
- **The 34/8 Lista is an Fe-rich, Mg-moderate, K-normal clay with no K–Fe excess.**
  - Greensand bags carry K/Al about 1 and Fe/Al 2–6.
  - 5% evolved glaucony in mudstone would give G of about +0.08. The bag-to-bag noise is about ±0.05, so the upper bound is about 2–3%.
- The one Lista bag with G 0.12 (34/8-3 A at 2070 m) has Cl 27,000 ppm, a K–Cl artefact.

## Q3. Why 34/8 differs from 34/7 (ranked by evidence)
1. **Photo colour.** 34/8-3 Lista renders greener (median a* −0.12 vs +1.5).
   - This is either genuinely greener Fe-smectite clay in the Visund-area Lista or a per-well rendering difference. The spec flagged per-well Photoshop versions as a risk (B5).
   - The XRF cannot tell these apart, because Fe/Al is the same as in the other wells.
2. **Barite coating.** Heavily weighted Lista bags (34/7-4) desaturate and score low; lightly weighted ones (34/8-3) do not.
3. **Facies and silt content.** The 34/8 Lista has higher Si/Al (4.0–4.4 vs 3.3) and K/Al.
   - This is a slightly siltier, more distal-fed claystone, or an XRF batch offset.
   - It would change how cuttings break and round, not whether glaucony is present.
4. **Mud and washing.** These are not documented for 34/8 (the Tertiary mud type is unconfirmed). An inhibitive mud preserves firm rounded smectite granules, while a dispersive one destroys them. This is plausible but untested.

## Q4. Out-of-window G > 0.2 bags (Nordland Gp)
- **34/7-4 at 840, 900, 920 and 1040 m:**
  - K/Al 0.36–0.44 and Fe/Al 0.71–1.02. These are ordinary mudstone values, nowhere near greensand (K/Al about 1, Fe/Al 2–6).
  - They exceed 0.2 only because the 34/7-4 baseline is a smectitic Hordaland mudstone (K/Al about 0.23).
  - Pleistocene glacigenic Nordland mud is richer in illite, chlorite, biotite and K-feldspar. G is not meaningful outside the Hordaland baseline facies.
- **Salt:** three of the four 34/7-4 bags carry Cl of 35,000–114,000 ppm, with depressed Al (29,000–48,000 vs 55,000–63,000 in neighbours).
  - Halite, whose Na is invisible to the handheld XRF, plus matrix absorption lowers Al more than K and Fe, which inflates both ratios.
  - The K–Cl slope was clipped to 0, so there was no correction.
- **34/7-9 at 480 m:** Ca is 10.3% (a shelly or carbonate bag), with K/Al 0.41 and Fe/Al 0.84. Again marginal.
- **Verdict:** these are mineralogy and matrix artefacts of the index, not pellet glauconite. **G > 0.2 is a sound label only inside the Hordaland/Utsira window.** Outside it, a firing bag needs both ratios at greensand magnitude to be believed.
