from pydub import AudioSegment
from pydub.effects import speedup
from numpy.random import uniform
# import numpy as np
# import librosa

# def pitch_shift( file_path, output_filename, semitones):
#     format = file_path[-3:]
#     sound = AudioSegment.from_file(file_path, format=format)
#     # for semitones in np.linspace(-1, 1, 21):
#     print(f"Trnasposing multimedia file {semitones} semitones")
#     semitones = int(semitones) * .083
#
#     y = np.frombuffer(sound._data, dtype=np.int16).astype(np.float32) / 2 ** 15
#     y = librosa.effects.pitch_shift(y, sound.frame_rate, n_steps=n_steps)
#     a = AudioSegment(np.array(y * (1 << 15), dtype=np.int16).tobytes(), frame_rate=sound.frame_rate, sample_width=2,
#                      channels=1)
#
#     hipitch_sound.export(f"multimedia/{output_filename}", format=format)
#     return "multimedia/" + output_filename

def pitch_shift( file_path, output_filename, semitones):
    format = file_path[-3:]
    sound = AudioSegment.from_file(file_path, format=format)
    # for semitones in np.linspace(-1, 1, 21):
    print(f"Trnasposing multimedia file {semitones} semitones")
    semitones = int(semitones) *.083



    new_sample_rate = int(sound.frame_rate * (2.0 ** semitones))
    hipitch_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
    #
    if semitones < 0:
        print(f"Standarizing file audio playback speed: {-semitones + 1}")
        hipitch_sound = hipitch_sound.speedup(1.2, 150, 10)
    # final_file = new_file.set_frame_rate(44100)
    hipitch_sound.export(f"multimedia/{output_filename}", format=format)
    return "multimedia/" + output_filename



    # new_file = sound.speedup(1.2, 150, 10)
    #