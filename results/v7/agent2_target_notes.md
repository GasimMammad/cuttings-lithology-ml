# v7 step 1: target design (Agent 2, geochemist), 2026-11-09

## Recommendations (decision list)
1. **Primary target T = within-well z of log10(Si/Al), UNCORRECTED for Ba.**
   - A ratio already cancels barite dilution, since BaSO4 dilutes Si and Al equally.
   - The Ba-Si/Al correlation that remains comes from handheld-XRF matrix absorption and from mud clay. Ba also carries real lithology signal: shale cuttings retain more mud and barite (local rho(Ba, Vsh) +0.085).
   - Empirically, Ba correction *lowers* local agreement with GR (median high-passed rho -0.19 uncorrected vs -0.15 Theil-Sen).
   - If the reviewer keeps the Ba-corrected version as primary, OLS and Theil-Sen are immaterial: the slopes differ by 0.06 or less in every well. Then use Theil-Sen with b clipped to b <= 0.
2. **Report as sensitivities** (all within-well z):
   - (i) T_TS = log10(Si/Al) - min(b_TS, 0) * (log10 Ba - median log10 Ba), where b_TS is the Theil-Sen slope of log10(Si/Al) on log10(Ba) over that well's Tertiary bags.
   - (ii) T_part = the same correction with b unclipped (full Ba partialling).
   - If photo skill holds on T_part, it is not riding on barite.
3. **Name the target honestly: "detrital quartz + biogenic silica vs clay", not "sand".**
   - Hordaland/Oligocene mudstones in Tampen are biosiliceous (opal-A/CT). Their median Si/Al is 4.0-5.4, against 3.3-3.4 for Lista claystone.
   - Glauconite pellets lower Si/Al in glauconitic sand: glauconite carries about 5-10% Al2O3.
   - Carbonate dilutes Si and Al equally, so the ratio is unaffected; but Al falls towards its detection limit in carbonate or clean-sand bags.
   - 34/7-6 runs the "wrong" way (high-passed rho +0.22). Treat it as a known biosiliceous/label anomaly and do not drop it after the fact.
4. **Secondary target C = within-well z of log10(Ca), Theil-Sen Ba-partialled.**
   - Do not use Ca/Al: it is inflated in clean sands.
   - C captures carbonate content: shell debris and forams, carbonate (calcite, dolomite, siderite) stringers and cement, and calcareous mudstone.
   - It also captures mud additives: gypsum (Ca + S), lime (24/9-3 seawater-lime mud), and cement drilled out below casing shoes.
   - Report rho(Ca, S) per well as a gypsum diagnostic. It is high in 34/8-3_A (+0.59) and 34/8-3 (+0.36), so read C there with caution.
   - C is nearly independent of GR (high-passed rho -0.08), so it adds a genuinely different visual question (white/calcareous chips).
5. **Exclusions (fix before running):**
   - Tertiary only (the reviewer's rule), and bags 0-15 m below casing shoes (cement, Ca spikes).
   - Bags with Al below the well's Tertiary 5th percentile, where the ratio is unstable. Flag them; drop them only from the target fit.
   - Never use Ti or Ti/Al: the Ba Lα and Ti Kα peaks overlap.
   - Never use Mg (often below detection) or K/Al as a sandiness proxy (KCl, illite and K-feldspar all confound it).
   - No separate Cl cut is needed for Si/Al. Keep Cl only as a leakage variable.
6. **Leakage / negative controls:**
   - High-passed log10 Ba and log10 Cl. Predicted T should not track them better than measured T does.
   - A within-well block-permuted T (10-bag blocks) as the null.
   - Ba is NOT a clean negative control unfiltered (rho with Vsh +0.25 via depth and mud weight). Use only its high-passed form.
7. **Mud additives found (Tertiary sections; from operator reports):**
   - Gyp-polymer in 34/4-6, 34/7-6, 34/7-9 and 34/7-10 (KCl only below 2413 m in 34/7-10).
   - Gyp/lignosulphonate in 34/7-4; seawater-lime-dextrid in 24/9-3; seawater top-hole in 24/9-4.
   - Not confirmed for 34/4-7, 34/7-1, 34/8-3 and 34/8-3_A.
   - Gypsum adds S and Ca; barite reaches about 2.5% Ba (p90) in the Tertiary.
   - rho(K, Cl) is +0.57 in 34/7-1, +0.43 in 34/7-6 and +0.35 in 24/9-4. KCl is not documented there; this may be brine retained in clay. It matters only for K-based targets (step 2 G already applies a Cl correction to K).

## Empirical check (v2 GR Vsh, support (D-10, D], Tertiary, 8 wells with labels)
Each cell is the within-well Spearman rho of the target against Vsh. "Local" means high-passed (minus the running median over ±50 m, with gaps > 30 m split); "unfiltered" means raw. Sand has negative rho.

| well | n | b_OLS | b_TS | raw local | raw unfiltered | TS local | partialled local | Ca local | Ba local | Cl local |
|---|---|---|---|---|---|---|---|---|---|---|
| 24/9-3 | 478 | -0.22 | -0.20 | -0.24 | -0.44 | -0.17 | -0.17 | -0.02 | +0.09 | +0.19 |
| 24/9-4 | 158 | -0.09 | -0.02 | -0.39 | -0.33 | -0.40 | -0.40 | +0.02 | +0.07 | +0.02 |
| 34/4-6 | 77 | +0.11 | +0.13 | -0.13 | +0.33 | -0.13 | -0.14 | -0.17 | +0.03 | +0.04 |
| 34/4-7 | 85 | -0.10 | -0.12 | -0.14 | +0.41 | -0.07 | -0.07 | -0.04 | +0.12 | -0.13 |
| 34/7-10 | 86 | +0.12 | +0.14 | -0.45 | +0.04 | -0.45 | -0.41 | -0.18 | +0.03 | +0.06 |
| 34/7-4 | 85 | -0.12 | -0.13 | -0.51 | +0.05 | -0.38 | -0.38 | -0.16 | +0.24 | +0.02 |
| 34/7-6 | 78 | -0.13 | -0.14 | +0.18 | +0.29 | +0.22 | +0.22 | -0.12 | +0.18 | -0.14 |
| 34/7-9 | 82 | +0.16 | +0.14 | -0.05 | +0.07 | -0.05 | -0.04 | +0.21 | +0.08 | +0.13 |
| **median** | | | | **-0.19** | +0.06 | -0.15 | -0.16 | -0.08 | +0.09 | +0.03 |

- Raw local rho is negative in 7 of 8 wells.
- Unfiltered rho is often *positive*. Depth trends dominate here: Nordland and Utsira at high Si/Al, biosiliceous Hordaland above Lista. This is why the high-passed primary endpoint is essential.
- Zr/Al (local rho about 0) and a CLR-PCA PC1 (about -0.13) were checked earlier and are not better than Si/Al.
- GR is itself an imperfect sand label here: glauconitic and K-feldspar-rich sands read high GR. Expect agreement of |rho| about 0.2, not about 0.6.
- Script and table: `/private/tmp/claude-501/-Users-gasimmammadov-Projects-cuttings-lithology-ml/6549f91e-15d0-4896-b785-21197e925e4a/scratchpad/v7b.py` and `v7_target_check.csv` (scratch, not repo).
