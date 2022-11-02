import os
from abc import ABC

from django_app.plugin_system.processing_classes.processor import Processor
from django_app.utility.os_utility import OsUtility


class ProcessorWithDestinationFolder(Processor, ABC):
    def _get_files_and_extra_info(self, source_path, destination_path) -> tuple[list[str], list[str], bool, bool]:
        sources = self._get_sources_files_by_file_type_from(source_path) if os.path.isdir(source_path) else [
            source_path]
        if os.path.isfile(source_path):
            output_path = OsUtility.get_path_without_file_ending(
                source_path) + self._processed_files_appendix if destination_path == "default" else destination_path
        else:
            output_path = source_path + self._processed_files_appendix if destination_path == "default" else destination_path

        if self._destination_path_string_is_file(output_path):
            return sources, [os.path.dirname(output_path) for _ in sources], True, False
        else:
            return sources, [output_path for _ in sources], False, True
