import pandas as pd
from pathlib import Path

from collections import Counter


def atom_economy(product_mass, reactant_mass):
    """
    Calculate atom economy as a percentage.
    """
    if reactant_mass == 0:
        raise ValueError("Reactant mass cannot be zero")
    return 100 * product_mass / reactant_mass


def e_factor(waste_mass, product_mass):
    """
    Calculate E-factor.
    """
    if product_mass == 0:
        raise ValueError("Product mass cannot be zero")
    return waste_mass / product_mass


def pmi(total_input_mass, product_mass):
    """
    Calculate Process Mass Intensity (PMI).
    """
    if product_mass == 0:
        raise ValueError("Product mass cannot be zero")
    return total_input_mass / product_mass


def overall_yield(yields):
    """
    Calculate overall yield from a list of step yields expressed as fractions.
    """
    if not yields:
        raise ValueError("Yields list cannot be empty")
    if any(y <= 0 or y > 1 for y in yields):
        raise ValueError("Each yield must be between 0 (exclusive) and 1 (inclusive)")
    result = 1.0
    for y in yields:
        result *= y
    return result


def step_penalty(num_steps, penalty_per_step=0.05):
    """
    Penalize long routes.
    """
    if num_steps < 1:
        raise ValueError("Number of steps must be at least 1")
    if not (0 < penalty_per_step < 1):
        raise ValueError("penalty_per_step must be between 0 and 1")
    return (1 - penalty_per_step) ** num_steps


SOLVENT_SCORES = {
    "water": 1,
    "ethanol": 2,
    "methanol": 3,
    "ethyl acetate": 3,
    "acetone": 3,
    "isopropanol": 3,
    "2-propanol": 3,
    "heptane": 4,
    "toluene": 6,
    "dichloromethane": 7,
    "dmf": 7,
    "thf": 6,
    "chloroform": 8,
    "benzene": 10,
    "hexane": 6,
    "acetonitrile": 5,
    "trifluorotoluene": 6,
    "mtbe": 5,
    "isopropyl acetate": 4,
}


def solvent_score(solvent_name):
    key = solvent_name.strip().lower()
    if key not in SOLVENT_SCORES:
        raise ValueError(f"Solvent '{solvent_name}' not found in SOLVENT_SCORES.")
    return SOLVENT_SCORES[key]


def solvent_assessment(solvent_name):
    score = solvent_score(solvent_name)
    if score <= 3:
        category = "Recommended"
    elif score <= 6:
        category = "Problematic"
    else:
        category = "Hazardous"
    return {"solvent": solvent_name, "score": score, "category": category}


def average_hazard_score(hazard_scores):
    valid_scores = [h for h in hazard_scores if h is not None]
    if not valid_scores:
        return None
    return sum(valid_scores) / len(valid_scores)


def calculate_route_metrics(route):
    """
    Calculate all green metrics for a Route object.
    Returns a dictionary of results.
    """

    # ---------------------------
    # Atom economy
    # ---------------------------
    ae_materials = [
        m for m in route.materials
        if m.include_in_atom_economy and m.molar_mass is not None and m.stoich_coeff is not None
    ]
    total_reactant_mass_ae = sum(m.molar_mass * m.stoich_coeff for m in ae_materials)

    if route.final_product_mw is None:
        atom_economy_value = None
    else:
        atom_economy_value = atom_economy(route.final_product_mw, total_reactant_mass_ae)

    # ---------------------------
    # PMI
    # ---------------------------
    pmi_materials = [
        m for m in route.materials
        if m.include_in_pmi and m.amount_g is not None
    ]
    total_input_mass = sum(m.amount_g for m in pmi_materials)

    if route.final_product_mass_isolated_g is None:
        pmi_value = None
    else:
        pmi_value = pmi(total_input_mass, route.final_product_mass_isolated_g)

    # ---------------------------
    # E-factor
    # ---------------------------
    ef_materials = [
        m for m in route.materials
        if m.include_in_efactor and m.amount_g is not None
    ]
    total_efactor_input_mass = sum(m.amount_g for m in ef_materials)

    if route.final_product_mass_isolated_g is None:
        e_factor_value = None
    else:
        waste_mass = total_efactor_input_mass - route.final_product_mass_isolated_g
        e_factor_value = e_factor(waste_mass, route.final_product_mass_isolated_g)

    # ---------------------------
    # Overall yield
    # ---------------------------
    step_yield_values = [
        step.step_yield_percent / 100
        for step in route.steps
        if step.step_yield_percent is not None
    ]

    computed_overall_yield = None
    if step_yield_values:
        computed_overall_yield = overall_yield(step_yield_values) * 100

    # ---------------------------
    # Step count and penalty
    # ---------------------------
    num_steps = route.number_of_steps if route.number_of_steps is not None else len(route.steps)
    step_penalty_value = step_penalty(num_steps) if num_steps else None

    # ---------------------------
    # Solvent summary
    # ---------------------------
    solvent_materials = [m for m in route.materials if m.role and m.role.lower() == "solvent"]

    solvent_results = []
    for m in solvent_materials:
        try:
            solvent_results.append(solvent_assessment(m.material_name))
        except ValueError:
            continue

    solvent_categories = [s["category"] for s in solvent_results]
    solvent_summary = dict(Counter(solvent_categories)) if solvent_categories else {}

    # ---------------------------
    # Hazard summary
    # ---------------------------
    hazard_values = [m.hazard_score for m in route.materials]
    avg_hazard = average_hazard_score(hazard_values)

    return {
        "drug_name": route.drug_name,
        "route_id": route.route_id,
        "route_name": route.route_name,
        "target_product": route.target_product,
        "atom_economy_percent": atom_economy_value,
        "pmi": pmi_value,
        "e_factor": e_factor_value,
        "overall_yield_percent_from_summary": route.overall_yield_percent,
        "overall_yield_percent_from_steps": computed_overall_yield,
        "number_of_steps": num_steps,
        "step_penalty": step_penalty_value,
        "average_hazard_score": avg_hazard,
        "solvent_summary": solvent_summary,
        "solvent_details": solvent_results,
    }