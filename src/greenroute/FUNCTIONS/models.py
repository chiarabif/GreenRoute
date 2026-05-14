from dataclasses import dataclass, field
from typing import Optional

__all__ = ["Route", "Step", "Material"]

@dataclass
class Material:
    """
    Store the information for one material used in one step of a route.
    """
    drug_name: str
    route_id: str
    step_number: int
    material_name: str
    role: str
    amount_g: Optional[float]
    molar_mass: Optional[float]
    stoich_coeff: Optional[float]
    include_in_atom_economy: bool
    include_in_pmi: bool
    include_in_efactor: bool
    solvent_assessment: Optional[str] = None
    hazard_score: Optional[float] = None
    source_or_note: Optional[str] = None


@dataclass
class Step:
    """
    Store the information for one synthetic step in a route.
    """
    drug_name: str
    route_id: str
    step_number: int
    step_name_or_reaction: str
    desired_product_name: str
    desired_product_mw: Optional[float]
    desired_product_stoich_coeff: Optional[float]
    step_yield_percent: Optional[float]
    product_mass_isolated_g: Optional[float]
    final_step_yn: bool
    notes: Optional[str] = None


@dataclass
class Route:
    """
    Store all information linked to one synthesis route.

    A Route object contains the route-level summary values together with the
    list of its steps and materials. It is the main object passed to the
    metric functions.
    """
    drug_name: str
    route_id: str
    route_name: str
    target_product: str
    final_product_mw: Optional[float]
    number_of_steps: Optional[int]
    overall_yield_percent: Optional[float]
    final_product_mass_isolated_g: Optional[float]

    app_atom_economy_percent: Optional[float] = None
    app_pmi: Optional[float] = None
    app_e_factor: Optional[float] = None
    app_overall_yield_percent: Optional[float] = None
    app_number_of_steps: Optional[int] = None
    app_value_source: Optional[str] = None
    calculation_basis: Optional[str] = None
    data_confidence: Optional[str] = None
    app_notes: Optional[str] = None

    source_or_reference: Optional[str] = None
    notes: Optional[str] = None
    steps: list[Step] = field(default_factory=list)
    materials: list[Material] = field(default_factory=list)