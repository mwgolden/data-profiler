import pandas as pd
import duckdb
import plotly.graph_objects as go
from plotly.io import to_html
from dataclasses import dataclass
from jinja2 import Environment, FileSystemLoader
from pathlib import Path
from .sql_queries import report_queries as q
from typing import Hashable, Any

env = Environment(loader=FileSystemLoader(Path.cwd() / "src" / "report" /  "templates"))

#root_type: str
#object_count: int
#object_path_count: int
#distinct_key_count: int
@dataclass
class SummaryCard:
    label: str
    value: Any

@dataclass
class Summary:
    summaries: list[SummaryCard]

@dataclass
class Table:
    title: str
    row_count: int
    headers: list[str]
    rows: list[dict[Hashable, Any]]

@dataclass
class Report:
    title: str
    source_file: str
    summary: Summary
    tables: list[Table]


def create_summary(df: pd.DataFrame) -> Summary:
    root_type = duckdb.sql(q["root_object_type"]).fetchone()[0]

    object_instance_count = duckdb.sql(q["object_instances"]).fetchone()[0]

    distinct_object_path_count = duckdb.sql(q["distinct_object_paths"]).fetchone()[0]

    distinct_keys = duckdb.sql(q["distinct_keys"]).fetchone()[0]

    summary = Summary([
        SummaryCard(label="Root Type", value=root_type.title()),
        SummaryCard(label="Object Count", value=object_instance_count),
        SummaryCard(label="Object Paths", value=distinct_object_path_count),
        SummaryCard(label="Distinct Keys", value=distinct_keys)
    ])

    return summary


def create_table(title, df: pd.DataFrame) -> Table:

    display_df = format_table(df)

    return Table(
        title=title,
        row_count=len(display_df),
        headers=display_df.columns,
        rows=display_df.to_dict("records")
    )

def format_table(df: pd.DataFrame) -> pd.DataFrame:
    display_df = df.copy()

    if "pct_coverage" in display_df.columns:
        display_df["pct_coverage"] = display_df["pct_coverage"].apply(pct_bar)

    return display_df

def pct_bar(pct: float) -> str:
    template = env.get_template("pct_bar.html")
    return template.render(
        pct=pct
    )

def generate_report(df: pd.DataFrame, file_name: str):

    obj_path_query = q["obj_path_query" ]
    obj_paths = duckdb.sql(obj_path_query).df()

    tables = [
        create_table(
            title="Object Paths",
            df=obj_paths
        )
    ]

    key_coverage_query = q["key_coverage_query"]
    
    path_series = obj_paths["Path"]
    for path in path_series:
        query = key_coverage_query.format(path)
        res = duckdb.sql(query).df()
        tables.append(
            create_table(
                title=path,
                df=res
            )
        )

    report_summary = create_summary(df)

    report = Report(
        title="JSON Profile",
        source_file=file_name,
        summary=report_summary,
        tables=tables
    )

    template = env.get_template("report.html")

    html = template.render(
        report=report
    )

    Path(Path.cwd() / "output" / "json-report.html").write_text(html)



