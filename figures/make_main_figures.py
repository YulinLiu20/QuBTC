"""Main-text figures 1-4.

Reads the replication data from Harvard Dataverse (doi:10.7910/DVN/THUHEB).
Set QUBTC_DATA to the folder of the unpacked dataset (the folder containing results/ and data/).
"""
import os
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.patches import Patch

DATA = os.environ.get("QUBTC_DATA", "dataverse")          # unpacked Dataverse dataset
D = os.path.join(DATA, "results", "")                      # estimates and summaries written by the notebooks
OUT = os.environ.get("QUBTC_FIGS", "figs/")
os.makedirs(OUT, exist_ok=True)
# ---- plot defaults ----
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "xtick.minor.visible": False, "ytick.minor.visible": False,
    "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": "#52514e",
    "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.labelcolor": "#0b0b0b",
    "pdf.fonttype": 42, "savefig.dpi": 300, "legend.frameon": False,
})
C1, C2, C3, C4, C5, C6, C7 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"
INK2, MUTED, BASE = "#52514e", "#898781", "#c3c2b7"
CM = 1 / 2.54

def panel(ax, letter, x=-0.14, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom", ha="left")

EVENTS = [("willow", "2024-12-09", "Willow"), ("gidney", "2025-05-21", "Gidney"), ("lopp", "2025-07-15", "Lopp proposal"),
          ("bip360", "2026-02-11", "BIP-360"), ("google", "2026-03-31", "Google ECDLP"), ("bip361", "2026-04-14", "BIP-361")]

# =============== FIG 1 ===============
snap = pd.DataFrame([
 ("2024-09-26", 6100041, 76863, 13579742), ("2024-12-08", 6197925, 106570, 13486056), ("2025-05-20", 6244510, 150814, 13469491),
 ("2025-07-14", 6220809, 155557, 13513308), ("2026-02-10", 6715796, 197146, 13071689), ("2026-03-30", 6710733, 204573, 13091282),
 ("2026-04-13", 6720898, 207878, 13083945), ("2026-09-22", 6938516, 217965, 12928883)], columns=["d", "L", "T", "C"])
snap["d"] = pd.to_datetime(snap.d); snap["E"] = (snap.L + snap["T"]) / 1e6
snap["share"] = (snap.L + snap["T"]) / (snap.L + snap["T"] + snap.C)
att = pd.read_parquet(os.path.join(DATA, "data", "analysis", "attention_daily.parquet"))
att["date"] = pd.to_datetime(att["date"])
att = att[(att.date >= "2024-06-01")]
types = pd.read_csv(D + "out40/q3_uneconomic_by_cls_type.csv").groupby("type")[["n_utxo", "btc"]].sum()

fig = plt.figure(figsize=(18.4 * CM, 11.5 * CM))
gs = fig.add_gridspec(2, 3, height_ratios=[1, 1], width_ratios=[1, 1, 0.9], hspace=0.55, wspace=0.55)
axA = fig.add_subplot(gs[0, :2]); axB = fig.add_subplot(gs[1, :2]); axC = fig.add_subplot(gs[:, 2])
# A exposed stock
axA.plot(snap.d, snap.E, color=C1, lw=1.4, marker="o", ms=3.5, zorder=3)
for _, r in snap.iloc[[0, -1]].iterrows():
    axA.annotate(f"{r.E:.2f}M BTC\n({r.share*100:.1f}% of supply)", (r.d, r.E), xytext=(0, -22) if _==0 else (-4, 8),
                 textcoords="offset points", ha="center" if _==0 else "right", fontsize=6.3, color="#0b0b0b")
axA.set_ylim(5.75, 7.45); axA.set_ylabel("Exposed supply\n(million BTC)")
for k, d, lab in EVENTS:
    dd = pd.Timestamp(d); axA.axvline(dd, color=BASE, lw=0.6, zorder=1)
axA.set_xlim(pd.Timestamp("2024-06-01"), pd.Timestamp("2026-10-01"))
axA.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); axA.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
panel(axA, "A", x=-0.09)
# B attention
axB.plot(att.date, att.attn_pc1, color=MUTED, lw=0.5, zorder=2)
ymax = 11.5
for k, d, lab in EVENTS:
    dd = pd.Timestamp(d); axB.axvline(dd, color=BASE, lw=0.6, zorder=1)
    w = att[(att.date >= dd - pd.Timedelta(days=2)) & (att.date <= dd + pd.Timedelta(days=7))]
    pk = w.loc[w.attn_pc1.idxmax()]
    axB.plot(pk.date, pk.attn_pc1, "o", color=C2, ms=3.5, zorder=4, mec="white", mew=0.5)
    axB.text(dd + pd.Timedelta(days=(4 if k=="bip361" else -3)), ymax, lab, rotation=90, fontsize=6, va="top", ha=("left" if k=="bip361" else "right"), color=INK2)
axB.set_ylim(-3, ymax); axB.set_ylabel("General quantum attention\n(s.d. units)")
axB.set_xlim(axA.get_xlim()); axB.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7]))
axB.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y")); panel(axB, "B", x=-0.09)
# C by script type
order = [("pubkey", "P2PK"), ("pubkeyhash", "P2PKH (reused)"), ("scripthash", "P2SH (revealed)"),
         ("witness_v0_keyhash", "P2WPKH (reused)"), ("witness_v0_scripthash", "P2WSH (revealed)"), ("witness_v1_taproot", "P2TR (all)")]
labs = [o[1] for o in order][::-1]; vals = [types.loc[o[0], "btc"] / 1e6 for o in order][::-1]
ns = [types.loc[o[0], "n_utxo"] / 1e6 for o in order][::-1]
y = np.arange(len(labs))
axC.barh(y, vals, color=C1, height=0.62)
for yi, v, n in zip(y, vals, ns):
    axC.text(v + 0.04, yi, f"{v:.2f}", va="center", fontsize=6.3)
axC.set_yticks(y); axC.set_yticklabels(labs); axC.set_xlabel("Exposed BTC at freeze date\n(million)")
axC.set_xlim(0, 2.6); axC.tick_params(axis="y", length=0); axC.spines["left"].set_visible(False)
panel(axC, "C", x=-0.55, y=1.0)
fig.savefig(OUT + "Fig1.png", bbox_inches="tight"); fig.savefig(OUT + "Fig1.pdf", bbox_inches="tight"); plt.close(fig)

# =============== FIG 2 ===============
eff = pd.read_csv(D + "est_20_effects.csv.gz")
q = eff[(eff.contrast == "LC") & (eff.variant == "all") & (eff.subgroup == "all") & (eff.pool == "main") & (eff.h == 90) &
        (eff.outcome == "c_y1_strict") & (eff.weight == "key") & (eff.rel_day == 30)].set_index("event")
pool = pd.read_csv(D + "est_20_pooled.csv")
pq = pool[(pool.contrast == "LC") & (pool.variant == "all") & (pool.subgroup == "all") & (pool.pool == "main") & (pool.h == 90) &
          (pool.outcome == "c_y1_strict") & (pool.weight == "key") & (pool.rel_day == 30)].iloc[0]
sub = pd.read_csv(D + "out20b/est_20b_subsets.csv")
hq = sub[(sub.contrast == "LC") & (sub.variant == "all") & (sub.subgroup == "all") & (sub.pool == "main") & (sub.h == 90) &
         (sub.outcome == "c_y1_strict") & (sub.weight == "key") & (sub.rel_day == 30) & (sub.subset == "C_high_attention")].iloc[0]
p21 = pd.read_csv(D + "est_21_pooled.csv")
rsq = p21[(p21.win == "main") & (p21.contrast == "RS2") & (p21.variant == "all") & (p21.subgroup == "all") & (p21.pool == "main") &
          (p21.h == 90) & (p21.outcome == "c_y1_strict") & (p21.weight == "key") & (p21.rel_day == 30)].iloc[0]
e23 = pd.read_csv(D + "out23/est_23_pc.csv")
r23 = e23[(e23.win == "main") & (e23.contrast == "RS2") & (e23.variant == "all") & (e23.subgroup == "all") & (e23.pool == "pre") &
          (e23.h == 90) & (e23.outcome == "c_y1_strict") & (e23.weight == "key") & (e23.rel_day == 30)].set_index("event")
rs, nt = r23.loc["randstorm"], r23.loc["randstorm_notice"]
rows = [(lab, q.loc[k, "beta"], q.loc[k, "ci90_lo"], q.loc[k, "ci90_hi"], C1, "o") for k, d, lab in EVENTS]
rows += [("Two high-attention\nevents, pooled", hq.beta_mean, hq.ci90_lo, hq.ci90_hi, C1, "D")]
rows += [("Six quantum events, pooled", pq.beta_mean, pq.ci90_lo, pq.ci90_hi, C1, "D")]
rows += [("Quantum events, same\nwallet-type contrast", rsq.beta_mean, rsq.ci90_lo, rsq.ci90_hi, C1, "D")]
rows += [("Randstorm notices\n(10 Oct 2023)", nt.beta, nt.ci90_lo, nt.ci90_hi, C4, "s")]
rows += [("Randstorm disclosure\n(14 Nov 2023)", rs.beta, rs.ci90_lo, rs.ci90_hi, C2, "s")]
fig = plt.figure(figsize=(18.4 * CM, 8.4 * CM))
gs = fig.add_gridspec(1, 3, width_ratios=[1.35, 1.1, 0.95], wspace=0.55)
ax = fig.add_subplot(gs[0])
ypos = np.array([11.8, 10.8, 9.8, 8.8, 7.8, 6.8, 5.4, 4.4, 3.2, 1.8, 0.6])
d2 = rs.beta / 4
ax.axvspan(-d2 * 100, d2 * 100, color="#e1e0d9", zorder=0, lw=0)
ax.axvline(0, color=INK2, lw=0.6, zorder=1)
for (lab, b, lo, hi, col, mk), yy in zip(rows, ypos):
    ax.plot([lo * 100, hi * 100], [yy, yy], color=col, lw=1.2, zorder=2, solid_capstyle="round")
    ax.plot(b * 100, yy, mk, color=col, ms=(3.2 if mk=="D" else 4.2), zorder=3, mec="white", mew=0.5)
ax.set_yticks(ypos); ax.set_yticklabels([r[0] for r in rows]); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False)
ax.set_xlabel("Effect on 30-day protective migration\n(percentage points; 90% interval)")
ax.set_xlim(-0.6, 3.1); ax.set_ylim(-0.1, 13.4)
ax.text(0, 13.35, "Equivalence\nbounds ±δ$_2$", fontsize=5.8, color=INK2, ha="center", va="top",
        bbox=dict(boxstyle="square,pad=0.1", fc="#e1e0d9", ec="none"), zorder=4)
panel(ax, "A", x=-0.62)
# B observed vs counterfactual
ax = fig.add_subplot(gs[1])
grp = [("Quantum\nevents", pq.level_T_mean, pq.beta_mean, C1), ("Randstorm\nnotices", nt.level_T, nt.beta, C4),
       ("Randstorm\ndisclosure", rs.level_T, rs.beta, C2)]
x = np.arange(len(grp)); w = 0.36
cfs = [l - b for _, l, b, _ in grp]; obs = [l for _, l, b, _ in grp]
ax.bar(x - w / 2 - 0.01, [c * 100 for c in cfs], width=w, color="#c3c2b7")
ax.bar(x + w / 2 + 0.01, [o * 100 for o in obs], width=w, color=[g[3] for g in grp])
for xi, (o, c) in enumerate(zip(obs, cfs)):
    ax.text(xi, max(o, c) * 100 + 0.12, f"×{o / c:.1f}", ha="center", fontsize=7, fontweight="bold")
ax.set_xticks(x); ax.set_xticklabels([g[0] for g in grp], fontsize=6); ax.set_ylabel("30-day protective migration (%)")
ax.set_ylim(0, 4.3); ax.tick_params(axis="x", length=0)
from matplotlib.legend_handler import HandlerTuple
ax.legend(handles=[Patch(color="#c3c2b7"), (Patch(color=C1), Patch(color=C4), Patch(color=C2))], labels=["Counterfactual", "Observed"],
          handler_map={tuple: HandlerTuple(ndivide=None, pad=0)}, loc="upper left", fontsize=6)
panel(ax, "B", x=-0.36)
# C pubform
pf = pd.read_csv(D + "pubform_by_month.csv", parse_dates=["m"])
ax = fig.add_subplot(gs[2])
ax.axvspan(pd.Timestamp("2012-04-01"), pd.Timestamp("2014-03-31"), color="#fbe1d6", lw=0, zorder=0)
ax.plot(pf.m, pf.share_u, color=C2, lw=1.2, zorder=2)
ax.text(pd.Timestamp("2013-04-01"), 1.06, "Treatment cohort\n(Apr 2012–Mar 2014)", ha="center", va="bottom", fontsize=6, color=INK2)
ax.set_ylim(0, 1.18); ax.set_yticks([0, 0.25, 0.5, 0.75, 1.0])
ax.set_ylabel("Share of new keys with\nuncompressed public keys")
ax.xaxis.set_major_locator(mdates.YearLocator(base=2)); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
ax.set_xlim(pd.Timestamp("2011-01-01"), pd.Timestamp("2016-12-31"))
panel(ax, "C", x=-0.36)
fig.savefig(OUT + "Fig2.png", bbox_inches="tight"); fig.savefig(OUT + "Fig2.pdf", bbox_inches="tight"); plt.close(fig)

# =============== FIG 3 ===============
seg = pd.read_csv(D + "out30/q2_segments.csv"); seg = seg[seg.grp == "L"].set_index("seg")
sens = pd.read_csv(D + "out30/q2_sensitivity.csv"); sens = sens[sens.grp == "L"]
rng = sens.groupby("seg").s0_btc.agg(["min", "max"])
segorder = [("A Confirmed migrated", "A  Confirmed migrated"), ("B Moved, still exposed", "B  Moved, still exposed"),
            ("C Active, not migrated", "C  Active, not migrated"), ("D Indeterminate", "D  Indeterminate"),
            ("E Behaviorally unreachable (lower bound)", "E  Behaviourally unreachable"), ("Exchange/custodian", "Exchange / custodian"), ("Dust <0.01 BTC", "Small keys (<0.01 BTC)")]
SEGCOL = {"A Confirmed migrated": C1, "B Moved, still exposed": C1, "C Active, not migrated": C1, "D Indeterminate": C3,
          "E Behaviorally unreachable (lower bound)": C7, "Exchange/custodian": C2, "Dust <0.01 BTC": C4}
fig = plt.figure(figsize=(18.4 * CM, 7.2 * CM))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.15], wspace=0.75)
ax = fig.add_subplot(gs[0])
yy = np.arange(len(segorder))[::-1]
for (k, lab), y in zip(segorder, yy):
    v = seg.loc[k, "s0_btc"] / 1e6
    col = SEGCOL[k]
    ax.barh(y, v, color=col, height=0.62)
    lo, hi = rng.loc[k, "min"] / 1e6, rng.loc[k, "max"] / 1e6
    if hi - lo > 1e-3:
        ax.plot([lo, hi], [y, y], color="#0b0b0b", lw=0.8); ax.plot([lo, lo], [y - 0.15, y + 0.15], color="#0b0b0b", lw=0.8)
        ax.plot([hi, hi], [y - 0.15, y + 0.15], color="#0b0b0b", lw=0.8)
    ax.text(max(v, hi) + 0.05, y, (f"{v:.3f}" if v < 0.01 else f"{v:.2f}") + f" ({seg.loc[k,'share_btc']*100:.1f}%)", va="center", fontsize=6.2)
ax.set_yticks(yy); ax.set_yticklabels([s[1] for s in segorder]); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False); ax.set_xlim(0, 3.0)
ax.set_xlabel("Starting exposed balance, legacy keys\n(million BTC, 8 Dec 2024)")
panel(ax, "A", x=-0.78)
# B composition by BTC/UTXO/keys
st = pd.read_csv(D + "out40/q3_stock_by_cls.csv").groupby("cls")[["n_keys", "n_utxo", "btc"]].sum()
cls = [("act", "Individual, active", C1), ("ind", "Individual, indeterminate", C3), ("dorm", "Behaviourally unreachable", C7),
       ("svc", "Exchange / custodian", C2), ("dust", "Small keys (<0.01 BTC)", C4)]
ax = fig.add_subplot(gs[1])
metrics = [("btc", "By BTC\n(7.16M)"), ("n_utxo", "By UTXO\n(99.2M)"), ("n_keys", "By key\n(14.0M)")]
for i, (m, lab) in enumerate(metrics):
    tot = st[m].sum(); left = 0
    for c, cl, col in cls:
        v = st.loc[c, m] / tot
        ax.barh(2 - i, v, left=left, color=col, height=0.6, edgecolor="white", linewidth=0.8)
        if v > 0.09:
            ax.text(left + v / 2, 2 - i, f"{v*100:.0f}%", ha="center", va="center", fontsize=6.2, color="white", fontweight="bold")
        left += v
ax.set_yticks([2, 1, 0]); ax.set_yticklabels([m[1] for m in metrics]); ax.tick_params(axis="y", length=0)
ax.spines["left"].set_visible(False); ax.set_xlim(0, 1); ax.set_xticks([0, 0.25, 0.5, 0.75, 1]); ax.set_xticklabels(["0", "25", "50", "75", "100"])
ax.set_xlabel("Share of exposed set at freeze date (%)")
ax.legend(handles=[Patch(color=col, label=cl) for c, cl, col in cls], loc="upper center", bbox_to_anchor=(0.42, -0.24), ncol=3, fontsize=6)
panel(ax, "B", x=-0.3)
fig.savefig(OUT + "Fig3.png", bbox_inches="tight"); fig.savefig(OUT + "Fig3.pdf", bbox_inches="tight"); plt.close(fig)

# =============== FIG 4 ===============
thr = pd.read_csv(D + "out40/q3_throughput.csv"); thr = thr[thr.alpha == 0.25].set_index("subset")
subs = [("act", "Individual, active (3.02M BTC)"), ("svc", "Exchange / custodian (1.50M BTC)"),
        ("reachable", "Reachable exposed (5.19M BTC)"), ("all_exposed_econ", "All exposed, economic UTXOs only"),
        ("all_exposed", "All exposed (7.16M BTC, 99.2M UTXOs)"), ("whole_set", "Entire UTXO set (full PQ migration)")]
fig = plt.figure(figsize=(18.4 * CM, 7.0 * CM))
gs = fig.add_gridspec(1, 2, width_ratios=[1.0, 1.0], wspace=0.9)
ax = fig.add_subplot(gs[0])
yy = np.arange(len(subs))[::-1]
for (k, lab), y in zip(subs, yy):
    lo, hi = thr.loc[k, "days_lower"], thr.loc[k, "days_upper"]
    col = C1 if k != "whole_set" else MUTED
    ax.plot([lo, hi], [y, y], color=col, lw=5, solid_capstyle="butt")
    ax.text(hi + 12, y, f"{lo:.0f}–{hi:.0f}", va="center", fontsize=6.2)
ax.set_yticks(yy); ax.set_yticklabels([s[1] for s in subs]); ax.tick_params(axis="y", length=0); ax.spines["left"].set_visible(False)
ax.set_xlim(0, 760); ax.set_xlabel("Days to migrate using 25% of block space")
panel(ax, "A", x=-1.02)
rc = pd.read_csv(D + "out40/q3_remaining_curve.csv")
ax = fig.add_subplot(gs[1])
sc = [("status_quo", "Status quo", C1), ("quarterly_warning", "Quarterly warnings", C3),
      ("personal_alert", "Annual personal alerts", C2), ("upper_bound", "All reachable coins\nmigrate within 3 years", C7)]
for k, lab, col in sc:
    r = rc[rc.scenario == k]
    ax.plot(r.month / 12, r.total / 1e6, color=col, lw=1.4)
    yend = r.total.iloc[-1] / 1e6
    off = {"status_quo": 0.25, "quarterly_warning": -0.05, "personal_alert": -0.35, "upper_bound": 0.0}[k]
    ax.text(15.3, yend + off, lab, va="center", fontsize=6.2, color="#0b0b0b")
ax.axhline(1.961, color=INK2, lw=0.6)
ax.text(0.2, 1.961 - 0.12, "Behaviourally unreachable coins (1.96M)", fontsize=5.8, va="top", color=INK2)
for yv in [5, 10, 15]: ax.axvline(yv, color="#e1e0d9", lw=0.6, zorder=0)
ax.set_xlim(0, 15); ax.set_ylim(0, 7.6); ax.set_xticks([0, 5, 10, 15])
ax.set_xlabel("Years after freeze date"); ax.set_ylabel("Exposed coins remaining\n(million BTC)")
panel(ax, "B", x=-0.22)
fig.savefig(OUT + "Fig4.png", bbox_inches="tight"); fig.savefig(OUT + "Fig4.pdf", bbox_inches="tight"); plt.close(fig)
print("ok")
