import numpy as np
import os
import pickle
from ..getmusic.utils.magenta_chord_recognition import Magenta
from ..pipeline.config import Config

class TokenHelper:
    """
    Initialize a TokenHelper instance.

    This constructor method updates the class-level instance variables based on a vocabulary file specified config class.

    Args:
        None

    Returns:
        None
    """
    tokens_to_ids = {}
    ids_to_tokens = []
    pad_index = None
    empty_index = None

    def __init__(self) -> None:
        self.updateClass(TokenHelper)
        
    @staticmethod
    def updateClass(cls):
        """
        Update class-level instance variables with token information.
        
        Args:
            cls (class): The class instance to be updated.

        Returns:
            None

        Example:
            >>> token_helper = TokenHelper()
            >>> token_helper.tokens_to_ids  # Updated with token mappings
            {'<token1>': 0, '<token2>': 1, ...}
        """
        if not bool(len(cls.tokens_to_ids)):
            config = Config().config
            with open(config['solver']['vocab_path'],'r') as f:
                tokens = f.readlines()

                for id, token in enumerate(tokens):
                    token, freq = token.strip().split('\t')
                    cls.tokens_to_ids[token] = id
                cls.ids_to_tokens = list(cls.tokens_to_ids.keys())
                cls.pad_index = cls.tokens_to_ids['<pad>']
                cls.empty_index = len(cls.ids_to_tokens)

class KeyChordDetails:
    pos_in_bar = None
    key_profile_path = None
    key_profile = None
    chord_pitch_out_of_key_prob  = None
    chord_change_prob = None
    key_change_prob = None
    key_chord_distribution = None
    key_chord_loglik = None
    key_chord_transition_distribution = None
    beat_note_factor = 4  # In MIDI format a note is always 4 beats
    max_notes_per_bar = 1  # 1/64 ... 128/64 # 
    pos_resolution = 4 # 16  # per beat (quarter note)
    bar_max = 32
    figure_size = None

    def __init__(self) -> None:
        if not bool(self.pos_in_bar):
            magenta = Magenta()
            self.pos_in_bar = self.beat_note_factor * self.max_notes_per_bar * self.pos_resolution
            self.figure_size = self.bar_max * self.pos_in_bar
            self.key_profile_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "getmusic", "utils", "key_profile.pickle")
            self.key_profile = pickle.load(open(self.key_profile_path, 'rb'))

            self.chord_pitch_out_of_key_prob = 0.01
            self.key_change_prob = 0.001
            self.chord_change_prob = 0.5
            self.key_chord_distribution = magenta._key_chord_distribution(
                chord_pitch_out_of_key_prob=self.chord_pitch_out_of_key_prob)
            self.key_chord_loglik = np.log(self.key_chord_distribution)
            self.key_chord_transition_distribution = magenta._key_chord_transition_distribution(
                self.key_chord_distribution,
                key_change_prob=self.key_change_prob,
                chord_change_prob=self.chord_change_prob)
            self.key_chord_transition_loglik = np.log(self.key_chord_transition_distribution)
