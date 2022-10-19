from abc import ABC

from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from django_app.plugin_system.processing_classes.preprocessor import Preprocessor


class EventHandler(Preprocessor, Postprocessor, ABC):
    def started_processing(self): pass

    def finished_all_files(self): pass

    def finished_file(self, file_path): pass
