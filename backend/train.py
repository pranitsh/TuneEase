import warnings
import torch
from getmusic.modeling.build import build_model
from getmusic.data.build import build_dataloader
from getmusic.utils.misc import merge_opts_to_config, modify_config_for_debug
from getmusic.engine.logger import Logger
from getmusic.engine.solver import Solver
from getmusic.distributed.launch import launch
from .pipeline.args import get_args
from .pipeline.train import config

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


def main_worker(local_rank, args):
    args.local_rank = local_rank
    args.global_rank = args.local_rank + args.node_rank * args.ngpus_per_node
    args.distributed = args.world_size > 1
    print(args)
    global config
    config = merge_opts_to_config(config, args.opts)
    if args.debug:
        config = modify_config_for_debug(config)
    
    logger = Logger(args)
    logger.save_config(config)

    model = build_model(config, args)

    if args.sync_bn:
        model = torch.nn.SyncBatchNorm.convert_sync_batchnorm(model)

    dataloader_info = build_dataloader(config, args)

    solver = Solver(config=config, args=args, model=model, dataloader=dataloader_info, logger=logger)

    if args.load_path is not None: 
        solver.resume(path=args.load_path, load_optimizer_and_scheduler=args.no_load_optimizer_and_scheduler, load_others=args.no_load_others)
    if args.auto_resume:
        solver.resume()
    solver.train()

if __name__ == '__main__':
    main()
