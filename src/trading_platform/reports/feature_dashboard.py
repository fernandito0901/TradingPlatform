"""Interactive feature dashboard using Plotly."""

from pathlib import Path

import pandas as pd
import plotly.express as px

from . import REPORTS_DIR


def generate_feature_dashboard(
    csv_file: str, out_file: str = str(REPORTS_DIR / "feature_dashboard.html")
) -> str:
    """Create an interactive dashboard showing feature distributions.

    Parameters
    ----------
    csv_file : str
        Path to the features CSV file.
    out_file : str, optional
        Destination HTML file, by default ``REPORTS_DIR / 'feature_dashboard.html'``.

    Returns
    -------
    str
        Path to the written HTML file.
    """
    df = pd.read_csv(csv_file)
    numeric = df.select_dtypes(include="number")
    if numeric.empty:
        raise ValueError("no numeric columns")
    fig = px.scatter_matrix(numeric, dimensions=numeric.columns)
    Path(out_file).parent.mkdir(parents=True, exist_ok=True)
    fig.write_html(out_file)
    return out_file
