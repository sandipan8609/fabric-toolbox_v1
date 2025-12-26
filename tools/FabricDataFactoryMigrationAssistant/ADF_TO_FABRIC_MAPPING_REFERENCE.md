# ADF to Fabric Pipeline Conversion Mapping Reference

## 📋 Table of Contents

- [Overview](#overview)
- [Connector Type Mappings](#connector-type-mappings)
- [Activity Transformation Mappings](#activity-transformation-mappings)
- [Authentication Method Conversions](#authentication-method-conversions)
- [Global Parameter Migration](#global-parameter-migration)
- [Dataset to DatasetSettings Transformation](#dataset-to-datasetsettings-transformation)
- [Property Mappings](#property-mappings)
- [Expression Transformations](#expression-transformations)
- [Reference Location Patterns](#reference-location-patterns)

---

## Overview

This document provides a comprehensive reference for all mapping rules used by the FabricDataFactoryMigrationAssistant tool when converting Azure Data Factory (ADF) and Azure Synapse Analytics pipelines to Microsoft Fabric Data Pipelines.

**Source Code Location**: `tools/FabricDataFactoryMigrationAssistant/adf_fabric_migrator/`

**Key Mapping Files**:
- `connector_mapper.py` - LinkedService to Connection type mappings
- `transformer.py` - Pipeline-level transformations
- `activity_transformer.py` - Activity-specific transformations
- `global_parameter_transformer.py` - Global parameter expression transformations

---

## Connector Type Mappings

### SQL Database Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `SqlServer` | `SqlServer` | Direct mapping |
| `AzureSqlDatabase` | `SQL` | Generic SQL connection type |
| `AzureSqlMI` | `SQL` | Azure SQL Managed Instance |
| `AzureSqlDW` | `SQL` | Azure Synapse SQL Pool (formerly SQL DW) |
| `MySql` | `MySQL` | Direct mapping |
| `AzureMySql` | `MySQL` | Azure Database for MySQL |
| `PostgreSql` | `PostgreSQL` | Direct mapping |
| `AzurePostgreSql` | `PostgreSQL` | Azure Database for PostgreSQL |
| `Oracle` | `SQL` | Mapped to generic SQL type |
| `Db2` | `SQL` | IBM Db2 |
| `Sybase` | `SQL` | SAP Sybase |
| `Teradata` | `SQL` | Teradata |
| `Informix` | `SQL` | IBM Informix |
| `Odbc` | `ODBC` | Generic ODBC connection |

**Connection Details Field Mapping (SQL-based)**:
```python
# ADF typeProperties → Fabric connectionDetails
{
    "server": ["server", "serverName"],          # ADF field names to try
    "database": ["database", "databaseName"]     # Maps to Fabric field
}
```

### Azure Storage Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `AzureBlobStorage` | `AzureBlobs` | Azure Blob Storage |
| `AzureDataLakeStore` | `AzureDataLakeStorage` | ADLS Gen1 |
| `AzureDataLakeStoreGen2` | `AzureDataLakeStorage` | ADLS Gen2 |
| `AzureFileStorage` | `AzureFiles` | Azure Files |
| `AzureTableStorage` | `AzureTables` | Azure Table Storage |

**Connection Details Field Mapping (Storage)**:
```python
# ADF typeProperties → Fabric connectionDetails
{
    "account": ["accountName", "storageAccount"]  # Storage account name
}
```

### Web and REST Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `RestService` | `RestService` | Direct mapping |
| `WebTable` | `Web` | Web page tables |
| `HttpServer` | `Web` | HTTP/HTTPS endpoints |
| `Http` | `Web` | HTTP connections |
| `Web` | `Web` | Generic web connection |
| `OData` | `OData` | OData services |

**Connection Details Field Mapping (Web)**:
```python
# ADF typeProperties → Fabric connectionDetails
{
    "url": ["url", "baseUrl", "serviceUri"]  # Service endpoint URL
}
```

### SharePoint and Office 365 Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `SharePointOnlineList` | `SharePointOnlineList` | SharePoint Online Lists |
| `Office365` | `Office365Outlook` | Office 365 Outlook |

**Connection Details Field Mapping (SharePoint)**:
```python
{
    "sharePointSiteUrl": ["siteUrl", "url", "baseUrl"]
}
```

### Azure Services Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `AzureFunction` | `AzureFunction` | Azure Functions |
| `AzureServiceBus` | `AzureServiceBus` | Service Bus |
| `AzureSearch` | `AzureAISearch` | Azure AI Search (formerly Cognitive Search) |
| `AzureDataExplorer` | `AzureDataExplorer` | Azure Data Explorer (Kusto) |
| `AzureKeyVault` | `AzureKeyVault` | Azure Key Vault |
| `EventHub` | `EventHub` | Azure Event Hubs |

**Connection Details Field Mapping (Azure Data Explorer)**:
```python
{
    "cluster": ["endpoint", "clusterUri"],
    "database": ["database", "databaseName"]
}
```

### Cloud Platform Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `AmazonS3` | `AmazonS3` | Amazon S3 |
| `GoogleCloudStorage` | `GoogleCloudStorage` | Google Cloud Storage |
| `Snowflake` | `Snowflake` | Snowflake Data Warehouse |
| `Databricks` | `Databricks` | Azure Databricks |

**Connection Details Field Mapping (Databricks)**:
```python
{
    "httpPath": ["httpPath", "path"]  # Databricks cluster HTTP path
}
```

### CRM and ERP Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `Dynamics` | `DynamicsCrm` | Dynamics 365 |
| `DynamicsCrm` | `DynamicsCrm` | Dynamics CRM |
| `DynamicsAX` | `DynamicsAX` | Dynamics AX |
| `Salesforce` | `Salesforce` | Salesforce |
| `CommonDataServiceForApps` | `CommonDataServiceForApps` | Power Platform Dataverse |

### Analytics and BI Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `GoogleAnalytics` | `GoogleAnalytics` | Google Analytics |
| `AzureDataLakeAnalytics` | `AzureDataLakeAnalytics` | Azure Data Lake Analytics |
| `AmazonRedshift` | `AmazonRedshift` | Amazon Redshift |

### Development and Collaboration Connectors

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `GitHub` | `GitHub` | GitHub repositories |
| `Tfs` | `VSTS` | Azure DevOps (formerly TFS/VSTS) |

### Fallback Mapping

| ADF LinkedService Type | Fabric Connection Type | Notes |
|------------------------|------------------------|-------|
| `CustomDataSource` | `Generic` | Generic/custom data source |
| **(any unmapped type)** | `Generic` | Fallback for unknown types |

---

## Activity Transformation Mappings

### Copy Activity Transformation

**ADF Structure**:
```json
{
  "type": "Copy",
  "inputs": [{"referenceName": "SourceDataset"}],
  "outputs": [{"referenceName": "SinkDataset"}],
  "typeProperties": {
    "source": { "type": "AzureSqlSource" },
    "sink": { "type": "AzureSqlSink" },
    "enableStaging": true,
    "stagingSettings": {
      "linkedServiceName": {"referenceName": "StagingStorage"}
    }
  }
}
```

**Fabric Structure**:
```json
{
  "type": "Copy",
  "typeProperties": {
    "source": {
      "type": "AzureSqlSource",
      "datasetSettings": {
        "type": "AzureSqlTable",
        "externalReferences": {
          "connection": "<fabric-connection-id>"
        }
      }
    },
    "sink": {
      "type": "AzureSqlSink",
      "datasetSettings": {
        "type": "AzureSqlTable",
        "externalReferences": {
          "connection": "<fabric-connection-id>"
        }
      }
    },
    "enableStaging": true,
    "stagingSettings": {
      "path": "staging",
      "externalReferences": {
        "connection": "<staging-connection-id>"
      }
    }
  }
}
```

**Transformation Rules**:
1. **Dataset Embedding**: Datasets are embedded as `datasetSettings` in source/sink
2. **LinkedService → Connection**: `linkedServiceName.referenceName` → `externalReferences.connection`
3. **Staging**: Staging LinkedService converted to connection reference
4. **Parameter Substitution**: Dataset parameters resolved at transformation time

### Lookup Activity Transformation

**ADF Structure**:
```json
{
  "type": "Lookup",
  "typeProperties": {
    "dataset": {"referenceName": "LookupDataset"},
    "source": {"type": "AzureSqlSource"}
  }
}
```

**Fabric Structure**:
```json
{
  "type": "Lookup",
  "typeProperties": {
    "datasetSettings": {
      "type": "AzureSqlTable",
      "externalReferences": {
        "connection": "<fabric-connection-id>"
      }
    },
    "source": {"type": "AzureSqlSource"}
  }
}
```

### GetMetadata Activity Transformation

**ADF Structure**:
```json
{
  "type": "GetMetadata",
  "typeProperties": {
    "dataset": {"referenceName": "MetadataDataset"},
    "fieldList": ["exists", "size"]
  }
}
```

**Fabric Structure**:
```json
{
  "type": "GetMetadata",
  "typeProperties": {
    "datasetSettings": {
      "type": "DelimitedText",
      "externalReferences": {
        "connection": "<fabric-connection-id>"
      }
    },
    "fieldList": ["exists", "size"]
  }
}
```

### Delete Activity Transformation

**ADF Structure**:
```json
{
  "type": "Delete",
  "typeProperties": {
    "dataset": {"referenceName": "DeleteDataset"},
    "recursive": true,
    "wildcardFileName": "*.txt"
  }
}
```

**Fabric Structure**:
```json
{
  "type": "Delete",
  "typeProperties": {
    "datasetSettings": {
      "type": "DelimitedText",
      "externalReferences": {
        "connection": "<fabric-connection-id>"
      }
    },
    "recursive": true,
    "wildcardFileName": "*.txt"
  }
}
```

### ExecutePipeline → InvokePipeline Transformation

**ADF Structure**:
```json
{
  "type": "ExecutePipeline",
  "typeProperties": {
    "pipeline": {"referenceName": "ChildPipeline"},
    "parameters": {"param1": "value1"}
  }
}
```

**Fabric Structure**:
```json
{
  "type": "InvokePipeline",
  "typeProperties": {
    "pipeline": {"referenceName": "ChildPipeline"},
    "parameters": {"param1": "value1"}
  },
  "externalReferences": {
    "connection": "<fabric-data-pipelines-connection-id>"
  }
}
```

**Critical Note**: ExecutePipeline requires a synthetic `FabricDataPipelines` LinkedService mapping for the connection reference.

### Custom Activity Transformation

**ADF Structure**:
```json
{
  "type": "Custom",
  "linkedServiceName": {"referenceName": "BatchLinkedService"},
  "typeProperties": {
    "command": "mycommand.exe",
    "resourceLinkedService": {"referenceName": "StorageLinkedService"},
    "referenceObjects": {
      "linkedServices": [
        {"referenceName": "LinkedService1"},
        {"referenceName": "LinkedService2"}
      ]
    }
  }
}
```

**Fabric Structure**:
```json
{
  "type": "Custom",
  "typeProperties": {
    "command": "mycommand.exe",
    "externalReferences": {
      "connection": "<resource-storage-connection-id>"
    },
    "extendedProperties": {
      "referenceObjects": {
        "linkedServices": [
          {"referenceName": "LinkedService1"},
          {"referenceName": "LinkedService2"}
        ]
      }
    }
  },
  "externalReferences": {
    "connection": "<batch-connection-id>"
  }
}
```

**4-Tier Connection Resolution** (Priority Order):
1. **Reference ID Mapping**: Use `referenceId` from UI mapping table
2. **Name-based Mapping**: Match `linkedServiceName.referenceName` directly
3. **LinkedService Bridge**: Fallback to bridge lookup table
4. **Connection Service**: Use deployed connection registry

**Reference Locations**:
- Activity-level: `linkedServiceName` → `externalReferences.connection`
- Resource-level: `typeProperties.resourceLinkedService` → `typeProperties.externalReferences.connection`
- Reference objects: `typeProperties.referenceObjects.linkedServices[]` → preserved in `extendedProperties`

### Control Flow Activities (No Transformation)

These activities require no special transformation as they don't reference external resources:

| Activity Type | Transformation | Notes |
|---------------|----------------|-------|
| `ForEach` | None | Nested activities transformed recursively |
| `IfCondition` | None | True/false branch activities transformed |
| `Until` | None | Loop activities transformed recursively |
| `Switch` | None | Case activities transformed recursively |
| `Wait` | None | Simple wait duration |
| `SetVariable` | None | Variable assignment |
| `AppendVariable` | None | Array variable append |
| `Filter` | None | Array filtering |

### Web Activity Transformation

**ADF Structure**:
```json
{
  "type": "Web",
  "typeProperties": {
    "url": "https://api.example.com/endpoint",
    "method": "POST",
    "linkedServices": [
      {"referenceName": "AuthLinkedService"}
    ]
  },
  "linkedServiceName": {"referenceName": "WebLinkedService"}
}
```

**Fabric Structure**:
```json
{
  "type": "Web",
  "typeProperties": {
    "url": "https://api.example.com/endpoint",
    "method": "POST"
  },
  "externalReferences": {
    "connection": "<web-connection-id>"
  }
}
```

**LinkedServices Array Handling**: Each LinkedService in the array is mapped separately with index-based referenceIds.

### DatabricksNotebook Transformation (Optional)

**ADF Structure**:
```json
{
  "type": "DatabricksNotebook",
  "linkedServiceName": {"referenceName": "DatabricksLinkedService"},
  "typeProperties": {
    "notebookPath": "/notebooks/mynotebook",
    "baseParameters": {"param1": "value1"}
  }
}
```

**Fabric Structure (Standard)**:
```json
{
  "type": "DatabricksNotebook",
  "typeProperties": {
    "notebookPath": "/notebooks/mynotebook",
    "baseParameters": {"param1": "value1"}
  },
  "externalReferences": {
    "connection": "<databricks-connection-id>"
  }
}
```

**Fabric Structure (TridentNotebook Conversion)** - When `enable_databricks_to_trident=True`:
```json
{
  "type": "TridentNotebook",
  "typeProperties": {
    "notebookId": "<fabric-notebook-id>",
    "parameters": {"param1": "value1"}
  },
  "externalReferences": {
    "connection": "<lakehouse-connection-id>"
  }
}
```

**Property Mappings for TridentNotebook**:
- `notebookPath` → `notebookId` (requires lookup from resolution.json)
- `baseParameters` → `parameters`
- `linkedServiceName` → Mapped to Lakehouse connection

### Script Activity Transformation

**ADF Structure**:
```json
{
  "type": "Script",
  "linkedServiceName": {"referenceName": "SqlLinkedService"},
  "typeProperties": {
    "scripts": [
      {"type": "Query", "text": "SELECT * FROM Table"}
    ]
  }
}
```

**Fabric Structure**:
```json
{
  "type": "Script",
  "typeProperties": {
    "scripts": [
      {"type": "Query", "text": "SELECT * FROM Table"}
    ]
  },
  "externalReferences": {
    "connection": "<sql-connection-id>"
  }
}
```

### SqlServerStoredProcedure Activity Transformation

**ADF Structure**:
```json
{
  "type": "SqlServerStoredProcedure",
  "linkedServiceName": {"referenceName": "SqlLinkedService"},
  "typeProperties": {
    "storedProcedureName": "sp_MyProcedure",
    "storedProcedureParameters": {"param1": {"value": "value1"}}
  }
}
```

**Fabric Structure**:
```json
{
  "type": "SqlServerStoredProcedure",
  "typeProperties": {
    "storedProcedureName": "sp_MyProcedure",
    "storedProcedureParameters": {"param1": {"value": "value1"}}
  },
  "externalReferences": {
    "connection": "<sql-connection-id>"
  }
}
```

---

## Authentication Method Conversions

### Managed Identity → Workspace Identity

**ADF Configuration**:
```json
{
  "type": "AzureSqlDatabase",
  "typeProperties": {
    "connectionString": "Server=myserver.database.windows.net;Database=mydb;",
    "authenticationType": "ManagedIdentity"
  }
}
```

**Fabric Configuration**:
```json
{
  "connectorType": "AzureSqlDatabase",
  "connectionDetails": {
    "server": "myserver.database.windows.net",
    "database": "mydb",
    "authenticationType": "WorkspaceIdentity"
  }
}
```

**Post-Migration Requirements**:
1. Grant Fabric Workspace Identity same permissions as ADF Managed Identity
2. Update firewall rules
3. Test connection in Fabric

### Service Principal Authentication

**ADF Configuration**:
```json
{
  "type": "AzureDataLakeStore",
  "typeProperties": {
    "dataLakeStoreUri": "https://mydatalake.azuredatalakestore.net",
    "servicePrincipalId": "app-id",
    "servicePrincipalKey": {"type": "SecureString", "value": "secret"},
    "tenant": "tenant-id"
  }
}
```

**Fabric Configuration**:
```json
{
  "connectorType": "AzureDataLakeStorageGen1",
  "connectionDetails": {
    "url": "https://mydatalake.azuredatalakestore.net",
    "authenticationType": "ServicePrincipal",
    "servicePrincipalId": "app-id",
    "servicePrincipalKey": "secret",
    "tenantId": "tenant-id"
  }
}
```

### SQL Authentication

**ADF Configuration**:
```json
{
  "type": "SqlServer",
  "typeProperties": {
    "connectionString": "Server=myserver;Database=mydb;User ID=user;Password=****;",
    "authenticationType": "SqlAuthentication"
  }
}
```

**Fabric Configuration**:
```json
{
  "connectorType": "SqlServer",
  "connectionDetails": {
    "server": "myserver",
    "database": "mydb",
    "authenticationType": "Basic",
    "username": "user",
    "password": "****"
  },
  "gatewayId": "gateway-id-here"
}
```

### Key-Based Authentication (Storage)

**ADF Configuration**:
```json
{
  "type": "AzureBlobStorage",
  "typeProperties": {
    "connectionString": "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=****;",
    "authenticationType": "AccountKey"
  }
}
```

**Fabric Configuration**:
```json
{
  "connectorType": "AzureBlobStorage",
  "connectionDetails": {
    "accountName": "myaccount",
    "authenticationType": "Key",
    "accountKey": "****"
  }
}
```

### Authentication Method Mapping Table

| ADF Authentication Type | Fabric Authentication Type | Notes |
|-------------------------|----------------------------|-------|
| `ManagedIdentity` | `WorkspaceIdentity` | Requires permission grant |
| `ServicePrincipal` | `ServicePrincipal` | Direct mapping |
| `SqlAuthentication` | `Basic` | Username/password |
| `AccountKey` | `Key` | Storage account key |
| `SasUri` | `SAS` | Shared Access Signature |
| `OAuth2` | `OAuth2` | OAuth 2.0 authentication |
| `Windows` | `Windows` | Windows authentication (on-premises) |
| `Anonymous` | `Anonymous` | No authentication |

---

## Global Parameter Migration

### ADF Global Parameters Structure

**ADF Factory Definition**:
```json
{
  "globalParameters": {
    "Environment": {
      "type": "String",
      "value": "Production"
    },
    "MaxRetries": {
      "type": "Int",
      "value": 3
    },
    "EnableLogging": {
      "type": "Bool",
      "value": true
    }
  }
}
```

### Fabric Variable Library Structure

**Fabric Variable Library**:
```json
{
  "displayName": "MyFactory_GlobalParameters_VariableLibrary",
  "description": "Migrated from ADF global parameters",
  "definition": {
    "variables": [
      {
        "name": "VariableLibrary_Environment",
        "type": "String",
        "defaultValue": "Production",
        "description": "Migrated from ADF global parameter: Environment"
      },
      {
        "name": "VariableLibrary_MaxRetries",
        "type": "Integer",
        "defaultValue": 3,
        "description": "Migrated from ADF global parameter: MaxRetries"
      },
      {
        "name": "VariableLibrary_EnableLogging",
        "type": "Boolean",
        "defaultValue": true,
        "description": "Migrated from ADF global parameter: EnableLogging"
      }
    ]
  }
}
```

### Expression Transformation Patterns

**Pattern 1: Standard Format**

ADF Expression:
```
@pipeline().globalParameters.Environment
```

Fabric Expression:
```
@variableLibrary('MyFactory_GlobalParameters_VariableLibrary').VariableLibrary_Environment
```

**Pattern 2: Curly-Brace Format**

ADF Expression:
```
@{pipeline().globalParameters.MaxRetries}
```

Fabric Expression:
```
@{variableLibrary('MyFactory_GlobalParameters_VariableLibrary').VariableLibrary_MaxRetries}
```

**Pattern 3: Function-Wrapped Format**

ADF Expression:
```
@concat('Retries:', string(pipeline().globalParameters.MaxRetries))
```

Fabric Expression:
```
@concat('Retries:', string(variableLibrary('MyFactory_GlobalParameters_VariableLibrary').VariableLibrary_MaxRetries))
```

### Data Type Mapping

| ADF Global Parameter Type | Fabric Variable Library Type | Notes |
|---------------------------|------------------------------|-------|
| `String` | `String` | Direct mapping |
| `Int` | `Integer` | Direct mapping |
| `Float` | `Number` | Direct mapping |
| `Bool` | `Boolean` | Direct mapping |
| `Array` | `String` | Serialized as JSON string |
| `Object` | `String` | Serialized as JSON string |
| `SecureString` | `String` | Marked as secure, requires actual value |

### libraryVariables Injection

**ADF Pipeline** (Original):
```json
{
  "name": "MyPipeline",
  "properties": {
    "activities": [
      {
        "name": "WebActivity",
        "type": "Web",
        "typeProperties": {
          "url": "@{pipeline().globalParameters.ApiEndpoint}",
          "body": {"env": "@{pipeline().globalParameters.Environment}"}
        }
      }
    ]
  }
}
```

**Fabric Pipeline** (Transformed):
```json
{
  "name": "MyPipeline",
  "properties": {
    "libraryVariables": {
      "MyFactory_VariableLibrary_ApiEndpoint": {
        "type": "String",
        "value": "https://api.example.com",
        "variableLibrary": "MyFactory_GlobalParameters_VariableLibrary"
      },
      "MyFactory_VariableLibrary_Environment": {
        "type": "String",
        "value": "Production",
        "variableLibrary": "MyFactory_GlobalParameters_VariableLibrary"
      }
    },
    "activities": [
      {
        "name": "WebActivity",
        "type": "Web",
        "typeProperties": {
          "url": "@{variableLibrary('MyFactory_GlobalParameters_VariableLibrary').VariableLibrary_ApiEndpoint}",
          "body": {"env": "@{variableLibrary('MyFactory_GlobalParameters_VariableLibrary').VariableLibrary_Environment}"}
        }
      }
    ]
  }
}
```

### Detection Regex Patterns

The tool uses three regex patterns to detect global parameter usage:

```python
patterns = {
    # Standard: @pipeline().globalParameters.paramName
    "standard": r"@pipeline\(\)\.globalParameters\.(\w+)",
    
    # Curly-brace: @{pipeline().globalParameters.paramName}
    "curly": r"@\{pipeline\(\)\.globalParameters\.(\w+)\}",
    
    # Nested: pipeline().globalParameters.paramName (in functions)
    "nested": r"(?<!@)(?<!@\{)pipeline\(\)\.globalParameters\.(\w+)"
}
```

---

## Dataset to DatasetSettings Transformation

### Transformation Rules

1. **Separate Dataset Definition** → **Embedded datasetSettings**
2. **LinkedService Reference** → **externalReferences.connection**
3. **Parameter Substitution** → Resolved at transformation time
4. **Type Properties** → Preserved in datasetSettings

### Copy Activity Example

**ADF Dataset Definition**:
```json
{
  "name": "SourceDataset",
  "type": "Microsoft.DataFactory/factories/datasets",
  "properties": {
    "type": "DelimitedText",
    "linkedServiceName": {"referenceName": "AzureBlobStorage1"},
    "typeProperties": {
      "location": {
        "type": "AzureBlobStorageLocation",
        "folderPath": "@dataset().FolderPath",
        "fileName": "data.csv",
        "container": "container1"
      },
      "columnDelimiter": ",",
      "escapeChar": "\\",
      "firstRowAsHeader": true
    },
    "parameters": {
      "FolderPath": {"type": "string"}
    }
  }
}
```

**ADF Activity Reference**:
```json
{
  "type": "Copy",
  "inputs": [
    {
      "referenceName": "SourceDataset",
      "parameters": {"FolderPath": "@pipeline().parameters.SourceFolder"}
    }
  ]
}
```

**Fabric Embedded DatasetSettings**:
```json
{
  "type": "Copy",
  "typeProperties": {
    "source": {
      "type": "DelimitedTextSource",
      "datasetSettings": {
        "type": "DelimitedText",
        "typeProperties": {
          "location": {
            "type": "AzureBlobStorageLocation",
            "folderPath": "@pipeline().parameters.SourceFolder",
            "fileName": "data.csv",
            "container": "container1"
          },
          "columnDelimiter": ",",
          "escapeChar": "\\",
          "firstRowAsHeader": true
        },
        "externalReferences": {
          "connection": "<fabric-connection-id>"
        }
      }
    }
  }
}
```

**Key Changes**:
1. Dataset definition embedded in activity
2. `@dataset().FolderPath` replaced with `@pipeline().parameters.SourceFolder`
3. `linkedServiceName` converted to `externalReferences.connection`
4. Type properties preserved

### Parameter Resolution

**Supported Parameter References**:
- `@dataset().parameterName` - Direct parameter reference
- `@{dataset().parameterName}` - Expression-wrapped parameter
- `@pipeline().parameters.X` - Pipeline parameter reference
- `@activity('ActivityName').output.Y` - Activity output reference
- `@variables('VariableName')` - Pipeline variable reference

**Resolution Process**:
1. Extract parameter values from activity inputs/outputs
2. Substitute parameter references with actual values or pipeline expressions
3. Embed resolved configuration into datasetSettings

---

## Property Mappings

### Connection String Parsing

**SQL Server Connection String**:
```
Input (ADF): "Server=myserver;Database=mydb;User ID=user;Password=****;"
Output (Fabric):
{
  "server": "myserver",
  "database": "mydb",
  "username": "user",
  "password": "****"
}
```

**Azure Storage Connection String**:
```
Input (ADF): "DefaultEndpointsProtocol=https;AccountName=myaccount;AccountKey=****;"
Output (Fabric):
{
  "accountName": "myaccount",
  "accountKey": "****"
}
```

### URL Extraction

**ADLS Gen2 URL**:
```
Input (ADF): "https://mystorage.dfs.core.windows.net"
Output (Fabric):
{
  "accountName": "mystorage"
}
```

**REST Service URL**:
```
Input (ADF): "https://api.example.com/v1"
Output (Fabric):
{
  "url": "https://api.example.com/v1"
}
```

### Privacy Level Assignment

**Default Privacy Levels**:
- Azure cloud services: `Organizational`
- On-premises resources: `Private`
- Public APIs: `Public`

**Privacy Level Enum**:
```python
class PrivacyLevel(str, Enum):
    PUBLIC = "Public"
    ORGANIZATIONAL = "Organizational"
    PRIVATE = "Private"
```

---

## Expression Transformations

### Global Parameter Expressions

See [Global Parameter Migration](#global-parameter-migration) section for complete details.

### Dataset Parameter Expressions

**ADF**:
```
@dataset().FolderPath
```

**Fabric** (resolved):
```
@pipeline().parameters.SourceFolder
```

### Pipeline Parameter Expressions

**No transformation required** - these work the same in both ADF and Fabric:
```
@pipeline().parameters.ParameterName
@pipeline().DataFactory
@pipeline().Pipeline
@pipeline().RunId
```

### Activity Output Expressions

**No transformation required** - these work the same in both ADF and Fabric:
```
@activity('ActivityName').output.firstRow.columnName
@activity('ActivityName').output.count
```

### Variable Expressions

**No transformation required** - these work the same in both ADF and Fabric:
```
@variables('VariableName')
@item()  # ForEach iteration
```

---

## Reference Location Patterns

### Reference ID Format

**Standard**: `{pipelineName}_{activityName}_{location}`

**Examples**:
- `MyPipeline_CopyActivity1_source` - Copy source dataset
- `MyPipeline_CopyActivity1_sink` - Copy sink dataset
- `MyPipeline_CopyActivity1_staging` - Copy staging storage
- `MyPipeline_CustomActivity1_activity` - Custom activity-level LinkedService
- `MyPipeline_CustomActivity1_resource` - Custom resource LinkedService
- `MyPipeline_CustomActivity1_refobj_0` - Custom reference object (index 0)
- `MyPipeline_WebActivity1_linkedService_0` - Web LinkedService (index 0)
- `MyPipeline_ExecutePipeline1_invoke` - Pipeline invocation connection
- `HDInsightPipeline_SparkActivity1_cluster` - HDInsight cluster
- `HDInsightPipeline_SparkActivity1_script` - HDInsight script storage

### Location Types

| Location | Description | Activity Types | Required |
|----------|-------------|----------------|----------|
| `invoke` | Pipeline invocation | ExecutePipeline | Yes |
| `activity` / `activity-level` | Direct activity LinkedService | Custom, Script, StoredProcedure, Databricks | Yes |
| `dataset` | Dataset-based connection | Copy, Lookup, GetMetadata, Delete | Yes |
| `source` | Copy source dataset | Copy | Yes |
| `sink` | Copy sink dataset | Copy | Yes |
| `staging` | Copy staging storage | Copy (when enableStaging=true) | Dynamic |
| `cluster` | HDInsight cluster | HDInsight* activities | Yes |
| `script` | HDInsight script storage | HDInsight activities | No |
| `jar` | HDInsight JAR storage | HDInsightSpark, HDInsightMapReduce | No |
| `file` | HDInsight file storage | HDInsight activities | No |
| `sparkJob` | HDInsight Spark job storage | HDInsightSpark | No |
| `linkedServices` | Web LinkedServices array | Web, WebHook | No |
| `resource` | Custom resource LinkedService | Custom | No |
| `reference-object` / `refobj_N` | Custom reference objects | Custom | No |

### Extraction Patterns

**ExecutePipeline** (synthetic LinkedService):
```python
{
  "referenceId": f"{pipelineName}_{activityName}_invoke",
  "location": "invoke",
  "linkedServiceName": "FabricDataPipelines",  # Synthetic
  "displayName": f"Invoke Pipeline: {targetPipelineName}",
  "isRequired": True
}
```

**Copy with Staging**:
```python
if activity.typeProperties.get("enableStaging"):
    {
      "referenceId": f"{pipelineName}_{activityName}_staging",
      "location": "staging",
      "linkedServiceName": stagingLinkedServiceName,
      "displayName": "Staging Storage",
      "isRequired": True  # Dynamic based on enableStaging flag
    }
```

**Custom Activity (3 locations)**:
```python
# Activity-level
{
  "referenceId": f"{pipelineName}_{activityName}_activity",
  "location": "activity-level",
  "linkedServiceName": activity.linkedServiceName.referenceName,
  "isRequired": True
}

# Resource-level
{
  "referenceId": f"{pipelineName}_{activityName}_resource",
  "location": "resource",
  "linkedServiceName": activity.typeProperties.resourceLinkedService.referenceName,
  "isRequired": False
}

# Reference objects (array)
for index, ls in enumerate(activity.typeProperties.referenceObjects.linkedServices):
    {
      "referenceId": f"{pipelineName}_{activityName}_refobj_{index}",
      "location": "reference-object",
      "linkedServiceName": ls.referenceName,
      "arrayIndex": index,
      "isRequired": False
    }
```

**Web Activity (LinkedServices array)**:
```python
# Activity-level LinkedService (optional)
if activity.linkedServiceName:
    {
      "referenceId": f"{pipelineName}_{activityName}_activity",
      "location": "activity-level",
      "isRequired": False
    }

# LinkedServices array (loop all, not just [0])
for index, ls in enumerate(activity.typeProperties.linkedServices):
    {
      "referenceId": f"{pipelineName}_{activityName}_linkedService_{index}",
      "location": "linkedServices",
      "linkedServiceName": ls.referenceName,
      "arrayIndex": index,
      "isRequired": False
    }
```

---

## Additional Mapping Resources

### Gateway Requirements

**Connectors Requiring Gateway**:
- `OnPremisesSql`
- `OnPremisesOracle`
- `OnPremisesFileSystem`
- `FileServer`
- `SelfHosted`
- `Hdfs`

**Gateway Types**:
- `VirtualNetwork` - For Azure VNet resources
- `OnPremises` - For on-premises data sources

### Mapping Confidence Levels

| Confidence Level | Description | Examples |
|------------------|-------------|----------|
| `HIGH` | Well-tested, direct mapping | SqlServer, AzureSqlDatabase, AzureBlobStorage |
| `MEDIUM` | Supported but may need adjustment | Databricks, HDInsight, Custom connectors |
| `LOW` | Limited support or fallback mapping | Generic, CustomDataSource |

### Special Handling Types

These connector types require special handling during migration:

- `HttpServer` - Maps to Web but needs URL transformation
- `CustomDataSource` - Always mapped to Generic
- `FileServer` - May need gateway configuration

---

## Code References

### Key Source Files

1. **connector_mapper.py** (Line 14-82):
   - `ADF_TO_FABRIC_TYPE_MAP` - Complete connector type mapping dictionary
   - 80+ connector mappings defined

2. **connector_mapper.py** (Line 86-142):
   - `CONNECTION_DETAILS_FIELD_MAPPING` - Field mapping for each connector type
   - Handles variations in property names between ADF and Fabric

3. **global_parameter_transformer.py** (Line 36-45):
   - Three regex patterns for detecting global parameter expressions
   - Standard, curly-brace, and function-wrapped formats

4. **activity_transformer.py** (Line 80-100):
   - Main activity transformation logic
   - Activity type-specific transformations

5. **transformer.py** (Line 89-100):
   - Pipeline-level transformation orchestration
   - Coordinates activity, parameter, and expression transformations

6. **models.py** (Line 13-82):
   - Data type definitions and enumerations
   - ComponentType, CompatibilityStatus, FabricTargetType, etc.

### Resolution Configuration

**resolution.json** - Runtime configuration for mappings:
```json
{
  "workspaceId": "95e132cd-cf5f-4e15-a9e1-7506994aa23c",
  "linkedServiceToConnectionId": {
    "ADF_LinkedService_Name": "fabric-connection-id"
  },
  "notebookIdByActivityName": {
    "NotebookActivityName": "fabric-notebook-id"
  }
}
```

---

## Summary

This reference document provides comprehensive mapping information for:

1. **50+ Connector Types** - LinkedService to Connection mappings
2. **20+ Activity Types** - Activity transformation rules
3. **5 Authentication Methods** - Authentication conversion patterns
4. **3 Expression Patterns** - Global parameter expression transformations
5. **14 Reference Locations** - Connection reference patterns by activity type

**Mapping Approach**:
- **Direct Mapping** - Where possible (SqlServer → SqlServer)
- **Generic Mapping** - For similar types (AzureSqlDatabase → SQL)
- **Fallback Mapping** - For unsupported types (Unknown → Generic)
- **4-Tier Resolution** - For complex scenarios (Custom activities)

**Key Transformation Principles**:
1. Datasets are embedded as `datasetSettings` in activities
2. LinkedServices become `externalReferences.connection` with connection IDs
3. Global parameters migrate to Variable Libraries with expression transformation
4. Managed Identity converts to Workspace Identity
5. Authentication methods map to Fabric equivalents

For implementation details, see the source code in `tools/FabricDataFactoryMigrationAssistant/adf_fabric_migrator/`.

---

*Last Updated: December 26, 2024*
*Source: FabricDataFactoryMigrationAssistant v1.0*
