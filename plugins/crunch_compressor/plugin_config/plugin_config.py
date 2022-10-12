from django_app.plugin_system.plugin import Plugin


class PdfCompressorPlugin(Plugin):
    PDF_MIME_TYPE = "application/pdf"

    def __init__(self, name: str):
        super().__init__(
            name=name,
            from_file_types=[self.PDF_MIME_TYPE],
            form="plugins.crunch_compressor.plugin_config.forms.PdfCompressorForm",
            task="plugins.crunch_compressor.plugin_config.tasks.PdfCompressionTask"
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
            name=name,
            from_file_types=["image/png"],
            form="plugins.crunch_compressor.plugin_config.forms.PngCompressorForm",
            task="plugins.crunch_compressor.plugin_config.tasks.PngCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type == "image/png":
            result.append(self.COMPRESSION_TYPE)
        return result


class ImageToPdfConvertPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            from_file_types=[
                "image/jpeg",
                "image/pjpeg",
                "image/png",
                "image/gif",
                "image/svg+xml",
                "image/webp",
            ],
            form="plugins.crunch_compressor.plugin_config.forms.ImageToPdfConvertForm",
            task="plugins.crunch_compressor.plugin_config.tasks.ImageToPdfConvertTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type in self._from_file_types:
            result.append("application/pdf")
        return result
