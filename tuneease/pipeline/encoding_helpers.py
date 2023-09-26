from ..getmusic.utils.midi_config import max_ts_denominator, max_notes_per_bar, duration_max, pos_resolution, min_tempo, max_tempo, tempo_quant, velocity_quant
import math

class TS:
    ts_dict = dict()
    ts_list = list()

    def __init__(self):
        for i in range(0, max_ts_denominator + 1):  # 1 ~ 64
            for j in range(1, ((2 ** i) * max_notes_per_bar) + 1):
                self.ts_dict[(j, 2 ** i)] = len(self.ts_dict)
                self.ts_list.append((j, 2 ** i))

def t2e(x):
    ts = TS()
    assert x in ts.ts_dict, 'unsupported time signature: ' + str(x)
    return ts.ts_dict[x]

def e2t(x):
    ts = TS()
    return ts.ts_list[x]

class Dur:
    dur_enc = list()
    dur_dec = list()

    def __init__(self) -> None:        
        for i in range(duration_max):
            for j in range(pos_resolution):
                self.dur_dec.append(len(self.dur_enc))
                for k in range(2 ** i):
                    self.dur_enc.append(len(self.dur_dec) - 1)

def d2e(x):
    dur = Dur()
    return dur.dur_enc[x] if x < len(dur.dur_enc) else dur.dur_enc[-1]

def e2d(x):
    dur = Dur()
    return dur.dur_dec[x] if x < len(dur.dur_dec) else dur.dur_dec[-1]

def time_signature_reduce(numerator, denominator):
    # reduction (when denominator is too large)
    global max_ts_denominator
    global max_notes_per_bar
    while denominator > 2 ** max_ts_denominator and denominator % 2 == 0 and numerator % 2 == 0:
        denominator //= 2
        numerator //= 2
    # decomposition (when length of a bar exceed max_notes_per_bar)
    while numerator > max_notes_per_bar * denominator:
        for i in range(2, numerator + 1):
            if numerator % i == 0:
                numerator //= i
                break
    return numerator, denominator

def v2e(x):
    return x // velocity_quant

def e2v(x):
    return (x * velocity_quant) + (velocity_quant // 2)

def b2e(x):
    x = max(x, min_tempo)
    x = min(x, max_tempo)
    x = x / min_tempo
    e = round(math.log2(x) * tempo_quant)
    return e

def e2b(x):
    return 2 ** (x / tempo_quant) * min_tempo
