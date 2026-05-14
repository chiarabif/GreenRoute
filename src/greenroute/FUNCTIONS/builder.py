import pandas as pd
from models import Route, Step, Material
__all__ = ["build_route", "build_step", "build_material"]

def build_material(row: pd.Series) -> Material:
    """
    Create a Material object from one row of the Materials sheet.
    """
    return Material(
        drug_name=row["Drug_Name"],
        route_id=row["Route_ID"],
        step_number=int(row["Step_Number"]),
        material_name=row["Material_Name"],
        role=row["Role"],
        amount_g=row["Amount_g"] if pd.notna(row["Amount_g"]) else None,
        molar_mass=row["Molar_Mass"] if pd.notna(row["Molar_Mass"]) else None,
        stoich_coeff=row["Stoich_Coeff"] if pd.notna(row["Stoich_Coeff"]) else None,
        include_in_atom_economy=bool(row["Include_in_Atom_Economy"]),
        include_in_pmi=bool(row["Include_in_PMI"]),
        include_in_efactor=bool(row["Include_in_Efactor"]),
        solvent_assessment=row["Solvent_Assessment"] if pd.notna(row["Solvent_Assessment"]) else None,
        hazard_score=row["Hazard_Score"] if pd.notna(row["Hazard_Score"]) else None,
        source_or_note=row["Source_or_Note"] if pd.notna(row["Source_or_Note"]) else None,
    )


def build_step(row: pd.Series) -> Step:
    """
    Create a Step object from one row of the Step_Data sheet.
    """
    return Step(
        drug_name=row["Drug_Name"],
        route_id=row["Route_ID"],
        step_number=int(row["Step_Number"]),
        step_name_or_reaction=row["Step_Name_or_Reaction"],
        desired_product_name=row["Desired_Product_Name"],
        desired_product_mw=row["Desired_Product_MW"] if pd.notna(row["Desired_Product_MW"]) else None,
        desired_product_stoich_coeff=row["Desired_Product_Stoich_Coeff"] if pd.notna(row["Desired_Product_Stoich_Coeff"]) else None,
        step_yield_percent=row["Step_Yield_%"] if pd.notna(row["Step_Yield_%"]) else None,
        product_mass_isolated_g=row["Product_Mass_Isolated_g"] if pd.notna(row["Product_Mass_Isolated_g"]) else None,
        final_step_yn=bool(row["Final_Step_YN"]),
        notes=row["Notes"] if pd.notna(row["Notes"]) else None,
    )


def build_route(route_id: str, routes_df: pd.DataFrame, steps_df: pd.DataFrame, materials_df: pd.DataFrame) -> Route:
    """
    Build one complete Route object from the three cleaned data tables.

    This function selects the route summary row, all matching steps, and all
    matching materials for one route ID, then combines them into a single
    Route object that can be passed to the metric functions.
    """
    route_row = routes_df.loc[routes_df["Route_ID"] == route_id].iloc[0]

    route_steps_df = steps_df.loc[steps_df["Route_ID"] == route_id].sort_values("Step_Number")
    route_materials_df = materials_df.loc[materials_df["Route_ID"] == route_id].sort_values(
        ["Step_Number", "Material_Name"]
    )

    steps = [build_step(row) for _, row in route_steps_df.iterrows()]
    materials = [build_material(row) for _, row in route_materials_df.iterrows()]

    return Route(
        drug_name=route_row["Drug_Name"],
        route_id=route_row["Route_ID"],
        route_name=route_row["Route_Name"],
        target_product=route_row["Target_Product"],
        final_product_mw=route_row["Final_Product_MW"] if pd.notna(route_row["Final_Product_MW"]) else None,
        number_of_steps=int(route_row["Number_of_Steps"]) if pd.notna(route_row["Number_of_Steps"]) else None,
        overall_yield_percent=route_row["Overall_Yield_%"] if pd.notna(route_row["Overall_Yield_%"]) else None,
        final_product_mass_isolated_g=route_row["Final_Product_Mass_Isolated_g"] if pd.notna(route_row["Final_Product_Mass_Isolated_g"]) else None,
        app_atom_economy_percent=route_row["App_Atom_Economy_%"] if "App_Atom_Economy_%" in route_row.index and pd.notna(route_row["App_Atom_Economy_%"]) else None,
        app_pmi=route_row["App_PMI"] if "App_PMI" in route_row.index and pd.notna(route_row["App_PMI"]) else None,
        app_e_factor=route_row["App_E_factor"] if "App_E_factor" in route_row.index and pd.notna(route_row["App_E_factor"]) else None,
        app_overall_yield_percent=route_row["App_Overall_Yield_%"] if "App_Overall_Yield_%" in route_row.index and pd.notna(route_row["App_Overall_Yield_%"]) else None,
        app_number_of_steps=int(route_row["App_Number_of_Steps"]) if "App_Number_of_Steps" in route_row.index and pd.notna(route_row["App_Number_of_Steps"]) else None,
        app_value_source=route_row["App_Value_Source"] if "App_Value_Source" in route_row.index and pd.notna(route_row["App_Value_Source"]) else None,
        calculation_basis=route_row["Calculation_Basis"] if "Calculation_Basis" in route_row.index and pd.notna(route_row["Calculation_Basis"]) else None,
        data_confidence=route_row["Data_Confidence"] if "Data_Confidence" in route_row.index and pd.notna(route_row["Data_Confidence"]) else None,
        app_notes=route_row["App_Notes"] if "App_Notes" in route_row.index and pd.notna(route_row["App_Notes"]) else None,
        source_or_reference=route_row["Source_or_Reference"] if "Source_or_Reference" in route_row.index and pd.notna(route_row["Source_or_Reference"]) else None,
        notes=route_row["Notes"] if "Notes" in route_row.index and pd.notna(route_row["Notes"]) else None,
        steps=steps,
        materials=materials,
    )