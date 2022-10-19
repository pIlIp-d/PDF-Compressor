from abc import ABC

from django_app.plugin_system.processing_classes.postprocessor import Postprocessor
from django_app.plugin_system.processing_classes.preprocessor import Preprocessor


class EventHandler(Preprocessor, Postprocessor, ABC):
    # is called before your processing task starts
    def started_processing(self): pass

    # is called after all processing has been finished and the result files exist in the destination directory
    def finished_all_files(self): pass
