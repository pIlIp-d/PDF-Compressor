from plugin_system.plugin import Plugin
import mimetypes
import subprocess
import re


def get_supported_types():
    raw_input_text = subprocess.check_output(["convert", "-list", "format"]).decode("utf-8")

    # any combination of (r/- w/- -/+) but ---
    mode_pattern = r"(?![-]{3})[r-][w-][-+]"

    input_types = []
    output_types = []

    # Iterate through the list of supported formats and split if contains mode Pattern. Afterward put them in the corresponding lists
    for line in raw_input_text.split("\n"):
        if re.search(mode_pattern, line):
            file_format, module, mode, *_ = re.split(r"\s+", line.strip())
            mime_type, _ = mimetypes.guess_type("file." + file_format.replace("*", "").lower())

            if mime_type is not None:
                if "r" in mode:
                    input_types.append(mime_type)
                if "w" in mode:
                    output_types.append(mime_type)
    return list(set(input_types)), list(set(output_types))

INPUT_TYPES, OUTPUT_TYPES = get_supported_types()

class ImageConverterPlugin(Plugin):
    def __init__(self, name: str):
        super().__init__(
            name,
            INPUT_TYPES,
            "plugin_system.plugins.image_converter.form.ImageConverterForm",
            "plugin_system.plugins.image_converter.task.ImageConverterTask",
            merger=True
        )

    def get_destination_types(self, from_file_type: str = None) -> list[str]:
        result = super().get_destination_types(from_file_type)
        if from_file_type in self._from_file_types:
            result.extend(OUTPUT_TYPES)
        return result

