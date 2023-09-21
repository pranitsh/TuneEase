import os
import time
import math
import torch
# from torch.nn.utils import clip_grad_norm_, clip_grad_norm
from getmusic.utils.misc import instantiate_from_config, format_seconds
from getmusic.distributed.distributed import reduce_dict
from getmusic.distributed.distributed import is_primary
from getmusic.utils.misc import get_model_parameters_info
from getmusic.engine.ema import EMA
# from torch.optim.lr_scheduler import CosineAnnealingLR
import getmusic.utils.midi_config as mc

try:
    from torch.cuda.amp import autocast, GradScaler
    AMP = True
except:
    print('Warning: import torch.amp failed, so no amp will be used!')
    AMP = False


root_dict = {'C': 0, 'C#': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
kind_dict = {'null': 0, 'm': 1, '+': 2, 'dim': 3, 'seven': 4, 'maj7': 5, 'm7': 6, 'm7b5': 7}

class Solver(object):
    def __init__(self, config, args, model, dataloader, logger, is_sample=False):
        self.config = config
        self.args = args
        self.model = model 
        self.dataloader = dataloader
        self.logger = logger #!PS
        if not is_sample:
            self.ckpt_dir = os.path.join(args.save_dir, 'checkpoint')
            self.oct_dir = os.path.join(args.save_dir, 'oct')
            os.makedirs(self.ckpt_dir, exist_ok=True)
            os.makedirs(self.oct_dir, exist_ok=True)

        self.ids_to_tokens = []
        with open(config['solver']['vocab_path'],'r') as f:
            tokens = f.readlines()
            for idx, token in enumerate(tokens):
                token, freq = token.strip().split('\t')
                self.ids_to_tokens.append(token)

            self.logger.log_info('Load dictionary: {} tokens.'.format(len(self.ids_to_tokens)))

        beat_note_factor =mc.beat_note_factor
        max_notes_per_bar = mc.max_notes_per_bar
        pos_resolution = mc.pos_resolution
        bar_max = mc.bar_max
        self.pos_in_bar = beat_note_factor * max_notes_per_bar * pos_resolution
        self.pad_index = mc.duration_max * mc.pos_resolution - 1
        self.figure_size = mc.bar_max * mc.beat_note_factor * mc.max_notes_per_bar * mc.pos_resolution
        #!PS
        adjust_lr = config['solver'].get('adjust_lr', 'sqrt')
        base_lr = config['solver'].get('base_lr', 1.0e-4)

        if adjust_lr == 'none':
            self.lr = base_lr
        elif adjust_lr == 'sqrt': 
            self.lr = base_lr * math.sqrt(args.world_size * config['dataloader']['batch_size'])
        elif adjust_lr == 'linear':
            self.lr = base_lr * args.world_size * config['dataloader']['batch_size']
        else:
            raise NotImplementedError('Unknown type of adjust lr {}!'.format(adjust_lr))
        self.logger.log_info('Get lr {} from base lr {} with {}'.format(self.lr, base_lr, adjust_lr))

        #!PS
        if 'ema' in config['solver'] and args.local_rank == 0:
            ema_args = config['solver']['ema']
            ema_args['model'] = self.model
            self.ema = EMA(**ema_args)
        else:
            self.ema = None

        self.logger.log_info(str(get_model_parameters_info(self.model)))

        self.model.to(torch.device("cpu"))
        
        self.device = self.args.local_rank
        print('self.device ',self.device)

        if self.args.distributed:
            self.logger.log_info('Distributed, begin DDP the model...')
            self.model = torch.nn.parallel.DistributedDataParallel(self.model, device_ids=[self.args.local_rank], find_unused_parameters=False) # 
            self.model = self.model.to(torch.device("cpu"))
            self.logger.log_info('Distributed, DDP model done!')
        
        self.args.amp = self.args.amp and AMP
        if self.args.amp:
            self.scaler = GradScaler()
            self.logger.log_info('Using AMP for training!')
        self.batch_size = self.config['dataloader']['batch_size']
        self.logger.log_info("{}: global rank {}: prepare solver done!".format(self.args.name, self.args.global_rank), check_primary=False)
        print(self.model)

    def resume(self, 
               path=None, 
               load_others=False
               ):
        if path is None:
            path = os.path.join(self.ckpt_dir, 'last.pth')

        if os.path.exists(path):
            # state_dict = torch.load(path, map_location='cuda:{}'.format(self.args.local_rank))
            print("1")
            state_dict = torch.load(path, map_location='cpu')
            print('2')
            if load_others:
                self.last_epoch = state_dict['last_epoch']
                self.last_iter = state_dict['last_iter']
            
            if isinstance(self.model, torch.nn.parallel.DistributedDataParallel):
                try:
                    self.model.module.load_state_dict(state_dict['model'])
                except:
                    model_dict = self.model.module.state_dict()
                    temp_state_dict = {k:v for k,v in state_dict['model'].items() if k in model_dict.keys()}
                    model_dict.update(temp_state_dict)
                    self.model.module.load_state_dict(model_dict)
            else:
                self.model.load_state_dict(state_dict['model'])

            if 'ema' in state_dict and self.ema is not None:
                try:
                    self.ema.load_state_dict(state_dict['ema'])
                except:
                    model_dict = self.ema.state_dict()
                    temp_state_dict = {k:v for k,v in state_dict['ema'].items() if k in model_dict.keys()}
                    model_dict.update(temp_state_dict)
                    self.ema.load_state_dict(model_dict)

            self.logger.log_info('Resume from {}'.format(path))
        else:
            raise ValueError('checkpoint not found')
    

    def validate_epoch(self):
        if self.logger is not None:
            self.logger.log_info("Enter validate_epoch")
            
        if 'validation_loader' not in self.dataloader:
            val = False
        else:
            if isinstance(self.validation_epochs, int):
                val = (self.last_epoch + 1) % self.validation_epochs == 0
            else:
                val = (self.last_epoch + 1) in self.validation_epochs        
        
        if val:
            if self.args.distributed:
                self.dataloader['validation_loader'].sampler.set_epoch(self.last_epoch)
            self.model.eval()
            overall_loss = None
            epoch_start = time.time()
            itr_start = time.time()
            itr = -1
            for itr, batch in enumerate(self.dataloader['validation_loader']):
                data_time = time.time() - itr_start
                step_start = time.time()
                loss = self.step(batch, phase='val')
                
                for loss_n, loss_dict in loss.items():
                    loss[loss_n] = reduce_dict(loss_dict)
                if overall_loss is None:
                    overall_loss = loss
                else:
                    for loss_n, loss_dict in loss.items():
                        for k, v in loss_dict.items():
                            overall_loss[loss_n][k] = (overall_loss[loss_n][k] * itr + loss[loss_n][k]) / (itr + 1)
                
                if self.logger is not None and (itr+1) % self.args.log_frequency == 0:
                    info = '{}: val'.format(self.args.name) 
                    info = info + ': Epoch {}/{} | iter {}/{}'.format(self.last_epoch, self.max_epochs, itr, self.dataloader['validation_iterations'])
                    for loss_n, loss_dict in loss.items():
                        info += ' ||'
                        info += '' if loss_n == 'none' else ' {}'.format(loss_n)
                        
                        for k in loss_dict:
                            info += ' | {}: {:.4f}'.format(k, float(loss_dict[k]))
                        
                    itr_time_avg = (time.time() - epoch_start) / (itr + 1)
                    info += ' || data_time: {dt}s | fbward_time: {fbt}s | iter_time: {it}s | epoch_time: {et} | left_time: {lt}'.format(
                            dt=round(data_time, 1),
                            fbt=round(time.time() - step_start, 1),
                            it=round(time.time() - itr_start, 1),
                            et=format_seconds(time.time() - epoch_start),
                            lt=format_seconds(itr_time_avg*(self.dataloader['train_iterations']-itr-1))
                            )

                    self.logger.log_info(info)
                itr_start = time.time()
                
            assert itr >= 0, "The data is too less to form one iteration!"
            self.dataloader['validation_iterations'] = itr + 1

            if self.logger is not None:
                
                info = '{}: val'.format(self.args.name) 
                for loss_n, loss_dict in overall_loss.items():
                    info += '' if loss_n == 'none' else ' {}'.format(loss_n)
                    info += ': Epoch {}/{}'.format(self.last_epoch, self.max_epochs)
                    for k in loss_dict:
                        info += ' | {}: {:.4f}'.format(k, float(loss_dict[k]))
                        self.logger.add_scalar(tag='val/{}/{}'.format(loss_n, k), scalar_value=float(loss_dict[k]), global_step=self.last_epoch)
                self.logger.log_info(info)

    def validate(self):
        self.validation_epoch()

    def infer_sample(self, x, tempo, not_empty_pos, condition_pos, use_ema=True, skip_step=0):
        self.model.eval()
        tic = time.time()
        
        if use_ema and self.ema is not None:
            print('use ema parameters')
            self.ema.modify_to_inference()

        model = self.model

        with torch.no_grad(): 
            x = x.cpu()
            tempo = tempo.cpu()
            not_empty_pos = not_empty_pos.cpu()
            condition_pos = condition_pos.cpu()
            assert x.size()[0] == 1
            ts = 6

            samples = model.infer_sample(x, tempo, not_empty_pos, condition_pos, skip_step=skip_step)

            print('sampling, the song has {} time units'.format(samples.size()[-1]))

            datum = samples[0]
            
            
            encoding = []
            for t in range(samples.size()[-1]):
                bar = t // self.pos_in_bar
                pos = t % self.pos_in_bar
                main_pitch = datum[0][t].item()
                main_dur = datum[1][t].item()
                assert (main_dur <= self.pad_index) and (main_pitch >= self.pad_index), 'pitch index is {} and dur index is {}'.format(main_pitch, main_dur)
                if (main_pitch != self.pad_index) and (main_dur < self.pad_index):
                    p = self.ids_to_tokens[main_pitch]
                    if p[0] == 'M':
                        p = p[1:]
                        encoding.append((bar,pos,80,p,self.ids_to_tokens[main_dur][1:],28,ts,tempo))
                    else:
                        print('out m')

                bass_pitch = datum[2][t].item()
                bass_dur = datum[3][t].item()
                assert bass_dur <= self.pad_index and bass_pitch >= self.pad_index, "{}, {}".format(bass_dur, bass_pitch)
                if (bass_pitch != self.pad_index) and (bass_dur < self.pad_index):
                    pitch = self.ids_to_tokens[bass_pitch]
                    dur = self.ids_to_tokens[bass_dur]
                    if pitch[0] == 'B':
                        pitch = pitch[1:].split(' ')
                        for p in pitch:
                            encoding.append((bar,pos,32,p,dur[1:],24,ts,tempo))
                    else:
                        print('out b')
                        
                drums_pitch = datum[4][t].item() # 128
                drums_dur = datum[5][t].item()
                assert drums_dur <= self.pad_index and drums_pitch >= self.pad_index, "{}, {}".format(drums_dur, drums_pitch)
                if (drums_pitch != self.pad_index) and (drums_dur < self.pad_index):
                    pitch = self.ids_to_tokens[drums_pitch]
                    dur = self.ids_to_tokens[drums_dur]
                    if pitch[0] == 'D':
                        pitch = pitch[1:].split(' ')
                        for p in pitch:
                            encoding.append((bar,pos,128,p,dur[1:],24,ts,tempo))
                    else:
                        print('out d')
                        
                guitar_pitch = datum[6][t].item() # 25
                guitar_dur = datum[7][t].item()
                assert guitar_dur <= self.pad_index and guitar_pitch >= self.pad_index, "{}, {}".format(guitar_dur, guitar_pitch)
                if (guitar_pitch != self.pad_index) and (guitar_dur < self.pad_index):
                    pitch = self.ids_to_tokens[guitar_pitch]
                    dur = self.ids_to_tokens[guitar_dur]
                    if pitch[0] == 'G':
                        pitch = pitch[1:].split(' ')
                        for p in pitch:
                            encoding.append((bar,pos,25,p,dur[1:],20,ts,tempo))
                    else:
                        print('out g')
                            
                piano_pitch = datum[8][t].item()
                piano_dur = datum[9][t].item()
                assert piano_dur <= self.pad_index and piano_pitch >= self.pad_index, "{}, {}".format(piano_dur, piano_pitch)
                if (piano_pitch != self.pad_index) and (piano_dur < self.pad_index):
                    pitch = self.ids_to_tokens[piano_pitch]
                    dur = self.ids_to_tokens[piano_dur]
                    if pitch[0] == 'P':
                        pitch = pitch[1:].split(' ')
                        for p in pitch:
                            encoding.append((bar,pos,0,p,dur[1:],24,ts,tempo))
                    else:
                        print('out p')
                            
                string_pitch = datum[10][t].item() # 48
                string_dur = datum[11][t].item()
                assert string_dur <= self.pad_index and string_pitch >= self.pad_index, 'p:{},d:{}'.format(string_pitch,string_dur)
                if (string_pitch != self.pad_index) and (string_dur < self.pad_index):
                    pitch = self.ids_to_tokens[string_pitch]
                    dur = self.ids_to_tokens[string_dur]
                    if pitch[0] == 'S':
                        pitch = pitch[1:].split(' ')
                        for p in pitch:
                            encoding.append((bar,pos,48,p,dur[1:],12,ts,tempo))
                    else:
                        print('out s')
                        
                # just for chord debug
                root_id = datum[12][t].item()
                kind_id = datum[13][t].item()
                if self.ids_to_tokens[root_id] in root_dict and self.ids_to_tokens[kind_id] in kind_dict:
                    root = root_dict[self.ids_to_tokens[root_id]]
                    kind = kind_dict[self.ids_to_tokens[kind_id]]
                    encoding.append((bar,pos,129,root,kind,1,ts,tempo))
                   
        encoding.sort()
        oct_line = ['<0-{}> <1-{}> <2-{}> <3-{}> <4-{}> <5-{}> <6-{}> <7-{}>'.format(e[0],e[1],e[2],e[3],e[4],e[5],e[6],e[7]) for e in encoding]
        
        if use_ema and self.ema is not None:
            self.ema.modify_to_train()

        return ' '.join(oct_line)
