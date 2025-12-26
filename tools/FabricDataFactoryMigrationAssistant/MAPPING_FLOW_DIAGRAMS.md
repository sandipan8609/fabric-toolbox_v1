# ADF to Fabric Mapping - Visual Flow Diagrams

## 📊 Mapping Process Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADF ARM Template Upload                      │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Component Extraction                          │
│  ┌──────────┬──────────┬──────────┬──────────┬────────────┐   │
│  │Pipelines │ Datasets │LinkedSvcs│ Triggers │GlobalParams│   │
│  └──────────┴──────────┴──────────┴──────────┴────────────┘   │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Mapping & Transformation                     │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │ 1. LinkedService → Connection (connector_mapper.py)     │  │
│  │    - 80+ type mappings                                   │  │
│  │    - Authentication conversion                           │  │
│  │    - Connection details extraction                       │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 2. Dataset → DatasetSettings (transformer.py)           │  │
│  │    - Embed in activities                                 │  │
│  │    - Parameter resolution                                │  │
│  │    - Connection reference                                │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 3. Activities → Fabric Activities (activity_transformer) │  │
│  │    - Activity-specific transformations                   │  │
│  │    - LinkedService → Connection mapping                  │  │
│  │    - Expression updates                                  │  │
│  ├──────────────────────────────────────────────────────────┤  │
│  │ 4. Global Params → Variable Library (global_param_*)    │  │
│  │    - Expression transformation (3 patterns)              │  │
│  │    - Data type mapping                                   │  │
│  │    - libraryVariables injection                          │  │
│  └──────────────────────────────────────────────────────────┘  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Fabric Deployment                            │
│  ┌──────────────┬─────────────┬──────────────┬──────────────┐  │
│  │ Connections  │ Var Library │  Pipelines   │  Schedules   │  │
│  │  (Step 5)    │  (Step 7)   │   (Step 9)   │   (Step 9)   │  │
│  └──────────────┴─────────────┴──────────────┴──────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 Connector Mapping Flow

```
ADF LinkedService
       ├── type: "AzureSqlDatabase"
       ├── typeProperties:
       │   ├── connectionString: "Server=...;Database=...;"
       │   └── authenticationType: "ManagedIdentity"
       └── name: "MyLinkedService"
              ↓
    ┌─────────────────────┐
    │ connector_mapper.py │
    │  map_adf_to_fabric  │
    └─────────────────────┘
              ↓
       [Mapping Logic]
       1. Type lookup: "AzureSqlDatabase" → "SQL"
       2. Parse connection string → server, database
       3. Auth conversion: "ManagedIdentity" → "WorkspaceIdentity"
       4. Confidence assessment: HIGH
              ↓
Fabric Connection
       ├── connectorType: "SQL"
       ├── connectionDetails:
       │   ├── server: "myserver.database.windows.net"
       │   ├── database: "mydb"
       │   └── authenticationType: "WorkspaceIdentity"
       ├── privacyLevel: "Organizational"
       └── displayName: "MyLinkedService"
```

---

## 📦 Copy Activity Transformation Flow

```
ADF Copy Activity
├── inputs: [Dataset_Source]
├── outputs: [Dataset_Sink]
└── typeProperties:
    ├── source: { type: "AzureSqlSource" }
    ├── sink: { type: "AzureSqlSink" }
    └── stagingSettings:
        └── linkedServiceName: "StagingStorage"
          ↓
   ┌──────────────────┐
   │ transformer.py   │
   │ Dataset Resolver │
   └──────────────────┘
          ↓
   [Dataset Resolution]
   1. Lookup Dataset_Source definition
   2. Extract LinkedService reference
   3. Resolve parameters: @dataset().Param → @pipeline().parameters.Value
   4. Map LinkedService → Connection ID
          ↓
   ┌──────────────────────┐
   │ activity_transformer │
   │  Copy-specific logic │
   └──────────────────────┘
          ↓
Fabric Copy Activity
├── typeProperties:
│   ├── source:
│   │   ├── type: "AzureSqlSource"
│   │   └── datasetSettings:
│   │       ├── type: "AzureSqlTable"
│   │       ├── typeProperties: { ... }
│   │       └── externalReferences:
│   │           └── connection: "<source-connection-id>"
│   ├── sink:
│   │   ├── type: "AzureSqlSink"
│   │   └── datasetSettings:
│   │       ├── type: "AzureSqlTable"
│   │       └── externalReferences:
│   │           └── connection: "<sink-connection-id>"
│   └── stagingSettings:
│       ├── path: "staging"
│       └── externalReferences:
│           └── connection: "<staging-connection-id>"
```

---

## 🌐 Global Parameter Transformation Flow

```
ADF Factory
├── globalParameters:
│   ├── Environment: { type: "String", value: "Prod" }
│   └── MaxRetries: { type: "Int", value: 3 }
└── pipelines:
    └── MyPipeline:
        └── activity: Web
            └── url: "@{pipeline().globalParameters.Environment}/api"
                    ↓
         ┌───────────────────────────┐
         │ global_parameter_detector │
         │  Scan for usage (3 regex) │
         └───────────────────────────┘
                    ↓
         [Detection Results]
         ✓ Found: Environment (in Web activity URL)
         ✓ Found: MaxRetries (in Web activity body)
         Pattern: @{pipeline().globalParameters.X}
                    ↓
         ┌─────────────────────────────────┐
         │ global_parameter_transformer    │
         │  Expression transformation      │
         └─────────────────────────────────┘
                    ↓
         [Transformation Steps]
         1. Create Variable Library: "MyFactory_GlobalParameters"
         2. Transform expressions:
            @{pipeline().globalParameters.Environment}
            ↓
            @{variableLibrary('MyFactory_GlobalParameters').VariableLibrary_Environment}
         3. Inject libraryVariables object into pipeline
         4. Deploy Variable Library BEFORE pipelines
                    ↓
Fabric Workspace
├── Variable Library: "MyFactory_GlobalParameters"
│   └── variables:
│       ├── VariableLibrary_Environment: "Prod"
│       └── VariableLibrary_MaxRetries: 3
└── Pipeline: MyPipeline
    ├── libraryVariables:
    │   └── MyFactory_VariableLibrary_Environment:
    │       ├── type: "String"
    │       ├── value: "Prod"
    │       └── variableLibrary: "MyFactory_GlobalParameters"
    └── activity: Web
        └── url: "@{variableLibrary('MyFactory_GlobalParameters').VariableLibrary_Environment}/api"
```

---

## 🔗 Custom Activity Connection Resolution

```
ADF Custom Activity
├── linkedServiceName: "BatchLinkedService"
└── typeProperties:
    ├── resourceLinkedService: "StorageLinkedService"
    └── referenceObjects:
        └── linkedServices:
            ├── "LinkedService1"
            └── "LinkedService2"
                ↓
      ┌─────────────────────────────┐
      │ custom_activity_resolver    │
      │  4-Tier Resolution Strategy │
      └─────────────────────────────┘
                ↓
      [Resolution Attempt - Tier 1]
      ✓ Check: referenceId mapping from UI
      Result: "Pipeline1_Custom1_activity" → "connection-id-123"
                ↓
      [If Tier 1 fails → Tier 2]
      ✓ Check: Direct name match
      Result: "BatchLinkedService" → connection lookup
                ↓
      [If Tier 2 fails → Tier 3]
      ✓ Check: linkedServiceBridge lookup table
      Result: "BatchLinkedService" → bridge mapping
                ↓
      [If Tier 3 fails → Tier 4]
      ✓ Check: ConnectionService fallback
      Result: Deployed connection registry
                ↓
Fabric Custom Activity
├── externalReferences:
│   └── connection: "<batch-connection-id>"
└── typeProperties:
    ├── externalReferences:
    │   └── connection: "<storage-connection-id>"
    └── extendedProperties:
        └── referenceObjects:
            └── linkedServices:
                ├── "LinkedService1"
                └── "LinkedService2"
```

---

## 📋 Reference ID Generation Flow

```
Pipeline: "MyPipeline"
└── Activity: "CopyActivity1" (Copy)
    ├── inputs: ["SourceDataset"]
    ├── outputs: ["SinkDataset"]
    └── stagingSettings:
        └── linkedServiceName: "StagingStorage"
            ↓
   ┌─────────────────────────┐
   │ Reference ID Generator  │
   │  Format: {pipeline}_{   │
   │    activity}_{location} │
   └─────────────────────────┘
            ↓
   [Generated Reference IDs]
   ├── "MyPipeline_CopyActivity1_source"
   │   └── Location: dataset (source)
   │       └── LinkedService from SourceDataset
   │
   ├── "MyPipeline_CopyActivity1_sink"
   │   └── Location: dataset (sink)
   │       └── LinkedService from SinkDataset
   │
   └── "MyPipeline_CopyActivity1_staging"
       └── Location: staging
           └── LinkedService: "StagingStorage"
            ↓
   [Mapping Table Entry]
   {
     "MyPipeline_CopyActivity1_source": "connection-id-1",
     "MyPipeline_CopyActivity1_sink": "connection-id-2",
     "MyPipeline_CopyActivity1_staging": "connection-id-3"
   }
            ↓
   [Transformation Application]
   activity.typeProperties.source.datasetSettings.externalReferences.connection
     ← "connection-id-1"
   activity.typeProperties.sink.datasetSettings.externalReferences.connection
     ← "connection-id-2"
   activity.typeProperties.stagingSettings.externalReferences.connection
     ← "connection-id-3"
```

---

## 🎯 Authentication Conversion Flow

```
ADF Managed Identity
├── LinkedService: "AzureSqlDatabase1"
├── authenticationType: "ManagedIdentity"
└── ADF Managed Identity:
    └── Object ID: "12345678-..."
        ↓
   ┌────────────────────────────┐
   │ Authentication Converter   │
   │  managedIdentityService    │
   └────────────────────────────┘
        ↓
   [Conversion Logic]
   1. Detect: "ManagedIdentity" → requires Workspace Identity
   2. Map: ADF Managed Identity → Workspace Identity
   3. Note: Permissions need manual grant
        ↓
Fabric Workspace Identity
├── Connection: "AzureSqlDatabase1"
├── authenticationType: "WorkspaceIdentity"
└── Fabric Workspace Identity:
    └── Object ID: "workspace-id-..."
        ↓
   [Post-Migration Required]
   1. Grant SQL permissions to Workspace Identity:
      ALTER ROLE db_datareader ADD MEMBER [workspace-name]
   2. Update firewall rules
   3. Test connection
```

---

## 📊 Data Flow Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│                        Browser (Client)                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  1. ARM Template Upload (never leaves browser)            │ │
│  │     ↓                                                       │ │
│  │  2. Parse & Profile (adf_parser.py)                       │ │
│  │     ├── Extract components                                 │ │
│  │     ├── Build dependency graph                            │ │
│  │     └── Detect global parameters                          │ │
│  │     ↓                                                       │ │
│  │  3. Map Connectors (connector_mapper.py)                  │ │
│  │     ├── Type lookup (80+ mappings)                        │ │
│  │     ├── Auth conversion                                    │ │
│  │     └── Connection details extraction                     │ │
│  │     ↓                                                       │ │
│  │  4. Transform Pipelines (transformer.py)                  │ │
│  │     ├── Dataset embedding                                  │ │
│  │     ├── Activity transformation                           │ │
│  │     ├── Expression transformation                         │ │
│  │     └── Global parameter conversion                       │ │
│  │     ↓                                                       │ │
│  │  5. Generate Fabric Definitions                           │ │
│  │     ├── Connection JSON                                    │ │
│  │     ├── Variable Library JSON                             │ │
│  │     ├── Pipeline JSON                                      │ │
│  │     └── Schedule JSON                                      │ │
│  └────────────────────────────────────────────────────────────┘ │
└────────────────────────┬─────────────────────────────────────────┘
                         │ HTTPS
                         ▼
┌──────────────────────────────────────────────────────────────────┐
│                    Microsoft Fabric API                          │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │  6. Deploy to Fabric Workspace                            │ │
│  │     ├── Create connections                                 │ │
│  │     ├── Deploy Variable Library                           │ │
│  │     ├── Deploy pipelines                                   │ │
│  │     └── Create schedules                                   │ │
│  └────────────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

---

## 🗂️ File Processing Flow

```
ARM Template (JSON)
    ↓
parser.py
    ├── parse_arm_template()
    │   ├── Extract resources by type
    │   ├── Build component models (ADFComponent)
    │   └── Extract dependencies
    │       ↓
    └── ProfileResult
        ├── pipelines: List[PipelineArtifact]
        ├── datasets: List[DatasetArtifact]
        ├── linkedServices: List[LinkedServiceArtifact]
        ├── triggers: List[TriggerArtifact]
        └── globalParameters: List[GlobalParameterReference]
            ↓
connector_mapper.py
    ├── map_connector(linkedService)
    │   ├── map_adf_to_fabric_type()
    │   ├── build_connection_details()
    │   └── determine_confidence()
    │       ↓
    └── ConnectorMapping
        ├── adf_type: str
        ├── fabric_type: str
        └── connection_details: Dict
            ↓
transformer.py
    ├── transform_pipeline_definition()
    │   ├── Transform activities (recursive)
    │   ├── Inject libraryVariables
    │   └── Apply expression transformations
    │       ↓
    └── Fabric Pipeline JSON
        ├── libraryVariables: {...}
        ├── activities: [transformed]
        └── parameters: [...]
            ↓
Fabric Deployment
    ├── POST /v1/workspaces/{id}/items (connections)
    ├── POST /v1/workspaces/{id}/items (variable library)
    ├── POST /v1/workspaces/{id}/dataPipelines (pipelines)
    └── POST /v1/workspaces/{id}/items (schedules)
```

---

## 📐 Mapping Lookup Tables

### Connector Type Lookup
```
┌─────────────────────────────────────────────────┐
│        ADF_TO_FABRIC_TYPE_MAP                   │
│  (80+ key-value pairs in connector_mapper.py)   │
├─────────────────────────────────────────────────┤
│  Input: ADF type        Output: Fabric type     │
├─────────────────────────────────────────────────┤
│  "AzureSqlDatabase"  →  "SQL"                   │
│  "SqlServer"         →  "SqlServer"             │
│  "AzureBlobStorage"  →  "AzureBlobs"            │
│  "RestService"       →  "RestService"           │
│  "Snowflake"         →  "Snowflake"             │
│  "Databricks"        →  "Databricks"            │
│  ...                 →  ...                     │
│  (unknown)           →  "Generic"               │
└─────────────────────────────────────────────────┘
```

### Field Mapping Lookup
```
┌─────────────────────────────────────────────────┐
│   CONNECTION_DETAILS_FIELD_MAPPING              │
│  (Per connector type field mappings)            │
├─────────────────────────────────────────────────┤
│  Fabric Type: "SQL"                             │
│  ┌───────────────────────────────────────────┐ │
│  │  "server": ["server", "serverName"]      │ │
│  │  "database": ["database", "databaseName"]│ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Fabric Type: "AzureBlobs"                      │
│  ┌───────────────────────────────────────────┐ │
│  │  "account": ["accountName","storageAcct"]│ │
│  └───────────────────────────────────────────┘ │
│                                                 │
│  Fabric Type: "Web"                             │
│  ┌───────────────────────────────────────────┐ │
│  │  "url": ["url", "baseUrl", "serviceUri"] │ │
│  └───────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

---

## 🎨 Legend

```
┌──────────┐
│   Box    │  Component or Process
└──────────┘

    ↓         Flow direction

[ Action ]    Processing step

{ Data }      Data structure

✓ Success     Positive outcome
✗ Failure     Negative outcome
⚠ Warning     Warning or partial support
```

---

*Visual diagrams for understanding ADF to Fabric pipeline conversion mapping*
