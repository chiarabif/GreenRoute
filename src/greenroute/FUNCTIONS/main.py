from pathlib import Path
import pandas as pd

from loader import load_excel_sheets
from cleaner import clean_routes_df, clean_steps_df, clean_materials_df
from validator import run_all_validations
from builder import build_route
from metrics import calculate_route_metrics


def main():
    project_root = Path(__file__).resolve().parents[3]
    file_path = project_root / "data" / "Excel-data2.xlsx"

    print("Using Excel file:", file_path)
    print("Exists:", file_path.exists())

    routes_df, steps_df, materials_df = load_excel_sheets(str(file_path))

    routes_df = clean_routes_df(routes_df)
    steps_df = clean_steps_df(steps_df)
    materials_df = clean_materials_df(materials_df)

    errors = run_all_validations(routes_df, steps_df, materials_df)

    print("\n--- VALIDATION RESULTS ---")
    if not errors:
        print("All validations passed.")
    else:
        print("Validation errors found:")
        for error in errors:
            print("-", error)
        return

    route_ids = routes_df["Route_ID"].dropna().unique().tolist()
    all_results = []

    print("\n--- CALCULATING METRICS FOR ALL ROUTES ---")
    for route_id in route_ids:
        try:
            route = build_route(route_id, routes_df, steps_df, materials_df)
            result = calculate_route_metrics(route)
            all_results.append(result)
            print(f"Done: {route_id}")
        except Exception as e:
            print(f"Error for {route_id}: {e}")

    results_df = pd.DataFrame(all_results)

    preferred_order = [
        "drug_name",
        "route_id",
        "route_name",
        "target_product",
        "atom_economy_percent",
        "pmi",
        "e_factor",
        "overall_yield_percent_from_summary",
        "overall_yield_percent_from_steps",
        "number_of_steps",
        "step_penalty",
        "average_hazard_score",
        "recommended_solvents_count",
        "problematic_solvents_count",
        "hazardous_solvents_count",
        "overall_solvent_profile",
    ]
    results_df = results_df[[col for col in preferred_order if col in results_df.columns]]

    print("\n--- RESULTS TABLE ---")
    print(results_df)

    output_dir = project_root / "data" / "results"
    output_dir.mkdir(parents=True, exist_ok=True)

    excel_output_path = output_dir / "calculated_green_metrics.xlsx"
    csv_output_path = output_dir / "calculated_green_metrics.csv"

    try:
        results_df.to_excel(excel_output_path, index=False)
        print("\nSaved Excel results to:", excel_output_path)
    except PermissionError:
        print(
            f"\nCould not save Excel file because it is open or locked:\n{excel_output_path}"
        )

    try:
        results_df.to_csv(csv_output_path, index=False)
        print("Saved CSV results to:", csv_output_path)
    except PermissionError:
        print(
            f"\nCould not save CSV file because it is open or locked:\n{csv_output_path}"
        )


if __name__ == "__main__":
    main()