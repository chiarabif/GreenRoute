import pandas as pd


def _clean_yes_no_column(series: pd.Series) -> pd.Series:
    """
    Convert a yes/no style column into True and False values.

    The function accepts common text variations such as Y, Yes, N, No,
    True, and False. Empty values are treated as False.
    """
    mapping = {
        "y": True,
        "yes": True,
        "true": True,
        "1": True,
        "n": False,
        "no": False,
        "false": False,
        "0": False,
        "": False,
    }

    return (
        series.fillna("")
        .astype(str)
        .str.strip()
        .str.lower()
        .map(mapping)
        .fillna(False)
    )


def clean_routes_df(routes_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Route_Summary table.

    This mainly removes extra spaces from text columns and standardizes
    empty cells so the route information is easier to use later in the
    pipeline.
    """
    routes_df = routes_df.copy()

    text_columns = routes_df.select_dtypes(include="object").columns
    for col in text_columns:
        routes_df[col] = routes_df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    return routes_df


def clean_steps_df(steps_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Step_Data table.

    Text columns are stripped, and the final-step column is converted into
    a proper boolean column.
    """
    steps_df = steps_df.copy()

    text_columns = steps_df.select_dtypes(include="object").columns
    for col in text_columns:
        steps_df[col] = steps_df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    if "Final_Step_YN" in steps_df.columns:
        steps_df["Final_Step_YN"] = _clean_yes_no_column(steps_df["Final_Step_YN"])

    return steps_df


def clean_materials_df(materials_df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the Materials table.

    Text columns are stripped, and the inclusion columns used for atom
    economy, PMI, and E-factor are converted into boolean values.
    """
    materials_df = materials_df.copy()

    text_columns = materials_df.select_dtypes(include="object").columns
    for col in text_columns:
        materials_df[col] = materials_df[col].apply(
            lambda x: x.strip() if isinstance(x, str) else x
        )

    yes_no_columns = [
        "Include_in_Atom_Economy",
        "Include_in_PMI",
        "Include_in_Efactor",
    ]

    for col in yes_no_columns:
        if col in materials_df.columns:
            materials_df[col] = _clean_yes_no_column(materials_df[col])

    return materials_df