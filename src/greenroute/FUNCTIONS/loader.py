from pathlib import Path
import pandas as pd


REQUIRED_SHEETS = ["Route_Summary", "Step_Data", "Materials"]


def load_excel_sheets(file_path: str) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Load the required sheets from the Excel workbook.

    Parameters
    ----------
    file_path : str
        Path to the Excel workbook.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        routes_df, steps_df, materials_df
    """
    excel_path = Path(file_path)

    if not excel_path.exists():
        raise FileNotFoundError(f"Excel file not found: {excel_path}")

    xls = pd.ExcelFile(excel_path)

    missing_sheets = [sheet for sheet in REQUIRED_SHEETS if sheet not in xls.sheet_names]
    if missing_sheets:
        raise ValueError(
            f"Missing required sheet(s): {missing_sheets}. "
            f"Available sheets: {xls.sheet_names}"
        )

    routes_df = pd.read_excel(excel_path, sheet_name="Route_Summary")
    steps_df = pd.read_excel(excel_path, sheet_name="Step_Data")
    materials_df = pd.read_excel(excel_path, sheet_name="Materials")

    return routes_df, steps_df, materials_df


def preview_dataframe(df: pd.DataFrame, name: str, n: int = 5) -> None:
    """
    Print a quick preview of a dataframe for debugging.
    """
    print(f"\n--- {name} ---")
    print(df.head(n))
    print("\nColumns:")
    print(list(df.columns))
    print("\nShape:")
    print(df.shape)
    print("\nDtypes:")
    print(df.dtypes)
    