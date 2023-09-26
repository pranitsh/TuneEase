import os
import torch
import numpy as np
from .getmusic.modeling.build import build_model
from .getmusic.utils.misc import merge_opts_to_config
from .getmusic.engine.logger import Logger
from .getmusic.engine.solver import Solver
from .pipeline.args import get_args
from .pipeline.encoding import encoding_to_MIDI
from .pipeline.file import F
from .pipeline.config import Config

def main(input_args = None, gpu = False):
    args = get_args(input_args)
    if gpu:
        torch.cuda.set_device(0)
    args.ngpus_per_node = 1
    args.world_size = 1
    args.local_rank = 0
    args.global_rank = args.local_rank + args.node_rank * args.ngpus_per_node
    args.distributed = args.world_size > 1
    config = Config().config
    config = merge_opts_to_config(config, args.opts)
    logger = Logger(args)
    model = build_model(config, args)
    dataloader_info = None
    solver = Solver(gpu=gpu, config=config, args=args, model=model, dataloader=dataloader_info, logger=logger, is_sample=True)
    assert args.load_path is not None
    solver.resume(path=args.load_path)
    conditional_track = np.array([False, False, False, False, False, False, True])
    conditional_name = args.conditional_tracks
    condition_inst = []
    if conditional_name[0] == "1":
        conditional_track[0] = True
        condition_inst.append('80')
    if conditional_name[1] == "1":
        conditional_track[1] = True
        condition_inst.append('32')
    if conditional_name[2] == "1":
        conditional_track[2] = True
    if conditional_name[3] == "1":
        conditional_track[3] = True
        condition_inst.append('25')
    if conditional_name[4] == "1":
        conditional_track[4] = True
        condition_inst.append('0')
    if conditional_name[5] == "1":
        conditional_track[5] = True
        condition_inst.append('48')
    # if 'c' in conditional_name:
    #     conditional_track[6] = True
    
    if all(conditional_track):
        print('You can\'t set all tracks as condition. We conduct uncontional generation based on selected content tracks. If you skip content tracks, this song is skipped.')
    content_track = np.array([False, False, False, False, False, False, False])
    content_name = args.content_tracks
    if content_name[0] == "1":
        content_track[0] = True
    if content_name[1] == "1":
        content_track[1] = True
    if content_name[2] == "1":
        content_track[2] = True
    if content_name[3] == "1":
        content_track[3] = True
    if content_name[4] == "1":
        content_track[4] = True
    if content_name[5] == "1":
        content_track[5] = True
    x, tempo, not_empty_pos, condition_pos, pitch_shift, tpc, have_cond = F("track_generation.py", args.file_path, conditional_track, content_track, condition_inst, args.chord_from_single)
    if not have_cond:
        print('chord error')
        return ""
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
    midi_obj = encoding_to_MIDI("track_generation.py", oct_final, tpc, args.decode_chord)
    save_path = os.path.join(os.path.splitext(args.file_path)[0]  + '{}2{}'.format(conditional_name, content_name) + ".mid")
    midi_obj.dump(save_path)    
    return save_path

if __name__ == '__main__':
    main()
