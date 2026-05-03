import pandas as pd
from pathlib import Path


# ---------------------------
# Your metric functions
# ---------------------------

def atom_economy(product_mass, reactant_mass):
    if reactant_mass == 0:
        raise ValueError("Reactant mass cannot be zero")
    return 100 * product_mass / reactant_mass


def e_factor(waste_mass, product_mass):
    if product_mass == 0:
        raise ValueError("Product mass cannot be zero")
    return waste_mass / product_mass


def pmi(total_input_mass, product_mass):
    if product_mass == 0:
        raise ValueError("Product mass cannot be zero")
    return total_input_mass / product_mass


def overall_yield(yields):
    if not yields:
        raise ValueError("Yields list cannot be empty")
    if any(y <= 0 or y > 1 for y in yields):
        raise ValueError("Each yield must be between 0 and 1")
    result = 1.0
    for y in yields:
        result *= y
    return result


def step_penalty(num_steps, penalty_per_step=0.05):
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
    "methylene dichloride": 7,
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
    key = str(solvent_name).strip().lower()
    if key not in SOLVENT_SCORES:
        raise ValueError(f"Solvent '{solvent_name}' not found.")
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


def average_material_hazard(scores):
    vals = [float(s) for s in scores if pd.notna(s)]
    if not vals:
        return None
    return sum(vals) / len(vals)