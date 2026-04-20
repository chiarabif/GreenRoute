def atom_economy(product_mass, reactant_mass):
    """
    Calculate atom economy.
    Higher value = more efficient reaction.
    """
    if reactant_mass == 0:
        raise ValueError("Reactant mass cannot be zero")
    return product_mass / reactant_mass


def e_factor(waste_mass, product_mass):
    """
    Calculate E-factor (environmental factor).
    Lower value = greener process.
    """
    if product_mass == 0:
        raise ValueError("Product mass cannot be zero")
    return waste_mass / product_mass


def pmi(total_input_mass, product_mass):
    """
    Calculate Process Mass Intensity (PMI).
    Lower value = more sustainable process.
    """
    if product_mass == 0:
        raise ValueError("Product mass cannot be zero")
    return total_input_mass / product_mass


def overall_yield(yields):
    """
    Calculate overall yield across multiple synthetic steps.
    Each yield should be a fraction (e.g., 0.85 for 85%).
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
    Calculate a step penalty factor reflecting inefficiency from many synthetic steps.
    Returns a multiplier between 0 and 1 — lower = more penalised.
    """
    if num_steps < 1:
        raise ValueError("Number of steps must be at least 1")
    if not (0 < penalty_per_step < 1):
        raise ValueError("penalty_per_step must be between 0 and 1")
    return (1 - penalty_per_step) ** num_steps


SOLVENT_SCORES = {
    "water":          1,
    "ethanol":        2,
    "methanol":       3,
    "ethyl acetate":  3,
    "acetone":        3,
    "isopropanol":    3,
    "heptane":        4,
    "toluene":        6,
    "dichloromethane":7,
    "dmf":            7,
    "thf":            6,
    "chloroform":     8,
    "benzene":        10,
    "hexane":         6,
}

def solvent_score(solvent_name):
    """
    Return a hazard/greenness score for a given solvent (1-10).
    1-3 = Recommended, 4-6 = Problematic, 7-10 = Hazardous.
    """
    key = solvent_name.strip().lower()
    if key not in SOLVENT_SCORES:
        raise ValueError(
            f"Solvent '{solvent_name}' not found. "
            f"Available solvents: {list(SOLVENT_SCORES.keys())}"
        )
    return SOLVENT_SCORES[key]


def solvent_assessment(solvent_name):
    """
    Return a human-readable greenness category for a solvent.
    Returns a dict with 'score' and 'category'.
    """
    score = solvent_score(solvent_name)
    if score <= 3:
        category = "Recommended"
    elif score <= 6:
        category = "Problematic"
    else:
        category = "Hazardous"
    return {"solvent": solvent_name, "score": score, "category": category}


def hazard_score(flammability, toxicity, reactivity, weights=(0.35, 0.45, 0.20)):
    """
    Calculate a composite hazard score (0-10).
    Lower score = safer process.
    """
    scores = (flammability, toxicity, reactivity)
    if any(not (0 <= s <= 10) for s in scores):
        raise ValueError("All hazard scores must be between 0 and 10")
    if abs(sum(weights) - 1.0) > 1e-6:
        raise ValueError("Weights must sum to 1")
    return sum(s * w for s, w in zip(scores, weights))