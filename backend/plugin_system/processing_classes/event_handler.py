from abc import ABC

from plugin_system.processing_classes.postprocessor import Postprocessor
from plugin_system.processing_classes.preprocessor import Preprocessor


class EventHandler(Preprocessor, Postprocessor, ABC):

    def started_processing(self):
        """
            is called before your processing task starts
        """
        pass

    def finished_all_files(self):
        """
            is called after all processing has been finished and the result files exist in the destination directory
        """
        pass

    def finished_merge(self):
        pass
