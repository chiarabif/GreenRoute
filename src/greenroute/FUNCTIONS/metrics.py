from collections import Counter


def atom_economy(product_mass, reactant_mass):
    """
    Return atom economy as a percentage.
    """
    if reactant_mass <= 0:
        raise ValueError("Reactant mass must be > 0")
    return 100 * product_mass / reactant_mass


def e_factor(waste_mass, product_mass):
    """
    Return the E-factor of a process.
    """
    if product_mass <= 0:
        raise ValueError("Product mass must be > 0")
    return waste_mass / product_mass


def pmi(total_input_mass, product_mass):
    """
    Return the process mass intensity (PMI).
    """
    if product_mass <= 0:
        raise ValueError("Product mass must be > 0")
    return total_input_mass / product_mass


def overall_yield(yields):
    """
    Multiply step yields written as fractions between 0 and 1.
    """
    if not yields:
        raise ValueError("Yields list cannot be empty")
    if any(y <= 0 or y > 1 for y in yields):
        raise ValueError("Each yield must be between 0 and 1")
    result = 1.0
    for y in yields:
        result *= y
    return result


def step_penalty(num_steps, penalty_per_step=0.05):
    """
    Apply a simple penalty factor based on the number of steps.
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
    "dcm": 7,
    "dmf": 7,
    "thf": 6,
    "chloroform": 8,
    "benzene": 10,
    "hexane": 6,
    "acetonitrile": 5,
    "trifluorotoluene": 6,
    "mtbe": 5,
    "isopropyl acetate": 4,
    "methyl ethyl ketone": 4,
    "mek": 4,
    "meoh": 3,
    "etoh/h2o": 2,
    "mecn/h2o (9:1)": 5,
}


def solvent_score(solvent_name):
    """
    Return the predefined score of a solvent.
    """
    key = solvent_name.strip().lower()
    if key not in SOLVENT_SCORES:
        raise ValueError(f"Solvent '{solvent_name}' not found in SOLVENT_SCORES.")
    return SOLVENT_SCORES[key]


def solvent_assessment(solvent_name):
    """
    Return the score and category of a solvent.
    """
    score = solvent_score(solvent_name)
    if score <= 3:
        category = "Recommended"
    elif score <= 6:
        category = "Problematic"
    else:
        category = "Hazardous"
    return {"solvent": solvent_name, "score": score, "category": category}


def average_hazard_score(hazard_scores):
    """
    Return the average of the valid hazard scores, ignoring None values.
    """
    valid_scores = [h for h in hazard_scores if h is not None]
    if not valid_scores:
        return None
    return sum(valid_scores) / len(valid_scores)


def _group_material_masses_by_step(route, include_attr_name):
    """
    Sum the included material masses for each step of a route.
    """
    step_input_masses = {}
    for material in route.materials:
        include_flag = getattr(material, include_attr_name, False)
        if include_flag and material.amount_g is not None:
            step_no = int(material.step_number)
            step_input_masses[step_no] = step_input_masses.get(step_no, 0.0) + float(material.amount_g)
    return step_input_masses


def _compute_required_step_output_masses(route):
    """
    Back-calculate the required output mass of each step on one common route basis.

    The calculation starts from the final product basis mass and moves backwards
    through the route using the step yields. This makes it possible to compare
    all steps on the same final-product basis.
    """
    if not route.steps:
        return None, None, "No steps available"

    steps = sorted(route.steps, key=lambda s: s.step_number)
    final_step = steps[-1]

    if final_step.desired_product_mw is None or final_step.desired_product_mw <= 0:
        return None, None, "Final step MW missing"

    if route.final_product_mass_isolated_g is not None and route.final_product_mass_isolated_g > 0:
        final_basis_mass = float(route.final_product_mass_isolated_g)
    elif final_step.product_mass_isolated_g is not None and final_step.product_mass_isolated_g > 0:
        final_basis_mass = float(final_step.product_mass_isolated_g)
    else:
        final_basis_mass = float(route.final_product_mw) if route.final_product_mw is not None else None

    if final_basis_mass is None or final_basis_mass <= 0:
        return None, None, "Final basis mass missing"

    required_output_mass = {}
    required_output_moles = {}

    required_output_mass[final_step.step_number] = final_basis_mass
    required_output_moles[final_step.step_number] = final_basis_mass / float(final_step.desired_product_mw)

    for idx in range(len(steps) - 1, 0, -1):
        current_step = steps[idx]
        previous_step = steps[idx - 1]

        if current_step.step_yield_percent is None or current_step.step_yield_percent <= 0:
            return None, None, f"Missing/invalid yield at step {current_step.step_number}"

        if previous_step.desired_product_mw is None or previous_step.desired_product_mw <= 0:
            return None, None, f"Missing MW at step {previous_step.step_number}"

        current_yield = float(current_step.step_yield_percent) / 100.0
        previous_required_moles = required_output_moles[current_step.step_number] / current_yield

        required_output_moles[previous_step.step_number] = previous_required_moles
        required_output_mass[previous_step.step_number] = (
            previous_required_moles * float(previous_step.desired_product_mw)
        )

    return required_output_mass, final_basis_mass, None


def _compute_scaled_route_pmi_or_efactor(route, include_attr_name):
    """
    Compute the scaled route-level input mass used for PMI or E-factor.

    For each step, the included input mass is converted into a step intensity
    and then rescaled to the common final route basis.
    """
    steps = sorted(route.steps, key=lambda s: s.step_number)
    if not steps:
        return None, None, "No steps available"

    step_input_masses = _group_material_masses_by_step(route, include_attr_name)
    required_output_masses, final_basis_mass, err = _compute_required_step_output_masses(route)

    if err is not None:
        return None, None, err

    total_scaled_input_mass = 0.0

    for step in steps:
        step_no = int(step.step_number)

        if step_no not in step_input_masses:
            continue

        if step.product_mass_isolated_g is None or step.product_mass_isolated_g <= 0:
            return None, None, f"Missing isolated product mass at step {step_no}"

        raw_step_input_mass = float(step_input_masses[step_no])
        raw_step_output_mass = float(step.product_mass_isolated_g)

        step_intensity = raw_step_input_mass / raw_step_output_mass
        scaled_step_input_mass = step_intensity * required_output_masses[step_no]
        total_scaled_input_mass += scaled_step_input_mass

    return total_scaled_input_mass, final_basis_mass, None


def calculate_route_metrics(route):
    """
    Calculate the final metrics for one route.

    The function first tries to calculate the metrics directly from the raw
    route data. If that is not possible, it falls back to the App_* values
    stored in the route summary.
    """
    ae_materials = [
        m for m in route.materials
        if m.include_in_atom_economy and m.molar_mass is not None and m.stoich_coeff is not None
    ]
    total_reactant_mass_ae = sum(float(m.molar_mass) * float(m.stoich_coeff) for m in ae_materials)

    calculated_atom_economy = None
    if route.final_product_mw is not None and total_reactant_mass_ae > 0:
        calculated_atom_economy = atom_economy(float(route.final_product_mw), total_reactant_mass_ae)

    scaled_pmi_input_mass, pmi_basis_mass, pmi_err = _compute_scaled_route_pmi_or_efactor(
        route, "include_in_pmi"
    )
    calculated_pmi = None
    if pmi_err is None and scaled_pmi_input_mass is not None and pmi_basis_mass is not None:
        calculated_pmi = pmi(scaled_pmi_input_mass, pmi_basis_mass)

    scaled_ef_input_mass, ef_basis_mass, ef_err = _compute_scaled_route_pmi_or_efactor(
        route, "include_in_efactor"
    )
    calculated_e_factor = None
    if ef_err is None and scaled_ef_input_mass is not None and ef_basis_mass is not None:
        waste_mass = scaled_ef_input_mass - ef_basis_mass
        calculated_e_factor = e_factor(waste_mass, ef_basis_mass)

    step_yield_values = [
        float(step.step_yield_percent) / 100.0
        for step in route.steps
        if step.step_yield_percent is not None
    ]
    calculated_stepwise_yield = None
    if step_yield_values:
        calculated_stepwise_yield = overall_yield(step_yield_values) * 100.0

    final_atom_economy = (
        calculated_atom_economy
        if calculated_atom_economy is not None
        else route.app_atom_economy_percent
    )
    used_fallback_atom_economy = calculated_atom_economy is None and route.app_atom_economy_percent is not None

    final_pmi = calculated_pmi if calculated_pmi is not None else route.app_pmi
    used_fallback_pmi = calculated_pmi is None and route.app_pmi is not None

    final_e_factor = calculated_e_factor if calculated_e_factor is not None else route.app_e_factor
    used_fallback_e_factor = calculated_e_factor is None and route.app_e_factor is not None

    final_overall_yield = (
        route.overall_yield_percent
        if route.overall_yield_percent is not None
        else route.app_overall_yield_percent
    )
    used_fallback_overall_yield = (
        route.overall_yield_percent is None and route.app_overall_yield_percent is not None
    )

    final_num_steps = (
        int(route.number_of_steps)
        if route.number_of_steps is not None
        else int(route.app_number_of_steps)
        if route.app_number_of_steps is not None
        else len(route.steps)
    )
    used_fallback_number_of_steps = (
        route.number_of_steps is None and route.app_number_of_steps is not None
    )

    solvent_materials = [m for m in route.materials if m.role and m.role.lower() == "solvent"]
    solvent_results = []
    unknown_solvents = []

    for m in solvent_materials:
        try:
            solvent_results.append(solvent_assessment(m.material_name))
        except ValueError:
            unknown_solvents.append(m.material_name)

    solvent_categories = [s["category"] for s in solvent_results]
    solvent_counts = Counter(solvent_categories)

    recommended_count = solvent_counts.get("Recommended", 0)
    problematic_count = solvent_counts.get("Problematic", 0)
    hazardous_count = solvent_counts.get("Hazardous", 0)

    if solvent_materials:
        if hazardous_count > 0:
            overall_solvent_profile = "Hazardous"
        elif problematic_count > 0:
            overall_solvent_profile = "Problematic"
        elif recommended_count > 0:
            overall_solvent_profile = "Recommended"
        elif unknown_solvents:
            overall_solvent_profile = "Unknown solvent data"
        else:
            overall_solvent_profile = "No solvent score"
    else:
        overall_solvent_profile = "No solvent data"

    hazard_values = [m.hazard_score for m in route.materials]
    avg_hazard = average_hazard_score(hazard_values)

    return {
        "drug_name": route.drug_name,
        "route_id": route.route_id,
        "route_name": route.route_name,
        "target_product": route.target_product,
        "display_atom_economy_percent": round(final_atom_economy, 2) if final_atom_economy is not None else None,
        "display_pmi": round(final_pmi, 2) if final_pmi is not None else None,
        "display_e_factor": round(final_e_factor, 2) if final_e_factor is not None else None,
        "display_overall_yield_percent": round(final_overall_yield, 2) if final_overall_yield is not None else None,
        "display_number_of_steps": final_num_steps,
        "used_fallback_atom_economy": used_fallback_atom_economy,
        "used_fallback_pmi": used_fallback_pmi,
        "used_fallback_e_factor": used_fallback_e_factor,
        "used_fallback_overall_yield": used_fallback_overall_yield,
        "used_fallback_number_of_steps": used_fallback_number_of_steps,
        "average_hazard_score": round(avg_hazard, 2) if avg_hazard is not None else None,
        "recommended_solvents_count": recommended_count,
        "problematic_solvents_count": problematic_count,
        "hazardous_solvents_count": hazardous_count,
        "overall_solvent_profile": overall_solvent_profile,
        "unknown_solvent_count": len(unknown_solvents),
        "calculated_atom_economy_percent": round(calculated_atom_economy, 2) if calculated_atom_economy is not None else None,
        "calculated_pmi": round(calculated_pmi, 2) if calculated_pmi is not None else None,
        "calculated_e_factor": round(calculated_e_factor, 2) if calculated_e_factor is not None else None,
        "calculated_stepwise_yield_percent": round(calculated_stepwise_yield, 2) if calculated_stepwise_yield is not None else None,
        "app_value_source": route.app_value_source,
        "calculation_basis": route.calculation_basis,
        "data_confidence": route.data_confidence,
        "app_notes": route.app_notes,
        "pmi_calc_status": "ok" if pmi_err is None else pmi_err,
        "efactor_calc_status": "ok" if ef_err is None else ef_err,
    }