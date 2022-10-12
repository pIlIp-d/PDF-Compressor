from django_app.plugin_system.plugin import Plugin


class PdfCompressorPlugin(Plugin):
    PDF_MIME_TYPE = "application/pdf"

    def __init__(self, name: str):
        super().__init__(
            name,
            [self.PDF_MIME_TYPE],
            "plugins.crunch_compressor.plugin_config.forms.PdfCompressorForm",
            "plugins.crunch_compressor.plugin_config.tasks.PdfCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        print(from_file_type)
        if from_file_type == self.PDF_MIME_TYPE:
            result.append(self.COMPRESSION_TYPE)
        return result


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
            [
                "image/jpeg",
                "image/pjpeg",
                "image/png",
                "image/gif",
                "image/svg+xml",
                "image/webp",
            ],
            "plugins.crunch_compressor.plugin_config.forms.ImageToPdfConvertForm",
            "plugins.crunch_compressor.plugin_config.tasks.ImageToPdfConvertTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type in self._from_file_types:
            result.append("application/pdf")
        return result
