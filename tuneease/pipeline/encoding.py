import miditoolkit
import math
from ..getmusic.utils.midi_config import POS_RESOLUTION, BEAT_NOTE_FACTOR, TRUNC_POS, MAX_PITCH, MAX_INST, FILTER_SYMBOLIC, FILTER_SYMBOLIC_PPL
from .encoding_helpers import t2e, e2t, d2e, e2d, time_signature_reduce, b2e, e2b, v2e, e2v
from .presets import RootKinds
from .item import Item
from ..getmusic.utils.magenta_chord_recognition import Magenta 
from .processing import normalize_to_c_major
from .key_chord import KeyChordDetails

def MIDI_to_encoding(filename, midi_obj, with_chord = None, condition_inst = None, chord_from_single = None):
    magenta = Magenta()
    k_c_d = KeyChordDetails()
    r_h = RootKinds()
    if filename == "track_generation.py":
        def time_to_pos(t):
            return round(t * POS_RESOLUTION / midi_obj.ticks_per_beat)
        notes_start_pos = [time_to_pos(j.start)
                        for i in midi_obj.instruments for j in i.notes]
        if len(notes_start_pos) == 0:
            return list()
        max_pos = max(notes_start_pos) + 1
        pos_to_info = [[None for _ in range(4)] for _ in range(
            max_pos)] 
        tsc = midi_obj.time_signature_changes 
        tpc = midi_obj.tempo_changes
        for i in range(len(tsc)):
            for j in range(time_to_pos(tsc[i].time), time_to_pos(tsc[i + 1].time) if i < len(tsc) - 1 else max_pos):
                if j < len(pos_to_info):
                    pos_to_info[j][1] = t2e(time_signature_reduce(
                        tsc[i].numerator, tsc[i].denominator))
        for i in range(len(tpc)):
            for j in range(time_to_pos(tpc[i].time), time_to_pos(tpc[i + 1].time) if i < len(tpc) - 1 else max_pos):
                if j < len(pos_to_info):
                    pos_to_info[j][3] = b2e(tpc[i].tempo)
        for j in range(len(pos_to_info)):
            if pos_to_info[j][1] is None:
                # MIDI default time signature
                pos_to_info[j][1] = t2e(time_signature_reduce(4, 4))
            if pos_to_info[j][3] is None:
                pos_to_info[j][3] = b2e(120.0)  # MIDI default tempo (BPM)
        cnt = 0
        bar = 0
        measure_length = None
        for j in range(len(pos_to_info)): 
            timesignature = e2t(pos_to_info[j][1])
            if cnt == 0:
                measure_length = timesignature[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // timesignature[1]
            pos_to_info[j][0] = bar
            pos_to_info[j][2] = cnt
            cnt += 1
            if cnt >= measure_length:  
                assert cnt == measure_length, 'invalid time signature change: pos = {}'.format(
                    j)
                cnt -= measure_length
                bar += 1
        encoding = []
                
        for inst in midi_obj.instruments:
            for note in inst.notes:
                if time_to_pos(note.start) >= TRUNC_POS:
                    continue
                info = pos_to_info[time_to_pos(note.start)]
                duration = d2e(time_to_pos(note.end) - time_to_pos(note.start))
                encoding.append([info[0], info[2], MAX_INST + 1 if inst.is_drum else inst.program, note.pitch + MAX_PITCH +
                                1 if inst.is_drum else note.pitch, duration, v2e(note.velocity), info[1], info[3]])
        if len(encoding) == 0:
            return list()
        encoding.sort()
        encoding, is_major, pitch_shift = normalize_to_c_major(filename, encoding)
        # extract chords
        if with_chord:
            max_pos = 0
            note_items = []
            for note in encoding:
                if (0 < note[3] < 128) and (note[2] in [0,25,32,48,80]):
                    if chord_from_single and (str(note[2]) not in condition_inst):
                        continue
                    timesignature = e2t(note[6])
                    measure_length = timesignature[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // timesignature[1]
                    max_pos = max(
                        max_pos, measure_length * note[0] + note[1] + e2d(note[4]))
                    note_items.append(Item(
                        name='On',
                        start = measure_length * note[0] + note[1],
                        end = measure_length * note[0] + note[1] + e2d(note[4]),
                        vel=e2v(note[5]),
                        pitch=note[3],
                        track=0))
            note_items.sort(key=lambda x: (x.start, -x.end))
            pos_per_chord = measure_length
            max_chords = round(max_pos // pos_per_chord + 0.5)
            if max_chords > 0:
                chords = magenta.infer_chords_for_sequence(note_items,
                                            pos_per_chord=pos_per_chord,
                                            max_chords=max_chords,
                                            key_chord_loglik=k_c_d.key_chord_loglik,
                                            key_chord_transition_loglik=k_c_d.key_chord_transition_loglik
                                            )
            else:
                chords = []
            bar_idx = 0
            for chord in chords:
                if chord == 'N.C.':
                    bar_idx+=1
                    continue
                r, k = chord.split(':')
                if k == '':
                    k = 'null'
                elif k == '7':
                    k = 'seven'
                encoding.append((bar_idx, 0, 129, r_h.root_dict[r], r_h.kind_dict[k], 0, t2e(time_signature_reduce(4, 4)), 0))
                bar_idx += 1
            encoding.sort()
        return encoding, pitch_shift, tpc
    elif filename == "position_generation.py":
        def time_to_pos(t):
            return round(t * POS_RESOLUTION / midi_obj.ticks_per_beat)
        notes_start_pos = [time_to_pos(j.start)
                        for i in midi_obj.instruments for j in i.notes]
        if len(notes_start_pos) == 0:
            return list()
        max_pos = max(notes_start_pos) + 1
        pos_to_info = [[None for _ in range(4)] for _ in range(
            max_pos)]  # (Measure, TimeSig, Pos, Tempo)
        tsc = midi_obj.time_signature_changes # [TimeSignature(numerator=4, denominator=4, time=0)]
        tpc = midi_obj.tempo_changes # [TempoChange(tempo=120.0, time=0)]
        for i in range(len(tsc)):
            for j in range(time_to_pos(tsc[i].time), time_to_pos(tsc[i + 1].time) if i < len(tsc) - 1 else max_pos):
                if j < len(pos_to_info):
                    pos_to_info[j][1] = t2e(time_signature_reduce(
                        tsc[i].numerator, tsc[i].denominator))
        for i in range(len(tpc)):
            for j in range(time_to_pos(tpc[i].time), time_to_pos(tpc[i + 1].time) if i < len(tpc) - 1 else max_pos):
                if j < len(pos_to_info):
                    pos_to_info[j][3] = b2e(tpc[i].tempo)
        for j in range(len(pos_to_info)):
            if pos_to_info[j][1] is None:
                # MIDI default time signature
                pos_to_info[j][1] = t2e(time_signature_reduce(4, 4))
            if pos_to_info[j][3] is None:
                pos_to_info[j][3] = b2e(120.0)  # MIDI default tempo (BPM)
        cnt = 0
        bar = 0
        measure_length = None
        for j in range(len(pos_to_info)): # 它这里是不管这个位置有没有音符，都占个位
            timesignature = e2t(pos_to_info[j][1])
            if cnt == 0:
                measure_length = timesignature[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // timesignature[1] # 比如一个3/4的ts，一个4/4的小节有16pos，所以3/4一小节就有12
            pos_to_info[j][0] = bar
            pos_to_info[j][2] = cnt
            cnt += 1
            if cnt >= measure_length:  # 如果cnt>了measure长度，就是下一个小节了，cnt清零，bar index加一
                assert cnt == measure_length, 'invalid time signature change: pos = {}'.format(
                    j)
                cnt -= measure_length
                bar += 1
        encoding = []
        for inst in midi_obj.instruments:
            for note in inst.notes:
                if time_to_pos(note.start) >= TRUNC_POS:
                    continue
                info = pos_to_info[time_to_pos(note.start)]
                duration = d2e(time_to_pos(note.end) - time_to_pos(note.start))
                encoding.append([info[0], info[2], MAX_INST + 1 if inst.is_drum else inst.program, note.pitch + MAX_PITCH +
                                1 if inst.is_drum else note.pitch, duration, v2e(note.velocity), info[1], info[3]])
        if len(encoding) == 0:
            return list()
        encoding.sort()
        encoding, is_major, pitch_shift = normalize_to_c_major(filename, encoding)
        # extract chords
        if with_chord:
            max_pos = 0
            note_items = []
            for note in encoding:
                if 0 < note[3] < 128: # and str(note[2]) in condition_inst:
                    timesignature = e2t(note[6])
                    measure_length = timesignature[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // timesignature[1]
                    max_pos = max(
                        max_pos, measure_length * note[0] + note[1] + e2d(note[4]))
                    note_items.append(Item(
                        name='On',
                        start = measure_length * note[0] + note[1],
                        end = measure_length * note[0] + note[1] + e2d(note[4]),
                        vel=e2v(note[5]),
                        pitch=note[3],
                        track=0))
            note_items.sort(key=lambda x: (x.start, -x.end))
            pos_per_chord = measure_length
            max_chords = round(max_pos // pos_per_chord + 0.5)
            if max_chords > 0:
                chords = magenta.infer_chords_for_sequence(note_items,
                                            pos_per_chord=pos_per_chord,
                                            max_chords=max_chords,
                                            key_chord_loglik=k_c_d.key_chord_loglik,
                                            key_chord_transition_loglik=k_c_d.key_chord_transition_loglik
                                            )
            else:
                chords = []    
            bar_idx = 0
            for chord in chords:
                if chord == 'N.C.':
                    bar_idx+=1
                    continue
                r, k = chord.split(':')
                if k == '':
                    k = 'null'
                elif k == '7':
                    k = 'seven'
                encoding.append((bar_idx, 0, 129, r_h.root_dict[r], r_h.kind_dict[k], 0, t2e(time_signature_reduce(4, 4)), 0))
                bar_idx += 1
            encoding.sort()
        return encoding, pitch_shift, tpc
    elif filename == "to_oct.py":
        def time_to_pos(t):
            return round(t * POS_RESOLUTION / midi_obj.ticks_per_beat)
        notes_start_pos = [time_to_pos(j.start)
                        for i in midi_obj.instruments for j in i.notes]
        if len(notes_start_pos) == 0:
            return list()
        max_pos = min(max(notes_start_pos) + 1, TRUNC_POS)
        pos_to_info = [[None for _ in range(4)] for _ in range(
            max_pos)]  # (Measure, TimeSig, Pos, Tempo)
        tsc = midi_obj.time_signature_changes # [TimeSignature(numerator=4, denominator=4, time=0)]
        tpc = midi_obj.tempo_changes # [TempoChange(tempo=120.0, time=0)]
        # filter tempo and ts change
        if len(tsc) > 1 or len(tpc) > 1:
            return ['welcome use my code']
        for i in range(len(tsc)):
            for j in range(time_to_pos(tsc[i].time), time_to_pos(tsc[i + 1].time) if i < len(tsc) - 1 else max_pos):
                if j < len(pos_to_info):
                    pos_to_info[j][1] = t2e(time_signature_reduce(
                        tsc[i].numerator, tsc[i].denominator))
        for i in range(len(tpc)):
            for j in range(time_to_pos(tpc[i].time), time_to_pos(tpc[i + 1].time) if i < len(tpc) - 1 else max_pos):
                if j < len(pos_to_info):
                    pos_to_info[j][3] = b2e(tpc[i].tempo)
        for j in range(len(pos_to_info)):
            if pos_to_info[j][1] is None:
                # MIDI default time signature
                pos_to_info[j][1] = t2e(time_signature_reduce(4, 4))
            if pos_to_info[j][3] is None:
                pos_to_info[j][3] = b2e(120.0)  # MIDI default tempo (BPM)
        cnt = 0
        bar = 0
        measure_length = None
        for j in range(len(pos_to_info)):
            timesignature = e2t(pos_to_info[j][1])
            if cnt == 0:
                measure_length = timesignature[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // timesignature[1]
            pos_to_info[j][0] = bar
            pos_to_info[j][2] = cnt
            cnt += 1
            if cnt >= measure_length:
                assert cnt == measure_length, 'invalid time signature change: pos = {}'.format(
                    j)
                cnt -= measure_length
                bar += 1
        encoding = []
        start_distribution = [0] * POS_RESOLUTION
        for inst in midi_obj.instruments:
            for note in inst.notes:
                if time_to_pos(note.start) >= TRUNC_POS:
                    continue
                start_distribution[time_to_pos(note.start) % POS_RESOLUTION] += 1
                info = pos_to_info[time_to_pos(note.start)]
                duration = d2e(time_to_pos(note.end) - time_to_pos(note.start))
                encoding.append((info[0], info[2], MAX_INST + 1 if inst.is_drum else inst.program, note.pitch + MAX_PITCH +
                                1 if inst.is_drum else note.pitch, duration, v2e(note.velocity), info[1], info[3]))
        if len(encoding) == 0:
            return list()
        tot = sum(start_distribution)
        start_ppl = 2 ** sum((0 if x == 0 else -(x / tot) *
                            math.log2((x / tot)) for x in start_distribution))
        # filter unaligned music
        if FILTER_SYMBOLIC:
            assert start_ppl <= FILTER_SYMBOLIC_PPL, 'filtered out by the symbolic filter: ppl = {:.2f}'.format(
                start_ppl)
        # normalize
        encoding.sort()
        encoding, is_major = normalize_to_c_major(filename, encoding)
        # extract chords
        max_pos = 0
        note_items = []
        for note in encoding:
            if 0 <= note[3] < 128:
                timesignature = e2t(note[6])
                measure_length = timesignature[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // timesignature[1]
                max_pos = max(
                    max_pos, measure_length * note[0] + note[1] + e2d(note[4]))
                note_items.append(Item(
                    name='On',
                    start = measure_length * note[0] + note[1],
                    end = measure_length * note[0] + note[1] + e2d(note[4]),
                    vel=e2v(note[5]),
                    pitch=note[3],
                    track=0))
        note_items.sort(key=lambda x: (x.start, -x.end))
        pos_per_chord = measure_length
        max_chords = round(max_pos // pos_per_chord + 0.5)
        chords = magenta.infer_chords_for_sequence(note_items,
                                        pos_per_chord=pos_per_chord,
                                        max_chords=max_chords,
                                        key_chord_loglik=k_c_d.key_chord_loglik,
                                        key_chord_transition_loglik=k_c_d.key_chord_transition_loglik
                                        )
        bar_idx = 0
        for chord in chords:
            r, k = chord.split(':')
            if k == '':
                k = 'null'
            elif k == '7':
                k = 'seven'
            encoding.append((bar_idx, 0, 129, r_h.root_dict[r], r_h.kind_dict[k], 0, t2e(time_signature_reduce(4, 4)), 0))
            bar_idx += 1
        encoding.sort()
        return encoding

def encoding_to_MIDI(filename, encoding, tpc = None, decode_chord=None):
    magenta = Magenta()
    r_h = RootKinds()
    if filename == "track_generation.py":
        tmp = encoding.strip().split('<0-')[1:]
        encoding = []
        for item in tmp:
            tmp2 = item.strip()[:-1].split('> <')
            encoding.append([int(tmp2[0])] + [int(i[2:]) for i in tmp2[1:]])
        del tmp
        bar_to_timesig = [list()
                        for _ in range(max(map(lambda x: x[0], encoding)) + 1)]
        for i in encoding:
            bar_to_timesig[i[0]].append(i[6])
        bar_to_timesig = [max(set(i), key=i.count) if len(
            i) > 0 else None for i in bar_to_timesig]
        for i in range(len(bar_to_timesig)):
            if bar_to_timesig[i] is None:
                bar_to_timesig[i] = t2e(time_signature_reduce(
                    4, 4)) if i == 0 else bar_to_timesig[i - 1]
        bar_to_pos = [None] * len(bar_to_timesig)
        cur_pos = 0
        for i in range(len(bar_to_pos)):
            bar_to_pos[i] = cur_pos
            ts = e2t(bar_to_timesig[i])
            measure_length = ts[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // ts[1]
            cur_pos += measure_length
        pos_to_tempo = [list() for _ in range(
            cur_pos + max(map(lambda x: x[1], encoding)))]
        for i in encoding:
            pos_to_tempo[bar_to_pos[i[0]] + i[1]].append(i[7])
        pos_to_tempo = [round(sum(i) / len(i)) if len(i) >
                        0 else None for i in pos_to_tempo]
        for i in range(len(pos_to_tempo)):
            if pos_to_tempo[i] is None:
                pos_to_tempo[i] = b2e(120.0) if i == 0 else pos_to_tempo[i - 1]
        midi_obj = miditoolkit.midi.parser.MidiFile()
        midi_obj.tempo_changes = tpc
        def get_tick(bar, pos):
            return (bar_to_pos[bar] + pos) * midi_obj.ticks_per_beat // POS_RESOLUTION
        midi_obj.instruments = [miditoolkit.containers.Instrument(program=(
            0 if i == 128 else i), is_drum=(i == 128), name=str(i)) for i in range(128 + 1)]
        for i in encoding:
            start = get_tick(i[0], i[1])
            program = i[2]
            if program == 129 and decode_chord:
                root_name = r_h.root_list[i[3]]
                kind_name = r_h.kind_list[i[4]]
                root_pitch_shift = r_h.root_dict[root_name]
                end = start + get_tick(0, e2d(1))
                for kind_shift in magenta._CHORD_KIND_PITCHES[kind_name]:
                    pitch = 36 + root_pitch_shift + kind_shift
                    midi_obj.instruments[1].notes.append(miditoolkit.containers.Note(
                    start=start, end=end, pitch=pitch, velocity=e2v(20)))
            elif program != 129:
                pitch = (i[3] - 128 if program == 128 else i[3])
                if pitch < 0:
                    continue
                duration = get_tick(0, e2d(i[4]))
                if duration == 0:
                    duration = 1
                end = start + duration
                velocity = e2v(i[5])

                midi_obj.instruments[program].notes.append(miditoolkit.containers.Note(
                    start=start, end=end, pitch=pitch, velocity=velocity))
        midi_obj.instruments = [
            i for i in midi_obj.instruments if len(i.notes) > 0]
        cur_ts = None
        for i in range(len(bar_to_timesig)):
            new_ts = bar_to_timesig[i]
            if new_ts != cur_ts:
                numerator, denominator = e2t(new_ts)
                midi_obj.time_signature_changes.append(miditoolkit.containers.TimeSignature(
                    numerator=numerator, denominator=denominator, time=get_tick(i, 0)))
                cur_ts = new_ts
        cur_tp = None
        for i in range(len(pos_to_tempo)):
            new_tp = pos_to_tempo[i]
            if new_tp != cur_tp:
                tempo = e2b(new_tp)
                midi_obj.tempo_changes.append(
                    miditoolkit.containers.TempoChange(tempo=tempo, time=get_tick(0, i)))
                cur_tp = new_tp
        return midi_obj
    elif filename == "to_oct.py":
        # TODO: filter out non-valid notes and error handling
        bar_to_timesig = [list()
                        for _ in range(max(map(lambda x: x[0], encoding)) + 1)]
        for i in encoding:
            bar_to_timesig[i[0]].append(i[6])
        bar_to_timesig = [max(set(i), key=i.count) if len(
            i) > 0 else None for i in bar_to_timesig]
        for i in range(len(bar_to_timesig)):
            if bar_to_timesig[i] is None:
                bar_to_timesig[i] = t2e(time_signature_reduce(
                    4, 4)) if i == 0 else bar_to_timesig[i - 1]
        bar_to_pos = [None] * len(bar_to_timesig)
        cur_pos = 0
        for i in range(len(bar_to_pos)):
            bar_to_pos[i] = cur_pos
            ts = e2t(bar_to_timesig[i])
            measure_length = ts[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // ts[1]
            cur_pos += measure_length
        pos_to_tempo = [list() for _ in range(
            cur_pos + max(map(lambda x: x[1], encoding)))]
        for i in encoding:
            pos_to_tempo[bar_to_pos[i[0]] + i[1]].append(i[7])
        pos_to_tempo = [round(sum(i) / len(i)) if len(i) >
                        0 else None for i in pos_to_tempo]
        for i in range(len(pos_to_tempo)):
            if pos_to_tempo[i] is None:
                pos_to_tempo[i] = b2e(120.0) if i == 0 else pos_to_tempo[i - 1]
        midi_obj = miditoolkit.midi.parser.MidiFile()
        def get_tick(bar, pos):
            return (bar_to_pos[bar] + pos) * midi_obj.ticks_per_beat // POS_RESOLUTION
        midi_obj.instruments = [miditoolkit.containers.Instrument(program=(
            0 if i == 128 else i), is_drum=(i == 128), name=str(i)) for i in range(128 + 1)]
        for i in encoding:
            start = get_tick(i[0], i[1])
            program = i[2]
            pitch = (i[3] - 128 if program == 128 else i[3])
            duration = get_tick(0, e2d(i[4]))
            if duration == 0:
                duration = 1
            end = start + duration
            velocity = e2v(i[5])
            midi_obj.instruments[program].notes.append(miditoolkit.containers.Note(
                start=start, end=end, pitch=pitch, velocity=velocity))
        midi_obj.instruments = [
            i for i in midi_obj.instruments if len(i.notes) > 0]
        cur_ts = None
        for i in range(len(bar_to_timesig)):
            new_ts = bar_to_timesig[i]
            if new_ts != cur_ts:
                numerator, denominator = e2t(new_ts)
                midi_obj.time_signature_changes.append(miditoolkit.containers.TimeSignature(
                    numerator=numerator, denominator=denominator, time=get_tick(i, 0)))
                cur_ts = new_ts
        cur_tp = None
        for i in range(len(pos_to_tempo)):
            new_tp = pos_to_tempo[i]
            if new_tp != cur_tp:
                tempo = e2b(new_tp)
                midi_obj.tempo_changes.append(
                    miditoolkit.containers.TempoChange(tempo=tempo, time=get_tick(0, i)))
                cur_tp = new_tp
        return midi_obj
    elif filename == "position_generation.py":
        tmp = encoding.strip().split('<0-')[1:]
        encoding = []
        for item in tmp:
            tmp2 = item.strip()[:-1].split('> <')
            encoding.append([int(tmp2[0])] + [int(i[2:]) for i in tmp2[1:]])
        del tmp
        
        bar_to_timesig = [list()
                        for _ in range(max(map(lambda x: x[0], encoding)) + 1)]
        for i in encoding:
            bar_to_timesig[i[0]].append(i[6])
        bar_to_timesig = [max(set(i), key=i.count) if len(
            i) > 0 else None for i in bar_to_timesig]
        for i in range(len(bar_to_timesig)):
            if bar_to_timesig[i] is None:
                bar_to_timesig[i] = t2e(time_signature_reduce(
                    4, 4)) if i == 0 else bar_to_timesig[i - 1]
        bar_to_pos = [None] * len(bar_to_timesig)
        cur_pos = 0
        for i in range(len(bar_to_pos)):
            bar_to_pos[i] = cur_pos
            ts = e2t(bar_to_timesig[i])
            measure_length = ts[0] * BEAT_NOTE_FACTOR * POS_RESOLUTION // ts[1]
            cur_pos += measure_length
        pos_to_tempo = [list() for _ in range(
            cur_pos + max(map(lambda x: x[1], encoding)))]
        for i in encoding:
            pos_to_tempo[bar_to_pos[i[0]] + i[1]].append(i[7])
        pos_to_tempo = [round(sum(i) / len(i)) if len(i) >
                        0 else None for i in pos_to_tempo]
        for i in range(len(pos_to_tempo)):
            if pos_to_tempo[i] is None:
                pos_to_tempo[i] = b2e(120.0) if i == 0 else pos_to_tempo[i - 1]
        midi_obj = miditoolkit.midi.parser.MidiFile()
        midi_obj.tempo_changes = tpc
        def get_tick(bar, pos):
            return (bar_to_pos[bar] + pos) * midi_obj.ticks_per_beat // POS_RESOLUTION
        midi_obj.instruments = [miditoolkit.containers.Instrument(program=(
            0 if i == 128 else i), is_drum=(i == 128), name=str(i)) for i in range(128 + 1)]
        for i in encoding:
            start = get_tick(i[0], i[1])
            program = i[2]
            if program == 129 and decode_chord:
                root_name = r_h.root_list[i[3]]
                kind_name = r_h.kind_list[i[4]]
                root_pitch_shift = r_h.root_dict[root_name]
                end = start + get_tick(0, e2d(1))
                for kind_shift in magenta._CHORD_KIND_PITCHES[kind_name]:
                    pitch = 36 + root_pitch_shift + kind_shift
                    midi_obj.instruments[1].notes.append(miditoolkit.containers.Note(
                    start=start, end=end, pitch=pitch, velocity=e2v(20)))
            elif program != 129:
                pitch = (i[3] - 128 if program == 128 else i[3])
                if pitch < 0:
                    continue
                duration = get_tick(0, e2d(i[4]))
                if duration == 0:
                    duration = 1
                end = start + duration
                velocity = e2v(i[5])
                midi_obj.instruments[program].notes.append(miditoolkit.containers.Note(
                    start=start, end=end, pitch=pitch, velocity=velocity))
        midi_obj.instruments = [
            i for i in midi_obj.instruments if len(i.notes) > 0]
        cur_ts = None
        for i in range(len(bar_to_timesig)):
            new_ts = bar_to_timesig[i]
            if new_ts != cur_ts:
                numerator, denominator = e2t(new_ts)
                midi_obj.time_signature_changes.append(miditoolkit.containers.TimeSignature(
                    numerator=numerator, denominator=denominator, time=get_tick(i, 0)))
                cur_ts = new_ts
        cur_tp = None
        for i in range(len(pos_to_tempo)):
            new_tp = pos_to_tempo[i]
            if new_tp != cur_tp:
                tempo = e2b(new_tp)
                midi_obj.tempo_changes.append(
                    miditoolkit.containers.TempoChange(tempo=tempo, time=get_tick(0, i)))
                cur_tp = new_tp
        return midi_obj
