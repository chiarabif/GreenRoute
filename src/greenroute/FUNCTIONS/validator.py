import pandas as pd


def validate_route_ids(routes_df: pd.DataFrame, steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Check that all Route_ID values in Step_Data and Materials exist in Route_Summary.
    Ignore blank rows.
    """
    errors = []

    valid_route_ids = set(routes_df["Route_ID"].dropna().astype(str))
    step_route_ids = set(steps_df["Route_ID"].dropna().astype(str))
    material_route_ids = set(materials_df["Route_ID"].dropna().astype(str))

    missing_from_steps = step_route_ids - valid_route_ids
    missing_from_materials = material_route_ids - valid_route_ids

    if missing_from_steps:
        errors.append(
            f"Route_ID(s) in Step_Data missing from Route_Summary: {sorted(missing_from_steps)}"
        )

    if missing_from_materials:
        errors.append(
            f"Route_ID(s) in Materials missing from Route_Summary: {sorted(missing_from_materials)}"
        )

    return errors


def validate_step_links(steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Check that every (Route_ID, Step_Number) pair in Materials exists in Step_Data.
    Ignore blank rows where Route_ID or Step_Number is missing.
    """
    errors = []

    clean_steps = steps_df.dropna(subset=["Route_ID", "Step_Number"]).copy()
    clean_materials = materials_df.dropna(subset=["Route_ID", "Step_Number"]).copy()

    valid_steps = set(
        zip(
            clean_steps["Route_ID"].astype(str),
            clean_steps["Step_Number"].astype(int)
        )
    )

    material_steps = set(
        zip(
            clean_materials["Route_ID"].astype(str),
            clean_materials["Step_Number"].astype(int)
        )
    )

    missing_steps = material_steps - valid_steps

    if missing_steps:
        errors.append(
            f"(Route_ID, Step_Number) pair(s) in Materials missing from Step_Data: {sorted(missing_steps)}"
        )

    return errors

def validate_metric_inputs(materials_df: pd.DataFrame) -> list[str]:
    """
    Check that rows included in each metric have the required data.
    """
    errors = []

    # Atom economy requires Molar_Mass and Stoich_Coeff
    ae_rows = materials_df.loc[materials_df["Include_in_Atom_Economy"] == True]
    bad_ae = ae_rows.loc[ae_rows["Molar_Mass"].isna() | ae_rows["Stoich_Coeff"].isna()]

    if not bad_ae.empty:
        for _, row in bad_ae.iterrows():
            errors.append(
                f"Atom economy input missing for Route_ID={row['Route_ID']}, "
                f"Step={row['Step_Number']}, Material={row['Material_Name']}"
            )

    # PMI requires Amount_g
    pmi_rows = materials_df.loc[materials_df["Include_in_PMI"] == True]
    bad_pmi = pmi_rows.loc[pmi_rows["Amount_g"].isna()]

    if not bad_pmi.empty:
        for _, row in bad_pmi.iterrows():
            errors.append(
                f"PMI input missing Amount_g for Route_ID={row['Route_ID']}, "
                f"Step={row['Step_Number']}, Material={row['Material_Name']}"
            )

    # E-factor requires Amount_g
    ef_rows = materials_df.loc[materials_df["Include_in_Efactor"] == True]
    bad_ef = ef_rows.loc[ef_rows["Amount_g"].isna()]

    if not bad_ef.empty:
        for _, row in bad_ef.iterrows():
            errors.append(
                f"E-factor input missing Amount_g for Route_ID={row['Route_ID']}, "
                f"Step={row['Step_Number']}, Material={row['Material_Name']}"
            )

    return errors


def run_all_validations(routes_df: pd.DataFrame, steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Run all validation checks and return a single list of errors.
    """
    errors = []
    errors.extend(validate_route_ids(routes_df, steps_df, materials_df))
    errors.extend(validate_step_links(steps_df, materials_df))
    errors.extend(validate_metric_inputs(materials_df))
    return errors