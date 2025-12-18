
import json
import uuid
import argparse
import sys
from copy import deepcopy

# ==========================================
# 1. CONFIGURATION
# ==========================================
CONFIG = {
    "workspace_id": "95e132cd-cf5f-4e15-a9e1-7506994aa23c",
    "notebook_id": "your_fabric_notebook_id",
    
    # Connections
    "warehouse_connection_id": "06f15094-5415-40ca-9647-985fa72a41fe",
    "lakehouse_connection_id": "e31de1f3-905a-400e-8c21-1bfcc5c7719c",
    "oracle_connection_id": "1320ffbd-c314-4267-be68-d3e63f7ff4df",
    
    # Artifacts
    "warehouse_artifact_id": "6068bf54-5806-44df-996b-f19fac38d18c",
    "warehouse_endpoint": "uz5qo3w55cyebj7ffmgl7aydcm-zuzodfk7z4ku5kpboudjssvchq.datawarehouse.fabric.microsoft.com",
    "lakehouse_artifact_id": "2d07daef-8c0b-454d-9a31-28faec11c440",
    "lakehouse_name": "lh_sbm_bronze_dev",

    # Optional: choose sink target for Copy activity ("blob" or "lakehouse")
    "target_sink": "lakehouse"  # change to "blob" if you want Blob as the output target
}

# ==========================================
# 2. DATA FLATTENING HELPERS
# ==========================================

def clean_val(val):
    """Sanitizes input values."""
    if str(val) == "[object Object]":
        return "FIX_ME_INVALID_OBJECT"
    return val

def get_flat_value(val):
    """
    Recursively drills down to get the raw primitive value (str/int/bool).
    Strips away any existing wrappers so we can re-format correctly.
    """
    if isinstance(val, dict):
        if "value" in val:
            return get_flat_value(val["value"])
        # Safer fallback: deterministic JSON for dicts without 'value'
        return json.dumps(val, ensure_ascii=False)
    if val is None:
        return ""
    return clean_val(val)

def is_expression(val):
    # Robust: expressions are strings that start with @ or = after trimming
    return isinstance(val, str) and val.strip().startswith(("@", "="))

# ==========================================
# 3. FORMATTERS
# ==========================================

def format_sp_param(val):
    """
    Stored Proc Parameters (Fabric):
    - Expression: { "value": { "value": "@...", "type": "Expression" }, "type": "String" }
    - Literal:    { "value": { "value": "...",  "type": "String"     }, "type": "String" }
    Matches the reference block provided by you.
    """
    raw = get_flat_value(val)
    return {
        "value": {
            "value": raw,
            "type": "Expression" if is_expression(raw) else "String"
        },
        "type": "String"
    }

def format_notebook_param(val):
    """
    Notebook Parameters: Strict Double Nesting
    { "value": { "value": "...", "type": "..." }, "type": "Expression" }
    """
    raw = get_flat_value(val)
    return {
        "value": {
            "value": raw,
            "type": "Expression" if is_expression(raw) else "String"
        },
        "type": "Expression"
    }

def format_invoke_param(val):
    """
    InvokePipeline Parameters: Conditional Nesting
    Expression -> double nested, outer type Expression
    Literal    -> single nested, type String
    """
    raw = get_flat_value(val)
    if is_expression(raw):
        return {
            "value": {
                "value": raw,
                "type": "Expression"
            },
            "type": "Expression"
        }
    else:
        return {
            "value": raw,
            "type": "String"
        }

# ==========================================
# 4. CONVERTERS
# ==========================================

def convert_stored_proc(act):
    """
    Convert ADF SqlServerStoredProcedure to Fabric shape
    - storedProcedureName: raw string
    - storedProcedureParameters: per format_sp_param (outer String, inner Expression/String)
    - connectionSettings: Warehouse; no top-level externalReferences
    """
    new_act = _base_props(act, "SqlServerStoredProcedure")
    tp_old = act.get("typeProperties", {})

    # Name MUST be a raw string (no wrapper)
    sp_name_raw = get_flat_value(tp_old.get("storedProcedureName", ""))

    # Build typeProperties in the Fabric shape
    new_act["typeProperties"] = {
        "storedProcedureName": sp_name_raw,
        "storedProcedureParameters": {}
    }

    # Parameters: always outer String, inner Expression/String
    for k, v in tp_old.get("storedProcedureParameters", {}).items():
        new_act["typeProperties"]["storedProcedureParameters"][k] = format_sp_param(v)

    # Warehouse connectionSettings (matches your reference)
    new_act["connectionSettings"] = {
        "name": "wh_sbm_gold",
        "properties": {
            "annotations": [],
            "type": "DataWarehouse",
            "typeProperties": {
                "endpoint": CONFIG["warehouse_endpoint"],
                "artifactId": CONFIG["warehouse_artifact_id"],
                "workspaceId": CONFIG["workspace_id"]
            },
            "externalReferences": {
                "connection": CONFIG["warehouse_connection_id"]
            }
        }
    }

    # No top-level externalReferences per your reference
    return new_act

def convert_invoke_pipeline(act):
    new_act = _base_props(act, "InvokePipeline")
    tp_old = act.get("typeProperties", {})

    new_act["typeProperties"] = {
        "waitOnCompletion": tp_old.get("waitOnCompletion", True),
        "operationType": "InvokeFabricPipeline",
        "pipelineId": tp_old.get("pipelineId", "placeholder_pipeline_id"),
        "workspaceId": CONFIG["workspace_id"],
        "parameters": {}
    }
    for k, v in tp_old.get("parameters", {}).items():
        new_act["typeProperties"]["parameters"][k] = format_invoke_param(v)

    # If your tenant expects a pipeline credential/connection, set it here; otherwise omit.
    return new_act

def convert_notebook(act):
    new_act = _base_props(act, "TridentNotebook")
    tp_old = act.get("typeProperties", {})

    new_act["typeProperties"] = {
        "notebookId": tp_old.get("notebookId", CONFIG["notebook_id"]),
        "workspaceId": CONFIG["workspace_id"],
        "parameters": {}
    }
    # Handle parameter source location (ADF uses baseParameters)
    base_params = tp_old.get("baseParameters", {}) or tp_old.get("parameters", {})
    for k, v in base_params.items():
        new_act["typeProperties"]["parameters"][k] = format_notebook_param(v)

    return new_act

def _build_blob_sink():
    """Blob sink using pipeline parameters 'blob_path' and 'file_name' (ADF-style)."""
    return {
        "type": "DelimitedTextSink",
        "storeSettings": {"type": "AzureBlobStorageWriteSettings"},
        "formatSettings": {
            "type": "DelimitedTextWriteSettings",
            "quoteAllText": True,
            "fileExtension": ".TXT"   # match your uppercase convention
        },
        "datasetSettings": {
            "type": "DelimitedText",
            "typeProperties": {
                "location": {
                    "type": "AzureBlobStorageLocation",
                    "folderPath": {"value": "@pipeline().parameters.blob_path", "type": "Expression"},
                    "fileName": {"value": "@pipeline().parameters.file_name", "type": "Expression"}
                },
                "columnDelimiter": "|",
                "escapeChar": "\\",
                "firstRowAsHeader": True,
                "quoteChar": ""
            }
        }
    }

def _build_lakehouse_sink():
    """Lakehouse sink mapping existing parameters 'blob_path' and 'file_name' to Files/ location."""
    return {
        "type": "DelimitedTextSink",
        "storeSettings": {"type": "LakehouseWriteSettings"},
        "formatSettings": {
            "type": "DelimitedTextWriteSettings",
            "quoteAllText": True,
            "fileExtension": ".TXT"
        },
        "datasetSettings": {
            "type": "DelimitedText",
            "connectionSettings": {
                "name": CONFIG["lakehouse_name"],
                "properties": {
                    "type": "Lakehouse",
                    "typeProperties": {
                        "workspaceId": CONFIG["workspace_id"],
                        "artifactId": CONFIG["lakehouse_artifact_id"],
                        "rootFolder": "Files"
                    },
                    "externalReferences": {"connection": CONFIG["lakehouse_connection_id"]}
                }
            },
            "typeProperties": {
                "location": {
                    "type": "LakehouseLocation",
                    "folderPath": {"value": "@pipeline().parameters.blob_path", "type": "Expression"},
                    "fileName": {"value": "@pipeline().parameters.file_name", "type": "Expression"}
                },
                "columnDelimiter": "|",
                "escapeChar": "\\",
                "firstRowAsHeader": True,
                "quoteChar": ""
            }
        }
    }

def convert_copy(act):
    """
    Copy:
    - Source: OracleSource gets datasetSettings with Oracle connection and wraps oracleReaderQuery as Expression
    - Sink: choose Blob or Lakehouse via CONFIG["target_sink"]; parameters mapped to existing pipeline ones
    """
    new_act = _base_props(act, "Copy")
    tp_old = act.get("typeProperties", {})
    source = tp_old.get("source", {}) or {}
    new_source = deepcopy(source)

    # Source: Oracle → add datasetSettings with Oracle connection
    if source.get("type") == "OracleSource":
        new_source["datasetSettings"] = {
            "annotations": [],
            "type": "OracleTable",
            "schema": [],
            "externalReferences": {"connection": CONFIG["oracle_connection_id"]}
        }
        if "oracleReaderQuery" in new_source:
            new_source["oracleReaderQuery"] = {
                "value": get_flat_value(new_source["oracleReaderQuery"]),
                "type": "Expression"
            }
    else:
        # Fallback: DelimitedText from Blob (if you have a blob connection id, set it here)
        new_source["datasetSettings"] = {
            "annotations": [],
            "type": "DelimitedText",
            "typeProperties": {
                "location": {
                    "type": "AzureBlobStorageLocation",
                    "container": {"value": "@pipeline().parameters.blob_container", "type": "Expression"},
                    "folderPath": {"value": "raw", "type": "String"}
                },
                "columnDelimiter": ",",
                "escapeChar": "\\",
                "firstRowAsHeader": True,
                "quoteChar": "\""
            },
            # NOTE: Using Lakehouse connection here is not ideal for Blob.
            # If you have a dedicated blob connection id, replace it below.
            "externalReferences": {"connection": CONFIG["lakehouse_connection_id"]}
        }

    # Sink: choose based on CONFIG
    new_sink = _build_lakehouse_sink() if CONFIG.get("target_sink") == "lakehouse" else _build_blob_sink()

    new_act["typeProperties"] = {
        "source": new_source,
        "sink": new_sink,
        "enableStaging": tp_old.get("enableStaging", False),
        # Preserve translator if present
        "translator": deepcopy(tp_old.get("translator", {}))
    }
    return new_act

def convert_lookup(act):
    """
    Convert ADF Lookup to Fabric Lookup reading from Warehouse.
    Handles common ADF patterns:
      - source.sqlReaderQuery (SQL text)
      - dataset-based Lookup (remove linkedServiceName; use Warehouse datasetSettings)
      - rare storedProcedureName usage (mapped to sqlReaderQuery if present)
    """
    new_act = _base_props(act, "Lookup")
    tp_old = act.get("typeProperties", {}) or {}

    # ADF sometimes has source as a dict with sqlReaderQuery or table/query attributes
    src_old = tp_old.get("source", {}) or {}

    # Determine the SQL to run:
    # Priority: explicit sqlReaderQuery → storedProcedureName (call) → inline query field → empty
    sql_expr = None
    if "sqlReaderQuery" in src_old:
        sql_expr = get_flat_value(src_old["sqlReaderQuery"])
    elif "storedProcedureName" in src_old:
        # Map SP name to a callable expression if needed; commonly Fabric Lookup expects SQL.
        # You may adjust this if you truly want to execute SP via Lookup (not typical).
        spname = get_flat_value(src_old["storedProcedureName"])
        # Minimal mapping: execute SP via T-SQL call pattern
        sql_expr = f"EXEC {spname}"
    elif "query" in src_old:
        sql_expr = get_flat_value(src_old["query"])
    else:
        sql_expr = ""  # no-op; safe default

    # Build Fabric Lookup typeProperties
    new_act["typeProperties"] = {
        "source": {
            "type": "DataWarehouseSource",
            "sqlReaderQuery": {
                "value": sql_expr,
                "type": "Expression" if is_expression(sql_expr) else "String"
            },
            "queryTimeout": src_old.get("queryTimeout", tp_old.get("queryTimeout", "02:00:00")),
            "partitionOption": "None"
        },
        "datasetSettings": {
            "annotations": [],
            "type": "DataWarehouseTable",
            "schema": [],
            "connectionSettings": {
                "name": "wh_sbm_gold",
                "properties": {
                    "annotations": [],
                    "type": "DataWarehouse",
                    "typeProperties": {
                        "endpoint": CONFIG["warehouse_endpoint"],
                        "artifactId": CONFIG["warehouse_artifact_id"],
                        "workspaceId": CONFIG["workspace_id"]
                    },
                    "externalReferences": {"connection": CONFIG["warehouse_connection_id"]}
                }
            }
        }
    }

    # ADF extras (firstRowOnly, etc.) → preserve if present
    if "firstRowOnly" in tp_old:
        new_act["typeProperties"]["firstRowOnly"] = tp_old["firstRowOnly"]

    return new_act

# ==========================================
# 5. CORE LOGIC
# ==========================================

def _base_props(old_act, new_type):
    return {
        "name": old_act.get("name", f"Unnamed_{new_type}"),
        "type": new_type,
        "dependsOn": deepcopy(old_act.get("dependsOn", [])),
        "policy": deepcopy(old_act.get("policy", {})),
        "userProperties": deepcopy(old_act.get("userProperties", []))
    }

def convert_activity_list(activities):
    if not isinstance(activities, list):
        return []
    converted = []
    for act in activities:
        atype = act.get("type")
        if atype == "DatabricksNotebook":
            new_act = convert_notebook(act)
        elif atype == "SqlServerStoredProcedure":
            new_act = convert_stored_proc(act)
        elif atype == "ExecutePipeline":
            new_act = convert_invoke_pipeline(act)
        elif atype == "Copy":
            new_act = convert_copy(act)
        elif atype == "Lookup":
            new_act = convert_lookup(act)
        else:
            new_act = deepcopy(act)
            # Remove ADF-only linkedServiceName
            if "linkedServiceName" in new_act:
                del new_act["linkedServiceName"]

        # Recurse into nested activity containers
        tp = new_act.get("typeProperties")
        if isinstance(tp, dict):
            if isinstance(tp.get("ifTrueActivities"), list):
                tp["ifTrueActivities"] = convert_activity_list(tp["ifTrueActivities"])
            if isinstance(tp.get("ifFalseActivities"), list):
                tp["ifFalseActivities"] = convert_activity_list(tp["ifFalseActivities"])
            if isinstance(tp.get("activities"), list):
                tp["activities"] = convert_activity_list(tp["activities"])
            if isinstance(tp.get("cases"), list):
                tp["cases"] = [
                    {**case, "activities": convert_activity_list(case.get("activities", []))}
                    for case in tp["cases"]
                ]
            if isinstance(tp.get("defaultActivities"), list):
                tp["defaultActivities"] = convert_activity_list(tp["defaultActivities"])

        converted.append(new_act)
    return converted

def process_pipeline(source_json):
    target = {
        "name": source_json.get("name", "ConvertedPipeline"),
        "objectId": str(uuid.uuid4()),
        "properties": deepcopy(source_json.get("properties", {}))
    }
    activities = target["properties"].get("activities")
    if isinstance(activities, list):
        target["properties"]["activities"] = convert_activity_list(activities)
    else:
        target["properties"]["activities"] = []
    return target

# ==========================================
# 6. CLI
# ==========================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-f", "--file", required=True, help="Input ADF JSON file")
    parser.add_argument("-o", "--output", help="Output Fabric JSON file")
    args = parser.parse_args()
    try:
        with open(args.file, 'r', encoding='utf-8') as f:
            source_data = json.load(f)
        print(f"Converting pipeline: {source_data.get('name')}...")
        result = process_pipeline(source_data)
        if args.output:
            with open(args.output, 'w', encoding='utf-8') as f:
                json.dump(result, f, indent=4)
            print(f"Success! Output saved to {args.output}")
        else:
            print(json.dumps(result, indent=4))
    except Exception as e:
        print(f"Error: {str(e)}", file=sys.stderr)
