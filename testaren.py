import re

audio_file = "text_files/audio_files/05-01-2017 13_09 587189291479399.txt"

audio_file = re.sub(r"\/audio_files", "", audio_file)
print(audio_file)
