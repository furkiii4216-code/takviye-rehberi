#!/usr/bin/env python3
"""Takviye Rehberi alarm seslerini uretir (sadece standart kutuphane, internet gerekmez).

Kullanim:  python3 make_sounds.py <klasor1> [<klasor2> ...]
Her ses, verilen tum klasorlere <ad>.wav olarak yazilir.
"""
import math
import os
import struct
import sys
import wave

SR = 24000

# Tinik (ratio, genlik, sonme carpani)
MARIMBA = [(1, 1.0, 1.0), (4, 0.25, 3.0), (10, 0.06, 6.0)]
BELL = [(1, 1.0, 1.0), (2.76, 0.5, 1.6), (5.4, 0.28, 2.4), (8.93, 0.14, 3.2)]
PLUCK = [(1, 1.0, 1.0), (2, 0.45, 1.8), (3, 0.25, 2.5), (4, 0.12, 3.5)]
TRI = [(1, 1.0, 1.0), (3, 0.11, 1.0), (5, 0.04, 1.0)]
CHIRP = [(1, 1.0, 1.0), (2, 0.2, 1.0)]
DROP = [(1, 1.0, 1.0), (2, 0.15, 1.2)]


def note(t, f, dur, decay, partials, vol=1.0, f_end=None, curve=1.0, vib=0.0):
    return dict(t=t, f=f, dur=dur, decay=decay, partials=partials, vol=vol,
                f_end=f if f_end is None else f_end, curve=curve, vib=vib)


def render(events, total, peak=0.85):
    n = int(SR * total)
    buf = [0.0] * n
    for ev in events:
        start = int(ev["t"] * SR)
        m = int(ev["dur"] * SR)
        phases = [0.0] * len(ev["partials"])
        for i in range(m):
            idx = start + i
            if idx >= n:
                break
            t = i / SR
            k = t / ev["dur"]
            f = ev["f"] + (ev["f_end"] - ev["f"]) * (k ** ev["curve"])
            if ev["vib"]:
                f *= 1 + ev["vib"] * math.sin(2 * math.pi * 30 * t)
            attack = 0.004
            fade = 0.03
            rem = ev["dur"] - t
            gate = min(1.0, t / attack) * min(1.0, max(0.0, rem / fade))
            s = 0.0
            for j, (ratio, amp, dm) in enumerate(ev["partials"]):
                phases[j] += 2 * math.pi * f * ratio / SR
                s += amp * math.sin(phases[j]) * math.exp(-ev["decay"] * dm * t)
            buf[idx] += s * gate * ev["vol"]
    mx = max(abs(x) for x in buf) or 1.0
    scale = peak / mx
    return [x * scale for x in buf]


def write_wav(path, samples):
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, x)) * 32767)) for x in samples))


C5, E5, G5, B5, C6, E6 = 523.25, 659.25, 783.99, 987.77, 1046.5, 1318.5

SOUNDS = {
    # Neseli, yukselen dort notalik jingle
    "melodi": ([
        note(0.00, C5, 0.9, 5.0, MARIMBA),
        note(0.17, E5, 0.9, 5.0, MARIMBA),
        note(0.34, G5, 0.9, 5.0, MARIMBA),
        note(0.51, C6, 1.3, 3.5, MARIMBA),
        note(1.55, C6, 0.8, 5.0, MARIMBA, vol=0.5),
    ], 2.5),
    # Iki vurusluk yumusak can
    "can": ([
        note(0.00, 880.0, 1.7, 2.4, BELL),
        note(0.50, E6, 1.7, 2.4, BELL, vol=0.85),
    ], 2.4),
    # Su damlasi
    "damla": ([
        note(0.00, 700, 0.28, 11, DROP, f_end=1500, curve=0.35),
        note(0.38, 560, 0.28, 11, DROP, vol=0.8, f_end=1250, curve=0.35),
        note(0.78, 880, 0.30, 10, DROP, vol=0.9, f_end=1900, curve=0.35),
    ], 1.3),
    # Kus cikirtisi
    "kus": ([
        note(0.00, 2300, 0.09, 14, CHIRP, f_end=3300),
        note(0.14, 2300, 0.09, 14, CHIRP, f_end=3300),
        note(0.28, 2300, 0.09, 14, CHIRP, f_end=3300),
        note(0.50, 2800, 0.35, 5, CHIRP, f_end=2200, vib=0.03),
    ], 1.1),
    # Dikkat ceken ding-dong ding-dong
    "zil": ([
        note(0.00, 988, 0.5, 6, TRI),
        note(0.24, 784, 0.5, 6, TRI),
        note(0.70, 988, 0.5, 6, TRI),
        note(0.94, 784, 0.7, 5, TRI),
    ], 1.8),
    # Arp (yukari ve asagi)
    "arp": ([
        note(0.00, C5, 1.0, 3.2, PLUCK),
        note(0.09, E5, 1.0, 3.2, PLUCK),
        note(0.18, G5, 1.0, 3.2, PLUCK),
        note(0.27, B5, 1.0, 3.2, PLUCK),
        note(0.36, E6, 1.2, 3.0, PLUCK),
        note(1.05, G5, 0.8, 4.0, PLUCK, vol=0.5),
        note(1.20, C6, 1.0, 3.5, PLUCK, vol=0.55),
    ], 2.3),
}


def main():
    dirs = sys.argv[1:]
    if not dirs:
        print("Kullanim: make_sounds.py <klasor> [<klasor> ...]")
        return 1
    for d in dirs:
        os.makedirs(d, exist_ok=True)
    for name, (events, total) in SOUNDS.items():
        samples = render(events, total)
        for d in dirs:
            write_wav(os.path.join(d, name + ".wav"), samples)
        print("%-8s %.1f sn" % (name, total))
    return 0


if __name__ == "__main__":
    sys.exit(main())
