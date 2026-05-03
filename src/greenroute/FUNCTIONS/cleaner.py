import pandas as pd


def yn_to_bool(value):
    if pd.isna(value):
        return False
    value = str(value).strip().upper()
    return value == "Y"


def clean_string_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    for col in df.columns:
        if df[col].dtype == "object":
            df[col] = df[col].apply(lambda x: x.strip() if isinstance(x, str) else x)
    return df


def clean_routes_df(routes_df: pd.DataFrame) -> pd.DataFrame:
    routes_df = clean_string_columns(routes_df)

    numeric_cols = [
        "Final_Product_MW",
        "Number_of_Steps",
        "Overall_Yield_%",
        "Final_Product_Mass_Isolated_g",
    ]

    for col in numeric_cols:
        if col in routes_df.columns:
            routes_df[col] = pd.to_numeric(routes_df[col], errors="coerce")

    return routes_df


def clean_steps_df(steps_df: pd.DataFrame) -> pd.DataFrame:
    steps_df = clean_string_columns(steps_df)

    numeric_cols = [
        "Step_Number",
        "Desired_Product_MW",
        "Desired_Product_Stoich_Coeff",
        "Step_Yield_%",
        "Product_Mass_Isolated_g",
    ]

    for col in numeric_cols:
        if col in steps_df.columns:
            steps_df[col] = pd.to_numeric(steps_df[col], errors="coerce")

    if "Final_Step_YN" in steps_df.columns:
        steps_df["Final_Step_YN"] = steps_df["Final_Step_YN"].apply(yn_to_bool)

    return steps_df


def clean_materials_df(materials_df: pd.DataFrame) -> pd.DataFrame:
    materials_df = clean_string_columns(materials_df)

    numeric_cols = [
        "Step_Number",
        "Amount_g",
        "Molar_Mass",
        "Stoich_Coeff",
        "Hazard_Score",
    ]

    for col in numeric_cols:
        if col in materials_df.columns:
            materials_df[col] = pd.to_numeric(materials_df[col], errors="coerce")

    yn_cols = [
        "Include_in_Atom_Economy",
        "Include_in_PMI",
        "Include_in_Efactor",
    ]

    for col in yn_cols:
        if col in materials_df.columns:
            materials_df[col] = materials_df[col].apply(yn_to_bool)

    return materials_df