import os
import ffmpeg
import whisper
import re
from spacy import load as spacy_load
import time
import warnings
import logging
import pathlib
from my_logger import logger


class AudioTranscriber:
    def __init__(self, audio_directory, text_directory, model: str = "large") -> None:
        self.model = model
        self.audio_directory = audio_directory
        self.text_directory = text_directory
        self.logger = logger

        self.logger.info("AudioTranscriber initialized")

    def get_audio_files(self) -> list:
        """
        Return a list of all audio file paths in the audio_files folder
        """
        dir_name = self.audio_directory

        list_of_files = filter(
            lambda x: os.path.isfile(os.path.join(dir_name, x)), os.listdir(dir_name)
        )

        # Sort list of files by size
        list_of_files = sorted(
            list_of_files, key=lambda x: os.stat(os.path.join(dir_name, x)).st_size
        )
        # Only return mp3, m4a and wav files
        return [
            os.path.join(dir_name, file_name)
            for file_name in list_of_files
            if file_name.endswith((".mp3", ".m4a", ".wav"))
        ]

    def is_transcribed(self, audio_file: str) -> bool:
        """
        Check if the audio file has already been transcribed
        """

        audio_file_path = pathlib.Path(audio_file)
        text_file_path = pathlib.Path("text_files") / audio_file_path.stem
        text_file_path = text_file_path.with_suffix(".txt")

        try:
            with text_file_path.open() as f:
                self.logger.info(f"{audio_file} has already been transcribed")
                return True
        except FileNotFoundError:
            return False

    def transcribe_audio(self, audio_file: str) -> str:
        warnings.filterwarnings("ignore")
        model = whisper.load_model(self.model)
        return model.transcribe(audio_file)["text"]

    def get_sentences(self, text: str) -> list:
        nlp = spacy_load("nb_core_news_sm")
        tokens = nlp(text)
        return [sent.text for sent in tokens.sents]

    def write_sentences_to_file(self, sentences: list, filename: str) -> None:
        filename = re.sub(r"\.m4a|\.mp3|\.wav", "", filename)
        filename = re.sub(r"audio_files/", "", filename)
        with open(filename, "w") as f:
            for sentence in sentences:
                f.write(sentence + "\n")

    def log_time_to_file(self, script_time: float, audio_file: str) -> None:
        script_time = (
            f"{int(script_time // 60)} minutes {int(script_time % 60)} seconds"
        )
        audio_file = re.sub(r"audio_files/", "", audio_file)
        self.logger.info(f"{audio_file}: {script_time}")
        self.logger.info("\n")

    def main(self):
        audio_files = self.get_audio_files()
        for audio_file in audio_files:
            if self.is_transcribed(audio_file):
                continue
            print(
                f"Transcribing file {audio_files.index(audio_file) + 1} of {len(audio_files)}"
            )
            start_time = time.time()
            string_from_audio = self.transcribe_audio(audio_file)
            sentences = self.get_sentences(string_from_audio)
            self.write_sentences_to_file(
                sentences, f"{self.text_directory}/{audio_file}.txt"
            )

            script_time = time.time() - start_time
            self.log_time_to_file(script_time, audio_file)


if __name__ == "__main__":
    transcriber = AudioTranscriber(
        audio_directory="audio_files", text_directory="text_files"
    )
    transcriber.main()
