from django_app.plugin_system.plugin import Plugin


class PdfCompressorPlugin(Plugin):

    def __init__(self, name: str, form: str = None):
        if form is None:
            form = "plugins.crunch_compressor.plugin_config.forms.PdfCompressorForm"
        super().__init__(
            name,
            [self.PDF_MIME_TYPE],
            form,
            "plugins.crunch_compressor.plugin_config.tasks.PdfCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type == self.PDF_MIME_TYPE:
            result.append(self.COMPRESSION_TYPE)
        return result

class GoodNotesCompressorPlugin(PdfCompressorPlugin):
    def __init__(self, name: str):
        super().__init__(name, "plugins.crunch_compressor.plugin_config.forms.GoodNotesCompressorForm")


class PngCompressorPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name,
            ["image/png"],
            "plugins.crunch_compressor.plugin_config.forms.PngCompressorForm",
            "plugins.crunch_compressor.plugin_config.tasks.PngCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type == "image/png":
            result.append(self.COMPRESSION_TYPE)
        return result


class ImageToPdfConvertPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name,
            ['image/xbm', 'image/bmp', 'image/webp', 'image/icns', 'image/sgi', 'image/gif', 'image/png', 'image/jpeg',
             'image/tiff', 'image/jp2'],
            "plugins.crunch_compressor.plugin_config.forms.ImageToPdfConvertForm",
            "plugins.crunch_compressor.plugin_config.tasks.ImageToPdfConvertTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type in self._from_file_types:
            result.append(self.PDF_MIME_TYPE)
        return result


class PdfToImageConvertPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name,
            [self.PDF_MIME_TYPE],
            "plugins.crunch_compressor.plugin_config.forms.PdfToImageConvertForm",
            "plugins.crunch_compressor.plugin_config.tasks.PdfToImageConvertTask",
            only_zip_as_result=True
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type == self.PDF_MIME_TYPE:
            result.append("image/png")
        return result
