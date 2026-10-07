"""Supplementary figures S1-S7.

Reads the replication data from Harvard Dataverse (doi:10.7910/DVN/THUHEB).
Set QUBTC_DATA to the folder of the unpacked dataset (the folder containing results/ and data/).
"""
import os, numpy as np, pandas as pd, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA = os.environ.get("QUBTC_DATA", "dataverse")          # unpacked Dataverse dataset
D = os.path.join(DATA, "results", "")                      # estimates and summaries written by the notebooks
OUT = os.environ.get("QUBTC_FIGS", "figs/")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({
    "font.family": "sans-serif", "font.sans-serif": ["Liberation Sans", "Arial", "Helvetica", "DejaVu Sans"],
    "font.size": 7, "axes.labelsize": 7, "axes.titlesize": 7, "xtick.labelsize": 6.5, "ytick.labelsize": 6.5,
    "legend.fontsize": 6.5, "axes.linewidth": 0.6, "xtick.major.width": 0.6, "ytick.major.width": 0.6,
    "xtick.major.size": 2.5, "ytick.major.size": 2.5, "axes.spines.top": False, "axes.spines.right": False,
    "axes.edgecolor": "#52514e", "xtick.color": "#52514e", "ytick.color": "#52514e", "axes.labelcolor": "#0b0b0b",
    "pdf.fonttype": 42, "savefig.dpi": 300, "legend.frameon": False,
})
C1, C2, C3, C4, C5, C6, C7 = "#2a78d6", "#eb6834", "#1baf7a", "#eda100", "#e87ba4", "#008300", "#4a3aa7"
INK2, MUTED, BASE, BAND = "#52514e", "#898781", "#c3c2b7", "#e1e0d9"
CM = 1 / 2.54
EVENTS = [("willow", "Willow"), ("gidney", "Gidney RSA estimate"), ("lopp", "Lopp proposal"),
          ("bip360", "BIP-360 merged"), ("google", "Google ECDLP estimate"), ("bip361", "BIP-361 merged")]

def panel(ax, letter, x=-0.14, y=1.04):
    ax.text(x, y, letter, transform=ax.transAxes, fontsize=10, fontweight="bold", va="bottom", ha="left")

def save(fig, name):
    fig.savefig(OUT + name + ".png", bbox_inches="tight"); fig.savefig(OUT + name + ".pdf", bbox_inches="tight"); plt.close(fig)

def have(*fs):
    return all(os.path.exists(D + f) for f in fs)

# ---------- S1: effect paths r = 0..30 with placebo band ----------
paths = pd.read_csv(D + "est_20_paths.csv.gz")
pp = paths[(paths.contrast == "LC") & (paths.variant == "all") & (paths.subgroup == "all") &
           (paths.outcome == "c_y1_strict") & (paths.weight == "key")].sort_values("rel_day")
fig, axes = plt.subplots(2, 3, figsize=(18.4 * CM, 9.0 * CM), sharex=True, sharey=True)
for ax, (k, lab) in zip(axes.flat, EVENTS):
    ax.fill_between(pp.rel_day, pp.q05 * 100, pp.q95 * 100, color=BAND, lw=0, label="Placebo 5–95%")
    ax.plot(pp.rel_day, pp[k] * 100, color=C1, lw=1.3, label="Event effect")
    ax.axhline(0, color=INK2, lw=0.5)
    ax.set_title(lab, fontsize=7)
for ax in axes[1]: ax.set_xlabel("Days since event")
for ax in axes[:, 0]: ax.set_ylabel("Cumulative effect (pp)")
axes[0, 0].legend(loc="upper left", fontsize=6)
save(fig, "FigS1")

# ---------- S2: first de-risking, exposed vs CEM-weighted control ----------
if have("out20b/est_20b_levels.csv"):
    lv = pd.read_csv(D + "out20b/est_20b_levels.csv")
    lv = lv[lv.outcome == "h_y1s_50"]
    fig, axes = plt.subplots(2, 3, figsize=(18.4 * CM, 9.0 * CM), sharex=True, sharey=True)
    for ax, (k, lab) in zip(axes.flat, EVENTS):
        for stat, col, nm in [("T", C1, "Exposed"), ("C", MUTED, "Control (CEM-weighted)")]:
            s = lv[(lv.event == k) & (lv.stat == stat)].sort_values("rel_day")
            ax.step(s.rel_day, s.value * 100, where="post", color=col, lw=1.2, label=nm)
        ax.set_title(lab, fontsize=7)
    for ax in axes[1]: ax.set_xlabel("Days since event")
    fig.supylabel("Keys that moved ≥50% of balance to new hash-protected addresses (%)", fontsize=7, x=0.04)
    axes[0, 0].legend(loc="upper left", fontsize=6)
    save(fig, "FigS2")

# ---------- S3: heterogeneity by balance tier ----------
eff = pd.read_csv(D + "est_20_effects.csv.gz")
pool = pd.read_csv(D + "est_20_pooled.csv")
sel = lambda d: d[(d.contrast == "LC") & (d.variant == "all") & (d.pool == "main") & (d.h == 90) &
                  (d.outcome == "c_y1_strict") & (d.weight == "key") & (d.rel_day == 30)]
e3, p3 = sel(eff), sel(pool)
tiers = [("0.01-1", "0.01–1 BTC", C1), ("1-10", "1–10 BTC", C3), ("10-100", "10–100 BTC", C4), ("100+", "≥100 BTC", C7)]
cols = [k for k, _ in EVENTS] + ["pooled"]
fig, ax = plt.subplots(figsize=(18.4 * CM, 7.0 * CM))
for j, (sg, lab, col) in enumerate(tiers):
    xs, b, lo, hi = [], [], [], []
    for i, k in enumerate(cols):
        r = (p3[p3.subgroup == sg].iloc[0] if k == "pooled" else e3[(e3.subgroup == sg) & (e3.event == k)].iloc[0])
        bb = r.beta_mean if k == "pooled" else r.beta
        xs.append(i + (j - 1.5) * 0.17); b.append(bb * 100); lo.append(r.ci90_lo * 100); hi.append(r.ci90_hi * 100)
    ax.errorbar(xs, b, yerr=[np.array(b) - np.array(lo), np.array(hi) - np.array(b)], fmt="o", ms=3, color=col,
                elinewidth=0.9, capsize=1.5, label=lab)
ax.axhline(0, color=INK2, lw=0.5)
ax.axvline(len(cols) - 1.5, color=BASE, lw=0.6, ls=":")
ax.set_xticks(range(len(cols))); ax.set_xticklabels(["Willow", "Gidney", "Lopp\nproposal", "BIP-360", "Google\nECDLP", "BIP-361", "Six events,\npooled"], fontsize=6.3)
ax.set_ylabel("Effect on 30-day migration (pp; 90% interval)")
ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, 1.12), fontsize=6.3)
save(fig, "FigS3")

# ---------- S4: stock bridge ----------
br = pd.read_csv(D + "out30/q2_bridge.csv")
labs = ["Exposed legacy\nsupply, 8 Dec 2024", "Starting coins\nspent", "New receipts by\nstarting keys",
        "Keys hash-protected\nin Dec 2024, later\nexposed", "Keys not in the\nDec 2024 snapshot", "Exposed legacy\nsupply, 22 Sep 2026"]
v = br.btc.values / 1e6
steps = [v[0], v[1], v[3], v[4], v[5], v[6]]
fig, ax = plt.subplots(figsize=(18.4 * CM, 6.5 * CM))
cum = 0
for i, (lab, s) in enumerate(zip(labs, steps)):
    if i in (0, len(steps) - 1):
        ax.bar(i, s, color=C1, width=0.6); top = s; cum = s if i == 0 else cum
        ax.text(i, s + 0.08, f"{s:.2f}", ha="center", fontsize=6.3)
    else:
        bottom = cum if s > 0 else cum + s
        ax.bar(i, abs(s), bottom=bottom, color=(C3 if s > 0 else C2), width=0.6)
        ax.text(i, max(cum, cum + s) + 0.08, f"{s:+.2f}".replace("-", "\u2212"), ha="center", fontsize=6.3)
        cum += s
ax.set_xticks(range(len(labs))); ax.set_xticklabels(labs, fontsize=6.2)
ax.set_ylabel("Million BTC"); ax.set_ylim(0, 8.3)
save(fig, "FigS4")

# ---------- S5: uneconomic outputs and fees by fee rate ----------
fe = pd.read_csv(D + "out40/q3_fees.csv")
subs = [("all_exposed", "All exposed outputs", C1), ("reachable", "Reachable exposed", C3), ("whole_set", "Entire UTXO set", MUTED)]
fig, axes = plt.subplots(1, 2, figsize=(18.4 * CM, 6.2 * CM))
for k, lab, col in subs:
    d = fe[fe.subset == k].sort_values("fee_sat_vb")
    axes[0].plot(d.fee_sat_vb, d.uneconomic_utxo_share * 100, marker="o", ms=3, color=col, lw=1.1, label=lab)
    axes[1].fill_between(d.fee_sat_vb, d.fee_btc_lower, d.fee_btc_upper, color=col, alpha=0.25, lw=0)
    axes[1].plot(d.fee_sat_vb, (d.fee_btc_lower + d.fee_btc_upper) / 2, color=col, lw=1.1, label=lab)
for ax in axes:
    ax.set_xscale("log"); ax.set_xticks([1, 2, 5, 10, 20, 50, 100]); ax.set_xticklabels(["1", "2", "5", "10", "20", "50", "100"])
    ax.set_xlabel("Fee rate (sat/vB)")
axes[0].set_ylabel("Outputs worth less than\ntheir spending fee (%)"); axes[0].legend(fontsize=6, loc="upper left")
axes[1].set_yscale("log"); axes[1].set_ylabel("Total migration fees (BTC)\n(one tx per key – one tx per output)")
panel(axes[0], "A"); panel(axes[1], "B")
plt.tight_layout()
save(fig, "FigS5")

# ---------- S6: calendar-time placebo diagnostic, exposed - control ----------
if have("out20b/est_20b_calendar.csv"):
    cal = pd.read_csv(D + "out20b/est_20b_calendar.csv", parse_dates=["event_date"])
    LBL = dict(EVENTS)
    fig, axes = plt.subplots(1, 2, figsize=(18.4 * CM, 6.6 * CM))
    for ax, r_, letter in zip(axes, [7, 30], ["A", "B"]):
        c = cal[(cal.kind == "curve") & (cal.rel_day == r_)].sort_values("event_date")
        d = cal[(cal.kind == "date") & (cal.rel_day == r_)]
        ax.fill_between(c.event_date, c.band_lo * 100, c.band_hi * 100, color=BAND, lw=0, label="Placebo 5–95% band")
        ax.plot(c.event_date, c.fit * 100, color=INK2, lw=1.0, label="Local-linear baseline (h = 90 d)")
        pl = d[d.in_pool_main.astype(str) == "True"]
        ax.scatter(pl.event_date, pl.theta * 100, s=9, color=MUTED, zorder=3, label="Placebo dates")
        mm = d[d.event_set == "main"]
        for e in mm.itertuples():
            hi = e.event in ("willow", "google")
            ax.scatter(e.event_date, e.theta * 100, s=26 if hi else 16, marker="D" if hi else "o", zorder=4,
                       color=C2 if hi else C4, edgecolor="white", linewidth=0.4)
            ax.annotate(LBL[e.event].replace(" estimate", "").replace(" merged", ""), (e.event_date, e.theta * 100),
                        fontsize=5.6, xytext=((3, -8) if e.event == "bip361" else (2, 3)), textcoords="offset points", color=INK2)
        nq = d[d.event_set == "nonquantum_news"]
        ax.scatter(nq.event_date, nq.theta * 100, s=14, marker="s", color=C1, zorder=4, label="Non-quantum news days")
        ax.axhline(0, color=INK2, lw=0.4)
        ax.set_xlim(pd.Timestamp("2024-05-01"), pd.Timestamp("2026-08-15"))
        ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
        ax.set_ylabel(f"Exposed − control, day +{r_} (pp)")
        panel(ax, letter, x=-0.16)
    from matplotlib.lines import Line2D
    hs = [plt.Rectangle((0, 0), 1, 1, color=BAND), Line2D([], [], color=INK2, lw=1), Line2D([], [], marker="o", ls="", color=MUTED, ms=3),
          Line2D([], [], marker="D", ls="", color=C2, ms=4), Line2D([], [], marker="o", ls="", color=C4, ms=3.5),
          Line2D([], [], marker="s", ls="", color=C1, ms=3.5)]
    fig.legend(hs, ["Placebo 5–95% band", "Local-linear baseline", "Placebo dates", "High-attention events", "Other quantum-risk events",
                    "Non-quantum news days"], loc="lower center", ncol=6, fontsize=6, bbox_to_anchor=(0.5, -0.06))
    plt.tight_layout(rect=(0, 0.05, 1, 1))
    save(fig, "FigS6")

# ---------- S7: Randstorm with a same-period placebo pool; notice path ----------
if have("out23/est_23_calendar_uc.csv", "out23/est_23_notice_path.csv"):
    cal = pd.read_csv(D + "out23/est_23_calendar_uc.csv", parse_dates=["event_date"])
    npth = pd.read_csv(D + "out23/est_23_notice_path.csv")
    fig = plt.figure(figsize=(18.4 * CM, 6.6 * CM))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.6, 1.0], wspace=0.35)
    ax = fig.add_subplot(gs[0])
    c = cal[cal.kind == "curve"].sort_values("event_date")
    d = cal[cal.kind == "date"]
    ax.fill_between(c.event_date, c.band_lo * 100, c.band_hi * 100, color=BAND, lw=0)
    ax.plot(c.event_date, c.baseline_all_h90 * 100, color=INK2, lw=1.0)
    pre = d[d.in_pre.astype(str) == "True"]; old = d[d.in_old_main.astype(str) == "True"]
    ax.scatter(pre.event_date, pre.theta * 100, s=9, color=MUTED, zorder=3, label="Placebo dates, 2022–2024")
    ax.scatter(old.event_date, old.theta * 100, s=9, facecolor="white", edgecolor=MUTED, zorder=3, label="Placebo dates, 2024–2026")
    for e, lab, col, mk in [("ftx", "FTX collapse", C1, "s"), ("randstorm_notice", "Randstorm notice (10 Oct 2023)", C4, "D"),
                            ("randstorm", "Randstorm disclosure (14 Nov 2023)", C2, "D")]:
        r = d[d.event == e]
        if len(r):
            ax.scatter(r.event_date, r.theta * 100, s=26, marker=mk, color=col, zorder=4, edgecolor="white", linewidth=0.4, label=lab)
    ax.axhline(0, color=INK2, lw=0.4)
    ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))
    ax.tick_params(axis="x", labelrotation=30)
    ax.set_ylabel("Uncompressed − compressed keys,\n30-day migration (pp)")
    ax.legend(fontsize=5.8, loc="upper center", bbox_to_anchor=(0.5, -0.24), ncol=3, columnspacing=1.0, handletextpad=0.3)
    panel(ax, "A", x=-0.12)
    ax = fig.add_subplot(gs[1])
    gap = 35
    ax.plot(npth.rel_day, npth.theta_notice * 100, color=C4, lw=1.3, label="Snapshot 9 Oct 2023")
    ax.plot(npth.rel_day, npth.theta_disclosure_shifted * 100, color=C2, lw=1.1, ls="--", label="Snapshot 13 Nov 2023")
    ax.axvline(gap, color=BASE, lw=0.6, ls=":")
    ax.set_ylim(-0.3, 6.2)
    ax.text(gap - 1, 4.7, "public\ndisclosure", fontsize=5.8, va="top", ha="right", color=INK2)
    ax.axhline(0, color=INK2, lw=0.4)
    ax.set_xlabel("Days since 10 Oct 2023"); ax.set_ylabel("Uncompressed − compressed,\ncumulative migration (pp)")
    ax.legend(fontsize=5.8, loc="upper left", bbox_to_anchor=(0.0, 1.0), handlelength=1.6)
    panel(ax, "B", x=-0.25)
    save(fig, "FigS7")
print("done:", sorted(os.listdir(OUT)))
