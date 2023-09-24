import numpy as np
import pickle
from ..getmusic.utils.midi_config import beat_note_factor, max_notes_per_bar, pos_resolution
from getmusic.utils.magenta_chord_recognition import _key_chord_distribution, _key_chord_transition_distribution

tokens_to_ids = {}
ids_to_tokens = []
pad_index = None
empty_index = None

pos_in_bar = beat_note_factor * max_notes_per_bar * pos_resolution

key_profile = pickle.load(open('getmusic/utils/key_profile.pickle', 'rb'))

chord_pitch_out_of_key_prob = 0.01
key_change_prob = 0.001
chord_change_prob = 0.5
key_chord_distribution = _key_chord_distribution(
    chord_pitch_out_of_key_prob=chord_pitch_out_of_key_prob)
key_chord_loglik = np.log(key_chord_distribution)
key_chord_transition_distribution = _key_chord_transition_distribution(
    key_chord_distribution,
    key_change_prob=key_change_prob,
    chord_change_prob=chord_change_prob)
key_chord_transition_loglik = np.log(key_chord_transition_distribution)
