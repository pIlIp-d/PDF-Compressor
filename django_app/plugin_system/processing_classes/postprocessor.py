from abc import ABC


class Postprocessor(ABC):
    # call after each processing of a file has been finished with source_file as the unchanged starting file
    # and destination_file the processed file
    def postprocess(self, source_file: str, destination_file: str) -> None: pass
