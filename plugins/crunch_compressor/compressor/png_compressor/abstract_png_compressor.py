from abc import ABC

from plugins.crunch_compressor.compressor.png_compressor.abstract_image_compressor import AbstractImageCompressor


# TODO check if multi-threaded execution of all PNGCompressor classes ends up not being inefficient


class AbstractPngCompressor(AbstractImageCompressor, ABC):
    def __init__(
            self,
            event_handlers=None,
            run_multi_threaded: bool = True
    ):
        super().__init__(
            event_handlers=event_handlers,
            file_type_from=["png"],
            file_type_to="png",
            run_multi_threaded=run_multi_threaded
        )
