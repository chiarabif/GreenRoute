import pandas as pd


def load_excel_sheets(file_path: str):
    """
    Load the three main sheets used in the project workbook.

    The function reads:
    - Route_Summary
    - Step_Data
    - Materials

    and returns them as pandas DataFrames.

    Parameters
    ----------
    file_path : str
        Path to the Excel workbook.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        The route summary table, the step table, and the materials table.
    """
    routes_df = pd.read_excel(file_path, sheet_name="Route_Summary")
    steps_df = pd.read_excel(file_path, sheet_name="Step_Data")
    materials_df = pd.read_excel(file_path, sheet_name="Materials")

    return routes_df, steps_df, materials_df