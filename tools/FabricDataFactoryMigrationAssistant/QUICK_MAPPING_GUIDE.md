# ADF to Fabric Pipeline - Quick Mapping Guide

## 🚀 Quick Reference for Common Mappings

This guide provides quick lookup tables for the most common ADF to Fabric conversions.

---

## Popular Connector Mappings

| ADF Type | Fabric Type | Auth Options |
|----------|-------------|--------------|
| `AzureSqlDatabase` | `SQL` | WorkspaceIdentity, Basic, ServicePrincipal |
| `SqlServer` | `SqlServer` | Basic, Windows (with gateway) |
| `AzureBlobStorage` | `AzureBlobs` | WorkspaceIdentity, Key, SAS |
| `AzureDataLakeStoreGen2` | `AzureDataLakeStorage` | WorkspaceIdentity, ServicePrincipal |
| `RestService` | `RestService` | Anonymous, Basic, OAuth2, ApiKey |
| `Snowflake` | `Snowflake` | Basic, KeyPair, OAuth |
| `Databricks` | `Databricks` | AccessToken, WorkspaceIdentity |

---

## Activity Transformations at a Glance

### Copy Activity
```
Dataset Reference → datasetSettings embedding
linkedServiceName → externalReferences.connection
Parameters resolved at transformation time
```

### ExecutePipeline
```
ExecutePipeline → InvokePipeline
Requires synthetic "FabricDataPipelines" connection
```

### Custom Activity
```
3 LinkedService locations:
1. linkedServiceName → externalReferences.connection
2. resourceLinkedService → typeProperties.externalReferences.connection
3. referenceObjects → preserved in extendedProperties
```

### Control Flow Activities
```
ForEach, IfCondition, Until, Switch → No transformation needed
Nested activities transformed recursively
```

---

## Authentication Conversions

| ADF Auth | Fabric Auth | Migration Note |
|----------|-------------|----------------|
| `ManagedIdentity` | `WorkspaceIdentity` | Grant permissions to Workspace Identity |
| `ServicePrincipal` | `ServicePrincipal` | Copy client ID/secret |
| `SqlAuthentication` | `Basic` | Username/password |
| `AccountKey` | `Key` | Storage account key |

---

## Global Parameters → Variable Libraries

### Expression Conversion

```
ADF:    @pipeline().globalParameters.Environment
Fabric: @variableLibrary('MyFactory_GlobalParameters').VariableLibrary_Environment
```

### Data Types

| ADF Type | Fabric Type |
|----------|-------------|
| `String` | `String` |
| `Int` | `Integer` |
| `Float` | `Number` |
| `Bool` | `Boolean` |
| `Array` | `String` (JSON) |
| `Object` | `String` (JSON) |

---

## Dataset Embedding Pattern

```
ADF Dataset (separate):
├── name: "MyDataset"
├── linkedServiceName: "MyLinkedService"
└── typeProperties: {...}

Fabric datasetSettings (embedded):
├── type: "DatasetType"
├── typeProperties: {...}
└── externalReferences:
    └── connection: "<connection-id>"
```

---

## Reference ID Patterns

| Pattern | Example |
|---------|---------|
| Copy source | `Pipeline1_Copy1_source` |
| Copy sink | `Pipeline1_Copy1_sink` |
| Copy staging | `Pipeline1_Copy1_staging` |
| Custom activity | `Pipeline1_Custom1_activity` |
| Custom resource | `Pipeline1_Custom1_resource` |
| Pipeline invoke | `Pipeline1_Execute1_invoke` |
| Web LinkedService | `Pipeline1_Web1_linkedService_0` |

---

## Common Field Mappings

### SQL Connectors
```
connectionString → parsed to:
  - server
  - database
  - username (if SQL auth)
  - password (if SQL auth)
```

### Storage Connectors
```
url → accountName extracted
connectionString → accountName + accountKey
```

### Web Connectors
```
url → url (direct)
baseUrl → url
serviceUri → url
```

---

## Gateway Requirements

**Requires Gateway**:
- On-premises SQL Server
- File Server
- SFTP (if on-premises)
- Any "OnPremises*" connector

**No Gateway**:
- All Azure cloud services
- Public REST APIs
- SaaS applications (Salesforce, Dynamics, etc.)

---

## Migration Checklist

### Pre-Migration
- [ ] Export ADF ARM template with all dependencies
- [ ] Document current authentication methods
- [ ] List all global parameters used
- [ ] Identify on-premises data sources (gateway needed)

### During Migration
- [ ] Upload ARM template for profiling
- [ ] Review connector compatibility
- [ ] Map Managed Identity → Workspace Identity
- [ ] Configure connections with credentials
- [ ] Set up global parameters → Variable Library
- [ ] Map LinkedServices to connections

### Post-Migration
- [ ] Grant Workspace Identity required permissions
- [ ] Test all connections in Fabric
- [ ] Validate pipeline execution
- [ ] Update firewall rules if needed
- [ ] Enable schedules after testing

---

## Key Differences: ADF vs Fabric

| Feature | ADF | Fabric |
|---------|-----|--------|
| **Datasets** | Separate reusable components | Embedded in activities |
| **Connections** | LinkedServices | Connections (workspace-scoped) |
| **Identity** | Managed Identity | Workspace Identity |
| **Global Params** | Factory-level parameters | Variable Libraries |
| **Triggers** | Built-in scheduling | Separate schedule items |
| **Folders** | Native folder structure | Preserved in migration |

---

## Troubleshooting Quick Tips

### Connection Fails
✅ Check Workspace Identity permissions  
✅ Verify credentials are correct  
✅ Test connection in Fabric UI  
✅ Check firewall rules  

### Pipeline Deploy Fails
✅ Ensure all connections deployed first  
✅ Check for unsupported activities  
✅ Validate expression syntax  
✅ Review error message details  

### Global Parameters Not Working
✅ Verify Variable Library deployed  
✅ Check expression transformation applied  
✅ Ensure libraryVariables injected  
✅ Validate variable names match  

---

## Useful Links

- **Full Mapping Reference**: [ADF_TO_FABRIC_MAPPING_REFERENCE.md](./ADF_TO_FABRIC_MAPPING_REFERENCE.md)
- **Connector Mapping Details**: [CONNECTOR_MAPPING.md](./CONNECTOR_MAPPING.md)
- **Tool README**: [README.md](./README.md)
- **Microsoft Fabric Docs**: https://learn.microsoft.com/fabric/

---

*Quick reference guide for FabricDataFactoryMigrationAssistant*
