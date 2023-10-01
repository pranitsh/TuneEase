from ..getmusic.utils.midi_config import (
    MAX_TS_DENOMINATOR,
    MAX_NOTES_PER_BAR,
    DURATION_MAX,
    POS_RESOLUTION,
    MIN_TEMPO,
    MAX_TEMPO,
    TEMPO_QUANT,
    VELOCITY_QUANT,
)
import math


class TS:
    ts_dict = dict()
    ts_list = list()

    def __init__(self):
        for i in range(0, MAX_TS_DENOMINATOR + 1):  # 1 ~ 64
            for j in range(1, ((2**i) * MAX_NOTES_PER_BAR) + 1):
                self.ts_dict[(j, 2**i)] = len(self.ts_dict)
                self.ts_list.append((j, 2**i))


def t2e(x):
    ts = TS()
    assert x in ts.ts_dict, "unsupported time signature: " + str(x)
    return ts.ts_dict[x]


def e2t(x):
    ts = TS()
    return ts.ts_list[x]


class Dur:
    dur_enc = list()
    dur_dec = list()

    def __init__(self) -> None:
        for i in range(DURATION_MAX):
            for j in range(POS_RESOLUTION):
                self.dur_dec.append(len(self.dur_enc))
                for k in range(2**i):
                    self.dur_enc.append(len(self.dur_dec) - 1)


def d2e(x):
    dur = Dur()
    return dur.dur_enc[x] if x < len(dur.dur_enc) else dur.dur_enc[-1]


def e2d(x):
    dur = Dur()
    return dur.dur_dec[x] if x < len(dur.dur_dec) else dur.dur_dec[-1]


def time_signature_reduce(numerator, denominator):
    # reduction (when denominator is too large)
    global MAX_TS_DENOMINATOR
    global MAX_NOTES_PER_BAR
    while (
        denominator > 2**MAX_TS_DENOMINATOR
        and denominator % 2 == 0
        and numerator % 2 == 0
    ):
        denominator //= 2
        numerator //= 2
    # decomposition (when length of a bar exceed max_notes_per_bar)
    while numerator > MAX_NOTES_PER_BAR * denominator:
        for i in range(2, numerator + 1):
            if numerator % i == 0:
                numerator //= i
                break
    return numerator, denominator


def v2e(x):
    return x // VELOCITY_QUANT


def e2v(x):
    return (x * VELOCITY_QUANT) + (VELOCITY_QUANT // 2)


def b2e(x):
    x = max(x, MIN_TEMPO)
    x = min(x, MAX_TEMPO)
    x = x / MIN_TEMPO
    e = round(math.log2(x) * TEMPO_QUANT)
    return e


def e2b(x):
    return 2 ** (x / TEMPO_QUANT) * MIN_TEMPO
