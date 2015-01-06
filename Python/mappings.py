# Mappings for the FHIR class generator

# Which class names to map to resources and elements
classmap = {
    'Structure': 'FHIRElement',
    'Resource': 'FHIRResource',
    'ResourceReference': 'FHIRReference',
    'Any': 'FHIRResource',
    
    'boolean': 'bool',
    'integer': 'int',
    'date': 'FHIRDate',
    'dateTime': 'FHIRDate',
    'instant': 'FHIRDate',
    'decimal': 'float',
    
    'string': 'str',
    'id': 'str',
    'oid': 'str',
    'uri': 'str',
    'base64Binary': 'str',
    'xhtml': 'str',
    'code': 'str',      # for now we're not generating enums for these
}

# Some properties (in Conformance, Profile and Questionnaire currently) can be
# any (value) type and have the `value[x]` form - how to substitute is defined
# here
starexpandtypes = {
    'integer',
    'decimal',
    'dateTime',
    'date',
    'instant',
    'string',
    'uri',
    'boolean',
    'code',
    'base64Binary',
    
    'Coding',
    'CodeableConcept',
    'Attachment',
    'Identifier',
    'Quantity',
    'Range',
    'Period',
    'Ratio',
    'HumanName',
    'Address',
    'Contact',
    'Schedule',
    'Resource',
}

# Which class names are native to the lannguage
natives = ['bool', 'int', 'float', 'str', 'dict']

# Which classes are to be expected from JSON decoding
jsonmap = {
    'FHIRElement': 'dict',
    'FHIRResource': 'dict',
    
    'str': 'str',
    'int': 'int',
    'bool': 'bool',
    'float': 'float',
    
    'FHIRDate': 'str',
}
jsonmap_default = 'dict'

# Properties that need to be renamed because of language keyword conflicts
reservedmap = {
    'class': 'klass',
    'import': 'importFrom',
    'modifier': 'mod',          # `modifierExtension` is called "modifier" in JSON
}

