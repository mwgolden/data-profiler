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
    tables: list[Table]


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

def generate_report(df: pd.DataFrame):

    obj_path_query = q["obj_path_query" ]
    obj_paths = duckdb.sql(obj_path_query).df()

    tables = [
        create_table(
            title="Object Paths",
            df=obj_paths
        )
    ]
    

    key_coverage_query = q["key_coverage_query"]

    
    path_series = obj_paths["path"]
    for path in path_series:
        query = key_coverage_query.format(path)
        res = duckdb.sql(query).df()
        tables.append(
            create_table(
                title=path,
                df=res
            )
        )

    report = Report(
        title="JSON Profile",
        source_file="??",
        tables=tables
    )

    template = env.get_template("report.html")

    html = template.render(
        report=report
    )

    Path(Path.cwd() / "output" / "json-report.html").write_text(html)



