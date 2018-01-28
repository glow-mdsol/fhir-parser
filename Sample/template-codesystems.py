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
from enum import Enum
{% for system in systems %}{% if system.generate_enum %}

class {{ system.name }}(Enum):
	""" {{ system.definition.description|wordwrap(width=120, wrapstring="\n") }}

	URL: {{ system.url }}
	{%- if system.definition.valueSet %}
	ValueSet: {{ system.definition.valueSet }}
	{%- endif %}
	"""
	URL = "{{ system.url }}"
	{%- for code in system.codes %}

	{{ code.name }} = "{{ code.code }}"
	""" {{ code.definition|wordwrap(width=112, wrapstring="\n	/// ") }}
	"""
	{%- endfor %}
{% endif %}{% endfor %}
