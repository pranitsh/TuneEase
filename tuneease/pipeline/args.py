import os
import datetime
import argparse
import numpy as np
from .compute import Node
from ..getmusic.utils.misc import seed_everything
from ..pathutility import PathUtility


def validate_binary_string(arg):
    if not arg.isdigit() or len(arg) != 7:
        raise argparse.ArgumentTypeError(
            "Binary string must be 7 characters long and consist of 0s and 1s only."
        )
    return arg


def get_args(input_args):
    node = Node()
    parser = argparse.ArgumentParser(description="PyTorch Training script")
    pathutil = PathUtility()
    if not pathutil.checkpoint_path():
        raise FileNotFoundError("Could not find the checkpoint.pth")
    # Contains additional args as necessary
    common_args = [
        ("--config_file", str, "configs/train.yaml", "path of config file"),
        (
            "--name",
            str,
            "inference_cache",
            "the name of this experiment, if not provided, set to the name of config file",
        ),
        ("--output", str, "cache", "directory to save the results"),
        ("--log_frequency", int, 10, "print frequency"),
        (
            "--load_path",
            str,
            pathutil.checkpoint_path(),
            "path to model that need to be loaded used for loading pretrained model",
        ),
        ("--resume_name", str, None, "resume one experiment with the given name"),
        ("--auto_resume", bool, False, "resume the training"),
        ("--num_node", int, node.NUM_NODE, "number of nodes for distributed training"),
        ("--ngpus_per_node", int, 8, "number of gpu on one node"),
        ("--node_rank", int, node.NODE_RANK, "node rank for distributed training"),
        ("--dist_url", str, node.DIST_URL, "url used to set up distributed training"),
        (
            "--gpu",
            int,
            0,
            "GPU id to use. If given, only the specific gpu will be used, and ddp will be disabled",
        ),
        ("--local_rank", int, -1, "node rank for distributed training"),
        ("--sync_bn", bool, False, "use sync BN layer"),
        ("--tensorboard", bool, False, "use tensorboard for logging"),
        ("--timestamp", bool, False, "use tensorboard for logging"),
        ("--seed", int, 0, "seed for initializing training"),
        ("--cudnn_deterministic", bool, False, "set cudnn.deterministic True"),
        ("--amp", bool, False, "automatic mixture of precesion"),
        (
            "--conditional_name",
            str,
            None,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--content_name",
            str,
            None,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--conditional_tracks",
            validate_binary_string,
            "0000000",
            "the content tracks to base the generation on",
        ),
        (
            "--content_tracks",
            validate_binary_string,
            "0000110",
            "the tracks to generate",
        ),
        ("--debug", bool, False, "set as debug mode"),
        (
            "--do_sample",
            bool,
            True,
            "I'm not sure what this does. Send a pull request please!",
        ),
        ("--file_path", str, None, "the output filepath"),
        (
            "--skip_step",
            int,
            0,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--decode_chord",
            bool,
            False,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--chord_from_single",
            bool,
            False,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--no_ema",
            bool,
            True,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--no_load_optimizer_and_scheduler",
            bool,
            True,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--no_load_others",
            bool,
            True,
            "I'm not sure what this does. Send a pull request please!",
        ),
        (
            "--training_model",
            bool,
            False,
            "If you are training the model, this changes the output directory to 'OUTPUT.'",
        ),
        ("--use_gpu", int, 0, "Whether to use GPU or not. False for CPU."),
    ]
    for arg, arg_type, default_val, help in common_args:
        parser.add_argument(arg, type=arg_type, default=default_val, help=help)
    parser.add_argument(
        "opts",
        help="Modify config options using the command-line",
        default=None,
        nargs=argparse.REMAINDER,
    )
    if input_args == None:
        args = parser.parse_args()
    else:
        args = parser.parse_args(input_args)
    args.cwd = os.path.abspath(os.path.dirname(__file__))
    # Common to all Args
    seed_everything(args.seed, args.cudnn_deterministic)
    # Modified logic to work with all args
    if args.resume_name is not None:
        args.name = args.resume_name
        args.config_file = os.path.join(
            args.output, args.resume_name, "configs", "config.yaml"
        )
        args.auto_resume = True
    else:
        if args.name == "":
            args.name = os.path.basename(args.config_file).replace(".yaml", "")
        if args.timestamp:
            assert (
                not args.auto_resume
            ), "for timstamp, auto resume is hard to find the save directory"
            time_str = datetime.datetime.now().strftime("%Y-%m-%d-%H-%M")
            args.name = time_str + "-" + args.name
    if args.debug:
        args.name = "debug"
        if args.gpu is None:
            args.gpu = 0
    if args.training_model:
        args.output = "OUTPUT"
    # Common to all args
    random_seconds_shift = datetime.timedelta(seconds=np.random.randint(60))
    now = (datetime.datetime.now() - random_seconds_shift).strftime("%Y-%m-%dT%H-%M-%S")
    args.save_dir = os.path.join(args.output, args.name, now)
    args.use_gpu = bool(int(args.use_gpu))
    return args
