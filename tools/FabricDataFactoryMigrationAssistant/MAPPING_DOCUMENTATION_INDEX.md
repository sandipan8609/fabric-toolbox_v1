# ADF to Fabric Mapping - Documentation Index

## 📚 Overview

This directory contains comprehensive documentation for understanding how the FabricDataFactoryMigrationAssistant tool converts Azure Data Factory (ADF) and Azure Synapse Analytics pipelines to Microsoft Fabric Data Pipelines.

---

## 📄 Documentation Files

### 1. **ADF_TO_FABRIC_MAPPING_REFERENCE.md** ⭐ Main Reference
**Purpose**: Comprehensive technical reference for all mapping rules

**Contains**:
- 50+ connector type mappings (LinkedService → Connection)
- 20+ activity transformation patterns
- Authentication method conversions (ManagedIdentity → WorkspaceIdentity)
- Global parameter migration details (ADF → Variable Libraries)
- Dataset to datasetSettings transformation rules
- Expression transformation patterns
- Reference ID location patterns
- Property field mappings

**Use When**: You need detailed technical information about specific mappings or transformations

**Key Sections**:
- Connector Type Mappings (SQL, Storage, Web, Azure Services, Cloud Platforms, CRM/ERP)
- Activity Transformation Mappings (Copy, Lookup, Custom, ExecutePipeline, etc.)
- Authentication Method Conversions
- Global Parameter Migration
- Dataset Embedding Patterns
- Reference Location Patterns

---

### 2. **QUICK_MAPPING_GUIDE.md** ⚡ Quick Reference
**Purpose**: Fast lookup for common migration scenarios

**Contains**:
- Popular connector mappings table
- Common activity transformations
- Authentication conversion quick reference
- Global parameter expression patterns
- Dataset embedding overview
- Reference ID patterns
- Migration checklist
- Troubleshooting quick tips

**Use When**: You need a quick answer or reference for common mappings

**Key Sections**:
- Popular Connector Mappings (top 7)
- Activity Transformations at a Glance
- Authentication Conversions
- Global Parameters → Variable Libraries
- Migration Checklist
- Troubleshooting Quick Tips

---

### 3. **CONNECTOR_MAPPING.md** 🔗 Connector Deep Dive
**Purpose**: Detailed connector mapping information with examples

**Contains**:
- Comprehensive connector type tables (50+ types)
- Gateway requirements
- Authentication methods per connector
- Connection details field mappings
- Property transformation examples
- Activity reference location types
- Migration best practices

**Use When**: You need specific information about LinkedService to Connection conversion

**Key Sections**:
- Cloud Databases (SQL, MySQL, PostgreSQL, etc.)
- Azure Storage (Blob, ADLS, Files, Tables)
- Web and REST Services
- Azure Services (Function, KeyVault, DataExplorer, etc.)
- Cloud Platforms (Snowflake, Databricks, AWS, GCP)
- CRM/ERP (Dynamics, Salesforce)
- Gateway Requirements
- Authentication Methods
- Activity Reference Location Types

---

### 4. **README.md** 📖 Tool Documentation
**Purpose**: Main documentation for the migration tool application

**Contains**:
- Tool overview and features
- Quick start guide
- Architecture details
- Data flow and privacy information
- User guide (step-by-step wizard)
- Deployment instructions
- Development setup
- Troubleshooting guide

**Use When**: You need to understand the tool itself, deployment, or usage

**Key Sections**:
- Key Features (upload-first profiling, connector mapping, global parameters)
- Quick Start (5-minute setup)
- User Guide (11-step wizard)
- Deployment to Azure
- Data Flow & Privacy
- Troubleshooting

---

## 🎯 Use Case → Document Mapping

### "I need to understand what ADF connector type maps to what Fabric connection type"
→ **QUICK_MAPPING_GUIDE.md** (Popular Connectors table)  
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Complete connector mappings)  
→ **CONNECTOR_MAPPING.md** (Detailed connector information)

### "I need to know how Copy activities are transformed"
→ **QUICK_MAPPING_GUIDE.md** (Activity transformations overview)  
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Copy Activity Transformation section)  
→ **CONNECTOR_MAPPING.md** (Copy Activities with Multiple Datasets)

### "I need to migrate global parameters"
→ **QUICK_MAPPING_GUIDE.md** (Quick expression conversion)  
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Global Parameter Migration section - complete details)  
→ **README.md** (Global Parameters Migration feature description)

### "I need to understand authentication conversions"
→ **QUICK_MAPPING_GUIDE.md** (Authentication Conversions table)  
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Authentication Method Conversions section)  
→ **CONNECTOR_MAPPING.md** (Authentication Methods section)

### "I need to deploy the migration tool"
→ **README.md** (Deployment section)  
→ **DEPLOYMENT.md** (if exists - detailed deployment guide)

### "I need to troubleshoot migration issues"
→ **QUICK_MAPPING_GUIDE.md** (Troubleshooting Quick Tips)  
→ **README.md** (Troubleshooting section - comprehensive)  
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Technical details for specific issues)

### "I need to understand dataset transformation"
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Dataset to DatasetSettings Transformation)  
→ **CONNECTOR_MAPPING.md** (Dataset Handling section)  
→ **README.md** (Dataset & Activity Support)

### "I need reference ID patterns for custom activities"
→ **QUICK_MAPPING_GUIDE.md** (Reference ID Patterns table)  
→ **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Reference Location Patterns - detailed)  
→ **CONNECTOR_MAPPING.md** (Activity Reference Location Types)

---

## 🔍 Finding Specific Information

### By Connector Type
1. Check **QUICK_MAPPING_GUIDE.md** for popular types
2. Look up in **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Connector Type Mappings section)
3. Get details from **CONNECTOR_MAPPING.md** (Supported Connectors section)

### By Activity Type
1. Check **QUICK_MAPPING_GUIDE.md** (Activity Transformations at a Glance)
2. Look up in **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Activity Transformation Mappings)
3. Get examples from **CONNECTOR_MAPPING.md** (Activity-Dataset Relationships)

### By Authentication Method
1. Check **QUICK_MAPPING_GUIDE.md** (Authentication Conversions)
2. Get details from **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Authentication Method Conversions)
3. See connector-specific auth in **CONNECTOR_MAPPING.md**

### By Expression Type
1. Check **QUICK_MAPPING_GUIDE.md** (Global Parameters expression)
2. Get patterns from **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (Expression Transformations)
3. Understand detection in **README.md** (Global Parameters Migration)

---

## 📊 Document Comparison

| Feature | Quick Guide | Mapping Reference | Connector Mapping | README |
|---------|-------------|-------------------|-------------------|--------|
| **Length** | Short (~6KB) | Comprehensive (~35KB) | Detailed (~20KB) | Full (~50KB) |
| **Depth** | Overview | Deep technical | Connector-focused | Tool-focused |
| **Format** | Tables & lists | Structured sections | Mixed | Mixed |
| **Examples** | Minimal | Many code examples | Configuration examples | User scenarios |
| **Best For** | Quick lookup | Technical reference | Connector details | Tool usage |

---

## 🗂️ Source Code References

The mapping logic is implemented in these Python files:

| File | Purpose | Key Content |
|------|---------|-------------|
| `connector_mapper.py` | Connector type mappings | `ADF_TO_FABRIC_TYPE_MAP` (80+ mappings) |
| `transformer.py` | Pipeline transformation | Pipeline-level orchestration |
| `activity_transformer.py` | Activity transformation | Activity-specific logic |
| `global_parameter_transformer.py` | Global param expressions | 3 regex patterns for detection |
| `global_parameter_detector.py` | Global param detection | Scans pipelines for usage |
| `custom_activity_resolver.py` | Custom activity mapping | 4-tier connection resolution |
| `parser.py` | ARM template parsing | Extracts components from ARM JSON |
| `models.py` | Data models | TypeScript-equivalent dataclasses |

---

## 🎓 Learning Path

### For First-Time Users
1. Start with **README.md** (understand the tool)
2. Review **QUICK_MAPPING_GUIDE.md** (get familiar with common patterns)
3. Reference **ADF_TO_FABRIC_MAPPING_REFERENCE.md** as needed

### For Technical Implementers
1. Start with **ADF_TO_FABRIC_MAPPING_REFERENCE.md** (comprehensive mappings)
2. Deep dive into **CONNECTOR_MAPPING.md** (connector specifics)
3. Review source code (Python files) for implementation details

### For Specific Migration Tasks
1. Identify your scenario in this index
2. Follow the recommended document path
3. Check troubleshooting sections if issues arise

---

## 📞 Additional Resources

- **Microsoft Fabric Documentation**: https://learn.microsoft.com/fabric/
- **Fabric REST API Reference**: https://learn.microsoft.com/rest/api/fabric/
- **Azure Data Factory Documentation**: https://learn.microsoft.com/azure/data-factory/
- **GitHub Issues**: For bug reports and feature requests
- **Tool Source Code**: `tools/FabricDataFactoryMigrationAssistant/adf_fabric_migrator/`

---

## 🔄 Document Maintenance

**Last Updated**: December 26, 2024

**Maintained By**: Fabric Customer Advisory Team (CAT)

**Update Frequency**: As needed when:
- New connector types are supported
- Activity transformations change
- New features are added to the tool
- Fabric API updates require changes

**Feedback**: Create an issue in the GitHub repository if you find errors or have suggestions for improving this documentation.

---

*This index helps you navigate the comprehensive ADF to Fabric migration documentation.*
