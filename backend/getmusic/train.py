config = {
    "model": {
        "target": "getmusic.modeling.models.dfm.DFM",
        "params": {
            "diffusion_config": {
                "target": "getmusic.modeling.roformer.diffusion_roformer.DiffusionRFM",
                "params": {
                    "diffusion_step": 100,
                    "alpha_init_type": 'alpha1',
                    "auxiliary_loss_weight": 0.001,
                    "adaptive_auxiliary_loss": True,
                    "roformer_config": {
                        "target": "getmusic.modeling.roformer.roformer_utils.DiffusionRoformerModel",
                        "params": {
                            "vocab_size": 11880,
                            "cond_weight": 0.5,
                        },
                    },
                },
            },
        },
    },
    "solver": {
        "base_lr": 3.0e-6,
        "adjust_lr": "none",
        "max_epochs": 50,
        "save_epochs": 10,
        "validation_epochs": 1,
        "sample_iterations": "epoch",
        "validate_iterations": 1000,
        "print_specific_things": True,
        "ema": {
            "decay": 0.90,
            "update_interval": 100,
            "device": "cpu",
        },
        "clip_grad_norm": {
            "target": "getmusic.engine.clip_grad_norm.ClipGradNorm",
            "params": {
                "start_iteration": 0,
                "end_iteration": 5000,
                "max_norm": 0.5,
            },
        },
        "optimizers_and_schedulers": [
            {
                "name": "none",
                "optimizer": {
                    "target": "torch.optim.AdamW",
                    "step_iteration": 1,
                    "params": {
                        "betas": [0.9, 0.999],
                        "weight_decay": 1.0e-2,
                    },
                },
                "scheduler": {
                    "step_iteration": 1,
                    "target": "getmusic.engine.lr_scheduler.LinearDecayLRWithWarmup",
                    "params": {
                        "min_lr": 1.0e-6,
                        "warmup_lr": 1.0e-4,
                        "warmup": 1000,
                        "T_max": 300000,
                    },
                },
            },
        ],
    },
    "dataloader": {
        "batch_size": 3,
        "num_workers": 28,
        "train_datasets": [
            {
                "target": "getmusic.data.bigdata.BigDataset",
                "params": {
                    "prefix": "train",
                    "path": "/your-data-path",
                    "vocab_size": 11880,
                },
            },
        ],
        "validation_datasets": [
            {
                "target": "getmusic.data.bigdata.BigDataset",
                "params": {
                    "prefix": "valid",
                    "path": "/your-data-path",
                    "vocab_size": 11880,
                },
            },
        ],
    },
}
