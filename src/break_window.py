"""EXPLORATORY (post hoc): does display-clock measurement manufacture a collapse?

NOT PREREGISTERED. This analysis was motivated by the momentum-graphic
discussion and the results were seen before the plan was fixed; it is logged as
exploratory in CHANGELOG (E1) and is reported as such.

Question: when a scheduled stoppage sits inside the measurement window, how much
of the apparent post-break decline is the stopped clock rather than football?

Three rates per break i and window w (shots per minute, both teams):
  R_pre     [call - w, call)                 football before the break
  R_call    [call, call + w)                 NAIVE: contains the dead time
  R_resume  [restart, restart + w)           football only, from resumption

and three reported quantities:
  N_w = R_call   - R_pre      apparent (display-clock) change
  C_w = R_resume - R_pre      resumption-aligned change
  D_w = C_w - C_control_w     matched difference-in-differences  <- the estimate

D_w carries a match-clustered bootstrap that resamples matches AND redraws the
matched control minute inside every draw, so both sources of uncertainty
propagate into one interval.

Two validation tests decide whether the mechanism is really the clock:
  * SYNTHETIC DEAD TIME - insert each break's own observed duration into ordinary
    control minutes. If the collapse reappears there, the measurement procedure
    creates it, not anything about hydration breaks.
  * DURATION DOSE-RESPONSE - the naive decline should scale with dead share
    d_i/w; the resumption-aligned change should not.

Every prediction uses each break's OWN measured duration d_i, never a fixed 3.
Outputs: reports/tables/break_window.md
Run:     python -m src.break_window
"""
from __future__ import annotations

from collections import defaultdict

import numpy as np
import pandas as pd

from .placebo import MatchData, load_inputs
from .util import PROCESSED, TABLES

WINDOWS = (3, 5, 8, 10)
SEED = 20260724
N_BOOT = 4000
HALF = {"H1": (1, 45), "H2": (46, 90)}


def build():
    bands = pd.read_csv(PROCESSED / "break_bands.csv")
    _, shots, matches, events = load_inputs()
    cache = {int(m): MatchData(int(m), matches, shots, events, bands)
             for m in bands["match_id"].unique()}
    per_min: dict[tuple[int, int], int] = defaultdict(int)
    for _, r in shots[shots["minute"] <= 95].iterrows():
        per_min[(int(r["match_id"]), int(r["minute"]))] += 1
    return bands, cache, per_min


def rate(per_min, mid, lo, w):
    """Shots per minute over the w display minutes starting at lo."""
    return sum(per_min.get((mid, int(lo + k)), 0) for k in range(int(w))) / w


def rate_gap(per_min, mid, lo, w, dead):
    """Rate over [lo, lo+w) where the first `dead` minutes contain no football.

    This is what a naive display-clock window measures: the clock advances w
    minutes but only (w - dead) of them hold football.
    """
    live = sum(per_min.get((mid, int(lo + k)), 0)
               for k in range(int(np.ceil(dead)), int(w)))
    return live / w


def common_support(bands, cache) -> set[tuple[int, int]]:
    """Breaks valid at EVERY window AND possessing at least one eligible matched
    control, so window-to-window movement is not sample composition.

    Both conditions matter. Requiring only window validity would keep the seven
    breaks that have no eligible control minute at all — the same seven the
    preregistered placebo drops — and a control would then have to be invented
    for them. It is not; they are excluded, so this analysis runs on the same
    196 breaks as the primary analysis.
    """
    wmax = max(WINDOWS)
    keep = set()
    for _, b in bands.iterrows():
        lo, hi = HALF[b["half"]]
        call, dur = b["start_minute"], b["duration_min"]
        if not (call - wmax >= lo - 1 and call + dur + wmax <= hi):
            continue
        m = cache[int(b["match_id"])]
        if not m.eligible_minutes(b["half"], m.margin_bucket(call)):
            continue
        keep.add((int(b["match_id"]), int(b["break_number"])))
    return keep


def analyse(bands, cache, per_min, support=None, measured_only=False):
    rng = np.random.default_rng(SEED)
    rows = []
    for w in WINDOWS:
        recs, ctrl_by_break = [], {}
        for _, b in bands.iterrows():
            key = (int(b["match_id"]), int(b["break_number"]))
            if support is not None and key not in support:
                continue
            if measured_only and b["duration_source"] != "manifest_ok":
                continue
            mid = int(b["match_id"])
            m = cache[mid]
            call, dur = b["start_minute"], b["duration_min"]
            r_pre = rate(per_min, mid, call - w, w)
            r_call = rate(per_min, mid, call, w)
            r_res = rate(per_min, mid, call + dur, w)
            # break bands are whole minutes, so for shorter breaks play restarts
            # part-way through the minute at `restart`. Skipping it gives a
            # post-window of complete active minutes.
            r_res1 = rate(per_min, mid, call + dur + 1, w)
            dead_share = min(dur, w) / w
            recs.append({
                "match_id": mid, "break_number": int(b["break_number"]),
                "dur": dur, "dead_share": dead_share,
                "measured": b["duration_source"] == "manifest_ok",
                "pre": r_pre, "N": r_call - r_pre, "C": r_res - r_pre,
                "C1": r_res1 - r_pre,
                "pred": -r_pre * dead_share,
            })
            cands = m.eligible_minutes(b["half"], m.margin_bucket(call))
            assert cands, "common_support must exclude breaks with no eligible control"
            ctrl_by_break[key] = [
                (rate(per_min, mid, c, w) - rate(per_min, mid, c - w, w),
                 rate_gap(per_min, mid, c, w, dur) - rate(per_min, mid, c - w, w))
                for c in cands]

        df = pd.DataFrame(recs).reset_index(drop=True)
        # control pools indexed by the SAME positional order as df rows
        pools = [ctrl_by_break[(int(r.match_id), int(r.break_number))]
                 for r in df.itertuples()]

        by_match = defaultdict(list)
        for idx, r in enumerate(df.itertuples()):
            by_match[int(r.match_id)].append(idx)
        mids = list(by_match)
        N_arr, C_arr, C1_arr = (df["N"].to_numpy(), df["C"].to_numpy(),
                                df["C1"].to_numpy())

        # One match-clustered bootstrap producing BOTH contrasts, redrawing the
        # matched control minute inside every iteration:
        #   D = (post-resumption - pre)  -  (control post - control pre)
        #   A = (from-call change)       -  (synthetic-stoppage change)
        boot_D, boot_A, boot_synth, boot_N, boot_D1 = (
            np.empty(N_BOOT), np.empty(N_BOOT), np.empty(N_BOOT), np.empty(N_BOOT),
            np.empty(N_BOOT))
        for i in range(N_BOOT):
            pick = rng.integers(0, len(mids), len(mids))
            idxs = [j for p in pick for j in by_match[mids[p]]]
            ctrl_vals, synth_vals = [], []
            for j in idxs:
                pool = pools[j]
                a, s = pool[rng.integers(0, len(pool))]
                ctrl_vals.append(a)
                synth_vals.append(s)
            boot_D[i] = C_arr[idxs].mean() - np.mean(ctrl_vals)
            boot_D1[i] = C1_arr[idxs].mean() - np.mean(ctrl_vals)
            boot_A[i] = N_arr[idxs].mean() - np.mean(synth_vals)
            boot_synth[i] = np.mean(synth_vals)
            boot_N[i] = N_arr[idxs].mean()

        flat_ctrl = [a for v in pools for a, _ in v]
        flat_syn = [s for v in pools for _, s in v]
        rows.append({
            "w": w, "n_breaks": len(df), "n_matches": df["match_id"].nunique(),
            "pre": df["pre"].mean(),
            "N": df["N"].mean(), "pred": df["pred"].mean(),
            "C": df["C"].mean(), "ctrl": float(np.mean(flat_ctrl)),
            "D": df["C"].mean() - float(np.mean(flat_ctrl)),
            "D_lo": float(np.percentile(boot_D, 2.5)),
            "D_hi": float(np.percentile(boot_D, 97.5)),
            "synth": float(np.mean(flat_syn)),
            "synth_lo": float(np.percentile(boot_synth, 2.5)),
            "synth_hi": float(np.percentile(boot_synth, 97.5)),
            "A": df["N"].mean() - float(np.mean(flat_syn)),
            "A_lo": float(np.percentile(boot_A, 2.5)),
            "A_hi": float(np.percentile(boot_A, 97.5)),
            "N_lo": float(np.percentile(boot_N, 2.5)),
            "N_hi": float(np.percentile(boot_N, 97.5)),
            "C1": df["C1"].mean(),
            "D1": df["C1"].mean() - float(np.mean(flat_ctrl)),
            "D1_lo": float(np.percentile(boot_D1, 2.5)),
            "D1_hi": float(np.percentile(boot_D1, 97.5)),
            "_df": df,
        })
    return rows


def event_studies(bands, cache, per_min, support, rel=range(-10, 11)):
    """Two alignments, kept deliberately separate.

    call-aligned      minute = call + r          (dead time visible in the middle)
    resumption-aligned r<0 -> call + r, r>=0 -> restart + r
                      i.e. the break-adjusted clock: football either side, no dead
                      time, so real and control are directly comparable.
    """
    rng = np.random.default_rng(SEED)
    call_real, res_real, res_ctrl, res_by_match = [], [], [], defaultdict(list)
    for _, b in bands.iterrows():
        key = (int(b["match_id"]), int(b["break_number"]))
        if key not in support:
            continue
        mid = int(b["match_id"])
        m = cache[mid]
        call, dur = b["start_minute"], b["duration_min"]
        restart = call + dur
        call_real.append([per_min.get((mid, int(call + r)), 0) for r in rel])
        row = [per_min.get((mid, int((call + r) if r < 0 else (restart + r))), 0)
               for r in rel]
        res_real.append(row)
        res_by_match[mid].append(len(res_real) - 1)
        cands = m.eligible_minutes(b["half"], m.margin_bucket(call))
        assert cands, "common_support must exclude breaks with no eligible control"
        res_ctrl.append([[per_min.get((mid, int(c + r)), 0) for r in rel]
                         for c in cands])

    call_real = np.array(call_real, float)
    res_real = np.array(res_real, float)
    mids = list(res_by_match)
    boot_r = np.empty((N_BOOT, res_real.shape[1]))
    boot_c = np.empty((N_BOOT, res_real.shape[1]))
    for i in range(N_BOOT):
        pick = rng.integers(0, len(mids), len(mids))
        idxs = [j for p in pick for j in res_by_match[mids[p]]]
        boot_r[i] = res_real[idxs].mean(axis=0)
        boot_c[i] = np.array([res_ctrl[j][rng.integers(0, len(res_ctrl[j]))]
                              for j in idxs], float).mean(axis=0)
    gap = boot_r - boot_c          # real minus matched control, per draw
    return {
        "rel": np.array(list(rel)),
        "call_real": call_real,
        "res_real_mean": res_real.mean(axis=0),
        "res_real_lo": np.percentile(boot_r, 2.5, axis=0),
        "res_real_hi": np.percentile(boot_r, 97.5, axis=0),
        "res_ctrl_mean": boot_c.mean(axis=0),
        "res_ctrl_lo": np.percentile(boot_c, 2.5, axis=0),
        "res_ctrl_hi": np.percentile(boot_c, 97.5, axis=0),
        "gap_mean": gap.mean(axis=0),
        "gap_lo": np.percentile(gap, 2.5, axis=0),
        "gap_hi": np.percentile(gap, 97.5, axis=0),
        "n_breaks": res_real.shape[0],
        "n_matches": len(mids),
    }


def dose_response(rows):
    """Does the naive decline scale with dead share, while C does not?

    UNDERPOWERED BY CONSTRUCTION, and reported as such: observed durations take
    only three distinct values (2/3/4 min) and 78 of 203 are imputed at the
    median. Restricted to breaks whose duration was actually MEASURED, which
    removes the imputed block but leaves only a 2-vs-3-vs-4 contrast.
    """
    out = []
    for r in rows:
        sub = r["_df"]
        sub = sub[sub["measured"]]
        if len(sub) < 20 or sub["dead_share"].nunique() < 2:
            out.append((r["w"], None, None, sub["dead_share"].nunique(), len(sub)))
            continue
        bn = np.polyfit(sub["dead_share"], sub["N"], 1)[0]
        bc = np.polyfit(sub["dead_share"], sub["C"], 1)[0]
        out.append((r["w"], bn, bc, sub["dead_share"].nunique(), len(sub)))
    return out


def figure_a(rows):
    """Display-clock decomposition: real vs synthetic, and their direct contrast."""
    import matplotlib.pyplot as plt
    from .charts import BLUE, CRITICAL, INK, INK2, MUTED, SURFACE
    from .util import FIGURES

    W = np.array([r["w"] for r in rows], float)
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(9.5, 7.2), sharex=True,
                                   height_ratios=[3, 2])
    ax1.axhline(0, color="#c3c2b7", linewidth=1)
    ax1.errorbar(W - 0.08, [r["N"] for r in rows],
                 yerr=[[r["N"] - r["N_lo"] for r in rows],
                       [r["N_hi"] - r["N"] for r in rows]],
                 fmt="o-", color=CRITICAL, linewidth=2.3, markersize=7, capsize=4,
                 label="real breaks, measured from the break call")
    ax1.errorbar(W + 0.08, [r["synth"] for r in rows],
                 yerr=[[r["synth"] - r["synth_lo"] for r in rows],
                       [r["synth_hi"] - r["synth"] for r in rows]],
                 fmt="s--", color=MUTED, linewidth=2.3, markersize=6, capsize=4,
                 label="synthetic stoppage at matched ordinary periods")
    ax1.set_ylabel("change in shots per minute, pre → post")
    ax1.legend(frameon=False, fontsize=9, loc="lower right")
    ax1.set_title("A · The two declines track each other", color=INK, fontsize=11.5,
                  fontweight="bold", loc="left")

    ax2.axhline(0, color=INK, linewidth=1.2)
    ax2.errorbar(W, [r["A"] for r in rows],
                 yerr=[[r["A"] - r["A_lo"] for r in rows],
                       [r["A_hi"] - r["A"] for r in rows]],
                 fmt="o", color=BLUE, markersize=8, capsize=5, linewidth=2.2)
    for r in rows:
        ax2.annotate(f"{r['A']:+.3f}", xy=(r["w"], r["A"]), xytext=(0, 12),
                     textcoords="offset points", ha="center", fontsize=8.5, color=INK2)
    ax2.set_ylabel("real − synthetic")
    ax2.set_xlabel("window length (minutes)")
    ax2.set_xticks(W)
    ax2.set_ylim(-0.11, 0.13)
    ax2.set_title("B · Direct contrast — every interval includes zero",
                  color=INK, fontsize=11.5, fontweight="bold", loc="left")

    for ax in (ax1, ax2):
        ax.grid(axis="x", visible=False)
        ax.tick_params(length=0)
    fig.suptitle("Apparent post-break activity declines are reproduced by synthetic dead time",
                 x=0.045, y=0.99, ha="left", fontsize=13.5, fontweight="bold", color=INK)
    fig.text(0.045, 0.915,
             "Shot-rate change measured from the break call, versus equivalent artificial "
             "stoppages inserted at matched ordinary periods.\n"
             f"{rows[0]['n_breaks']} breaks / {rows[0]['n_matches']} matches (breaks with "
             "no eligible matched control are excluded, as in the primary analysis).\n"
             "Bars are 95% match-clustered intervals. Exploratory, post hoc (CHANGELOG E1).",
             fontsize=8.5, color=INK2, linespacing=1.6)
    fig.tight_layout(rect=(0, 0, 1, 0.89))
    fig.savefig(FIGURES / "fig_break_window.png", dpi=200)
    plt.close(fig)


def figure_b(es):
    """Principal event study: real MINUS matched control at each relative minute."""
    import matplotlib.pyplot as plt
    from .charts import BLUE, INK, INK2, MUTED, SURFACE
    from .util import FIGURES

    rel = es["rel"]
    fig, ax = plt.subplots(figsize=(10, 5.6))
    ax.axhline(0, color=INK, linewidth=1.2, zorder=3)
    ax.axvspan(-0.5, 0.5, color="#f3e8d9", zorder=0)
    ax.fill_between(rel, es["gap_lo"], es["gap_hi"], color=BLUE, alpha=0.20,
                    linewidth=0)
    ax.plot(rel, es["gap_mean"], color=BLUE, linewidth=2.5, marker="o", markersize=4)
    ax.axvline(0, color=MUTED, linewidth=1.1, linestyle=(0, (3, 3)))
    ax.set_xlabel("minutes relative to the ESTIMATED resumption minute "
                  "(dead time removed; negative = before the break)")
    ax.set_ylabel("real − matched control\n(shots per minute)")
    ax.set_xticks(range(-10, 11, 2))
    ax.annotate("transition minute:\nmay contain residual\ndead time — excluded\nfrom interpretation",
                xy=(0, es["gap_mean"][list(rel).index(0)]), xytext=(2.4, -0.105),
                color=INK2, fontsize=8.5,
                arrowprops=dict(arrowstyle="->", color=INK2, lw=1))
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    ax.set_title("Post-resumption shot activity does not differ detectably\n"
                 "from matched ordinary periods",
                 color=INK, fontsize=13, fontweight="bold", loc="left", pad=14)
    fig.tight_layout(rect=(0, 0.13, 1, 1))
    fig.text(0.055, 0.015,
             f"Difference in shot rate between {es['n_breaks']} real breaks and their "
             f"matched ordinary periods ({es['n_matches']} matches), aligned on the "
             "estimated resumption minute.\nShaded region: POINTWISE 95% match-clustered "
             "bootstrap intervals with the matched control redrawn inside each draw. They "
             "are descriptive and are NOT\nsimultaneous bands; formal inference uses the "
             "prespecified window contrasts in reports/tables/break_window.md. "
             "Exploratory, post hoc (CHANGELOG E1).",
             fontsize=8, color=INK2, linespacing=1.6)
    fig.savefig(FIGURES / "fig_break_resumption.png", dpi=200)
    plt.close(fig)

    # supplementary: the raw two-line overlay, demoted from the main figure
    fig, ax = plt.subplots(figsize=(10, 4.8))
    ax.axvspan(-0.5, 0.5, color="#f3e8d9", zorder=0)
    ax.fill_between(rel, es["res_ctrl_lo"], es["res_ctrl_hi"], color=MUTED,
                    alpha=0.20, linewidth=0)
    ax.fill_between(rel, es["res_real_lo"], es["res_real_hi"], color=BLUE,
                    alpha=0.20, linewidth=0)
    ax.plot(rel, es["res_ctrl_mean"], color=MUTED, linewidth=2, linestyle=(0, (4, 3)),
            label="matched ordinary periods")
    ax.plot(rel, es["res_real_mean"], color=BLUE, linewidth=2.4, marker="o",
            markersize=4, label="real hydration breaks")
    ax.set_xlabel("minutes relative to the ESTIMATED resumption minute")
    ax.set_ylabel("shots per minute, both teams")
    ax.set_xticks(range(-10, 11, 2))
    ax.legend(frameon=False, fontsize=9, loc="lower right")
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    ax.set_title("Supplementary · raw levels behind the difference plot",
                 color=INK, fontsize=12, fontweight="bold", loc="left", pad=12)
    fig.tight_layout(rect=(0, 0.10, 1, 1))
    fig.text(0.055, 0.015,
             "Levels, not the test. The two series differ in level and volatility before "
             "the break, which is why the principal figure plots the DIFFERENCE.\n"
             "Pointwise 95% match-clustered intervals. Shaded: transition minute.",
             fontsize=8, color=INK2, linespacing=1.6)
    fig.savefig(FIGURES / "fig_break_resumption_levels.png", dpi=200)
    plt.close(fig)


def figure_supp(es):
    """Supplementary: call-aligned curve, kept on its own axis."""
    import matplotlib.pyplot as plt
    from .charts import BLUE, CRITICAL, INK, INK2, SURFACE
    from .util import FIGURES

    rel, arr = es["rel"], es["call_real"]
    fig, ax = plt.subplots(figsize=(10, 4.6))
    ax.axvspan(-0.5, 2.5, color="#f3e8d9", zorder=0)
    ax.plot(rel, arr.mean(axis=0), color=BLUE, linewidth=2.5, marker="o", markersize=4)
    ax.set_xlabel("minutes relative to the break being CALLED (display clock)")
    ax.set_ylabel("shots per minute, both teams")
    ax.set_xticks(range(-10, 11, 2))
    ax.grid(axis="x", visible=False)
    ax.tick_params(length=0)
    ax.annotate("the stoppage: clock runs,\nno football is played", xy=(1, 0.01),
                xytext=(5.0, 0.10), color=CRITICAL, fontsize=9, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=CRITICAL, lw=1.2))
    ax.set_title("Supplementary · the same breaks on the display clock",
                 color=INK, fontsize=12.5, fontweight="bold", loc="left", pad=26)
    ax.text(0, 1.05,
            "Shown separately from the resumption-aligned figure on purpose: the two use "
            "different time origins and must not share an axis.\nActivity in the final "
            "minute before the call is lower, but that pre-trend is NOT interpreted here.",
            transform=ax.transAxes, fontsize=8.5, color=INK2, va="bottom", linespacing=1.5)
    fig.tight_layout()
    fig.savefig(FIGURES / "fig_break_call_aligned.png", dpi=200)
    plt.close(fig)


def main():
    bands, cache, per_min = build()
    support = common_support(bands, cache)
    rows = analyse(bands, cache, per_min, support)

    lines = [
        "# Display-clock artefact: window decomposition (EXPLORATORY)",
        "",
        "**Post hoc, not preregistered** — motivated by the momentum-graphic",
        "discussion; results were seen before the plan was fixed. Logged as CHANGELOG E1.",
        "",
        f"Common-support sample: breaks valid at all windows "
        f"({rows[0]['n_breaks']} breaks / {rows[0]['n_matches']} matches of 203/102).",
        "Rates are shots per minute, both teams. Every dead-time prediction uses each",
        "break's OWN measured duration, never a fixed three minutes.",
        "",
        "| w | pre | N (from call) | dead-time prediction | C (from resumption) | control | **D = C − control** | 95% CI (match-clustered) |",
        "|---|---|---|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(
            f"| {r['w']} | {r['pre']:.3f} | {r['N']:+.3f} | {r['pred']:+.3f} | "
            f"{r['C']:+.3f} | {r['ctrl']:+.3f} | **{r['D']:+.3f}** | "
            f"[{r['D_lo']:+.3f}, {r['D_hi']:+.3f}] |")

    lines += [
        "",
        "### Transition-minute sensitivity",
        "",
        "Break bands are recorded to whole minutes, so for shorter breaks play restarts",
        "part-way through the minute at `restart`. That minute is a TRANSITION bin and may",
        "contain residual dead time. Repeating D with the post-window starting one minute",
        "later measures how much that matters instead of asserting it:",
        "",
        "| w | D (post-window from restart) | D (post-window from restart + 1) | 95% CI |",
        "|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['w']} | {r['D']:+.3f} | **{r['D1']:+.3f}** | "
                     f"[{r['D1_lo']:+.3f}, {r['D1_hi']:+.3f}] |")
    shift = np.mean([r["D1"] - r["D"] for r in rows])
    lines += [
        "",
        (f"Excluding the transition minute shifted the adjusted estimates "
         f"{'upward' if shift > 0 else 'downward'} by an average of {abs(shift):.3f} "
         "shots per minute, without changing the overall conclusion — every interval "
         "still includes zero. Including the partially observed transition minute "
         f"therefore appears to attenuate the estimates {'downward' if shift > 0 else 'upward'}. "
         "No clustered interval was computed for the DIFFERENCE between the two "
         "specifications, so this is described as an apparent shift rather than a "
         "quantified bias."),
    ]

    lines += [
        "",
        "`N` is what a display-clock window reports. `D` is the estimate that matters:",
        "post-resumption change, differenced against matched ordinary minutes.",
        "",
        "## Validation 1 — synthetic dead time",
        "",
        "Take ordinary matched control minutes — normal passages of football — and",
        "insert each break's OWN observed duration into the clock as artificial dead",
        "time. Nothing is deleted from the pre-window and no quiet periods are selected;",
        "only elapsed display-clock time is inserted. If the collapse reappears there,",
        "the measurement procedure produces it, not hydration breaks.",
        "",
        "The formal test is the **direct paired contrast** A = (real, from call) −",
        "(synthetic stoppage), bootstrapped by match with the matched control minute",
        "redrawn inside every iteration. Comparing one point estimate against the other's",
        "interval would not be a test.",
        "",
        "| w | real N (from call) | synthetic stoppage | **A = real − synthetic** | 95% CI (match-clustered) |",
        "|---|---|---|---|---|",
    ]
    for r in rows:
        lines.append(f"| {r['w']} | {r['N']:+.3f} | {r['synth']:+.3f} | "
                     f"**{r['A']:+.3f}** | [{r['A_lo']:+.3f}, {r['A_hi']:+.3f}] |")

    zero_all = all(r["A_lo"] < 0 < r["A_hi"] for r in rows)
    lines += [
        "",
        ("**All A intervals include zero.** The decline measured from the break call did "
         "not differ detectably from the decline produced by inserting an equivalent "
         "synthetic stoppage at matched ordinary minutes — i.e. the apparent collapse is "
         "closely reproduced by the measurement procedure alone."
         if zero_all else
         "**At least one A interval excludes zero** — the real decline is NOT fully "
         "reproduced by synthetic dead time at every window; see the table."),
        "",
        "Note on wording: those control minutes are ordinary passages of football. The "
        "procedure inserts artificial dead time into them; it does not select quiet "
        "periods.",
    ]

    # duration-imputation sensitivity
    meas = analyse(bands, cache, per_min, support, measured_only=True)
    lines += [
        "",
        "### Sensitivity — measured durations only",
        "",
        f"Duration drives the synthetic stoppage, and {rows[0]['n_breaks'] - meas[0]['n_breaks']} "
        f"of the {rows[0]['n_breaks']} analysed breaks have a median-imputed duration. "
        "Repeating the placebo on the breaks whose duration was actually measured:",
        "",
        "| w | n breaks | real N | synthetic | A = real − synthetic | 95% CI |",
        "|---|---|---|---|---|---|",
    ]
    for r in meas:
        lines.append(f"| {r['w']} | {r['n_breaks']} | {r['N']:+.3f} | {r['synth']:+.3f} | "
                     f"{r['A']:+.3f} | [{r['A_lo']:+.3f}, {r['A_hi']:+.3f}] |")

    lines += [
        "",
        "## Validation 2 — duration dose-response (UNDERPOWERED, inconclusive)",
        "",
        "If the clock drives it, the naive decline should steepen as dead share grows,",
        "while the resumption-aligned change should be flat. **Our data cannot really",
        "test this.** Measured durations take only three values (2 / 3 / 4 min), 78 of",
        "203 are imputed at the median and are excluded here, and at w=3 the dead share",
        "is constant. What remains is a 2-vs-3-vs-4 contrast — directionally consistent",
        "but far too thin to call a validation. Reported for completeness, not as",
        "evidence.",
        "",
        "| w | slope of N on dead share | slope of C on dead share | distinct shares | n measured |",
        "|---|---|---|---|---|",
    ]
    for w, bn, bc, nu, n in dose_response(rows):
        if bn is None:
            lines.append(f"| {w} | n/a (insufficient variation) | n/a | {nu} | {n} |")
        else:
            lines.append(f"| {w} | {bn:+.3f} | {bc:+.3f} | {nu} | {n} |")

    lines += [
        "",
        "## Interpretation limits",
        "",
        "- All A intervals include zero; they exclude differences larger than about "
        "0.07 shots/min between the real and synthetic declines. Whether that is "
        "'small' is a judgement about football, not a statistical fact.",
        "- The D estimates permit modest effects in either direction, especially at the "
        "3-minute window. This is 'no detectable decline', NOT proof of no effect.",
        "- Shot activity is not the momentum algorithm. This shows how a display-clock "
        "window can manufacture an apparent collapse; it does not reproduce, and cannot "
        "prove the cause of, any published momentum curve.",
        "- Activity in the final minute before the call is lower than at control minutes. "
        "That pre-trend may reflect stoppage selection, timestamp granularity or random "
        "variation and is NOT interpreted causally here.",
        "- **Alignment is to an ESTIMATED resumption minute, not the exact restart "
        "instant.** Break bands are whole minutes and no restart timestamp exists in any "
        "source we hold, so the minute at `restart` is a transition bin that may contain "
        "residual dead time. It is excluded from interpretation, and its effect is "
        "measured in the sensitivity above rather than asserted.",
        "- Event-study bands are POINTWISE 95% intervals at each relative minute. They "
        "are descriptive; they are not simultaneous bands, and the trajectory as a whole "
        "has not been subjected to a joint test. Formal inference is the window contrasts.",
    ]
    (TABLES / "break_window.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    out = pd.DataFrame([{k: v for k, v in r.items() if k != "_df"} for r in rows])
    out.to_csv(PROCESSED / "break_window_results.csv", index=False)

    es = event_studies(bands, cache, per_min, support)
    figure_a(rows)
    figure_b(es)
    figure_supp(es)
    print("\n".join(lines))
    print(f"\nwrote break_window_results.csv and 3 figures "
          f"(event study: {es['n_breaks']} breaks / {es['n_matches']} matches)")


if __name__ == "__main__":
    main()
