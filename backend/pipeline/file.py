import miditoolkit
import torch
import numpy as np
from .encoding import MIDI_to_encoding
from .key_chord import TokenHelper, KeyChordDetails
from .encoding_helpers  import b2e, t2e, time_signature_reduce
from .presets import inst_to_row, prog_to_abrv, RootKinds
from ..getmusic.utils.midi_config import bar_max, deduplicate, sample_len_max, sample_overlap_rate
from .file_helpers import get_midi_dict, timeout, get_hash, lock_set, lock_write, writer

track_name = ['lead', 'bass', 'drum', 'guitar', 'piano', 'string']

def create_pos_from_str(str_cmd, pos):
    print(str_cmd)
    if str_cmd == '-':
        return pos
    track_cmds = str_cmd.split(';')
    for track_cmd in track_cmds:
        track_id, start_pos, end_pos = track_cmd.split(',')
        if end_pos != '':
            pos[int(track_id) * 2][int(start_pos):int(end_pos)] = 1
            pos[int(track_id) * 2 + 1][int(start_pos):int(end_pos)] = 1
        else:
            pos[int(track_id) * 2][int(start_pos):] = 1
            pos[int(track_id) * 2 + 1][int(start_pos):] = 1
    return pos


def F(filename, file_name, conditional_tracks = None, content_tracks = None, condition_inst = None, chord_from_single = None):
    t_h = TokenHelper()
    k_c_d = KeyChordDetails()
    r_h = RootKinds()
    if filename == "track_generation.py":
        empty_tracks = ~conditional_tracks & ~content_tracks
        
        conditional_tracks &= ~empty_tracks # emptied tracks can not be condition
        conditional_tracks = torch.tensor(conditional_tracks).float()
        conditional_tracks = conditional_tracks.view(7,1).repeat(1,2).reshape(14,1)
        empty_tracks = torch.tensor(empty_tracks).float()
        empty_tracks = empty_tracks.view(7,1).repeat(1,2).reshape(14,1)

        midi_obj = miditoolkit.midi.parser.MidiFile(file_name)

        if conditional_tracks[-1]:
            with_chord = True
        else:
            with_chord = False

        # try:
        encoding, pitch_shift, tpc = MIDI_to_encoding('track_generation.py', midi_obj, with_chord, condition_inst, chord_from_single)

        if len(encoding) == 0:
            print('ERROR(BLANK): ' + file_name + '\n', end='')
            return None, 0
        bar_index_offset = 0

        figure_size = encoding[-1][0] * k_c_d.pos_in_bar + encoding[-1][1]

        pad_length = 1 #(512 - figure_size % 512)

        figure_size += pad_length
        conditional_bool = conditional_tracks.repeat(1,figure_size)
        
        empty_pos = empty_tracks.repeat(1, figure_size).type(torch.bool)
        datum = t_h.pad_index * torch.ones(14, figure_size, dtype=float)
        oov = 0
        inv = 0
        
        chord_list = []
        
        tempo = b2e(67)

        lead_start = 0

        idx = 0
        while idx != len(encoding) - 1:
            e = encoding[idx]

            bar = e[0]
            pos = e[1]
            inst = e[2]
            pitch = e[3]

            if inst == 80:
                tempo = e[7]
                assert tempo != 0, 'bad tempo'
            
            # assert e[6] == 6
            
            if e[2] == 129:
                row = inst_to_row[str(inst)]
                r = r_h.root_list[e[3]]
                k = r_h.kind_list[e[4]]
                datum[2 * row][k_c_d.pos_in_bar * bar + pos : k_c_d.pos_in_bar * (bar + 1) + pos] = t_h.tokens_to_ids[r]
                datum[2 * row + 1][k_c_d.pos_in_bar * bar + pos : k_c_d.pos_in_bar * (bar + 1) + pos] = t_h.tokens_to_ids[k]
                idx += 1
                continue
            
            chord_list = [str(e[3])]

            for f_idx in range(idx + 1, len(encoding)):
                if (encoding[f_idx][0] == bar) and (encoding[f_idx][1] == pos) and (encoding[f_idx][2] == inst):
                    if encoding[f_idx][3] != pitch:
                        chord_list.append(str(encoding[f_idx][3]))
                        pitch = encoding[f_idx][3]
                else:
                    break
            
            idx = max(idx + 1, f_idx)
            
                    
            dur = e[4]
            if dur == 0:
                continue
            
            if not (str(inst) in inst_to_row):
                continue
            
            row = inst_to_row[str(inst)]
            dur = t_h.tokens_to_ids['T'+str(e[4])] # duration
            
            chord_string = ' '.join(chord_list)
            token = prog_to_abrv[str(inst)] + chord_string

            if token in t_h.tokens_to_ids:
                pitch = t_h.tokens_to_ids[token]
                assert (dur < t_h.pad_index) and (pitch > t_h.pad_index), 'pitch index is {} and dur index is {}'.format(pitch, dur)
                datum[2 * row][k_c_d.pos_in_bar * bar + pos] = pitch
                datum[2 * row + 1][k_c_d.pos_in_bar * bar + pos] = dur
                inv += 1
            else:
                oov += 1

        datum = torch.where(empty_pos, t_h.empty_index, datum)
        datum = torch.where(((datum != t_h.empty_index).float() * (1 - conditional_bool)).type(torch.bool), t_h.empty_index + 1, datum)

        # datum = datum[:,:1280]
        # conditional_bool = conditional_bool[:,:1280]

        # if trunc:
        datum = datum[:,:512]
        conditional_bool = conditional_bool[:,:512]

        not_empty_pos = (torch.tensor(np.array(datum)) != t_h.empty_index).float()

        have_cond = True
        
        for i in range(14):
            if with_chord and conditional_tracks[i] == 1 and ((datum[i] == t_h.pad_index).sum() + (datum[i] == t_h.empty_index).sum()) == min(512,figure_size):
                have_cond = False
                break

        return datum.unsqueeze(0), torch.tensor(tempo), not_empty_pos, conditional_bool, pitch_shift, tpc, have_cond
    elif filename == "position_generation.py":
        midi_obj = miditoolkit.midi.parser.MidiFile(file_name)

        encoding, pitch_shift, tpc = MIDI_to_encoding("position_generation.py", midi_obj)

        if len(encoding) == 0:
            print('ERROR(BLANK): ' + file_name + '\n', end='')
            return None, 0

        bar_index_offset = 0

        figure_size = max(encoding[-1][0] * k_c_d.pos_in_bar + encoding[-1][1], 512)

        pad_length = 1 #(512 - figure_size % 512)

        figure_size += pad_length

        datum = t_h.pad_index * torch.ones(14, figure_size, dtype=float)
        
        oov = 0
        inv = 0
        
        chord_list = []
        
        tempo = b2e(67)

        lead_start = 0

        idx = 0

        track_set = set()

        while idx != len(encoding) - 1:
            e = encoding[idx]

            bar = e[0]
            pos = e[1]
            inst = e[2]
            pitch = e[3]

            if inst == 80:
                tempo = e[7]
                assert tempo != 0, 'bad tempo'
            
            # assert e[6] == 6
            
            if e[2] == 129:
                row = inst_to_row[str(inst)]
                r = r_h.root_list[e[3]]
                k = r_h.kind_list[e[4]]
                datum[2 * row][k_c_d.pos_in_bar * bar + pos : k_c_d.pos_in_bar * (bar + 1) + pos] = t_h.tokens_to_ids[r]
                datum[2 * row + 1][k_c_d.pos_in_bar * bar + pos : k_c_d.pos_in_bar * (bar + 1) + pos] = t_h.tokens_to_ids[k]
                idx += 1
                continue
            
            chord_list = [str(e[3])]

            for f_idx in range(idx + 1, len(encoding)):
                if (encoding[f_idx][0] == bar) and (encoding[f_idx][1] == pos) and (encoding[f_idx][2] == inst):
                    if encoding[f_idx][3] != pitch:
                        chord_list.append(str(encoding[f_idx][3]))
                        pitch = encoding[f_idx][3]
                else:
                    break
            
            idx = max(idx + 1, f_idx)
            
                    
            dur = e[4]
            if dur == 0:
                continue
            
            if not (str(inst) in inst_to_row):
                continue
            
            row = inst_to_row[str(inst)]
            dur = t_h.tokens_to_ids['T'+str(e[4])] # duration
            
            chord_string = ' '.join(chord_list)
            token = prog_to_abrv[str(inst)] + chord_string

            track_set.add(track_name[prog_to_abrv[str(inst)]])

            if token in t_h.tokens_to_ids:
                pitch = t_h.tokens_to_ids[token]
                assert (dur < t_h.pad_index) and (pitch > t_h.pad_index), 'pitch index is {} and dur index is {}'.format(pitch, dur)
                datum[2 * row][k_c_d.pos_in_bar * bar + pos] = pitch
                datum[2 * row + 1][k_c_d.pos_in_bar * bar + pos] = dur
                inv += 1
            else:
                oov += 1

        datum[:,-pad_length:] = t_h.empty_index

        print('The music has {} tracks, with {} positions'.format(track_set, datum.size()[1]))
        print('Representation Visualization:')
        print('\t0,1,2,3,4,5,6,7,8,...\n(0)lead\n(1)bass\n(2)drum\n(3)guitar\n(4)piano\n(5)string\n(6)chord')
        print('Example: condition on 100 to 200 position of lead, 300 to 400 position of piano, write command like this:\'0,100,200;4,300,400')
        condition_str = input('Input positions you want to condition on:')
        empty_str = input('Input positions you want to empty:')

        empty_pos = torch.zeros_like(datum)
        condition_pos = torch.zeros_like(datum)
        empty_pos = create_pos_from_str(empty_str, empty_pos)
        condition_pos = create_pos_from_str(condition_str, condition_pos)

        datum = torch.where(empty_pos.type(torch.bool), t_h.empty_index, datum)
        datum = torch.where(((datum != t_h.empty_index).float() * (1 - condition_pos)).type(torch.bool), t_h.empty_index + 1, datum)
        
        not_empty_pos = (torch.tensor(np.array(datum)) != t_h.empty_index).float()
        
        return datum.unsqueeze(0), torch.tensor(tempo), not_empty_pos, condition_pos, pitch_shift, tpc
    elif filename == "to_oct.py":
        try:
            with timeout(seconds=600):
                midi_obj = miditoolkit.midi.parser.MidiFile(file_name)
            # check abnormal values in parse result
            assert all(0 <= j.start < 2 ** 31 and 0 <= j.end < 2 **
                    31 for i in midi_obj.instruments for j in i.notes), 'bad note time'
            assert all(0 < j.numerator < 2 ** 31 and 0 < j.denominator < 2 **
                    31 for j in midi_obj.time_signature_changes), 'bad time signature value'
            assert 0 < midi_obj.ticks_per_beat < 2 ** 31, 'bad ticks per beat'
        except BaseException as e:
            print('ERROR(PARSE): ' + file_name + ' ' + str(e) + '\n', end='')
            return None
        midi_notes_count = sum(len(inst.notes) for inst in midi_obj.instruments)
        if midi_notes_count == 0:
            print('ERROR(BLANK): ' + file_name + '\n', end='')
            return None
        
        no_empty_tracks = {'80':0,'32':0,'128':0,'25':0,'0':0,'48':0}
        for inst in midi_obj.instruments:
            no_empty_tracks[str(inst.program)] = 1

        if no_empty_tracks['80'] == 0 or sum(no_empty_tracks.values()) <= 1:
            print('ERROR(BAD TRACKS): ' + file_name + '\n', end='')
            return False
        try:
            e = MIDI_to_encoding("to_oct.py", midi_obj)
            
            if len(e) == 0:
                print('ERROR(BLANK): ' + file_name + '\n', end='')
                return None

            if len(e) == 1:
                print('ERROR(TEMPO CHANGE): ' + file_name + '\n', end='')
                return False

            # if ts_filter:
            allowed_ts = t2e(time_signature_reduce(4, 4))
            if not all(i[6] == allowed_ts for i in e):
                print('ERROR(TSFILT): ' + file_name + '\n', end='')
                return None
            if deduplicate:
                duplicated = False
                dup_file_name = ''
                midi_hash = '0' * 32
                try:
                    midi_hash = get_hash(e)
                except BaseException as e:
                    pass
                lock_set.acquire()
                midi_dict = get_midi_dict()
                if midi_hash in midi_dict:
                    dup_file_name = midi_dict[midi_hash]
                    duplicated = True
                else:
                    midi_dict[midi_hash] = file_name
                lock_set.release()
                if duplicated:
                    print('ERROR(DUPLICATED): ' + midi_hash + ' ' +
                        file_name + ' == ' + dup_file_name + '\n', end='')
                    return None
            output_str_list = []
            sample_step = max(round(sample_len_max / sample_overlap_rate), 1)
            for p in range(0, len(e), sample_step):
                L = p
                R = min(p + sample_len_max, len(e)) - 1
                bar_index_list = [e[i][0]
                                for i in range(L, R + 1) if e[i][0] is not None]
                bar_index_min = 0
                bar_index_max = 0
                if len(bar_index_list) > 0:
                    bar_index_min = min(bar_index_list)
                    bar_index_max = max(bar_index_list)
                    
                # to make bar index start from 0
                bar_index_offset = -bar_index_min
                e_segment = []
                for i in e[L: R + 1]:
                    if i[0] is None or i[0] + bar_index_offset < bar_max:
                        e_segment.append(i)
                    else:
                        break
                tokens_per_note = 8
                output_words = ([('<{}-{}>'.format(j, k if j > 0 else k + bar_index_offset) if k is not None else '<unk>') for i in e_segment for j, k in enumerate(i)])  # tokens_per_note - 1 for append_eos functionality of binarizer in fairseq
                output_str_list.append(' '.join(output_words))

            # no empty
            if not all(len(i.split()) > tokens_per_note * 2 - 1 for i in output_str_list):
                print('ERROR(ENCODE): ' + file_name + '\n', end='')
                return False
            try:
                lock_write.acquire()
                writer(file_name, output_str_list)
            except BaseException as e:
                print('ERROR(WRITE): ' + file_name + ' ' + str(e) + '\n', end='')
                return False
            finally:
                lock_write.release()
            print('SUCCESS: ' + file_name + '\n', end='')
            return True
        except BaseException as e:
            print('ERROR(PROCESS): ' + file_name + ' ' + str(e) + '\n', end='')
            return False
        print('ERROR(GENERAL): ' + file_name + '\n', end='')
        return False
