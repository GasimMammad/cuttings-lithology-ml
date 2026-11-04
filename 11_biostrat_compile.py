"""
Compile the NPD Bulletin 10 biostratigraphic age framework for the Tampen wells.

Source: https://www.sodir.no/en/whats-new/publications/npd-bulletins/bulletin-10/
        well-stratigraphy/  (7 well pages, fetched 2026-08-01)
All depths are m RKB, transcribed verbatim from the Bulletin 10 text.

Outputs (in ~/sinkite_ml_work/biostrat/):
  BIOSTRAT_units.csv        one row per dated unit
  BIOSTRAT_sr.csv           one row per Sr isotope analysis
  BIOSTRAT_tops.dat         Petrel 3-column well-tops (well, top MD, surface)
  BIOSTRAT_flags.csv        THGU depth, Utsira presence/thickness, age gap
  BIOSTRAT_sand_crosscheck.csv   user's mapped sands vs dated units
"""
import csv
from pathlib import Path

OUT = Path.home() / "sinkite_ml_work" / "biostrat"
OUT.mkdir(parents=True, exist_ok=True)

# =============================================================================
# UNITS -- verbatim from Bulletin 10.
# NB DEPTH CONVENTION: Bulletin 10 writes intervals DEEPEST FIRST, e.g.
# "Lower Oligocene (1390-1270 m)" means BASE 1390 m, TOP 1270 m. The tuple
# fields are therefore (well, unit, BASE, TOP, ...). Verified against the NPD
# lithostratigraphic tops: 34/4-6 Hordaland Gp top 1250 / Utsira top 1210,
# 34/4-7 Hordaland 1200 / Utsira 1180, 34/7-1 Hordaland 1170 / Utsira 1150.
# =============================================================================
# (well, unit, base_m, top_m, age, litho_unit, forams, lithology)
UNITS = [
 # ---- 34/4-6 ----
 ("34/4-6","Lower Oligocene",1390,1270,"latest Early Oligocene","Hordaland Group",
  "Rotaliatina bulimoides assemblage + Gyroidina soldanii mamillata assemblage; "
  "Diatom sp. 3; also T. alsatica, G. soldanii girardana; no planktonics. "
  "NSB 7b (King 1989), NSR 7B (Gradstein & Backstrom 1996), lower NSP 9c",
  "Lowermost part: coarse WHITE QUARTZOSE SAND. Rest: mainly silty mudstones"),
 ("34/4-6","Upper Oligocene",1270,1250,"earliest Late Oligocene","Hordaland Group",
  "Turrilina alsatica assemblage; Diatom sp. 3; also G. soldanii girardana; "
  "no planktonics. NSB 8a, upper NSP 9c (King 1989)",
  "Mainly silty mudstones"),
 ("34/4-6","Upper Miocene-Lower Pliocene",1250,1210,
  "latest Late Miocene to earliest Early Pliocene","Utsira Formation",
  "Ehrenbergina variabilis assemblage (benthic) + Neogloboquadrina atlantica "
  "(sinistral) assemblage (planktonic); also E. pygmeus, C. telegdi, C. dutemplei, "
  "G. bulloides, one N. atlantica (dextral). G. subglobosa-E. variabilis zone "
  "(Stratlab 1986); tentatively NSB 13b",
  "Dominated by GLAUCONITIC SAND. Some quartzose sand, silt, clay (most may be caved)"),
 ("34/4-6","Upper Pliocene",1210,1000,"Late Pliocene (Gelasian, max 2.75 Ma)",
  "Nordland Group",
  "Cibicides grossus-Elphidiella hannai assemblage + N. atlantica (sinistral) "
  "(upper main part) + N. pachyderma (dextral); also E. excavatum (common), "
  "C. teretis (common), C. lobatulus, N. affine, B. tenerrima, B. marginata. "
  "NSB 15a, NSR 12",
  "Poorly sorted clastics (DIAMICTON); clay dominant, silt, sand, ice-rafted "
  "pebbles. Two blocky sand bodies ~1150-1135 m. Sand dominantly quartzose but "
  "GLAUCONITE PRESENT IN MOST SAMPLES"),
 # ---- 34/4-7 ----
 ("34/4-7","Lower-Upper Oligocene",1220,1200,
  "close to Early/Late Oligocene boundary (28.5 Ma)","Hordaland Group",
  "Turrilina alsatica assemblage; Diatom sp. 3. Upper NSB 7b / lower NSB 8a; "
  "upper NSR 7B; lower NSP 9c","Mainly silty mudstones"),
 ("34/4-7","Upper Miocene-Lower Pliocene",1200,1180,"Late Miocene-Early Pliocene",
  "Utsira Formation",
  "Ehrenbergina variabilis assemblage + N. atlantica (sinistral) assemblage; "
  "also G. bulloides, one N. atlantica (dextral). G. subglobosa-E. variabilis "
  "zone; tentatively NSB 13b",
  "Dominated by GLAUCONITIC SAND. Some quartzose sand, silt, clay (most may be caved)"),
 ("34/4-7","Upper Pliocene",1180,1000,"Late Pliocene (Gelasian, max 2.75 Ma)",
  "Nordland Group",
  "Cibicides grossus assemblage + Elphidiella hannai assemblage + N. atlantica "
  "(sinistral) (upper main part); also E. excavatum, C. teretis, N. affine, "
  "B. tenerrima, I. islandica, G. bulloides, N. pachyderma (dextral), "
  "G. inflata (few). NSB 15a, NSR 12",
  "Poorly sorted clastics (DIAMICTON); clay dominant. Two blocky sand bodies "
  "~1095-1160 m. Sand dominantly quartzose but GLAUCONITE PRESENT IN MOST SAMPLES"),
 # ---- 34/7-1 ----
 ("34/7-1","Lower Oligocene",1200,1170,
  "Early Oligocene close to Early/Late Oligocene boundary","Hordaland Group",
  "Rotaliatina bulimoides assemblage; Diatom sp. 3; also T. alsatica, "
  "G. soldanii girardana; no in situ planktonics. NSB 7b, NSR 7B, lower NSP 9c",
  "Mainly silty mudstones"),
 ("34/7-1","Upper Miocene-Lower Pliocene",1170,1150,"Late Miocene-Early Pliocene",
  "Utsira Formation",
  "Cibicides dutemplei assemblage + N. atlantica (sinistral) assemblage (lower "
  "part); also E. pygmeus, C. telegdi, U. venusta saxonica (1 specimen), "
  "G. bulloides. E. variabilis NOT recorded here (recorded in 34/8-1, 34/8-3 A, "
  "34/4-6, 34/4-7, 34/2-4). Tentatively NSB 13b",
  "Dominated by GLAUCONITIC SAND. Some quartzose sand, silt, clay (most may be caved)"),
 ("34/7-1","Upper Pliocene",1150,1000,"Late Pliocene (Gelasian, max 2.75 Ma)",
  "Nordland Group",
  "Cibicides grossus assemblage + Elphidiella hannai assemblage + N. atlantica "
  "(sinistral) (upper main part) + Globigerina bulloides assemblage; also "
  "E. excavatum (common), C. teretis (common), N. affine, B. marginata. "
  "NSB 15a, NSR 12",
  "Poorly sorted clastics (DIAMICTON); clay dominant. Two blocky sand bodies "
  "~1050-1125 m. Sand dominantly quartzose but GLAUCONITE PRESENT IN MOST SAMPLES"),
 # ---- 34/8-3 A ----
 ("34/8-3 A","Lower-Upper Oligocene",1300,1240,
  "latest Early to earliest Late Oligocene","Hordaland Group",
  "Turrilina alsatica assemblage; also G. soldanii girardana; no in situ "
  "planktonics. Upper NSB 7b / lower NSB 8a; upper NSR 7B",
  "Mainly silty mudstones"),
 ("34/8-3 A","Lower Miocene",1240,1180,"Early Miocene","Hordaland Group",
  "Diatom sp. 4 - Diatom sp. 5 assemblage; Eponides umbonatus - Stilostomella sp. "
  "assemblage. NSP 10, NSA 10 (King 1989). UNCONFORMABLE on Lower-Upper Oligocene",
  "Mainly silty mudstones"),
 ("34/8-3 A","Upper Miocene",1180,1140,"Late Miocene","Utsira Formation",
  "Uvigerina pygmea langeri assemblage + Ehrenbergina variabilis assemblage "
  "(lowermost part); Bolboforma fragori assemblage (also B. metzmacheri, "
  "B. clodiusi); also G. subglobosa, C. telegdi, M. communis, S. bulloides. "
  "NSB 13a / lower 13b",
  "Sand, silt and clay; sand mainly GLAUCONITIC"),
 ("34/8-3 A","Upper Miocene-Lower Pliocene",1140,1120,
  "latest Late Miocene to earliest Early Pliocene","Utsira Formation",
  "Ehrenbergina variabilis assemblage (upper main part) + N. atlantica "
  "(sinistral) assemblage; also C. telegdi, E. pygmeus, G. bulloides, one "
  "N. atlantica (dextral). Upper NSB 13b",
  "Sand, silt and clay; sand mainly GLAUCONITIC. Some quartzose sand in upper "
  "part probably caved from Upper Pliocene"),
 ("34/8-3 A","Upper Pliocene",1120,1000,"Late Pliocene (Gelasian, max 2.75 Ma)",
  "Nordland Group",
  "Cibicides grossus assemblage + N. atlantica (sinistral) (upper main part) + "
  "Globigerina bulloides assemblage; also E. hannai (upper part), E. excavatum, "
  "C. teretis (common), C. lobatulus, N. affine (common), B. tenerrima. "
  "NSB 15a, NSR 12. UNCONFORMABLE on Upper Miocene-Lower Pliocene",
  "Poorly sorted clastics (DIAMICTON); clay dominant. Sand dominantly quartzose "
  "but GLAUCONITE PRESENT THROUGHOUT and quite common in lowermost part"),
 # ---- 34/8-1 ----
 ("34/8-1","Lower Oligocene",1360,1260,"latest Early Oligocene","Hordaland Group",
  "Rotaliatina bulimoides assemblage; Diatom sp. 3; also common T. alsatica; "
  "no planktonics. NSB 7b, NSR 7B, lower NSP 9c","Mainly silty mudstones"),
 ("34/8-1","Upper Oligocene",1260,1170,"earliest Late Oligocene","Hordaland Group",
  "Turrilina alsatica assemblage; Diatom sp. 3; also G. soldanii girardana; "
  "no planktonics. NSB 8a, upper NSP 9c","Mainly silty mudstones"),
 ("34/8-1","Lower Miocene",1170,1140,"Early Miocene","Hordaland Group",
  "Diatom sp. 4 - Diatom sp. 5 assemblage. NSP 10. UNCONFORMABLE on "
  "Lower-Upper Oligocene","Silty mudstones with SOME GLAUCONITIC SAND"),
 ("34/8-1","Upper Miocene-Lower Pliocene",1140,1090,"Late Miocene-Early Pliocene",
  "Utsira Formation",
  "Ehrenbergina variabilis assemblage + N. atlantica (sinistral) (lower part); "
  "also G. bulloides, few N. atlantica (dextral), Bolboforma spp. (B. subfragori, "
  "B. metzmacheri, B. clodiusi, B. compressibadenensis, B. fragori, "
  "B. pseudohystrix - probably reworked). Tentatively NSB 13b",
  "Dominated by GLAUCONITIC SAND. Some quartzose sand, silt, clay (most may be caved)"),
 ("34/8-1","Upper Pliocene",1090,800,"Late Pliocene (Gelasian, max 2.75 Ma)",
  "Nordland Group",
  "Cibicides grossus assemblage + N. atlantica (sinistral) (upper main part); "
  "also E. hannai, E. excavatum (common), C. teretis (common), C. scaldisiensis, "
  "N. affine, B. tenerrima, B. marginata, G. bulloides, N. pachyderma (dextral). "
  "NSB 15a, NSR 12",
  "Poorly sorted clastics (DIAMICTON); clay dominant. Sand dominantly quartzose "
  "but GLAUCONITE PRESENT THROUGHOUT, quite common in lowermost part"),
 # ---- 34/7-2 ----
 ("34/7-2","Oligocene (unspecified)",1070,1035,"Oligocene, unspecified",
  "Hordaland Group",
  "Mostly sponge spicules (rod-shaped and Geodia sp.); pyritised diatoms "
  "throughout, radiolaria in lower part; Diatom sp. 3 at 1070 and 1060 m. NSP 9c",
  "Mainly silty mudstone with SOME SAND RICH IN SPONGE SPICULES"),
 ("34/7-2","Upper Miocene-Lower Pliocene",1035,1025,"Late Miocene-Early Pliocene",
  "Utsira Formation",
  "E. variabilis assemblage + N. atlantica (sinistral) (lower part) at 1030 m; "
  "also G. subglobosa, C. telegdi, Hoeglundina elegans. "
  "G. subglobosa-E. variabilis zone; tentatively NSB 13b",
  "Dominated by GLAUCONITIC SAND. Some quartzose sand, silt and clay"),
 ("34/7-2","Upper Pliocene",1025,919,"Late Pliocene","Nordland Group",
  "Cibicides grossus assemblage + N. atlantica (sinistral) (upper part) + "
  "Globigerina bulloides assemblage; also E. hannai through most of section. "
  "NSB 15a",
  "Poorly sorted clastics (DIAMICTON) with clay dominant, silt, sand, few "
  "ice-rafted pebbles. Quartzose sand dominant ~1020-1000 m; samples at "
  "1021.5 m (SWC) and 1020 m (DC) also contain SOME GLAUCONITIC SAND"),
 # ---- 34/2-4 ----
 ("34/2-4","Lower-Upper Oligocene",1600,1520,
  "latest Early to earliest Late Oligocene","Hordaland Group",
  "Gyroidina soldanii girardana assemblage; Diatom sp. 3. Upper NSB 7b / lower "
  "NSB 8a; upper NSR 7B; NSP 9c","Primarily silty mudstones"),
 ("34/2-4","Upper Miocene-Lower Pliocene",1520,1470,"Late Miocene-Early Pliocene",
  "Utsira Formation",
  "Ehrenbergina variabilis assemblage + N. atlantica (sinistral) (lower part); "
  "also G. subglobosa, E. pygmeus, C. telegdi, C. dutemplei, G. bulloides, few "
  "N. atlantica (dextral). G. subglobosa-E. variabilis zone; tentatively NSB 13b",
  "Sand, silt and clay. LOWER PART sand mainly GLAUCONITIC; upper part mainly "
  "quartzose with pebbles - pebbles and most quartzose sand probably caved"),
 ("34/2-4","Upper Pliocene",1470,1300,"Late Pliocene (Gelasian, max 2.75 Ma)",
  "Nordland Group",
  "Cibicides grossus-Elphidiella hannai assemblage + N. atlantica (sinistral) "
  "(upper main part); also E. excavatum, C. teretis (common), C. scaldisiensis, "
  "N. affine, B. tenerrima, B. marginata, G. bulloides, N. pachyderma (dextral), "
  "G. inflata (few). NSB 15a, NSR 12",
  "Poorly sorted clastics (DIAMICTON); clay dominant. Two blocky sand bodies "
  "~1380-1360 m. Sand dominantly quartzose but GLAUCONITE IN MOST SAMPLES"),
]

# =============================================================================
# Sr ISOTOPE DATA -- verbatim. host_lithology is judged from the Bulletin 10
# lithology text for the interval the SAMPLE spans (item 5 of the request).
# =============================================================================
SR = [
 # well, litho_unit, sample, type, ratio, 2s, age, lab, fossils, host_lithology, from_sand
 ("34/4-6","Utsira Fm","1240-1220 m","DC",0.709010,0.000014,5.69,"IFE",
  "Calcareous benthic index foraminifera",
  "Utsira Fm 1250-1210 m = dominated by glauconitic sand","SAND (glauconitic)"),
 ("34/4-6","Hordaland Gr","1280-1250 m","DC",0.708127,0.000017,26.27,"IFE",
  "Calcareous benthic index foraminifera",
  "Upper Oligocene 1270-1250 m + top Lower Oligocene = silty mudstones "
  "(the white quartzose sand is at the BASE of the unit, ~1390 m)","MUDSTONE"),
 ("34/4-7","Utsira Fm","1192 m","SWC",0.709032,0.000013,5.13,"IFE",
  "Calcareous benthic index foraminifera",
  "Utsira Fm 1200-1180 m = dominated by glauconitic sand","SAND (glauconitic)"),
 ("34/4-7","Utsira Fm","1200-1180 m","DC",0.709020,0.000013,5.46,"IFE",
  "Calcareous benthic index foraminifera",
  "Utsira Fm 1200-1180 m = dominated by glauconitic sand","SAND (glauconitic)"),
 ("34/4-7","Hordaland Gr","1210 m","DC",0.708077,0.000039,27.64,"IFE",
  "Calcareous benthic index foraminifera",
  "Lower-Upper Oligocene 1220-1200 m = mainly silty mudstones","MUDSTONE"),
 ("34/7-1","Hordaland Gr","1200-1190 m","DC",0.708133,0.000029,26.14,"IFE",
  "Calcareous benthic index foraminifera",
  "Lower Oligocene 1200-1170 m = mainly silty mudstones","MUDSTONE"),
 ("34/8-1","Utsira Fm","1130-1110 m","DC",0.709036,0.000017,5.03,"IFE",
  "Calcareous benthic index foraminifera",
  "Utsira Fm 1140-1090 m = dominated by glauconitic sand","SAND (glauconitic)"),
 ("34/8-1","Hordaland Gr","1280 m","DC",0.708039,0.000045,28.61,"IFE",
  "Calcareous benthic index foraminifera",
  "Upper Oligocene 1260-1170 m = mainly silty mudstones","MUDSTONE"),
 ("34/8-1","Hordaland Gr","1300 m","DC",0.708055,0.000047,28.20,"IFE",
  "Calcareous benthic index foraminifera",
  "Lower Oligocene 1360-1260 m = mainly silty mudstones","MUDSTONE"),
 ("34/7-2","Utsira Fm","1130 m [SEE NOTE]","SWC",0.709044,0.000008,4.74,
  "Univ. Bergen","25 tests of E. variabilis, G. subglobosa",
  "Utsira Fm ~1035-1025 m = dominated by glauconitic sand","SAND (glauconitic)"),
 ("34/7-2","Utsira Fm","1130 m [SEE NOTE]","SWC",0.709051,0.000008,4.21,
  "Univ. Bergen","27 tests of E. variabilis",
  "Utsira Fm ~1035-1025 m = dominated by glauconitic sand","SAND (glauconitic)"),
 ("34/2-4","Utsira Fm","1490-1470 m","DC",0.709068,0.000011,2.62,"IFE",
  "Calcareous benthic index foraminifera",
  "Utsira Fm 1520-1470 m, upper part = mainly quartzose sand, probably caved. "
  "BULLETIN STATES THIS AGE IS 'OBVIOUSLY TOO YOUNG, probably analytical error'",
  "SAND (quartzose, upper Utsira) - AGE REJECTED BY SOURCE"),
 ("34/2-4","Utsira Fm","1510-1500 m","DC",0.709032,0.000008,5.13,"Univ. Bergen",
  "16 tests of E. variabilis, G. subglobosa",
  "Utsira Fm 1520-1470 m, lower part = sand mainly glauconitic","SAND (glauconitic)"),
]

# user's mapped sand bodies (from the classifier work, Vsh<0.30 runs >=8 m)
MAPPED = {"34/4-6": [(1359,1377),(1379,1387)]}


def main():
    with open(OUT/"BIOSTRAT_units.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["well","unit","top_m_RKB","base_m_RKB","thickness_m","age",
                    "litho_unit","key_foram_assemblage","lithology"])
        for well, unit, base, top, age, lu, fo, li in UNITS:
            w.writerow([well, unit, top, base, base - top, age, lu, fo, li])
    with open(OUT/"BIOSTRAT_sr.csv","w",newline="") as f:
        w = csv.writer(f)
        w.writerow(["well","litho_unit","sample_interval","sample_type",
                    "corrected_87Sr_86Sr","2sigma_error","age_Ma","laboratory",
                    "analysed_fossils","host_lithology_from_bulletin",
                    "SAND_or_MUDSTONE"])
        for s in SR:
            w.writerow(list(s))
    # Petrel 3-column well tops -- kept separate from the NPD tops
    with open(OUT/"BIOSTRAT_tops.dat","w") as f:
        f.write("# BIOSTRAT_tops -- NPD Bulletin 10 biostratigraphic unit tops\n")
        f.write("# Source: sodir.no Bulletin 10 well-stratigraphy pages, "
                "fetched 2026-08-01\n")
        f.write("# Depths are m MD RKB. SEPARATE from the NPD lithostratigraphic tops.\n")
        f.write("# WELL  MD  SURFACE      (MD = TOP of the unit)\n")
        for well, unit, base, top, *_ in UNITS:
            surf = f"BIO_{unit.replace(' ','_').replace('(','').replace(')','')}"
            f.write(f'"{well}" {top} "{surf}"\n')
        # add the base of the deepest unit per well so intervals close
        for well in dict.fromkeys(u[0] for u in UNITS):
            deepest = max(u[2] for u in UNITS if u[0] == well)
            f.write(f'"{well}" {deepest} "BIO_BASE_STUDIED_INTERVAL"\n')
    print(f"units: {len(UNITS)}   Sr analyses: {len(SR)}")
    print(f"written -> {OUT}")


if __name__ == "__main__":
    main()
