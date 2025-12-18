
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

    # Connections (GUIDs from your tenant)
    "warehouse_connection_id": "06f15094-5415-40ca-9647-985fa72a41fe",
    "lakehouse_connection_id": "e31de1f3-905a-400e-8c21-1bfcc5c7719c",
    "oracle_connection_id": "1320ffbd-c314-4267-be68-d3e63f7ff4df",

    # Artifacts
    "warehouse_artifact_id": "6068bf54-5806-44df-996b-f19fac38d18c",
    "warehouse_endpoint": "uz5qo3w55cyebj7ffmgl7aydcm-zuzodfk7z4ku5kpboudjssvchq.datawarehouse.fabric.microsoft.com",
    "lakehouse_artifact_id": "2d07daef-8c0b-454d-9a31-28faec11c440",
    "lakehouse_name": "lh_sbm_bronze_dev",

    # Copy sink selection: "lakehouse" | "blob" | "blobfs"
    # - lakehouse -> LakehouseWriteSettings
    # - blob      -> AzureBlobStorageWriteSettings
    # - blobfs    -> AzureBlobFSWriteSettings (ADLS Gen2 style)
    "target_sink": "lakehouse",

    # Parameter candidates to support multiple pipeline conventions
    "param_candidates": {
        "source_container": ["containerName", "blob_container"],
        "sink_folder": ["destinationPath", "blob_path"],
        "sink_file": ["fileName", "file_name"]
    }
}

# ==========================================
# 2. HELPERS
# ==========================================

def clean_val(val):
    """Sanitizes input values (surface suspicious markers)."""
    if str(val) == "[object Object]":
        return "FIX_ME_INVALID_OBJECT"
    return val

def get_flat_value(val):
    """
    Recursively unwrap ADF shapes to plain values.
    Dicts without 'value' -> JSON string for deterministic behavior.
    """
    if isinstance(val, dict):
        if "value" in val:
            return get_flat_value(val["value"])
        return json.dumps(val, ensure_ascii=False)
    if val is None:
        return ""
    return clean_val(val)

def is_expression(val):
    return isinstance(val, str) and val.strip().startswith(("@", "="))

def expr_param(name):
    """Build a Fabric expression wrapper for pipeline().parameters.<name>"""
    return {"value": f"@pipeline().parameters.{name}", "type": "Expression"}

def select_param_name(pipeline_props, key):
    """
    Pick the first available parameter name from candidates in CONFIG['param_candidates'][key].
    pipeline_props: the full 'properties' object from the pipeline (has 'parameters')
    """
    candidates = CONFIG["param_candidates"].get(key, [])
    params = (pipeline_props or {}).get("parameters", {}) or {}
    for c in candidates:
        if c in params:
            return c
    # Fallback to first candidate even if not present (expression will still be valid syntactically)
    return candidates[0] if candidates else None

# ==========================================
# 3. FORMATTERS (Exact Fabric shapes)
# ==========================================

def format_sp_param(val):
    """
    Stored Proc Parameters (Fabric as per your reference):
    - Outer type always "String"
    - Inner { "value": <raw>, "type": "Expression" | "String" }
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
    Notebook Parameters: double-nested, outer type=Expression; inner toggles.
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
    """InvokePipeline params: expressions double-nested, literals single."""
    raw = get_flat_value(val)
    if is_expression(raw):
        return {"value": {"value": raw, "type": "Expression"}, "type": "Expression"}
    else:
        return {"value": raw, "type": "String"}

def format_generic_value(val):
    """Utility to preserve Expression/Literal with single nesting (non-SP contexts)."""
    raw = get_flat_value(val)
    return {"value": raw, "type": "Expression" if is_expression(raw) else "String"}

# ==========================================
# 4. CONVERTERS
# ==========================================

def convert_stored_proc(act):
    # To match your Fabric reference block exactly
    new_act = _base_props(act, "SqlServerStoredProcedure")
    tp_old = act.get("typeProperties", {}) or {}

    sp_name_raw = get_flat_value(tp_old.get("storedProcedureName", ""))

    new_act["typeProperties"] = {
        "storedProcedureName": sp_name_raw,
        "storedProcedureParameters": {}
    }

    for k, v in tp_old.get("storedProcedureParameters", {}).items():
        new_act["typeProperties"]["storedProcedureParameters"][k] = format_sp_param(v)

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
            "externalReferences": {"connection": CONFIG["warehouse_connection_id"]}
        }
    }
    return new_act

def convert_invoke_pipeline(act):
    new_act = _base_props(act, "InvokePipeline")
    tp_old = act.get("typeProperties", {}) or {}

    new_act["typeProperties"] = {
        "waitOnCompletion": tp_old.get("waitOnCompletion", True),
        "operationType": "InvokeFabricPipeline",
        "pipelineId": tp_old.get("pipelineId", "placeholder_pipeline_id"),
        "workspaceId": CONFIG["workspace_id"],
        "parameters": {}
    }
    for k, v in tp_old.get("parameters", {}).items():
        new_act["typeProperties"]["parameters"][k] = format_invoke_param(v)
    return new_act

def convert_notebook(act):
    new_act = _base_props(act, "TridentNotebook")
    tp_old = act.get("typeProperties", {}) or {}

    new_act["typeProperties"] = {
        "notebookId": tp_old.get("notebookId", CONFIG["notebook_id"]),
        "workspaceId": CONFIG["workspace_id"],
        "parameters": {}
    }
    base_params = tp_old.get("baseParameters", {}) or tp_old.get("parameters", {})
    for k, v in base_params.items():
        new_act["typeProperties"]["parameters"][k] = format_notebook_param(v)
    return new_act

def _build_sink(folder_param_name, file_param_name):
    """
    Build sink block based on CONFIG['target_sink'] and selected parameter names.
    - folder_param_name: e.g., destinationPath or blob_path
    - file_param_name:   e.g., fileName or file_name
    """
    target = CONFIG.get("target_sink", "lakehouse").lower()

    if target == "lakehouse":
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
                        "folderPath": expr_param(folder_param_name),
                        "fileName": expr_param(file_param_name)
                    },
                    "columnDelimiter": "|",
                    "escapeChar": "\\",
                    "firstRowAsHeader": True,
                    "quoteChar": ""
                }
            }
        }

    if target == "blobfs":
        # ADLS Gen2-style sink
        return {
            "type": "DelimitedTextSink",
            "storeSettings": {"type": "AzureBlobFSWriteSettings"},
            "formatSettings": {
                "type": "DelimitedTextWriteSettings",
                "quoteAllText": True,
                "fileExtension": ".TXT"
            },
            "datasetSettings": {
                "type": "DelimitedText",
                "typeProperties": {
                    "location": {
                        "type": "AzureBlobFSLocation",
                        "folderPath": expr_param(folder_param_name),
                        "fileName": expr_param(file_param_name)
                    },
                    "columnDelimiter": "|",
                    "escapeChar": "\\",
                    "firstRowAsHeader": True,
                    "quoteChar": ""
                }
            }
        }

    # Default: blob
    return {
        "type": "DelimitedTextSink",
        "storeSettings": {"type": "AzureBlobStorageWriteSettings"},
        "formatSettings": {
            "type": "DelimitedTextWriteSettings",
            "quoteAllText": True,
            "fileExtension": ".TXT"
        },
        "datasetSettings": {
            "type": "DelimitedText",
            "typeProperties": {
                "location": {
                    "type": "AzureBlobStorageLocation",
                    "folderPath": expr_param(folder_param_name),
                    "fileName": expr_param(file_param_name)
                },
                "columnDelimiter": "|",
                "escapeChar": "\\",
                "firstRowAsHeader": True,
                "quoteChar": ""
            }
        }
    }

def convert_copy(act, pipeline_props=None):
    """
    Copy:
    - Source: handle OracleSource OR DelimitedTextSource (Blob read)
    - Sink: select via CONFIG['target_sink'] and map folder/file params detected from pipeline
    - Preserve translator if present
    """
    new_act = _base_props(act, "Copy")
    tp_old = act.get("typeProperties", {}) or {}
    source = tp_old.get("source", {}) or {}
    new_source = deepcopy(source)

    # --- Source handling ---
    stype = source.get("type")

    if stype == "OracleSource":
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

    elif stype == "DelimitedTextSource":
        # Map Blob read settings and expressions
        # Detect container param name from pipeline properties
        container_param = select_param_name(pipeline_props, "source_container") or "containerName"
        new_source = {
            "type": "DelimitedTextSource",
            "storeSettings": {"type": "AzureBlobStorageReadSettings"},
            "recursive": source.get("recursive", False),
            # Wrap these as Expressions if they were expressions in ADF
            "modifiedDatetimeStart": format_generic_value(source.get("modifiedDatetimeStart")),
            "wildcardFileName": format_generic_value(source.get("wildcardFileName")),
            "formatSettings": {"type": "DelimitedTextReadSettings"},
            "datasetSettings": {
                "annotations": [],
                "type": "DelimitedText",
                "typeProperties": {
                    "location": {
                        "type": "AzureBlobStorageLocation",
                        "container": expr_param(container_param),
                        # If you have folder path param, you can add it here. For ADF, it's often implicit via wildcard/fileName.
                    }
                }
            }
        }

    else:
        # Fallback to basic DelimitedText with Blob location (rare paths)
        container_param = select_param_name(pipeline_props, "source_container") or "containerName"
        new_source = {
            "type": "DelimitedTextSource",
            "storeSettings": {"type": "AzureBlobStorageReadSettings"},
            "formatSettings": {"type": "DelimitedTextReadSettings"},
            "datasetSettings": {
                "annotations": [],
                "type": "DelimitedText",
                "typeProperties": {
                    "location": {
                        "type": "AzureBlobStorageLocation",
                        "container": expr_param(container_param)
                    }
                }
            }
        }

    # --- Sink handling ---
    folder_param = select_param_name(pipeline_props, "sink_folder") or "destinationPath"
    file_param = select_param_name(pipeline_props, "sink_file") or "fileName"
    new_sink = _build_sink(folder_param, file_param)

    new_act["typeProperties"] = {
        "source": new_source,
        "sink": new_sink,
        "enableStaging": tp_old.get("enableStaging", False),
        "translator": deepcopy(tp_old.get("translator", {}))
    }
    return new_act

def convert_lookup(act):
    """
    Lookup → Fabric Lookup reading from Warehouse.
    Supports:
      - source.sqlReaderQuery
      - source.storedProcedureName (mapped to EXEC ...)
      - source.query
    """
    new_act = _base_props(act, "Lookup")
    tp_old = act.get("typeProperties", {}) or {}
    src_old = tp_old.get("source", {}) or {}

    if "sqlReaderQuery" in src_old:
        sql_expr = get_flat_value(src_old["sqlReaderQuery"])
    elif "storedProcedureName" in src_old:
        sql_expr = f"EXEC {get_flat_value(src_old['storedProcedureName'])}"
    elif "query" in src_old:
        sql_expr = get_flat_value(src_old["query"])
    else:
        sql_expr = ""

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
    if "firstRowOnly" in tp_old:
        new_act["typeProperties"]["firstRowOnly"] = tp_old["firstRowOnly"]
    return new_act

def convert_get_metadata(act, pipeline_props=None):
    """
    GetMetadata:
    - Build datasetSettings for Blob (AzureBlobStorageReadSettings) with container param.
    - Preserve fieldList, storeSettings, formatSettings if present.
    """
    new_act = _base_props(act, "GetMetadata")
    tp_old = act.get("typeProperties", {}) or {}
    dataset_old = tp_old.get("dataset", {}) or {}

    container_param = select_param_name(pipeline_props, "source_container") or "containerName"

    new_ds = {
        "annotations": [],
        "type": "DelimitedText",
        "typeProperties": {
            "location": {
                "type": "AzureBlobStorageLocation",
                "container": expr_param(container_param)
            }
        }
    }

    new_act["typeProperties"] = {
        "datasetSettings": new_ds,
        "fieldList": tp_old.get("fieldList", []),
        "storeSettings": {"type": "AzureBlobStorageReadSettings"},
        "formatSettings": {"type": "DelimitedTextReadSettings"}
    }
    return new_act

def convert_set_variable(act):
    """
    SetVariable:
    - Keep variableName
    - Wrap value as Expression/String appropriately
    """
    new_act = _base_props(act, "SetVariable")
    tp_old = act.get("typeProperties", {}) or {}
    val = tp_old.get("value", {})
    new_act["typeProperties"] = {
        "variableName": tp_old.get("variableName", ""),
        "value": format_generic_value(val)
    }
    return new_act

def convert_for_each(act, pipeline_props=None):
    """
    ForEach:
    - Preserve items (Expression or String)
    - Recurse into inner activities
    - isSequential preserved
    """
    new_act = _base_props(act, "ForEach")
    tp_old = act.get("typeProperties", {}) or {}
    items_old = tp_old.get("items")

    new_act["typeProperties"] = {
        "items": format_generic_value(items_old),
        "isSequential": tp_old.get("isSequential", True),
        "activities": convert_activity_list(tp_old.get("activities", []), pipeline_props)
    }
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

def convert_activity_list(activities, pipeline_props=None):
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
            new_act = convert_copy(act, pipeline_props)
        elif atype == "Lookup":
            new_act = convert_lookup(act)
        elif atype == "GetMetadata":
            new_act = convert_get_metadata(act, pipeline_props)
        elif atype == "SetVariable":
            new_act = convert_set_variable(act)
        elif atype == "ForEach":
            new_act = convert_for_each(act, pipeline_props)
        else:
            new_act = deepcopy(act)
            if "linkedServiceName" in new_act:
                del new_act["linkedServiceName"]

        # Recurse into nested containers inside typeProperties
        tp = new_act.get("typeProperties")
        if isinstance(tp, dict):
            if isinstance(tp.get("ifTrueActivities"), list):
                tp["ifTrueActivities"] = convert_activity_list(tp["ifTrueActivities"], pipeline_props)
            if isinstance(tp.get("ifFalseActivities"), list):
                tp["ifFalseActivities"] = convert_activity_list(tp["ifFalseActivities"], pipeline_props)
            if isinstance(tp.get("activities"), list):
                tp["activities"] = convert_activity_list(tp["activities"], pipeline_props)
            if isinstance(tp.get("cases"), list):
                tp["cases"] = [
                    {**case, "activities": convert_activity_list(case.get("activities", []), pipeline_props)}
                    for case in tp["cases"]
                ]
            if isinstance(tp.get("defaultActivities"), list):
                tp["defaultActivities"] = convert_activity_list(tp["defaultActivities"], pipeline_props)

        converted.append(new_act)
    return converted

def process_pipeline(source_json):
    props = deepcopy(source_json.get("properties", {}))
    target = {
        "name": source_json.get("name", "ConvertedPipeline"),
        "objectId": str(uuid.uuid4()),
        "properties": props
    }
    activities = props.get("activities")
    if isinstance(activities, list):
        target["properties"]["activities"] = convert_activity_list(activities, props)
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
