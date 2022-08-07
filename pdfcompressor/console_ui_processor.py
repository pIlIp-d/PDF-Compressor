from pdfcompressor.compressor.processor import Processor
from pdfcompressor.utility.console_utility import ConsoleUtility
from pdfcompressor.utility.os_utility import OsUtility


class ConsoleUIProcessor(Processor):

    def __init__(self, processor: Processor = None):
        super().__init__(processor)

    def preprocess(self, source: str, destination: str) -> None:
        super().preprocess(source, destination)
        ConsoleUtility.print("Compressing " + ConsoleUtility.get_file_string(source))

    def postprocess(self, source: str, destination: str) -> None:
        ConsoleUtility.print_stats(OsUtility.get_file_size(source), OsUtility.get_file_size(destination))
        ConsoleUtility.print("")
        super().postprocess(source, destination)
