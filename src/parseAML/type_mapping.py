# TODO : Verify ARIS keys
# http://www.opengroup.org/xsd/archimate/3.0/archimate3_Model.xsd

type_map = {
    # Business Layer
    "ST_ARCHIMATE_BUSINESS_ACTOR": "BusinessActor",
    "ST_ARCHIMATE_BUSINESS_ROLE": "BusinessRole",
    "ST_ARCHIMATE_BUSINESS_COLLABORATION": "BusinessCollaboration",
    "ST_ARCHIMATE_BUSINESS_INTERFACE": "BusinessInterface",
    "ST_ARCHIMATE_BUSINESS_PROCESS": "BusinessProcess",
    "ST_ARCHIMATE_BUSINESS_FUNCTION": "BusinessFunction",
    "ST_ARCHIMATE_BUSINESS_INTERACTION": "BusinessInteraction",
    "ST_ARCHIMATE_BUSINESS_EVENT": "BusinessEvent",
    "ST_ARCHIMATE_BUSINESS_SERVICE": "BusinessService",
    "ST_ARCHIMATE_BUSINESS_OBJECT": "BusinessObject",
    "ST_ARCHIMATE_CONTRACT": "Contract",
    "ST_ARCHIMATE_REPRESENTATION": "Representation",
    "ST_ARCHIMATE_PRODUCT": "Product",

    # Application Layer

    "ST_ARCHIMATE_APPLICATION_COMPONENT": "ApplicationComponent",
    "ST_ARCHIMATE_APPLICATION_INTERFACE": "ApplicationInterface",
    "ST_ARCHIMATE_APPLICATION_COLLABORATION": "ApplicationCollaboration",
    "ST_ARCHIMATE_APPLICATION_FUNCTION": "ApplicationFunction",
    "ST_ARCHIMATE_APPLICATION_PROCESS": "ApplicationProcess",
    "ST_ARCHIMATE_APPLICATION_EVENT": "ApplicationEvent",
    "ST_ARCHIMATE_APPLICATION_SERVICE": "ApplicationService",
    "ST_APPL_SYS_TYPE": "ApplicationComponent", # Special type, from ServiceNow CMDB import
    "ST_ARCHIMATE_DATA_OBJECT": "DataObject",

    # Technology layer

    "ST_ARCHIMATE_NODE": "Node",
    "ST_ARCHIMATE_DEVICE": "Device",
    "ST_ARCHIMATE_PATH": "Path",
    "ST_ARCHIMATE_NETWORK": "CommunicationNetwork",
    "ST_ARCHIMATE_SYSTEM_SOFTWARE": "SystemSoftware",
    "ST_ARCHIMATE_TECHNOLOGY_COLLABORATION": "TechnologyCollaboration",
    "ST_ARCHIMATE_TECHNOLOGY_INTERFACE": "TechnologyInterface",
    "ST_ARCHIMATE_TECHNOLOGY_FUNCTION": "TechnologyFunction",
    "ST_ARCHIMATE_TECHNOLOGY_PROCESS": "TechnologyProcess",
    "ST_ARCHIMATE_TECHNOLOGY_INTERACTION": "TechnologyInteraction",
    "ST_ARCHIMATE_TECHNOLOGY_EVENT": "TechnologyEvent",
    "ST_ARCHIMATE_TECHNOLOGY_SERVICE": "TechnologyService",
    "ST_ARCHIMATE_ARTIFACT": "Artifact",

    # Physical elements

    "ST_ARCHIMATE_EQUIPMENT": "Equipment",
    "ST_ARCHIMATE_FACILITY": "Facility",
    "ST_ARCHIMATE_DISTRIBUTION_NETWORK": "DistributionNetwork",
    "ST_ARCHIMATE_MATERIAL": "Material",

    #  Motivation

    "ST_ARCHIMATE_STAKEHOLDER": "Stakeholder",
    "ST_ARCHIMATE_DRIVER": "Driver",
    "ST_ARCHIMATE_ASSESSMENT": "Assessment",
    "ST_ARCHIMATE_GOAL": "Goal",
    "ST_ARCHIMATE_OUTCOME": "Outcome",
    "ST_ARCHIMATE_PRINCIPLE": "Principle",
    "ST_ARCHIMATE_REQUIREMENT": "Requirement",
    "ST_ARCHIMATE_CONSTRAINT": "Constraint",
    "ST_ARCHIMATE_MEANING": "Meaning",
    "ST_ARCHIMATE_VALUE": "Value",

    # Strategy

    "ST_ARCHIMATE_RESOURCE": "Resource",
    "ST_ARCHIMATE_CAPABILITY": "Capability",
    "ST_ARCHIMATE_COURSE_OF_ACTION": "CourseOfAction",

    # Implementation & Migration

    "ST_ARCHIMATE_WORK_PACKAGE": "WorkPackage",
    "ST_ARCHIMATE_DELIVERABLE": "Deliverable",
    "ST_ARCHIMATE_IMPLEMENTATION_EVENT": "ImplementationEvent",
    "ST_ARCHIMATE_PLATEAU": "Plateau",
    "ST_ARCHIMATE_GAP": "Gap",
    "ST_ARCHIMATE_GROUP": "Grouping",
    "ST_ARCHIMATE_Location": "Location",

    # Composite

    "ST_ARCHIMATE_GROUPING": "Grouping",
    "ST_ARCHIMATE_LOCATION": "Location",

    # Junction

    "ST_ARCHIMATE_AND_JUNCTION": "AndJunction",
    "ST_ARCHIMATE_OR_JUNCTION": "OrJunction",
    "ST_ARCHIMATE_JUNCTION": "AndJunction",

    # Relationships

    "CT_ARCHIMATE_ASSOCIATION": "Association",
    "CT_ARCHIMATE_IS_ASSIGNED_TO": "Assignment",
    "CT_ARCHIMATE_REALIZES": "Realization",
    "CT_ARCHIMATE_SERVES": "Serving",
    "CT_ARCHIMATE_IS_COMPOSED_OF": "Composition",
    "CT_ARCHIMATE_AGGREGATES": "Aggregation",
    "CT_ARCHIMATE_ACCESSES": "Access",  # ! TODO Access Type enum
    "CT_ARCHIMATE_INFLUENCES": "Influence",  # TODO InfluenceStrengthEnum, InfluenceModiferType
    "CT_ARCHIMATE_TRIGGERS": "Triggering",
    "CT_ARCHIMATE_FLOW": "Flow",
    "CT_ARCHIMATE_IS_SPECIALIZATION_OF": "Specialization",
    "CT_ARCHIMATE_EXCHNG_INFO": "Association",  # TODO WHAT IS THAT???

    # Other
    "?": "Label"

}

accessType = ('Access', 'Read', 'Write', 'ReadWrite')
influenceStrength = ('+', '++', '-', '--', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9', '10')

archi_category = {
    # Business Layer
    "BusinessActor": "Business",
    "BusinessRole": "Business",
    "BusinessCollaboration": "Business",
    "BusinessInterface": "Business",
    "BusinessProcess": "Business",
    "BusinessFunction": "Business",
    "BusinessInteraction": "Business",
    "BusinessEvent": "Business",
    "BusinessService": "Business",
    "BusinessObject": "Business",
    "Contract": "Business",
    "Representation": "Business",
    "Product": "Business",

    # Application Layer

    "ApplicationComponent": "Application",
    "ApplicationInterface": "Application",
    "ApplicationCollaboration": "Application",
    "ApplicationFunction": "Application",
    "ApplicationProcess": "Application",
    "ApplicationEvent": "Application",
    "ApplicationService": "Application",
    "DataObject": "Application",

    # Technology layer

    "Node": "Technology",
    "Device": "Technology",
    "Path": "Technology",
    "CommunicationNetwork": "Technology",
    "SystemSoftware": "Technology",
    "TechnologyCollaboration": "Technology",
    "TechnologyInterface": "Technology",
    "TechnologyFunction": "Technology",
    "TechnologyProcess": "Technology",
    "TechnologyInteraction": "Technology",
    "TechnologyEvent": "Technology",
    "TechnologyService": "Technology",
    "Artifact": "Technology",

    # Physical elements

    "Equipment": "Physical",
    "Facility": "Physical",
    "DistributionNetwork": "Physical",
    "Material": "Physical",

    #  Motivation

    "Stakeholder": "Motivation",
    "Driver": "Motivation",
    "Assessment": "Motivation",
    "Goal": "Motivation",
    "Outcome": "Motivation",
    "Principle": "Motivation",
    "Requirement": "Motivation",
    "Constraint": "Motivation",
    "Meaning": "Motivation",
    "Value": "Motivation",

    # Strategy

    "Resource": "Strategy",
    "Capability": "Strategy",
    "CourseOfAction": "Strategy",

    # Implementation & Migration

    "WorkPackage": "Implementation & Migration",
    "Deliverable": "Implementation & Migration",
    "ImplementationEvent": "Implementation & Migration",
    "Plateau": "Implementation & Migration",
    "Gap": "Implementation & Migration",

    # Other

    "Grouping": "Other",
    "Location": "Other",

    # Junction

    "Junction": "Junction",
    "OrJunction": "Junction",
    "AndJunction": "Junction",

    # Relationships

    "Association": "Relationship",
    "Assignment": "Relationship",
    "Realization": "Relationship",
    "Serving": "Relationship",
    "Composition": "Relationship",
    "Aggregation": "Relationship",
    "Access": "Relationship",
    "Influence":  "Relationship",
    "Triggering": "Relationship",
    "Flow": "Relationship",
    "Specialization": "Relationship",

}

archi_type_map = {
    # Business Layer
    "BusinessActor": "BusinessActor",
    "BusinessRole": "BusinessRole",
    "BusinessCollaboration": "BusinessCollaboration",
    "BusinessInterface": "BusinessInterface",
    "BusinessProcess": "BusinessProcess",
    "BusinessFunction": "BusinessFunction",
    "BusinessInteraction": "BusinessInteraction",
    "BusinessEvent": "BusinessEvent",
    "BusinessService": "BusinessService",
    "BusinessObject": "BusinessObject",
    "Contract": "Contract",
    "Representation": "Representation",
    "Product": "Product",

    # Application Layer

    "ApplicationComponent": "ApplicationComponent",
    "ApplicationInterface": "ApplicationInterface",
    "ApplicationCollaboration": "ApplicationCollaboration",
    "ApplicationFunction": "ApplicationFunction",
    "ApplicationProcess": "ApplicationProcess",
    "ApplicationEvent": "ApplicationEvent",
    "ApplicationService": "ApplicationService",
    "DataObject": "DataObject",

    # Technology layer

    "Node": "Node",
    "Device": "Device",
    "Path": "Path",
    "CommunicationNetwork": "CommunicationNetwork",
    "SystemSoftware": "SystemSoftware",
    "TechnologyCollaboration": "TechnologyCollaboration",
    "TechnologyInterface": "TechnologyInterface",
    "TechnologyFunction": "TechnologyFunction",
    "TechnologyProcess": "TechnologyProcess",
    "TechnologyInteraction": "TechnologyInteraction",
    "TechnologyEvent": "TechnologyEvent",
    "TechnologyService": "TechnologyService",
    "Artifact": "Artifact",

    # Physical elements

    "Equipment": "Equipment",
    "Facility": "Facility",
    "DistributionNetwork": "DistributionNetwork",
    "Material": "Material",

    #  Motivation

    "Stakeholder": "Stakeholder",
    "Driver": "Driver",
    "Assessment": "Assessment",
    "Goal": "Goal",
    "Outcome": "Outcome",
    "Principle": "Principle",
    "Requirement": "Requirement",
    "Constraint": "Constraint",
    "Meaning": "Meaning",
    "Value": "Value",

    # Strategy

    "Resource": "Resource",
    "Capability": "Capability",
    "CourseOfAction": "CourseOfAction",

    # Implementation & Migration

    "WorkPackage": "WorkPackage",
    "Deliverable": "Deliverable",
    "ImplementationEvent": "ImplementationEvent",
    "Plateau": "Plateau",
    "Gap": "Gap",

    # Other

    "Grouping": "Grouping",
    "Location": "Location",

    # Junction

    "Junction": "Junction",
    "OrJunction": "OrJunction",
    "AndJunction": "AndJunction",

    # Relationships

    "Association": "Association",
    "Assignment": "Assignment",
    "Realization": "Realization",
    "Serving": "Serving",
    "Composition": "Composition",
    "Aggregation": "Aggregation",
    "Access": "Access",
    "Influence": "Influence",
    "Triggering": "Triggering",
    "Flow": "Flow",
    "Specialization": "Specialization",

}