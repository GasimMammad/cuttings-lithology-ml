"""
v7 step 1 (V7_PLAN.md FINAL, 68502f3): can cuttings photographs predict the
XRF chemistry of the SAME bag?

Primary: R-D (ResNet-50 RGB, per-well z over the Tertiary shoe-masked set,
PCA 32, Ridge alpha 1), leave-one-well-out over 11 wells, target T1 =
z_well(log10 Si/Al) uncorrected. Per held-out well: Spearman of high-passed
(+/-50 m running median removed within stretches) predicted vs measured T1;
one-sided Wilcoxon of the 11 rho > 0. Claim needs p < 0.05 AND median rho
>= 0.10. Everything else (sensitivities, baselines, leakage controls,
nulls, lag profile, capture sessions, downstream AUC) as in the plan.

Run:  python 52_v7_photo_to_xrf.py
"""
import json
from importlib import import_module

import lasio
import numpy as np
import pandas as pd
from scipy.stats import chi2, spearmanr, theilslopes, wilcoxon
from sklearn.decomposition import PCA
from sklearn.linear_model import Ridge
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

import config as C
from features import FEATURE_NAMES

EV = import_module("29_v2_evaluate")
BL = import_module("34_v3_baselines")
XS = import_module("35_v3_xrf_shallow")
CM = import_module("42_v4_cement_mask")

OUT = C.WORK_DIR / "v7"
RNG = np.random.default_rng(7)
ELEM = ["SI", "AL", "BA", "CA", "CL", "S", "ZN", "PB"]
AREA = lambda w: w[:4]  # 24_9, 34_4, 34_7, 34_8
ALPHAS = [1, 10, 100, 1e3, 1e4]
MIN_STRETCH = 30
N_SHIFT = 200


# ----------------------------------------------------------------------------
# data
# ----------------------------------------------------------------------------
def xrf_table(base):
    out = pd.DataFrame(np.nan, index=base.index, columns=ELEM)
    for w in base.well.unique():
        f = C.SSD_ROOT / "Wells" / w / "DRILLING" / f"{w}_CUTTINGS_XRF_1.LAS"
        if not f.exists():
            continue
        d = lasio.read(str(f), engine="normal").df()[ELEM]
        d.index = np.round(d.index.values.astype(float), 2)
        d = d[~d.index.duplicated()]
        m = (base.well == w).values
        out.loc[m, ELEM] = d.reindex(np.round(base.depth_m.values[m], 2)).values
    return out


def zwell(v, wells, sel):
    """z-score within well, statistics from the rows in `sel` only."""
    z = np.full(len(v), np.nan)
    for w in np.unique(wells[sel]):
        m = sel & (wells == w)
        mu, sd = np.nanmean(v[m]), np.nanstd(v[m])
        z[m] = (v[m] - mu) / (sd if sd > 1e-12 else 1.0)
    return z


def zwell_mat(X, wells, sel, ref=None):
    ref = X if ref is None else ref
    Z = np.full(X.shape, np.nan)
    for w in np.unique(wells[sel]):
        m = sel & (wells == w)
        mu = np.nanmean(ref[m], axis=0)
        sd = np.nanstd(ref[m], axis=0)
        sd[sd < 1e-9] = 1.0
        Z[m] = (X[m] - mu) / sd
    return Z


def ts_resid(y, x, wells, sel, clip_neg_only=False):
    """Per-well Theil-Sen of y on x; return y - b*(x - median x)."""
    r = np.full(len(y), np.nan)
    for w in np.unique(wells[sel]):
        m = sel & (wells == w) & np.isfinite(y) & np.isfinite(x)
        b = theilslopes(y[m], x[m])[0]
        if clip_neg_only:
            b = min(b, 0.0)
        r[m] = y[m] - b * (x[m] - np.median(x[m]))
    return r


def ols_resid(y, Xc, wells, sel):
    r = np.full(len(y), np.nan)
    for w in np.unique(wells[sel]):
        m = sel & (wells == w) & np.isfinite(y) & np.isfinite(Xc).all(1)
        A = np.c_[np.ones(m.sum()), Xc[m]]
        beta, *_ = np.linalg.lstsq(A, y[m], rcond=None)
        r[m] = y[m] - A @ beta
    return r


# ----------------------------------------------------------------------------
# high-pass and stretches
# ----------------------------------------------------------------------------
def stretch_ids(d, gap=30.0, groups=None):
    """Stretch id per row (rows in any order): split at depth gaps > gap and,
    if given, wherever `groups` changes along depth."""
    o = np.argsort(d, kind="stable")
    brk = np.r_[False, np.diff(d[o]) > gap]
    if groups is not None:
        g = np.asarray(groups)[o]
        brk |= np.r_[False, g[1:] != g[:-1]]
    sid = np.empty(len(d), int)
    sid[o] = np.cumsum(brk)
    return sid


def highpass(d, v, half=50.0, gap=30.0, groups=None, bags=None):
    """v minus centred running median within stretches; window +/-half m, or
    +/-`bags` neighbours if bags is given."""
    sid = stretch_ids(d, gap, groups)
    out = np.full(len(v), np.nan)
    for s in np.unique(sid):
        ix = np.flatnonzero(sid == s)
        ix = ix[np.argsort(d[ix], kind="stable")]
        dd, vv = d[ix], v[ix]
        for k in range(len(ix)):
            if bags is None:
                m = (dd >= dd[k] - half) & (dd <= dd[k] + half)
                med = np.nanmedian(vv[m])
            else:
                med = np.nanmedian(vv[max(0, k - bags):k + bags + 1])
            out[ix[k]] = vv[k] - med
    return out


def rho(a, b):
    m = np.isfinite(a) & np.isfinite(b)
    if m.sum() < 10:
        return np.nan
    return float(spearmanr(a[m], b[m])[0])


def partial_rho(a, b, Ctrl):
    """Spearman partial correlation: ranks, OLS out the controls, correlate."""
    m = np.isfinite(a) & np.isfinite(b) & np.isfinite(Ctrl).all(1)
    if m.sum() < 20:
        return np.nan
    rk = lambda x: pd.Series(x).rank().values
    A = np.c_[np.ones(m.sum()), np.column_stack([rk(c) for c in Ctrl[m].T])]
    ra, rb = rk(a[m]), rk(b[m])
    ea = ra - A @ np.linalg.lstsq(A, ra, rcond=None)[0]
    eb = rb - A @ np.linalg.lstsq(A, rb, rcond=None)[0]
    return float(np.corrcoef(ea, eb)[0, 1])


# ----------------------------------------------------------------------------
# models
# ----------------------------------------------------------------------------
def fit_rd(X, y, w=None):
    p = make_pipeline(StandardScaler(), PCA(n_components=32, random_state=0), Ridge(alpha=1.0))
    p.fit(X, y)
    return p


def fit_re(X, y, w=None):
    p = make_pipeline(StandardScaler(), Ridge(alpha=1.0))
    p.fit(X, y)
    return p


def well_weights(wells):
    u, inv, cnt = np.unique(wells, return_inverse=True, return_counts=True)
    sw = 1.0 / cnt[inv]
    return sw * len(sw) / sw.sum()


def fit_raw(X, y, wells, d, alpha):
    sc = StandardScaler().fit(X)
    r = Ridge(alpha=alpha).fit(sc.transform(X), y, sample_weight=well_weights(wells))
    return lambda Xn: r.predict(sc.transform(Xn))


def raw_inner_alpha(X, y, wells, d):
    """Inner LOWO over the training wells; criterion = median per-well
    high-passed Spearman."""
    score = {}
    for a in ALPHAS:
        rr = []
        for v in np.unique(wells):
            tr, te = wells != v, wells == v
            f = fit_raw(X[tr], y[tr], wells[tr], d[tr], a)
            p = f(X[te])
            rr.append(rho(highpass(d[te], p), highpass(d[te], y[te])))
        score[a] = np.nanmedian(rr)
    return max(score, key=score.get), score


def cv_predict(X, y, wells, d, sel, kind, fold_of):
    """Cross-validated predictions on rows `sel`; fold_of(well) -> fold key."""
    pred = np.full(len(y), np.nan)
    info = {}
    ok = sel & np.isfinite(y) & np.isfinite(X).all(1)
    folds = np.array([fold_of(w) for w in wells])
    for f in np.unique(folds[ok]):
        tr, te = ok & (folds != f), ok & (folds == f)
        if kind == "RD":
            pred[te] = fit_rd(X[tr], y[tr]).predict(X[te])
        elif kind == "RE":
            pred[te] = fit_re(X[tr], y[tr]).predict(X[te])
        elif kind == "RAW":
            a, sc = raw_inner_alpha(X[tr], y[tr], wells[tr], d[tr])
            pred[te] = fit_raw(X[tr], y[tr], wells[tr], d[tr], a)(X[te])
            info[f] = {"alpha": a, "inner": {str(k): round(v, 4) for k, v in sc.items()}}
    return pred, info


# ----------------------------------------------------------------------------
# evaluation
# ----------------------------------------------------------------------------
def per_well_hp(pred, y, wells, d, sel, **hp):
    rows = {}
    for w in np.unique(wells[sel]):
        m = sel & (wells == w) & np.isfinite(pred) & np.isfinite(y)
        if m.sum() < MIN_STRETCH:
            continue
        rows[w] = rho(highpass(d[m], pred[m], **hp), highpass(d[m], y[m], **hp))
    return pd.Series(rows, dtype=float)


def summarise(s, alt="greater"):
    s = s.dropna()
    if len(s) < 3:
        return {"n_wells": len(s)}
    bs = np.median(RNG.choice(s.values, (10000, len(s))), axis=1)
    return {"n_wells": int(len(s)), "median_rho": float(s.median()),
            "n_pos": int((s > 0).sum()),
            "wilcoxon_p": float(wilcoxon(s.values, alternative=alt).pvalue),
            "boot95_median": [float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5))]}


def circ_null(hp_p, hp_y, d):
    """Per-well circular-shift null within stretches >= MIN_STRETCH bags
    (no wrap across gaps). Returns observed rho on those rows and p."""
    sid = stretch_ids(d)
    keep = np.zeros(len(d), bool)
    order = {}
    for s in np.unique(sid):
        ix = np.flatnonzero(sid == s)
        if len(ix) >= MIN_STRETCH:
            keep[ix] = True
            order[s] = ix[np.argsort(d[ix])]
    if keep.sum() < MIN_STRETCH:
        return np.nan, np.nan
    obs = rho(hp_p[keep], hp_y[keep])
    null = []
    for f in np.linspace(0.02, 0.98, N_SHIFT):
        sh = hp_p.copy()
        for s, ix in order.items():
            L = len(ix)
            k = int(np.clip(round(f * L), 10, L - 10))
            sh[ix] = np.roll(hp_p[ix], k)
        null.append(rho(sh[keep], hp_y[keep]))
    null = np.array(null)
    return obs, float((1 + (null >= obs).sum()) / (1 + len(null)))


def lag_profile(hp_p, hp_y, d, lags=range(-5, 6)):
    """rho(photo k, chem k+m) within stretches, and the no-skill curve
    rho(0) * ACF_chem(m)."""
    sid = stretch_ids(d)
    prof, acf = {}, {}
    for m in lags:
        a, b, c = [], [], []
        for s in np.unique(sid):
            ix = np.flatnonzero(sid == s)
            ix = ix[np.argsort(d[ix])]
            if len(ix) <= abs(m):
                continue
            i0 = ix[max(0, -m):len(ix) - max(0, m)]
            i1 = ix[max(0, m):len(ix) - max(0, -m)]
            a.append(hp_p[i0]); b.append(hp_y[i1]); c.append(hp_y[i0])
        a, b, c = map(np.concatenate, (a, b, c))
        prof[m] = rho(a, b)
        acf[m] = rho(c, b)
    return prof, acf


def block(pred, y, wells, d, sel, tag, extra=None):
    s = per_well_hp(pred, y, wells, d, sel)
    out = {"tag": tag, **summarise(s), "per_well": s.round(4).to_dict()}
    if extra:
        out.update(extra)
    return out, s


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    base, emb = EV.load_tables()
    wells = base.well.values
    d = base.depth_m.values.astype(float)
    x = xrf_table(base)
    L = {e: np.log10(x[e].values.astype(float) + (0 if e in ("SI", "AL", "BA", "CA") else 1.0)) for e in ELEM}
    for e in ("SI", "AL", "BA", "CA"):
        L[e][~(x[e].values > 0)] = np.nan

    tert = d < np.array([XS.TOP_SHETLAND[w] for w in wells])
    shoe = CM.shoe_mask(base)
    has = np.isfinite(L["SI"]) & np.isfinite(L["AL"])
    S = tert & ~shoe & has
    P = ~tert & ~shoe & has  # pre-Tertiary, descriptive
    print(f"bags: all {len(base)}, Tertiary {tert.sum()}, shoe-masked {(tert & shoe).sum()}, "
          f"no XRF {(tert & ~shoe & ~has).sum()}, selected S {S.sum()}, pre-Tertiary P {P.sum()}")

    lsial = L["SI"] - L["AL"]
    al_p5 = np.zeros(len(base), bool)
    for w in np.unique(wells[S]):
        m = S & (wells == w)
        al_p5[m] = x.AL.values[m] < np.nanpercentile(x.AL.values[m], 5)

    def targets(sel):
        T = {}
        T["T1"] = zwell(lsial, wells, sel)
        T["T1_TS"] = zwell(ts_resid(lsial, L["BA"], wells, sel, clip_neg_only=True), wells, sel)
        T["T2_Ca"] = zwell(ts_resid(L["CA"], L["BA"], wells, sel), wells, sel)
        T["BA"] = zwell(L["BA"], wells, sel)
        T["ZNPB"] = zwell(ols_resid(np.log10(x.ZN.values + x.PB.values + 1),
                                    np.c_[L["BA"], lsial], wells, sel), wells, sel)
        return T

    def inputs(sel):
        rgb = emb["rgb"].astype(float)
        E15 = base[FEATURE_NAMES].values.astype(float)
        R15 = base[["ref_" + c for c in FEATURE_NAMES]].values.astype(float)
        return {"RD": zwell_mat(rgb, wells, sel), "RE": zwell_mat(E15, wells, sel, R15)}

    T, X = targets(S), inputs(S)
    lowo = lambda w: w
    res, perwell = {}, {}

    # ---- primary
    pRD, _ = cv_predict(X["RD"], T["T1"], wells, d, S, "RD", lowo)
    r, s = block(pRD, T["T1"], wells, d, S, "PRIMARY R-D T1 LOWO +/-50 m")
    r["claim_pass"] = bool(r.get("wilcoxon_p", 1) < 0.05 and r.get("median_rho", 0) >= 0.10)
    res["primary"] = r; perwell["primary"] = s
    print(json.dumps(r, indent=1))

    # ---- per-well circular-shift null, Fisher (secondary), lag profile
    circ, lagp, lagacf = {}, {}, {}
    for w in np.unique(wells[S]):
        m = S & (wells == w) & np.isfinite(pRD)
        hp_p, hp_y = highpass(d[m], pRD[m]), highpass(d[m], T["T1"][m])
        circ[w] = circ_null(hp_p, hp_y, d[m])
        lagp[w], lagacf[w] = lag_profile(hp_p, hp_y, d[m])
    ps = np.array([v[1] for v in circ.values() if np.isfinite(v[1])])
    res["circular_null"] = {"per_well": {w: {"rho_kept": round(o, 4), "p": round(p, 4)} for w, (o, p) in circ.items()},
                            "fisher_p_secondary": float(chi2.sf(-2 * np.log(ps).sum(), 2 * len(ps)))}
    lp = pd.DataFrame(lagp).T; la = pd.DataFrame(lagacf).T
    noskill = la.mul(lp[0], axis=0)
    res["lag_profile"] = {"median_rho_by_lag": lp.median().round(4).to_dict(),
                          "median_noskill_by_lag": noskill.median().round(4).to_dict(),
                          "per_well_excess_at_0_vs_shoulders":
                              (lp[0] - lp[[-1, 1]].mean(axis=1)).round(4).to_dict()}
    lp.to_csv(OUT / "lag_profile_per_well.csv"); noskill.to_csv(OUT / "lag_noskill_per_well.csv")

    # ---- not-mud condition: partial Spearman controlling hp Ba, Ca/Al, Cl
    pr = {}
    for w in np.unique(wells[S]):
        m = S & (wells == w) & np.isfinite(pRD)
        ctrl = np.column_stack([highpass(d[m], v[m]) for v in (L["BA"], L["CA"] - L["AL"], L["CL"])])
        pr[w] = partial_rho(highpass(d[m], pRD[m]), highpass(d[m], T["T1"][m]), ctrl)
    pr = pd.Series(pr)
    r = {"tag": "T1-P partial (hp Ba, Ca/Al, Cl)", **summarise(pr), "per_well": pr.round(4).to_dict()}
    r["not_mud_condition_pass"] = bool(np.sign(pr.median()) == np.sign(res["primary"].get("median_rho", 0))
                                       and pr.median() >= 0.05)
    res["T1_P"] = r; perwell["T1_P"] = pr

    # ---- sensitivities
    for tag, hp in (("hp +/-25 m", {"half": 25.0}), ("hp +/-5 bags", {"bags": 5})):
        s = per_well_hp(pRD, T["T1"], wells, d, S, **hp)
        res[f"sens {tag}"] = {**summarise(s), "per_well": s.round(4).to_dict()}; perwell[f"sens {tag}"] = s
    s = pd.Series({w: rho(pRD[S & (wells == w)], T["T1"][S & (wells == w)]) for w in np.unique(wells[S])})
    res["sens unfiltered"] = {**summarise(s), "per_well": s.round(4).to_dict()}; perwell["sens unfiltered"] = s

    p, _ = cv_predict(X["RD"], T["T1_TS"], wells, d, S, "RD", lowo)
    res["sens T1-TS"], perwell["sens T1-TS"] = block(p, T["T1_TS"], wells, d, S, "R-D on T1-TS")

    S2 = S & ~al_p5
    T2, X2 = targets(S2), inputs(S2)
    p, _ = cv_predict(X2["RD"], T2["T1"], wells, d, S2, "RD", lowo)
    res["sens S-Al"], perwell["sens S-Al"] = block(p, T2["T1"], wells, d, S2, "R-D T1 without Al<p5")

    pRE, _ = cv_predict(X["RE"], T["T1"], wells, d, S, "RE", lowo)
    res["sens R-E"], perwell["sens R-E"] = block(pRE, T["T1"], wells, d, S, "R-E engineered")

    pRAW, info = cv_predict(X["RD"], T["T1"], wells, d, S, "RAW", lowo)
    res["sens R-RAW"], perwell["sens R-RAW"] = block(pRAW, T["T1"], wells, d, S, "R-RAW inner-LOWO alpha",
                                                     {"alpha_per_fold": info})

    pA, _ = cv_predict(X["RD"], T["T1"], wells, d, S, "RD", AREA)
    res["sens LOAO"], perwell["sens LOAO"] = block(pA, T["T1"], wells, d, S, "R-D leave-one-area-out")

    # ---- secondary target Ca
    p, _ = cv_predict(X["RD"], T["T2_Ca"], wells, d, S, "RD", lowo)
    res["secondary T2 Ca"], perwell["secondary T2 Ca"] = block(p, T["T2_Ca"], wells, d, S, "R-D on T2 Ca (Ba-partialled)")
    gyp = {w: rho(L["CA"][S & (wells == w)], L["S"][S & (wells == w)]) for w in np.unique(wells[S])}
    res["secondary T2 Ca"]["rho_Ca_S_gypsum_flag"] = {k: round(v, 3) for k, v in gyp.items()}

    # ---- baselines (same series, same high-pass, sign from training wells), paired vs R-D
    hpw = lambda v, w: highpass(d[S & (wells == w)], v[S & (wells == w)])
    dw = BL.dry_weight(base)
    for name, sig in (("relative depth", d.copy()), ("bag dry weight", np.log10(dw))):
        tr_rho = {w: rho(hpw(sig, w), hpw(T["T1"], w)) for w in np.unique(wells[S])}
        s = {}
        for w in tr_rho:
            others = [tr_rho[v] for v in tr_rho if v != w and np.isfinite(tr_rho[v])]
            sign = np.sign(np.nanmean(others)) if others else 1.0
            s[w] = sign * tr_rho[w] if np.isfinite(tr_rho[w]) else np.nan
        s = pd.Series(s)
        both = pd.concat([perwell["primary"], s], axis=1).dropna()
        paired = float(wilcoxon(both.iloc[:, 0] - both.iloc[:, 1], alternative="greater").pvalue) if len(both) >= 5 else np.nan
        res[f"baseline {name}"] = {**summarise(s), "per_well": s.round(4).to_dict(),
                                   "paired_RD_gt_baseline_p": paired, "n_paired": int(len(both))}
        perwell[f"baseline {name}"] = s

    # ---- leakage / negative controls
    p, _ = cv_predict(X["RD"], T["BA"], wells, d, S, "RD", lowo)
    res["leak photo->Ba"], perwell["leak photo->Ba"] = block(p, T["BA"], wells, d, S, "R-D on z log Ba")
    for nm, v in (("Ba", L["BA"]), ("Cl", L["CL"])):
        s = pd.Series({w: rho(hpw(pRD, w), hpw(v, w)) for w in np.unique(wells[S])})
        res[f"leak rho(pred T1, hp {nm})"] = {"median_rho": float(s.median()), "per_well": s.round(4).to_dict()}
    p, _ = cv_predict(X["RD"], T["ZNPB"], wells, d, S, "RD", lowo)
    res["neg control Zn+Pb resid"], perwell["neg control Zn+Pb"] = block(
        p, T["ZNPB"], wells, d, S, "R-D on Zn+Pb residual (ambiguous if it fails)")

    # ---- capture sessions (always run)
    cs_f = OUT / "capture_sessions.csv"
    if cs_f.exists():
        cs = pd.read_csv(cs_f)
        key = base[["well", "depth_m"]].merge(cs[["well", "depth_m", "session", "reshoot"]].drop_duplicates(["well", "depth_m"]),
                                              on=["well", "depth_m"], how="left")
        sess = key.session.fillna(-1).values
        s = {}
        for w in np.unique(wells[S]):
            m = S & (wells == w)
            s[w] = rho(highpass(d[m], pRD[m], groups=sess[m]), highpass(d[m], T["T1"][m], groups=sess[m]))
        s = pd.Series(s)
        res["sens within capture sessions"] = {**summarise(s), "per_well": s.round(4).to_dict(),
                                               "sessions_per_well": pd.Series(sess[S]).groupby(wells[S]).nunique().to_dict()}
        perwell["sens within capture sessions"] = s
        rs = key.reshoot.fillna(False).values.astype(bool)
        rows = {}
        for w in np.unique(wells[S & rs]):
            m = S & (wells == w)
            e = np.abs(highpass(d[m], pRD[m]) - highpass(d[m], T["T1"][m]))  # same z scale only roughly
            rows[w] = {"n_reshoot": int(rs[m].sum()), "abs_err_reshoot_median": float(np.nanmedian(e[rs[m]])),
                       "abs_err_other_median": float(np.nanmedian(e[~rs[m]]))}
        res["reshoot check (descriptive)"] = rows
    else:
        res["sens within capture sessions"] = "capture_sessions.csv missing: run 52a first"

    # ---- downstream (EXPLORATORY): AUC of predicted T1 for v2 GR labels inside S
    lab = base.label.values
    v2 = pd.read_csv(C.WORK_DIR / "v2_results" / "predictions.csv")
    dn = {}
    for w in np.unique(wells[S]):
        m = S & (wells == w) & np.isin(lab, ["sand", "clay"])
        y = lab[m] == "sand"
        if y.sum() >= 3 and (~y).sum() >= 3:
            dn[w] = {"n_sand": int(y.sum()), "n_clay": int((~y).sum()),
                     "auc_predT1": EV.auc(y, pRD[m]), "auc_v2_E2": EV.auc(y, v2.p_E2.values[m]),
                     "local_auc_predT1": BL.local_auc(d[m], pRD[m], y, 50)[0]}
    res["downstream GR labels (exploratory)"] = dn

    # ---- pre-Tertiary, descriptive (own normalisation set)
    TP, XP = targets(P), inputs(P)
    okw = [w for w in np.unique(wells[P]) if (P & (wells == w)).sum() >= MIN_STRETCH]
    Pk = P & np.isin(wells, okw)
    p, _ = cv_predict(XP["RD"], TP["T1"], wells, d, Pk, "RD", lowo)
    res["pre-Tertiary (descriptive)"], perwell["pre-Tertiary"] = block(p, TP["T1"], wells, d, Pk, "R-D T1 pre-Tertiary")

    # ---- save
    pd.DataFrame(perwell).round(4).to_csv(OUT / "step1_per_well.csv")
    pd.DataFrame({"well": wells, "depth_m": d, "in_S": S, "T1": T["T1"], "pred_RD": pRD,
                  "pred_RE": pRE, "pred_RAW": pRAW, "pred_LOAO": pA}).to_csv(OUT / "step1_predictions.csv", index=False)
    with open(OUT / "step1_results.json", "w") as f:
        json.dump(res, f, indent=1, default=float)
    print("\n===== summary =====")
    for k, v in res.items():
        if isinstance(v, dict) and "median_rho" in v:
            print(f"{k:45s} med rho {v['median_rho']:+.3f}  pos {v.get('n_pos','-')}/{v.get('n_wells','-')}  "
                  f"p {v.get('wilcoxon_p', float('nan')):.4f}")
    print("claim_pass:", res["primary"]["claim_pass"], " not_mud_pass:", res["T1_P"]["not_mud_condition_pass"])
    print("Fisher (secondary):", res["circular_null"]["fisher_p_secondary"])
    print("lag median:", res["lag_profile"]["median_rho_by_lag"])
    print("no-skill:  ", res["lag_profile"]["median_noskill_by_lag"])


if __name__ == "__main__":
    main()
