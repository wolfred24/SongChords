import re

chromatic_scale_regex = [r"C(?!\#)|D[Oo](?!#)", r"C#|D[Oo]#", r"D(?!\#)|R[Ee](?!\#)", r"D#|R[Ee]#",
                         r"E|M[Ii]", r"F(?!\#)|F[Aa](?!\#)", r"F#|F[Aa]#", r"G(?!\#)|S[Oo][Ll](?!\#)",
                         r"G#|S[Oo][Ll]#", r"A(?!\#)|L[Aa](?!\#)", r"A#|L[Aa]#", r"B|S[Ii]"]
chromatic_scale = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

def transpose(song, transposition_semitones):
    transposition_semitones = int(transposition_semitones)
    regex_chords_pattern = r"[ABCDEFGMRSL][oOeEiIaA#]?[lLsm791#/]?[aABCDEFG]?[ju13m/7a#]?[sj7]?[47]?(?=\s*[\[\]\(\)|SRMLABCDEFG\dx\n])"
    chords = re.findall(regex_chords_pattern, song)
    lirycs = re.split(regex_chords_pattern, song)
    degree = 0
    transposed_lirycs_and_chords = ""
    position = 0
    for chord in chords:
        degree = 0
        for tone in chromatic_scale_regex:
            if re.match(tone, chord):
                chord_symbols = re.split(tone, chord)
                current_tone = re.match(tone, chord)
                transposed_degree = degree + transposition_semitones
                if transposed_degree > 11: transposed_degree = transposed_degree - 12
                if transposed_degree < 0: transposed_degree = transposed_degree + 12
                transposed_tone = chromatic_scale[transposed_degree]
                transposed_chord = transposed_tone + chord_symbols[1]
                transposed_lirycs_and_chords = transposed_lirycs_and_chords + lirycs[position] + transposed_chord
                # print(f"Degree:  {degree}")
                # print(f"Current tone: {str(current_tone)}")
                # print(f"Transposed degree: {transposed_degree}")
                # print(f"Transposed tone: {transposed_chord}")
                break
            degree = degree + 1
        position = position + 1
    transposed_lirycs_and_chords = transposed_lirycs_and_chords + lirycs[position]
    # print(transposed_lirycs_and_chords)
    # print(lirycs)
    # print(chords)
    return transposed_lirycs_and_chords
