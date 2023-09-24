import os
import torch
from getmusic.modeling.build import build_model
from getmusic.utils.misc import merge_opts_to_config
from getmusic.engine.logger import Logger
from getmusic.engine.solver import Solver
import numpy  as np
from .pipeline.args import get_args
from .pipeline.encoding import encoding_to_MIDI
from .pipeline.file import F
from .pipeline.train import config


def main(gpu = False):

    args = get_args()
    
    if gpu:
        torch.cuda.set_device(0)
    args.ngpus_per_node = 1
    args.world_size = 1

    args.local_rank = 0

    args.global_rank = args.local_rank + args.node_rank * args.ngpus_per_node
    args.distributed = args.world_size > 1

    global config
    config = merge_opts_to_config(config, args.opts)

    logger = Logger(args)

    global tokens_to_ids
    global ids_to_tokens
    global empty_index
    global pad_index

    with open(config['solver']['vocab_path'],'r') as f:
        tokens = f.readlines()

        for id, token in enumerate(tokens):
            token, freq = token.strip().split('\t')
            tokens_to_ids[token] = id
            ids_to_tokens.append(token)
        pad_index = tokens_to_ids['<pad>']
        empty_index = len(ids_to_tokens)

    model = build_model(config, args)

    dataloader_info = None

    solver = Solver(gpu=gpu, config=config, args=args, model=model, dataloader=dataloader_info, logger=logger, is_sample=True)

    assert args.load_path is not None
    solver.resume(path=args.load_path)

    for file_name in [args.file_path]: #!PS
        conditional_track = np.array([False, False, False, False, False, False, True])
        conditional_name = input('Select condition tracks (\'b\' for bass, \'d\' for drums, \'g\' for guitar, \'l\' for lead, \'p\' for piano, \'s\' for strings, \'c\' for chords; multiple choices; input any other key to skip):')
        condition_inst = []
        if 'l' in conditional_name:
            conditional_track[0] = True
            condition_inst.append('80')
        if 'b' in conditional_name:
            conditional_track[1] = True
            condition_inst.append('32')
        if 'd' in conditional_name:
            conditional_track[2] = True
        if 'g' in conditional_name:
            conditional_track[3] = True
            condition_inst.append('25')
        if 'p' in conditional_name:
            conditional_track[4] = True
            condition_inst.append('0')
        if 's' in conditional_name:
            conditional_track[5] = True
            condition_inst.append('48')
        # if 'c' in conditional_name:
        #     conditional_track[6] = True
        
        if all(conditional_track):
            print('You can\'t set all tracks as condition. We conduct uncontional generation based on selected content tracks. If you skip content tracks, this song is skipped.')
            
        content_track = np.array([False, False, False, False, False, False, False])
        content_name = input('Select content tracks (\'b\' for bass, \'d\' for drums, \'g\' for guitar, \'l\' for lead, \'p\' for piano, \'s\' for strings; multiple choices):')
        if 'l' in content_name:
            content_track[0] = True
        if 'b' in content_name:
            content_track[1] = True
        if 'd' in content_name:
            content_track[2] = True
        if 'g' in content_name:
            content_track[3] = True
        if 'p' in content_name:
            content_track[4] = True
        if 's' in content_name:
            content_track[5] = True

        if all(conditional_track):
            print('You can\'t set all tracks as condition. We conduct uncontional generation based on selected content tracks.')
            conditional_track = np.array([False, False, False, False, False, False, False])
            if not any(content_track):
                print('No content tracks is selected. skip this song')
                continue

        x, tempo, not_empty_pos, condition_pos, pitch_shift, tpc, have_cond = F("track_generation.py", file_name, conditional_track, content_track, condition_inst, args.chord_from_single)

        if not have_cond:
            print('chord error')
            continue

        oct_line = solver.infer_sample(x, tempo, not_empty_pos, condition_pos, use_ema=args.no_ema)
        
        data = oct_line.split(' ')

        oct_final_list = []
        for start in range(3, len(data),8):
            if 'pad' not in data[start] and 'pad' not in data[start+1]:
                pitch = int(data[start][:-1].split('-')[1])
                if data[start-1] != '<2-129>' and data[start-1] != '<2-128>':
                    pitch -= pitch_shift
                data[start] = '<3-{}>'.format(pitch) # re-normalize            
                oct_final_list.append(' '.join(data[start-3:start+5]))
        
        oct_final = ' '.join(oct_final_list)
        midi_obj = encoding_to_MIDI(oct_final, tpc, args.decode_chord)
        save_path = os.path.join(os.path.splitext(args.file_path)[0]  + '{}2{}'.format(conditional_name, content_name) + ".mid")
        midi_obj.dump(save_path)    
        return save_path


if __name__ == '__main__':
    main()
