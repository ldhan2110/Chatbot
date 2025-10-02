from sqlalchemy import text
import json


def format_sql_for_sqlalchemy(sql_string: str):
    # Remove triple backticks and any leading/trailing whitespace
    sql_cleaned = sql_string.strip().strip("```").strip()

    # Optional: Remove language hints like "sql" if present at start
    if sql_cleaned.lower().startswith("sql"):
        sql_cleaned = sql_cleaned[3:].strip()

    sql_cleaned = sql_cleaned.rstrip(";")

    return sql_cleaned


def fetch_schema_context(engine, schema: str = "C##PIDEV") -> dict:
    # Table comments
    table_query = text("""
        SELECT
            t.table_name AS table_name,
            c.comments   AS table_comment
        FROM all_tables t
        JOIN all_tab_comments c
            ON t.owner = c.owner
           AND t.table_name = c.table_name
            AND t.table_name = 'ADM_USR'
        WHERE t.owner = :schema
    """)

    # Column comments
    column_query = text("""
        SELECT
            col.table_name,
            col.column_name,
            col.data_type,
            col.data_length,
            col.data_precision,
            col.data_scale,
            col.nullable,
            col_comments.comments AS column_comment
        FROM all_tab_columns col
        LEFT JOIN all_col_comments col_comments
            ON col.owner = col_comments.owner
        AND col.table_name = col_comments.table_name
        AND col.column_name = col_comments.column_name
        WHERE col.owner = :schema
        AND col.table_name = 'ADM_USR'
        ORDER BY col.table_name, col.column_id
    """)

    with engine.connect() as conn:
        # Fetch tables
        tables = conn.execute(table_query, {"schema": schema}).mappings().all()
        # Fetch columns
        columns = conn.execute(
            column_query, {"schema": schema}).mappings().all()

    # Organize into dict
    schema_context: dict[str, dict] = {}
    for row in tables:
        schema_context[row["table_name"]] = {
            "table_comment": row["table_comment"],
            "columns": {}
        }

    for row in columns:
        tbl = row["table_name"]
        if tbl in schema_context:
            schema_context[tbl]["columns"][row["column_name"]] = {
                "data_type": row["data_type"],
                "data_length": row["data_length"],
                "nullable": row["nullable"],
                "column_comment": row["column_comment"]
            }

    return json.dumps(schema_context, indent=2)


def convert_schema_to_flat(input_schema: str | dict) -> dict:
    # If it's a string, parse it into a dict
    if isinstance(input_schema, str):
        input_schema = json.loads(input_schema)

    tables = []
    for table_name, table_data in input_schema.items():
        table_entry = {
            "name": table_name,
            "description": table_data.get("table_comment", ""),
            "columns": []
        }
        for col_name, col_info in table_data.get("columns", {}).items():
            col_type = col_info["data_type"]
            if "data_length" in col_info and col_info["data_length"]:
                col_type = f"{col_type}({col_info['data_length']})"

            table_entry["columns"].append({
                "name": col_name,
                "type": col_type,
                "description": ""  # can fill with col_comments if available
            })
        tables.append(table_entry)

    return {"tables": tables}


__all__ = ["format_sql_for_sqlalchemy",
           "fetch_schema_context", "convert_schema_to_flat"]
