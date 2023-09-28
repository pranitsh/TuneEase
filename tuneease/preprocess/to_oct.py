# Copyright (c) Microsoft Corporation. All rights reserved.
# Licensed under the MIT License.
#

from multiprocessing import Pool
import os
import sys
from ..getmusic.utils.midi_config import BAR_MAX, MAX_NOTES_PER_BAR, BEAT_NOTE_FACTOR, POS_RESOLUTION, MAX_INST, MAX_PITCH, DURATION_MAX, MAX_TEMPO, MAX_VELOCITY, SAMPLE_LEN_MAX, POOL_NUM
from ..pipeline.encoding_helpers import TS, v2e, b2e
from ..pipeline.file import F
sys.path.append('/'.join(os.path.abspath(__file__).split('/')[:-2]))

data_zip = None
# (0 Measure, 1 Pos, 2 Program, 3 Pitch, 4 Duration, 5 Velocity, 6 TimeSig, 7 Tempo)
# (Measure, TimeSig)
# (Pos, Tempo)
# Percussion: Program=128 Pitch=[128,255]
def gen_dictionary(file_name):
    ts = TS()
    num = 0
    with open(file_name, 'w') as f:
        for j in range(BAR_MAX):
            print('<0-{}>'.format(j), num, file=f)
        for j in range(BEAT_NOTE_FACTOR * MAX_NOTES_PER_BAR * POS_RESOLUTION):
            print('<1-{}>'.format(j), num, file=f)
        for j in range(MAX_INST + 1 + 1):
            # max_inst + 1 for percussion
            print('<2-{}>'.format(j), num, file=f)
        for j in range(2 * MAX_PITCH + 1 + 1):
            # max_pitch + 1 ~ 2 * max_pitch + 1 for percussion
            print('<3-{}>'.format(j), num, file=f)
        for j in range(DURATION_MAX * POS_RESOLUTION):
            print('<4-{}>'.format(j), num, file=f)
        for j in range(v2e(MAX_VELOCITY) + 1):
            print('<5-{}>'.format(j), num, file=f)
        for j in range(len(ts.ts_list)):
            print('<6-{}>'.format(j), num, file=f)
        for j in range(b2e(MAX_TEMPO) + 1):
            print('<7-{}>'.format(j), num, file=f)

def G(file_name):
    try:
        return F("to_oct.py", file_name)
    except BaseException as e:
        print('ERROR(UNCAUGHT): ' + file_name + '\n', end='')
        return False

def str_to_encoding(s):
    encoding = [int(i[3: -1]) for i in s.split() if 's' not in i]
    tokens_per_note = 8
    assert len(encoding) % tokens_per_note == 0
    encoding = [tuple(encoding[i + j] for j in range(tokens_per_note))
                for i in range(0, len(encoding), tokens_per_note)]
    return encoding

def encoding_to_str(e):
    bar_index_offset = 0
    p = 0
    tokens_per_note = 8
    return ' '.join((['<{}-{}>'.format(j, k if j > 0 else k + bar_index_offset) for i in e[p: p +\
                SAMPLE_LEN_MAX] if i[0] + bar_index_offset < BAR_MAX for j, k in enumerate(i)]))   # 8 - 1 for append_eos functionality of binarizer in fairseq

if __name__ == '__main__':
    data_path = sys.argv[1]
    prefix = sys.argv[2]
    if os.path.exists(prefix):
        print('Output path {} already exists! Please delete existing files'.format(prefix))
        sys.exit(0)
    os.system('mkdir -p {}'.format(prefix))
    file_list = []
    for (dirpath, dirnames, filenames) in os.walk(data_path):
        for filename in filenames:
            if filename.endswith('.mid'): 
                file_list.append(os.path.join(dirpath, filename))
    file_list.sort()
    # random.shuffle(file_list)
    # gen_dictionary('{}/dict.txt'.format(prefix))
    ok_cnt = 0
    all_cnt = 0
    total_file_cnt = len(file_list)
    file_list_split = file_list
    output_file = '{}/oct.txt'.format(prefix)
    with Pool(POOL_NUM) as p:
        result = list(p.imap_unordered(G, file_list_split))
        all_cnt += sum((1 if i is not None else 0 for i in result))
        ok_cnt += sum((1 if i is True else 0 for i in result))
    output_file = None
    print('{}/{} ({:.2f}%) MIDI files successfully processed'.format(ok_cnt,
                                                                     all_cnt, ok_cnt / all_cnt * 100))
