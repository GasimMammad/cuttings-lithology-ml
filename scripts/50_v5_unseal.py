"""
v5 -- unseal the rater key and score raters A and B against the
LOCKED panel consensus (results/v5/panel_consensus_LOCKED.csv, commit f595585),
exactly as fixed by the panel's final adjudication. Primary: SAND vs NOT-SAND
(MUD, OTHER); UNRESOLVED, UNRESOLVED-SILT, NO-CORE out. Sensitivities S1 (U-SILT
= NOT-SAND), S2 (U-SILT = SAND), S3 (drop i29, i35), S4 (i27 = MUD).
"""
import math

import pandas as pd
from scipy.stats import binomtest

K = pd.read_csv("results/v4/spotcheck_key.csv")
P = pd.read_csv("results/v5/panel_consensus_LOCKED.csv")
d = K.merge(P[["item", "final"]], on="item")


def wilson(k, n, z=1.96):
    if n == 0:
        return float("nan"), float("nan")
    p = k / n; den = 1 + z * z / n; c = (p + z * z / (2 * n)) / den
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / den
    return max(0, c - h), min(1, c + h)


def rater_sand(x):
    return {"SAND": "SAND", "HET": "NOT", "MUD": "NOT", "OTHER": "NOT"}.get(x, None)


def score(df, label_map, tag):
    df = df.copy()
    df["ref"] = df.final.map(label_map)
    df = df[df.ref.notna()]
    out = [f"{tag}: n resolved {len(df)} (disputed {int((df.stratum == 'disputed').sum())}, agreed {int((df.stratum == 'agreed').sum())})"]
    for r in ("a", "b"):
        ok = (df[f"class_{r}"].map(rater_sand) == df.ref)
        lo, hi = wilson(ok.sum(), len(df))
        out.append(f"   rater {r.upper()}: {ok.sum()}/{len(df)} correct ({lo:.2f}-{hi:.2f})")
    dis = df[df.stratum == "disputed"]
    if len(dis):
        a_right = int((dis.ref == "SAND").sum())
        bt = binomtest(a_right, len(dis), 0.5)
        ci = bt.proportion_ci(method="exact")
        out.append(f"   disputed: consensus SAND (A right) {a_right} vs NOT-SAND (B right) {len(dis) - a_right}; "
                   f"P(A right) {a_right / len(dis):.2f} [{ci.low:.2f}-{ci.high:.2f}], exact binomial p {bt.pvalue:.3f}")
    agr = df[df.stratum == "agreed"]
    if len(agr):
        both_wrong = int((agr.class_a.map(rater_sand) != agr.ref).sum())
        out.append(f"   agreed: both raters wrong together {both_wrong}/{len(agr)}")
    return "\n".join(out)


base = {"SAND": "SAND", "MUD": "NOT", "OTHER": "NOT"}
print(d.groupby(["stratum", "final"]).size().unstack(fill_value=0).to_string(), "\n")
print("NO-CORE bins:", d[d.final == "NO-CORE"][["item", "class_a", "class_b"]].to_string(index=False), "\n")
print(score(d, base, "PRIMARY"))
print(score(d, {**base, "UNRESOLVED-SILT": "NOT"}, "S1 U-SILT=NOT-SAND"))
print(score(d, {**base, "UNRESOLVED-SILT": "SAND"}, "S2 U-SILT=SAND"))
print(score(d[~d.item.isin(["i29", "i35"])], base, "S3 drop i29,i35"))
d4 = d.copy(); d4.loc[d4.item == "i27", "final"] = "MUD"
print(score(d4, base, "S4 i27=MUD"))
d.to_csv("results/v5/unsealed_scoring_table.csv", index=False)
