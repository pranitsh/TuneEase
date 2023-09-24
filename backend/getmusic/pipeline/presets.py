prog_to_abrv = {'80':'M', '32':'B', '128':'D', '25':'G', '0':'P', '48':'S',}
inst_to_row = {'80':0, '32':1, '128':2, '25':3, '0':4, '48':5, '129':6}
track_name = {'M':'lead', 'B':'bass','D':'drum', 'G':'guitar', 'P':'piano', 'S':'string'}

root_dict = {'C': 0, 'C#': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'F#': 6, 'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11}
kind_dict = {'null': 0, 'm': 1, '+': 2, 'dim': 3, 'seven': 4, 'maj7': 5, 'm7': 6, 'm7b5': 7}
root_list = list(root_dict.keys())
kind_list = list(kind_dict.keys())