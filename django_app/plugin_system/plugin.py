import importlib
import json
from abc import ABC
from functools import reduce

from django_app import settings


class Plugin(ABC):
    COMPRESSION_TYPE = "compression"

    def __init__(self, name: str, from_file_types: list, form: str, task: str):
        self.name = name
        self._task = task
        self._form = form
        self._from_file_types = from_file_types

    def get_destination_types(self, from_file_type: str):
        def ___deduplicate(l: list) -> list:
            return list(set(l))

        if from_file_type is None:
            # return all possible destination types of all possible input types
            return ___deduplicate(
                reduce(
                    lambda sum_list, next_list: sum_list + next_list,
                    [self.get_destination_types(a) for a in self._from_file_types],
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
        except BaseException:
            raise ImportError("Plugin configuration caused error while loading %s. Plugin: '%s'" %
                             (import_path, self.name))

    def _get_form_class(self):
        return self._import_by_string_path(self._form)

    def get_task(self):
        return self._import_by_string_path(self._task)

    @classmethod
    def get_processing_plugin_by_name(cls, name: str):
        for plugin in settings.PROCESSOR_PLUGINS:
            if plugin.name == name:
                return plugin
        raise ImportError("Plugin not Found. Plugin: " + name)

    def get_input_file_types(self):
        return self._from_file_types

    def get_form_html_and_script(self, destination_file_type: str) -> tuple[str, str]:
        def ___get_container(__form_element):
            return f"""
                       <div class="form_element">
                           <span class="helptext">{__form_element.help_text}</span>
                           <span>{__form_element.label}</span>
                           {__form_element}
                       </div>
                       """

        def ___get_javascript(__hierarchy):
            # initialize_form_hierarchy is called after the form is loaded
            config_script = "function initialize_form_hierarchy(){"
            # add javascript for hierarchy configuration
            for form_container in __hierarchy.keys():
                if __hierarchy.get(form_container).get("type") == "bool":
                    hide_state = "" if __hierarchy.get(form_container).get("hide_state") == "True" else "!"
                    config_script += """
                                let %s = document.getElementById("id_%s")
                                %s.onchange = function () {
                                    update_visibility_of_container("not_%s", %sthis.checked);
                                }; %s.onchange();""" \
                                     % (form_container, form_container, form_container, form_container, hide_state,
                                        form_container)
                elif __hierarchy.get(form_container).get("type") == "choice":
                    string_list = json.dumps(__hierarchy.get(form_container).get("values_for_deactivation"))
                    config_script += """
                                let %s = document.getElementById("id_%s")
                                %s.onchange = function () {
                                    let hide = %s.includes(this.value);
                                    update_visibility_of_container("not_%s", hide);
                                }; %s.onchange();""" \
                                     % (form_container, form_container, form_container, string_list, form_container,
                                        form_container)
            return config_script + "}"

        html = ""
        form = self._get_form_class()()
        hierarchy = form.get_hierarchy()
        for form_element in form:
            open_hierarchy_containers = 0
            for container in hierarchy.keys():
                # open hierarchy containers around child element
                if form_element.html_name in hierarchy.get(container).get("children"):
                    html += "<div class='not_%s'>" % container
                    open_hierarchy_containers += 1

            html += ___get_container(form_element)

            # close open hierarchy containers
            for i in range(open_hierarchy_containers):
                html += "</div>"

        html += f"<input type='hidden' name='destination_file_type' value='{destination_file_type}'>"
        return html, ___get_javascript(hierarchy)
