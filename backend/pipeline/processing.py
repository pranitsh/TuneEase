import numpy as np
from .key_chord import KeyChordDetails

def normalize_to_c_major(filename, e):
    k_c_d = KeyChordDetails()
    if filename == "track_generation.py":
        def get_pitch_class_histogram(notes, use_duration=True, use_velocity=True, normalize=True):
            weights = np.ones(len(notes))
            if use_duration:
                weights *= [note[4] for note in notes]  
            if use_velocity:
                weights *= [note[5] for note in notes] 
            histogram, _ = np.histogram([note[3] % 12 for note in notes], bins=np.arange(
                13), weights=weights, density=normalize)
            if normalize:
                histogram /= (histogram.sum() + (histogram.sum() == 0))
            return histogram

        pitch_histogram = [i for i in e if i[2] < 128]
        print("Is this it?")
        print(e[0])
        if len(pitch_histogram) == 0:
            return e, True, 0

        histogram = get_pitch_class_histogram(pitch_histogram)
        key_candidate = np.dot(k_c_d.key_profile, histogram)
        key_temp = np.where(key_candidate == max(key_candidate))
        major_index = key_temp[0][0]
        minor_index = key_temp[0][1]
        major_count = histogram[major_index]
        minor_count = histogram[minor_index % 12]
        key_number = 0
        if major_count < minor_count:
            key_number = minor_index
            is_major = False
        else:
            key_number = major_index
            is_major = True
        real_key = key_number
        # transposite to C major or A minor
        if real_key <= 11:
            trans = 0 - real_key
        else:
            trans = 21 - real_key
        pitch_shift = trans

        e = [tuple(k + pitch_shift if j == 3 and i[2] != 128 else k for j, k in enumerate(i))
            for i in e]
        return e, is_major, pitch_shift
    elif filename == "position_generation.py":
        def get_pitch_class_histogram(notes, use_duration=True, use_velocity=True, normalize=True):
            weights = np.ones(len(notes))
            # Assumes that duration and velocity have equal weight
            if use_duration:
                weights *= [note[4] for note in notes]  # duration
            if use_velocity:
                weights *= [note[5] for note in notes]  # velocity
            histogram, _ = np.histogram([note[3] % 12 for note in notes], bins=np.arange(
                13), weights=weights, density=normalize)
            if normalize:
                histogram /= (histogram.sum() + (histogram.sum() == 0))
            return histogram

        histogram = get_pitch_class_histogram([i for i in e if i[2] < 128])
        key_candidate = np.dot(k_c_d.key_profile, histogram)
        key_temp = np.where(key_candidate == max(key_candidate))
        major_index = key_temp[0][0]
        minor_index = key_temp[0][1]
        major_count = histogram[major_index]
        minor_count = histogram[minor_index % 12]
        key_number = 0
        if major_count < minor_count:
            key_number = minor_index
            is_major = False
        else:
            key_number = major_index
            is_major = True
        real_key = key_number
        # transposite to C major or A minor
        if real_key <= 11:
            trans = 0 - real_key
        else:
            trans = 21 - real_key
        pitch_shift = trans

        e = [tuple(k + pitch_shift if j == 3 and i[2] != 128 else k for j, k in enumerate(i))
            for i in e]
        return e, is_major, pitch_shift
    elif filename == "to_oct.py":
        def get_pitch_class_histogram(notes, use_duration=True, use_velocity=True, normalize=True):
            weights = np.ones(len(notes))
            # Assumes that duration and velocity have equal weight
            if use_duration:
                weights *= [note[4] for note in notes]  # duration
            if use_velocity:
                weights *= [note[5] for note in notes]  # velocity
            histogram, _ = np.histogram([note[3] % 12 for note in notes], bins=np.arange(
                13), weights=weights, density=normalize)
            if normalize:
                histogram /= (histogram.sum() + (histogram.sum() == 0))
            return histogram

        histogram = get_pitch_class_histogram([i for i in e if i[2] < 128])
        key_candidate = np.dot(k_c_d.key_profile, histogram)
        key_temp = np.where(key_candidate == max(key_candidate))
        major_index = key_temp[0][0]
        minor_index = key_temp[0][1]
        major_count = histogram[major_index]
        minor_count = histogram[minor_index % 12]
        key_number = 0
        if major_count < minor_count:
            key_number = minor_index
            is_major = False
        else:
            key_number = major_index
            is_major = True
        real_key = key_number
        # transposite to C major or A minor
        if real_key <= 11:
            trans = 0 - real_key
        else:
            trans = 21 - real_key
        pitch_shift = trans

        # _e = []
        # for i in e:
        #     for j, k in enumerate(i):
        #         if i[2] == 128:
        #             _e.append(i)
        #         else:

        e = [tuple(k + pitch_shift if j == 3 and i[2] != 128 else k for j, k in enumerate(i))
            for i in e]
        return e, is_major
