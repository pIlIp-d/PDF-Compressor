from abc import ABC

from PIL import Image

from plugin_system.processing_classes.processor import Processor


class AbstractImageCompressor(Processor, ABC):
    def __init__(
            self,
            file_type_from: list[str] = "png",
            file_type_to: str = "png",
            event_handlers=None,
            run_multi_threaded: bool = True
    ):
        super().__init__(
            event_handlers=event_handlers,
            file_type_from=file_type_from,
            file_type_to=file_type_to,
            run_multi_threaded=run_multi_threaded
        )

    @staticmethod
    def _is_valid_image(path: str) -> bool:
        try:
            with Image.open(path) as img:
                img.verify()
            return True
        except:
            # couldn't open and verify -> not a valid image
            return False

    def _compare_and_use_better_option(self, file_option_1: str, file_option_2: str, destination_file: str) -> None:
        size_option_1 = self._get_file_size(file_option_1)
        size_option_2 = self._get_file_size(file_option_2)

        # compression worked -> copy file to final destination
        if self._is_valid_image(file_option_2) and size_option_1 > size_option_2 or \
                not self._is_valid_image(file_option_1):
            self._copy_file(file_option_2, destination_file)
        # error in output file -> copy source file to destination
        else:
            self._copy_file(file_option_1, destination_file)
