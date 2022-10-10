from django_app.plugin_system.plugin import Plugin


class PdfCompressorPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name=name,
            from_file_types=["pdf", "png"],
            form="plugins.pdfcompressor.pdf_compressor_form.PdfCompressorForm",
            task="plugins.pdfcompressor.pdf_compression_task.PdfCompressionTask"
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type == "pdf" or from_file_type == "png":
            result.append(self.COMPRESSION_TYPE)
        return result
