"""
    Dummy apptest.py for greenroute.

    If you don't know what this is for, just leave it empty.
    Read more about pytest fixtures under:
    - https://docs.pytest.org/en/stable/fixture.html
    - https://docs.pytest.org/en/stable/writing_plugins.html
"""
import pytest

#tests were performed using limiting value in order to find out any flaws in the metrics functions
from greenroute.FUNCTIONS.metrics import (
    atom_economy,
    e_factor,
    pmi,
    overall_yield,
    step_penalty,
    solvent_score,
    solvent_assessment,
    average_hazard_score,
)

def test_atom_economy():
    with pytest.raises(ValueError):
        atom_economy(100, 0)

def test_e_factor():
    with pytest.raises(ValueError):
        e_factor(100, 0)

def test_pmi():
    with pytest.raises(ValueError):
        pmi(500, 0)

def test_overall_yield():
    with pytest.raises(ValueError):
        overall_yield([0.8, 0.0, 0.9])

def test_step_penalty():
    with pytest.raises(ValueError):
        step_penalty(0)

def test_solvent_score():
    with pytest.raises(ValueError):
        solvent_score("unknown_solvent")

def test_solvent_assessment():
    with pytest.raises(ValueError):
        solvent_assessment("unknown_solvent")

def test_average_hazard_score():
    assert average_hazard_score([None, None, None]) is None
