#
#  CodeSystems.py
#  client-py
#
#  Generated from FHIR {{ info.version }} on {{ info.date }}.
#  {{ info.year }}, SMART Health IT.
#
#

from enum import Enum


class CodeSystemValue(Enum):
    """
    Base CodeSystemValue class

    Inheriting from Enum allows us to do things like:
    >>> _type = SampleCodeSystemValue('type')
    """

    @property
    def as_coding_dict(self):
        return dict(display=self.value, system=self.url, code=self.name)

    @property
    def text(self):
        return self.value

    @property
    def url(self):
        return self.URL.value

    @property
    def experimental(self):
        return self.EXPERIMENTAL.value if hasattr(self, "EXPERIMENTAL") else False

{%- for system in systems %}
{%- if system.generate_enum %}


class {{system.name}}(CodeSystemValue):
    """ {{ system.definition.description|wordwrap(width=120, wrapstring="\n") }}

    URL: {{ system.url }}
    {%- if system.definition.valueSet %}
    ValueSet: {{ system.definition.valueSet }}
    {%- endif %}
    """
    URL = "{{ system.url }}"
    {%- if system.definition.experimental is defined %}
    EXPERIMENTAL = {{system.definition.experimental}}
    {%- endif %}
    {%- for code in system.codes %}

    """ {{ code.definition|wordwrap(width=112, wrapstring="\n	/// ") }}
    """
    {{code.name}} = "{{ code.code }}"
    {%- endfor %}
{%- endif %}
{%- endfor %}
