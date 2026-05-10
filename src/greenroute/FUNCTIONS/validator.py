import pandas as pd


def validate_required_columns(df: pd.DataFrame, required_columns: list[str], table_name: str) -> list[str]:
    """
    Check that a table contains all the columns it is supposed to have.

    Returns a list of error messages. If the list is empty, the table has
    all the required columns.
    """
    missing = [col for col in required_columns if col not in df.columns]
    if not missing:
        return []
    return [f"{table_name}: missing required columns {missing}"]


def validate_no_missing_route_ids(routes_df: pd.DataFrame, steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Check that every table has a Route_ID and that no Route_ID is missing.
    """
    errors = []

    for table_name, df in [
        ("Route_Summary", routes_df),
        ("Step_Data", steps_df),
        ("Materials", materials_df),
    ]:
        if "Route_ID" not in df.columns:
            errors.append(f"{table_name}: Route_ID column is missing")
            continue

        if df["Route_ID"].isna().any():
            errors.append(f"{table_name}: some Route_ID values are missing")

    return errors


def validate_step_links(routes_df: pd.DataFrame, steps_df: pd.DataFrame) -> list[str]:
    """
    Check that every step refers to a route that exists in Route_Summary.
    """
    errors = []

    if "Route_ID" not in routes_df.columns or "Route_ID" not in steps_df.columns:
        return errors

    valid_route_ids = set(routes_df["Route_ID"].dropna().astype(str))
    step_route_ids = set(steps_df["Route_ID"].dropna().astype(str))

    unknown_ids = sorted(step_route_ids - valid_route_ids)
    if unknown_ids:
        errors.append(f"Step_Data: unknown Route_ID values {unknown_ids}")

    return errors


def validate_material_links(routes_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Check that every material row refers to a route that exists in Route_Summary.
    """
    errors = []

    if "Route_ID" not in routes_df.columns or "Route_ID" not in materials_df.columns:
        return errors

    valid_route_ids = set(routes_df["Route_ID"].dropna().astype(str))
    material_route_ids = set(materials_df["Route_ID"].dropna().astype(str))

    unknown_ids = sorted(material_route_ids - valid_route_ids)
    if unknown_ids:
        errors.append(f"Materials: unknown Route_ID values {unknown_ids}")

    return errors


def validate_final_step_per_route(steps_df: pd.DataFrame) -> list[str]:
    """
    Check that each route has exactly one final step.
    """
    errors = []

    if "Route_ID" not in steps_df.columns or "Final_Step_YN" not in steps_df.columns:
        return errors

    final_counts = (
        steps_df.groupby("Route_ID", dropna=True)["Final_Step_YN"]
        .sum()
    )

    for route_id, count in final_counts.items():
        if count != 1:
            errors.append(f"Step_Data: route {route_id} has {int(count)} final steps instead of 1")

    return errors


def validate_positive_step_numbers(steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Check that step numbers are present and positive in the step and material tables.
    """
    errors = []

    for table_name, df in [("Step_Data", steps_df), ("Materials", materials_df)]:
        if "Step_Number" not in df.columns:
            errors.append(f"{table_name}: Step_Number column is missing")
            continue

        invalid = df["Step_Number"].isna() | (pd.to_numeric(df["Step_Number"], errors="coerce") <= 0)
        if invalid.any():
            errors.append(f"{table_name}: some Step_Number values are missing or not positive")

    return errors


def run_all_validations(routes_df: pd.DataFrame, steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> list[str]:
    """
    Run all validation checks used before calculating the route metrics.

    Returns one list containing all detected problems. If the list is empty,
    the workbook passed all validation checks.
    """
    errors = []

    errors.extend(
        validate_required_columns(
            routes_df,
            [
                "Drug_Name",
                "Route_ID",
                "Route_Name",
                "Target_Product",
            ],
            "Route_Summary",
        )
    )

    errors.extend(
        validate_required_columns(
            steps_df,
            [
                "Drug_Name",
                "Route_ID",
                "Step_Number",
                "Desired_Product_Name",
                "Final_Step_YN",
            ],
            "Step_Data",
        )
    )

    errors.extend(
        validate_required_columns(
            materials_df,
            [
                "Drug_Name",
                "Route_ID",
                "Step_Number",
                "Material_Name",
                "Role",
            ],
            "Materials",
        )
    )

    errors.extend(validate_no_missing_route_ids(routes_df, steps_df, materials_df))
    errors.extend(validate_step_links(routes_df, steps_df))
    errors.extend(validate_material_links(routes_df, materials_df))
    errors.extend(validate_final_step_per_route(steps_df))
    errors.extend(validate_positive_step_numbers(steps_df, materials_df))

    return errors