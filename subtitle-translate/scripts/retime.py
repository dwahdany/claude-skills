# /// script
# requires-python = ">=3.10"
# dependencies = ["srt"]
# ///
"""Re-time SRT cues so the reading speed (characters per second, CPS) stays under a target.

Passes (never introduces new overlaps; a neighbour is only trimmed while it stays
at or above the target reading speed and above --min-dur, and by at most --max-delay / --max-lead):
  1. extend each cue's end into free space before the next cue, keeping a small gap
  1b. if still too short, delay the next cue's start (bounded), balancing CPS between the two
  2. if still too short, pull the start earlier (bounded), trimming a slack previous cue if needed
  3. with --merge: join a still-starving single-line cue with the following
     single-line cue when they are adjacent and fit on two lines, then redo 1-2
"""
import argparse, re
from datetime import timedelta
import srt

TAG_RE = re.compile(r"<[^>]+>|\{\\[^}]*\}")

def chars(text):
    return len(TAG_RE.sub("", text).replace("\n", ""))

def dur(c):
    return (c.end - c.start).total_seconds()

def cps(c):
    d = dur(c)
    return chars(c.content) / d if d > 0 else float("inf")

def needed(c, a):
    return min(a.max_dur, max(a.min_dur, chars(c.content) / a.target_cps))

def equalising_shift(taker_chars, taker_dur, donor_chars, donor_dur):
    """Seconds to move from donor to taker so both end up at the same CPS."""
    tot = taker_chars + donor_chars
    return (taker_chars * donor_dur - donor_chars * taker_dur) / tot if tot else 0.0

def extend(subs, a):
    gap = timedelta(seconds=a.gap)
    for i, s in enumerate(subs):                      # pass 1: push the end into free space
        want = s.start + timedelta(seconds=needed(s, a))
        if i + 1 < len(subs):
            want = min(want, subs[i + 1].start - gap)
        if want > s.end:
            s.end = want
    for i in range(len(subs) - 1):                    # pass 1b: borrow from the next cue (delay its start)
        s, n = subs[i], subs[i + 1]
        deficit = needed(s, a) - dur(s)
        if deficit <= 0:
            continue
        slack = dur(n) - needed(n, a)
        x_eq = equalising_shift(chars(s.content), dur(s), chars(n.content), dur(n))
        x = min(deficit, a.max_delay, dur(n) - a.min_dur, max(slack, x_eq))
        if x <= 0:
            continue
        n.start += timedelta(seconds=x)
        s.end = max(s.end, n.start - gap)
    for i, s in enumerate(subs):                      # pass 2: bounded lead-in (may trim a slack previous cue)
        deficit = needed(s, a) - dur(s)
        if deficit <= 0:
            continue
        earliest = s.start - timedelta(seconds=min(deficit, a.max_lead))
        if i > 0:
            p = subs[i - 1]
            floor = p.end + gap
            if floor > earliest:
                slack = dur(p) - needed(p, a)
                y_eq = equalising_shift(chars(s.content), dur(s), chars(p.content), dur(p))
                y = min((floor - earliest).total_seconds(), dur(p) - a.min_dur, max(slack, y_eq))
                if y > 0:
                    p.end -= timedelta(seconds=y)
                    floor = p.end + gap
            earliest = max(earliest, floor)
        if earliest < s.start:
            s.start = earliest
    return subs

def merge(subs, a):
    out, i, merged = [], 0, 0
    while i < len(subs):
        s = subs[i]
        if i + 1 < len(subs):
            n = subs[i + 1]
            starving = cps(s) > a.merge_cps or dur(s) < a.merge_min_dur
            adjacent = 0 <= (n.start - s.end).total_seconds() <= a.merge_gap
            single = "\n" not in s.content and "\n" not in n.content
            fits = (chars(s.content) + chars(n.content) <= a.merge_max_chars
                    and (n.end - s.start).total_seconds() <= a.max_dur)
            if starving and adjacent and single and fits:
                out.append(srt.Subtitle(index=0, start=s.start, end=n.end,
                                        content=s.content + "\n" + n.content))
                merged += 1
                i += 2
                continue
        out.append(s)
        i += 1
    return out, merged

def overlaps(subs):
    return sum(1 for x, y in zip(subs, subs[1:]) if x.end > y.start)

def stats(subs, a):
    c = sorted(cps(s) for s in subs)
    d = [dur(s) for s in subs]
    return {"cues": len(subs),
            f"over_{a.target_cps:g}cps": sum(x > a.target_cps for x in c),
            "over_20cps": sum(x > 20 for x in c),
            "under_1s": sum(x < 1.0 for x in d),
            "median_cps": round(c[len(c) // 2], 1),
            "p90_cps": round(c[int(len(c) * 0.9)], 1),
            "max_cps": round(c[-1], 1),
            "overlaps": overlaps(subs)}

p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
p.add_argument("inp"); p.add_argument("out")
p.add_argument("--target-cps", type=float, default=15)
p.add_argument("--min-dur", type=float, default=1.0)
p.add_argument("--max-dur", type=float, default=7.0)
p.add_argument("--gap", type=float, default=0.08)
p.add_argument("--max-lead", type=float, default=0.3)
p.add_argument("--max-delay", type=float, default=0.5)
p.add_argument("--merge", action="store_true")
p.add_argument("--merge-cps", type=float, default=20)
p.add_argument("--merge-min-dur", type=float, default=1.0)
p.add_argument("--merge-gap", type=float, default=0.4)
p.add_argument("--merge-max-chars", type=int, default=84)
a = p.parse_args()

subs = list(srt.sort_and_reindex(srt.parse(open(a.inp, encoding="utf-8").read())))
before = stats(subs, a)
print("before:", before)
extend(subs, a)
merged = 0
if a.merge:
    subs, merged = merge(subs, a)
    extend(subs, a)
after = stats(subs, a)
assert after["overlaps"] <= before["overlaps"], "introduced overlaps"
assert all(dur(s) > 0 for s in subs), "non-positive duration"
print("after: ", after, f"merged={merged}")
open(a.out, "w", encoding="utf-8").write(srt.compose(subs))
