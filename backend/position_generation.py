import os
import warnings
import torch
from getmusic.modeling.build import build_model
from getmusic.utils.misc import merge_opts_to_config, modify_config_for_debug
from .pipeline.train import config
from getmusic.engine.logger import Logger
from getmusic.engine.solver import Solver
from getmusic.distributed.launch import launch
from .pipeline.args import get_args
from .pipeline.encoding import encoding_to_MIDI
from .pipeline.file import F


def main_worker(local_rank, args):

    args.local_rank = local_rank

    args.global_rank = args.local_rank + args.node_rank * args.ngpus_per_node
    args.distributed = args.world_size > 1

    global config
    config = merge_opts_to_config(config, args.opts)
    if args.debug:
        config = modify_config_for_debug(config)

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

    if args.sync_bn:
        model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)

    dataloader_info = None

    solver = Solver(config=config, args=args, model=model, dataloader=dataloader_info, logger=logger, is_sample=True)

    assert args.load_path is not None
    solver.resume(path=args.load_path)

    file_list = [os.path.join(args.file_path, n) for n in os.listdir(args.file_path) if (n[-4:].lower() == '.mid' or n[-5:].lower() == '.midi') and ('iter' not in n.lower())]
    file_list.sort()

    for file_name in file_list:
        print(file_name)

        if '.pth' in file_name:
            continue
        y = input('skip?')
        if 'y' in y:
            continue

        x, tempo, not_empty_pos, condition_pos, pitch_shift, tpc = F("position_generation.py", file_name)

        oct_line = solver.infer_sample(x, tempo, not_empty_pos, condition_pos, use_ema=args.no_ema, skip_step=args.skip_step)
        
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

        midi_obj = encoding_to_MIDI("position_generation.py", oct_final, tpc, args.decode_chord)

        save_path = os.path.join(args.file_path, 'position-{}'.format(file_name.split('/')[-1]))

        midi_obj.dump(save_path)    

def main():
    args = get_args()

    if args.gpu is not None:
        warnings.warn('You have chosen a specific GPU. This will completely disable ddp.')
        torch.cuda.set_device(args.gpu)
        args.ngpus_per_node = 1
        args.world_size = 1
    else:
        print('args.num_node ', args.num_node)
        if args.num_node == 1:
            args.dist_url == "auto"
        else:
            assert args.num_node > 1
       
        args.ngpus_per_node = torch.cuda.device_count()
        args.world_size = args.ngpus_per_node * args.num_node # 
    
    launch(main_worker, args.ngpus_per_node, args.num_node, args.node_rank, args.dist_url, args=(args,))


if __name__ == '__main__':
    main()
