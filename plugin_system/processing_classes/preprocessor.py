from abc import ABC


class Preprocessor(ABC):
    def preprocess(self, source_file: str, destination_file: str) -> None:
        """
        is called before a file has been processed<br>
        you can implement it for logging, metadata editing or similar things
        :param source_file: the actual source file
        :param destination_file: temporary destination file, name/directory might differ from final destination file
        """
        pass
