import os
import datetime
import argparse
import numpy as np
from .compute import NUM_NODE, NODE_RANK, DIST_URL
from ..getmusic.utils.misc import seed_everything


def get_args():
    parser = argparse.ArgumentParser(description='PyTorch Training script')
    # Contains additional args as necessary
    common_args = [
        ('--config_file', str, 'configs/train.yaml', 'path of config file'),
        ('--name', str, 'inference_cache', 'the name of this experiment, if not provided, set to the name of config file'),
        ('--output', str, 'cache', 'directory to save the results'),
        ('--log_frequency', int, 10, 'print frequency'),
        ('--load_path', str, '/backend/getmusic/checkpoint.pth', 'path to model that need to be loaded used for loading pretrained model'),
        ('--resume_name', str, None, 'resume one experiment with the given name'),
        ('--auto_resume', bool, False, 'resume the training'),
        ('--num_node', int, NUM_NODE, 'number of nodes for distributed training'),
        ('--ngpus_per_node', int, 8, 'number of gpu on one node'),
        ('--node_rank', int, NODE_RANK, 'node rank for distributed training'),
        ('--dist_url', str, DIST_URL, 'url used to set up distributed training'),
        ('--gpu', int, 0, 'GPU id to use. If given, only the specific gpu will be used, and ddp will be disabled'),
        ('--local_rank', int, -1, 'node rank for distributed training'),
        ('--sync_bn', bool, False, 'use sync BN layer'),
        ('--tensorboard', bool, False, 'use tensorboard for logging'),
        ('--timestamp', bool, False, 'use tensorboard for logging'),
        ('--seed', int, 0, 'seed for initializing training'),
        ('--cudnn_deterministic', bool, False, 'set cudnn.deterministic True'),
        ('--amp', bool, False, 'automatic mixture of precesion'),
        ('--conditional_name', str, None),
        ('--content_name', str, None),
        ('--debug', bool, False, 'set as debug mode'),
        ('--do_sample', bool, True),
        ('--file_path', str, None, "the output filepath"),
        ('--skip_step', int, 0),
        ('--decode_chord', bool, False),
        ('--chord_from_single', bool, False),
        ('--no_ema', bool, True)
        ('--no_load_optimizer_and_scheduler', bool, True),
        ('--no_load_others', bool, True)
        ('--training_model', bool, False, "If you are training the model, this changes the output directory to 'OUTPUT'")
    ]
    for arg, arg_type, default_val, help in common_args:
        parser.add_argument(arg, type=arg_type, default=default_val, help=help)
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    args = parser.parse_args()
    args.cwd = os.path.abspath(os.path.dirname(__file__))
    # Common to all Args
    seed_everything(args.seed, args.cudnn_deterministic)
    # Modified logic to work with all args
    if args.resume_name is not None:
        args.name = args.resume_name
        args.config_file = os.path.join(args.output, args.resume_name, 'configs', 'config.yaml')
        args.auto_resume = True
    else:
        if args.name == '':
            args.name = os.path.basename(args.config_file).replace('.yaml', '')
        if args.timestamp:
            assert not args.auto_resume, "for timstamp, auto resume is hard to find the save directory"
            time_str = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M')
            args.name = time_str + '-' + args.name
    if args.debug:
        args.name = 'debug'
        if args.gpu is None:
            args.gpu = 0
    if args.training_model:
        args.output = "OUTPUT"
    # Common to all args
    random_seconds_shift = datetime.timedelta(seconds=np.random.randint(60))
    now = (datetime.datetime.now() - random_seconds_shift).strftime('%Y-%m-%dT%H-%M-%S')
    args.save_dir = os.path.join(args.output, args.name, now)
    return args