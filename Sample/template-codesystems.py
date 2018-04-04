#
#  CodeSystems.py
#  client-py
#
#  Generated from FHIR {{ info.version }} on {{ info.date }}.
#  {{ info.year }}, SMART Health IT.
#
#  THIS HAS BEEN ADAPTED FROM Swift Enums WITHOUT EVER BEING IMPLEMENTED IN
#  Python, FOR DEMONSTRATION PURPOSES ONLY.
#
# Each instance has the URL defined for the purposes of building the
from enum import Enum


class CodeSystemValue(Enum):
    @property
    def as_coding_dict(self):
        return dict(display=self.value, system=self.URL, code=self.name)

    @property
    def text(self):
        return self.value

{% for system in systems %}{% if system.generate_enum %}

class {{ system.name }}(CodeSystemValue):
	""" {{ system.definition.description|wordwrap(width=120, wrapstring="\n") }}

	URL: {{ system.url }}
	{%- if system.definition.valueSet %}
	ValueSet: {{ system.definition.valueSet }}
	{%- endif %}
	"""
	URL = "{{ system.url }}"
    {%- if system.definition.experimental is defined %}}
    EXPERIMENTAL = {{system.definition.experimental}}
    {%endif%}
	{%- for code in system.codes %}

	""" {{ code.definition|wordwrap(width=112, wrapstring="\n	/// ") }}
	"""
	{{ code.name }} = "{{ code.code }}"
	{%- endfor %}
{% endif %}{% endfor %}
