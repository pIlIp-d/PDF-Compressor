import importlib
import json
from abc import ABC
from functools import reduce
import htmgem.tags as gem

from django_app import settings


class Plugin(ABC):
    COMPRESSION_TYPE = "compression"
    PDF_MIME_TYPE = "application/pdf"

    def __init__(
            self,
            name: str,
            from_file_types: list,
            form: str,
            task: str,
            only_zip_as_result: bool = False,
            merger: bool = False
    ):
        self.name = name
        self._from_file_types = from_file_types
        self._form = form
        self._task = task
        self._only_zip_as_result = only_zip_as_result
        self._merger = merger

    def get_destination_types(self, from_file_type: str):
        def ___deduplicate(list_with_duplicates: list) -> list:
            return list(set(list_with_duplicates))

        if from_file_type is None:
            # return all possible destination types of all possible input types
            return ___deduplicate(
                reduce(
                    lambda sum_list, next_list: sum_list + next_list,
                    [self.get_destination_types(file_type) for file_type in self._from_file_types],
                    list()
                )
            )
        else:  # from_file_type not in self._from_file_types:
            return []

    def _import_by_string_path(self, import_path: str):
        try:
            path = import_path.split(".")
            module_path = ".".join(path[:-1])
            module = importlib.import_module(module_path)
            imported_class = getattr(module, path[-1])
            return imported_class
        except BaseException as be:
            if settings.DEBUG:
                print(be)
            raise ImportError("Plugin configuration caused error while loading %s. Plugin: '%s'" %
                              (import_path, self.name))

    def get_form_class(self):
        return self._import_by_string_path(self._form)

    def get_task(self):
        return self._import_by_string_path(self._task)

    @classmethod
    def get_processing_plugin_by_name(cls, name: str):
        for plugin in settings.PROCESSOR_PLUGINS:
            if plugin.name == name:
                return plugin
        raise ValueError("Plugin not Found. Plugin: " + name)

    def get_input_file_types(self):
        return self._from_file_types

    def get_form_html_and_script(self, destination_file_type: str) -> tuple[str, str]:
        form = self.get_form_class()()
        advanced_form_fields = form.get_advanced_options()
        hierarchy = form.get_hierarchy()

        def ___get_javascript():
            def ___get_js_for_element(element, function_string):
                return """
                       let {0} = document.getElementById("id_{0}");
                       {0}.onchange = function(){{update_visibility_of_container("not_{0}", {1})}};
                       {0}.onchange();""".format(element, function_string)

            def ___get_bool_type(hierarchy_element):
                hide_state = "" if hierarchy.get(hierarchy_element).get("hide_state") == "True" else "!"
                return ___get_js_for_element(hierarchy_element, hide_state + "this.checked")

            def ___get_choice_type(hierarchy_element):
                string_list = json.dumps(hierarchy.get(hierarchy_element).get("values_for_deactivation"))
                return ___get_js_for_element(hierarchy_element, string_list + ".includes(this.value)")

            def ___get_advanced_options_checkbox():
                # add event listener for advanced_options_checkbox and initially update the visibility
                return """
                document.getElementById('advanced_options_checkbox').onchange = function(){
                    update_advanced_options(this.checked)
                };
                update_advanced_options(false)
                """

            # initialize_form_hierarchy is called after the form is loaded
            config_script = "function initialize_form(){"
            # add javascript for hierarchy configuration
            for form_container in hierarchy.keys():
                # type == bool
                if hierarchy.get(form_container).get("type") == "bool":
                    config_script += ___get_bool_type(form_container)
                # type == choice
                elif hierarchy.get(form_container).get("type") == "choice":
                    config_script += ___get_choice_type(form_container)

                if advanced_form_fields:
                    config_script += ___get_advanced_options_checkbox()
            return config_script + "}"

        def ___get_input_html(input_type: str, input_name: str, input_value: str):
            return gem.input_({"type": input_type, "name": input_name, "value": input_value})

        def ___get_help_text_span(help_text: str):
            return gem.span({"class": "helptext"}, help_text) if help_text != "" else ""

        def ___get_form_element_html(__form_element):
            advanced_settings_class = "advanced_setting" if __form_element.name in advanced_form_fields else ""
            return gem.div(
                {"class": "form_element " + advanced_settings_class, "title": __form_element.help_text}, [
                    gem.span(__form_element.label),
                    str(__form_element)
                ]
            )

        def ___hierarchy_containers_around_form_element(element):
            for current_container in hierarchy.keys():
                if element.html_name in hierarchy.get(current_container).get("children"):
                    yield current_container

        # generate form html
        form_html = gem.div({"class": "form_element"}, [
            gem.span("Show advanced options:"),
            '<input type="checkbox" id="advanced_options_checkbox">'
        ]) if advanced_form_fields else ""

        for form_element in form:
            form_element_html = ___get_form_element_html(form_element)
            for container in ___hierarchy_containers_around_form_element(form_element):
                form_element_html = gem.div({"class": "not_%s" % container}, form_element_html)
            form_html += form_element_html

        form_html += ___get_input_html("hidden", "destination_file_type", destination_file_type)

        # add plugin specific hidden-input
        if self._merger:
            form_html += ___get_input_html("hidden", "merge_files", "on")
        if self._only_zip_as_result:  # todo finish implement
            form_html += ___get_input_html("hidden", "only_zip_as_result", "on")

        return form_html, ___get_javascript()
