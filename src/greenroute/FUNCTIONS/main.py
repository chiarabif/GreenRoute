from pathlib import Path
import pandas as pd

from loader import load_excel_sheets
from cleaner import clean_routes_df, clean_steps_df, clean_materials_df
from validator import run_all_validations
from builder import build_route
from metrics import calculate_route_metrics


def _order_output_columns(results_df: pd.DataFrame) -> pd.DataFrame:
    """
    Reorder the columns of the final results table so the exported file is
    easier to read.

    Parameters
    results_df : pd.DataFrame
        Table containing the route metrics for all routes.

    Returns
    pd.DataFrame
        The same table with the columns reordered.
    """
    preferred_order = [
        "drug_name",
        "route_id",
        "route_name",
        "target_product",
        "display_atom_economy_percent",
        "display_pmi",
        "display_e_factor",
        "display_overall_yield_percent",
        "display_number_of_steps",
        "used_fallback_atom_economy",
        "used_fallback_pmi",
        "used_fallback_e_factor",
        "used_fallback_overall_yield",
        "used_fallback_number_of_steps",
        "average_hazard_score",
        "recommended_solvents_count",
        "problematic_solvents_count",
        "hazardous_solvents_count",
        "overall_solvent_profile",
        "unknown_solvent_count",
        "app_value_source",
        "calculation_basis",
        "data_confidence",
        "app_notes",
        "calculated_atom_economy_percent",
        "calculated_pmi",
        "calculated_e_factor",
        "calculated_stepwise_yield_percent",
        "pmi_calc_status",
        "efactor_calc_status",
    ]

    ordered_cols = [col for col in preferred_order if col in results_df.columns]
    remaining_cols = [col for col in results_df.columns if col not in ordered_cols]
    return results_df[ordered_cols + remaining_cols]


def _save_results(results_df: pd.DataFrame, output_dir: Path) -> None:
    """
    Save the final results table as both an Excel file and a CSV file.

    Parameters
    results_df : pd.DataFrame
        Final table containing the route metrics.
    output_dir : Path
        Folder where the result files should be saved.

    No returns
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_output_path = output_dir / "calculated_green_metrics.xlsx"
    csv_output_path = output_dir / "calculated_green_metrics.csv"

    try:
        results_df.to_excel(excel_output_path, index=False)
        print(f"Saved Excel results to: {excel_output_path}")
    except PermissionError:
        print(f"Could not save Excel file because it is open or locked:\n{excel_output_path}")

    try:
        results_df.to_csv(csv_output_path, index=False)
        print(f"Saved CSV results to: {csv_output_path}")
    except PermissionError:
        print(f"Could not save CSV file because it is open or locked:\n{csv_output_path}")


def main() -> None:
    """
    Run the full green-metrics workflow from the Excel workbook.

    This function loads the workbook, cleans the three sheets, checks that the
    data is valid, builds the route objects, calculates the metrics for every
    route, and exports the final comparison table.

    """
    project_root = Path(__file__).resolve().parents[3]
    excel_path = project_root / "data" / "Excel-data2.xlsx"

    print(f"Using Excel file: {excel_path}")
    print(f"Exists: {excel_path.exists()}")

    routes_df, steps_df, materials_df = load_excel_sheets(str(excel_path))

    routes_df = clean_routes_df(routes_df)
    steps_df = clean_steps_df(steps_df)
    materials_df = clean_materials_df(materials_df)

    errors = run_all_validations(routes_df, steps_df, materials_df)

    print("\n--- VALIDATION RESULTS ---")
    if errors:
        print("Validation errors found:")
        for error in errors:
            print(f"- {error}")
        return

    print("All validations passed.")

    route_ids = routes_df["Route_ID"].dropna().unique().tolist()
    results = []

    print("\n--- CALCULATING METRICS FOR ALL ROUTES ---")
    for route_id in route_ids:
        try:
            route = build_route(route_id, routes_df, steps_df, materials_df)
            results.append(calculate_route_metrics(route))
            print(f"Done: {route_id}")
        except Exception as exc:
            print(f"Error for {route_id}: {exc}")

    results_df = pd.DataFrame(results)
    results_df = _order_output_columns(results_df)

    print("\n--- RESULTS TABLE ---")
    print(results_df)

    _save_results(results_df, project_root / "data" / "results")


if __name__ == "__main__":
    main()