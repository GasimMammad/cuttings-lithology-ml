# v2 label decisions (2026-11-05)

Gamma ray (GR) is the only label source, so label quality is decided by
which stretch of log is trusted and what counts as "clean sand" and "pure
shale" in it. v2 makes those choices with three rules applied to every well,
including the five v1 wells.

## Rule 1: one zone = one open-hole logging run

A label zone, its sand anchor and its shale anchor must all lie inside the
same wireline run, below the casing shoe that run was logged under.

Why:

- **Calibration changes from run to run.** In 34/7-4, run 1 reads ~71 API in
  Nordland claystone and run 2 reads ~33 API in Hordaland claystone. The
  Kyrre claystone reads ~70 API in 34/7-10 but ~36 API in 34/7-4.
- **GR logged through casing is attenuated and looks like sand.** The step
  sits exactly at the casing shoe in every case checked against the Sodir
  casing table (`wellbore_casing_and_lot`, downloaded 2026-11-05):

| well | shoe | depth (m MD) | GR above vs below |
|---|---|---|---|
| 34/7-9 | 20" | 899 | ~21 vs ~45 API |
| 34/7-10 | 20" | 901 | ~21 vs ~50 |
| 34/4-7 | 20" | 902 | ~21 vs ~40 |
| 34/7-6 | 20" | 935 | ~25 vs ~50 |
| 34/8-3 | 13 3/8" | 1302 | ~38 vs ~65 |
| 34/8-3 A | 13 3/8" | 944 | ~50 vs ~80 |
| 34/7-1 | 30" | 476 | ~31 vs ~65 |

Consequences:

- **34/8-3:** the "sand bodies" at 1204-1311 m in the earlier PARTB work lie
  above the 13 3/8" shoe. They are casing attenuation, not sand.
- **34/7-1:** the v1 sand anchor (360-460 m, "Nordland sand interior") lies
  inside the 30" conductor. No clean sand exists in any 34/7-1 open-hole run,
  so 34/7-1 gets no labels in v2. In v1 it contributed 246 clay labels and
  no sand.
- **24/9-3 and 24/9-4:** in v1 the sand anchor (Grid Fm) and shale anchor
  (Sele Fm / Hordaland 1660-1850 m) were in different runs. In v2 each run
  has its own anchors.
- **34/4-6:** the Tertiary zone is trimmed to below the 20" shoe at 904 m,
  where the GR level changes. The Lunde zones are dropped, because neither
  run segment holds both a clean sand and a mudstone anchor.

Verification: `verify_runs` (scratch check, results in the session log)
matched the composite curve against each individual run file inside every
zone and anchor. All Tertiary zones match one run at 88-100%. 34/4-6 and 34/7-6
have composites only. The Jurassic zones match run 2 at 32-86%, which looks like depth-matching shifts, and run 2 is the only run covering those depths.

## Rule 2: exclude known GR pitfalls

| unit | problem | source |
|---|---|---|
| Balder Fm | tuffaceous shales "generally characterized by low gamma readings and high sonic"; a GR label calls them sand | Sodir FactPages, Balder Fm; NPD Bulletin 5 |
| Ness Fm | coals read low GR | standard log interpretation |
| Rannoch Fm | "high mica content ... produces an anomalously high gamma ray log response"; a GR label calls it shale | Sodir FactPages, Rannoch Fm; NPD Bulletin 3 |
| Draupne Fm | hot (uranium-rich) shale, off-scale GR | standard |

The low-GR "body" at 1701-1720 m in 34/4-7 (PARTB) is Balder. So are the
low-GR spikes at the Balder level in 34/7-4, 34/7-9, 34/7-10 and 34/7-6.

## Rule 3: anchors

- **Sand anchor:** the interior of the cleanest blocky sand in the run,
  inside a named unit.
- **Shale anchor:** a thick homogeneous marine claystone in the same run
  (Hordaland Gp or Lista Fm in the Tertiary, Drake Fm in the Jurassic).

| well | zone (m) | sand anchor | GR clean | shale anchor | GR shale |
|---|---|---|---|---|---|
| 24/9-3 | 212-460 | Utsira Fm 405-435 | 15 | Nordland claystone 240-265 | 61 |
| 24/9-3 | 520-1555 | Grid Fm 1205-1250 | 18 | Hordaland claystone 900-1030 | 42 |
| 24/9-3 | 1595-1912, 1985-2014 | Hermod Fm 1988-2012 | 19 | Hordaland claystone 1840-1910 | 35 |
| 24/9-3 | 2040-2830 | Heimdal Fm 2220-2300 | 29 | Sele Fm 2065-2200 | 59 |
| 24/9-4 | 760-1168 | upper Grid Fm 1100-1155 | | Hordaland claystone 950-1060 | |
| 24/9-4 | 1185-1580 | Grid Fm 1210-1236 | | Hordaland claystone 1250-1320 | |
| 34/4-6 | 915-1653, 1692-1770 | unnamed Hordaland sand 1361-1375 | 20 | Lista Fm 1695-1765 | 39 |
| 34/4-7 | 915-1695, 1736-1820 | sand above NPD Utsira top 1078-1098 | | Lista Fm 1740-1820 | |
| 34/7-4 | 978-1680, 1716-1825 | unnamed Eocene sand (NPD 1625-1675) 1622-1662 | 17 | Hordaland claystone 1240-1350 | 37 |
| 34/7-9 | 915-1652, 1685-1780 | unnamed Eocene sand (NPD 1445-1511) 1452-1505 | 18 | Lista Fm 1690-1780 | 39 |
| 34/7-10 | 915-1677, 1730-1845 | Utsira sand, operator pick, 995-1035 | | Hordaland claystone 1400-1470 | |
| 34/7-6 | 950-1670, 1710-1840 | Oligocene Hordaland sand 1222-1275 | 18 | Lista Fm 1770-1840 | 39 |
| 34/8-3 | Etive, Dunlin, Statfjord | Etive Fm 2868-2879 | 43 | Drake Fm 2968-3002 | 103 |
| 34/8-3 A | Heather-Tarbert, Etive, Drake | Etive Fm 3098-3112 | 52 | Drake Fm 3186-3225 | 106 |

Full values with P10-P90: `~/sinkite_ml_work_v2/03_endmembers.csv`.

## Geological context used

- In the Tampen area (Snorre, Visund) the Utsira Fm is thin, glauconitic or
  poorly developed and rests directly on the Hordaland Gp (Eidvin & Rundberg
  2001; Gregersen & Johannessen 2007). This fits the absence of clean sand
  in the NPD Utsira interval of 34/8-3 A (70-80 API). The clean sand in 34/7
  wells sits ABOVE the NPD Utsira top (the operator places the Utsira higher,
  e.g. 993-1045 m in 34/7-10).
- The Hordaland Gp on the Tampen Spur contains unnamed Eocene and Oligocene
  sandstones fed from the East Shetland Platform (Rundberg & Eidvin 2005).
  NPD lists them as "NO FORMAL NAME" units (e.g. 34/7-9 1445-1511 m).
- Around the top-Hordaland unconformity over Snorre-Visund, sand up to 150 m
  thick was injected or extruded in the early Pleistocene (Løseth et al.
  2013). Rundberg & Eidvin (2016) dispute this. For labelling, only lithology matters, not the
  emplacement mode.

## Resulting labels (W_1 depths)

| | sand | clay | mixed | unstable |
|---|---|---|---|---|
| v1 (5 wells) | 85 used in tier 2 | | | |
| v2 (10 wells) | 123 | 467 | 252 | 512 |

Wells with >=3 sand and >=3 clay: 24/9-3 (72 sand), 24/9-4 (10), 34/7-4 (7),
34/7-6 (10), 34/7-9 (9), 34/8-3 (6, Jurassic), 34/8-3 A (4, Jurassic).

## References

- Eidvin, T. & Rundberg, Y. 2001. Late Cainozoic stratigraphy of the Tampen
  area (Snorre and Visund fields) in the northern North Sea, with emphasis on
  the chronology of early Neogene sands. Norsk Geologisk Tidsskrift 81.
- Gregersen, U. & Johannessen, P.N. 2007. Distribution of the Neogene Utsira
  Sand and the succeeding deposits in the Viking Graben area, North Sea.
  Marine and Petroleum Geology 24.
- Løseth, H., Raulline, B. & Nygård, A. 2013. Late Cenozoic geological
  evolution of the northern North Sea: development of a Miocene unconformity
  reshaped by large-scale Pleistocene sand intrusion. Journal of the
  Geological Society 170, 133-145. doi:10.1144/jgs2011-165
- Rundberg, Y. & Eidvin, T. 2005. Controls on depositional history and
  architecture of the Oligocene-Miocene succession, northern North Sea Basin.
  NPF Special Publication 12.
- Rundberg, Y. & Eidvin, T. 2016. Discussion on "Late Cenozoic geological
  evolution of the northern North Sea...". Journal of the Geological Society
  173, 384-393.
- Sodir (Norwegian Offshore Directorate) FactPages: lithostratigraphy (Balder
  Fm, Rannoch Fm, Hordaland Gp), wellbore casing table.
