from ansi.colour import fg

from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from django_app.plugin_system.processing_classes.preprocessor import Preprocessor


class ConsoleUIProcessor(Preprocessor, Postprocessor):

    def preprocess(self, source_file: str, destination_file: str) -> None:
        print("Compressing " + fg.yellow(source_file))

    def postprocess(self, source_file: str, destination_file: str) -> None:
        # ConsoleUtility.print_stats(
        #     OsUtility.get_file_size(source_file), OsUtility.get_file_size(destination_file), "File"
        # )
        # ConsoleUtility.print("")
        pass
