import os
import whisper
import re
from spacy import load as spacy_load
import time
import warnings


def get_audio_files() -> list:
    """
    Return a list of all audio file paths in the audio_files folder
    """
    return list(os.listdir("audio_files"))


def is_transcribed(audio_file: str) -> bool:
    """
    Check if the audio file has already been transcribed
    """
    text_file = re.sub(r"\.m4a|\.mp3|\.wav", "", audio_file) + ".txt"

    if transcribed := os.path.exists(f"text_files/{text_file}"):
        print(f"{audio_file} has already been transcribed")
    else:
        print(f"Transcribing {audio_file}")

    return transcribed


def transcribe_audio(audio_file) -> str:
    warnings.filterwarnings("ignore")
    model = whisper.load_model("medium")
    return model.transcribe(audio_file)["text"]


def get_sentences(text: str) -> list:
    nlp = spacy_load("nb_core_news_sm")
    tokens = nlp(text)
    return [sent.text for sent in tokens.sents]


def write_sentences_to_file(sentences: list, filename: str) -> None:
    # Remove audio file extension from filename
    filename = re.sub(r"\.m4a|\.mp3|\.wav", "", filename)
    with open(filename, "w") as f:
        for sentence in sentences:
            f.write(sentence + "\n")


def log_time_to_file(script_time, log_filename: str, audio_file: str) -> None:
    script_time = f"{int(script_time // 60)} minutes {int(script_time % 60)} seconds"
    with open(log_filename, "a") as f:
        f.write(f"{audio_file}:\n")
        f.write(f"{script_time}\n")
        f.write("\n")


def main():
    audio_files = get_audio_files()
    for audio_file in audio_files:
        if is_transcribed(audio_file):
            continue
        print(
            f"Transcribing audio file number {audio_files.index(audio_file) + 1} of {len(audio_files)}"
        )
        audio_file_path = f"audio_files/{audio_file}"
        start_time = time.time()
        string_from_audio = transcribe_audio(audio_file_path)
        sentences = get_sentences(string_from_audio)
        write_sentences_to_file(sentences, f"text_files/{audio_file}.txt")
        script_time = time.time() - start_time
        log_time_to_file(script_time, "time_log.txt", audio_file=audio_file)


if __name__ == "__main__":
    main()
