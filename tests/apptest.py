import pandas as pd

from greenroute.WEBSITE.app import (
    load_results,
    get_molecule_image_path,
    get_reaction_scheme_path,
    get_molecule_summary,
    render_tags,
    render_molecule_card,
    highlight_best_worst,
)


# Tests that load_results returns an empty DataFrame when the CSV file does not exist.
def test_load_results_returns_empty_dataframe_when_file_missing(tmp_path):
    load_results.clear()

    missing_csv = tmp_path / "missing.csv"

    result = load_results(missing_csv)

    assert isinstance(result, pd.DataFrame)
    assert result.empty


# Tests that load_results correctly reads an existing CSV file.
def test_load_results_reads_existing_csv(tmp_path):
    load_results.clear()

    csv_file = tmp_path / "results.csv"
    csv_file.write_text(
        "drug_name,route_name,score\n"
        "Ibuprofen,Boots,85\n"
    )

    result = load_results(csv_file)

    assert len(result) == 1
    assert result.loc[0, "drug_name"] == "Ibuprofen"
    assert result.loc[0, "route_name"] == "Boots"
    assert result.loc[0, "score"] == 85


# Tests that load_results corrects the spelling from Sertralin to Sertraline.
def test_load_results_corrects_sertralin_spelling(tmp_path):
    load_results.clear()

    csv_file = tmp_path / "results.csv"
    csv_file.write_text(
        "drug_name,route_name,score\n"
        "Sertralin,Pfizer,90\n"
    )

    result = load_results(csv_file)

    assert result.loc[0, "drug_name"] == "Sertraline"

# Tests that get_molecule_image_path returns None when the molecule is not in the dictionary.
def test_get_molecule_image_path_unknown_molecule(tmp_path, monkeypatch):
    monkeypatch.setattr("greenroute.WEBSITE.app.SMILES_IMAGE_DIR", tmp_path)

    result = get_molecule_image_path("Unknown Molecule")

    assert result is None


# Tests that get_molecule_image_path returns the correct image path when the molecule exists and the image file exists.
def test_get_molecule_image_path_existing_file(tmp_path, monkeypatch):
    fake_image = tmp_path / "ibuprofen.png"
    fake_image.write_text("fake image content")

    fake_files = {
        "Ibuprofen": "ibuprofen.png"
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.SMILES_IMAGE_DIR", tmp_path)
    monkeypatch.setattr("greenroute.WEBSITE.app.molecule_image_files", fake_files)

    result = get_molecule_image_path("Ibuprofen")

    assert result == fake_image
    assert result.exists()


# Tests that get_molecule_image_path returns None when the molecule is in the dictionary but the image file does not exist.
def test_get_molecule_image_path_missing_file(tmp_path, monkeypatch):
    fake_files = {
        "Ibuprofen": "ibuprofen.png"
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.SMILES_IMAGE_DIR", tmp_path)
    monkeypatch.setattr("greenroute.WEBSITE.app.molecule_image_files", fake_files)

    result = get_molecule_image_path("Ibuprofen")

    assert result is None


# Tests that get_molecule_image_path uses the correct filename from the molecule_image_files dictionary.
def test_get_molecule_image_path_uses_correct_filename(tmp_path, monkeypatch):
    fake_image = tmp_path / "sertraline.png"
    fake_image.write_text("fake image content")

    fake_files = {
        "Sertraline": "sertraline.png"
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.SMILES_IMAGE_DIR", tmp_path)
    monkeypatch.setattr("greenroute.WEBSITE.app.molecule_image_files", fake_files)

    result = get_molecule_image_path("Sertraline")

    assert result == fake_image
    assert result.name == "sertraline.png"

# Tests that get_reaction_scheme_path returns None when the route name does not match any known keyword.
def test_get_reaction_scheme_path_unknown_route(tmp_path, monkeypatch):
    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    result = get_reaction_scheme_path("unknown route")

    assert result is None


# Tests that get_reaction_scheme_path returns the correct image path when the route keyword matches and the image file exists.
def test_get_reaction_scheme_path_existing_boots_file(tmp_path, monkeypatch):
    fake_image = tmp_path / "ibuprofen_boots.png"
    fake_image.write_text("fake image content")

    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    result = get_reaction_scheme_path("Boots route")

    assert result == fake_image
    assert result.exists()


# Tests that get_reaction_scheme_path returns None when the route keyword matches but the image file does not exist.
def test_get_reaction_scheme_path_missing_file(tmp_path, monkeypatch):
    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    result = get_reaction_scheme_path("Boots route")

    assert result is None


# Tests that get_reaction_scheme_path matches route names without caring about uppercase or lowercase letters.
def test_get_reaction_scheme_path_case_insensitive(tmp_path, monkeypatch):
    fake_image = tmp_path / "ibuprofen_boots.png"
    fake_image.write_text("fake image content")

    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    result = get_reaction_scheme_path("BOOTS ROUTE")

    assert result == fake_image


# Tests that alternative route names which map to the same image return the same file path.
def test_get_reaction_scheme_path_alternative_names_same_image(tmp_path, monkeypatch):
    fake_image = tmp_path / "ibuprofen_bhc.png"
    fake_image.write_text("fake image content")

    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    assert get_reaction_scheme_path("BHC route") == fake_image
    assert get_reaction_scheme_path("Hoechst route") == fake_image
    assert get_reaction_scheme_path("Celanese route") == fake_image


# Tests that continuous-flow and continuous flow route names both return the flow reaction image.
def test_get_reaction_scheme_path_continuous_flow_variations(tmp_path, monkeypatch):
    fake_image = tmp_path / "ibuprofen_flow.png"
    fake_image.write_text("fake image content")

    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    assert get_reaction_scheme_path("continuous-flow process") == fake_image
    assert get_reaction_scheme_path("continuous flow process") == fake_image


# Tests that sitagliptin second-generation route names return the second-generation image.
def test_get_reaction_scheme_path_sitagliptin_second_generation(tmp_path, monkeypatch):
    fake_image = tmp_path / "sitagliptin_merck_2nd_gen.png"
    fake_image.write_text("fake image content")

    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    assert get_reaction_scheme_path("2nd generation route") == fake_image
    assert get_reaction_scheme_path("second generation route") == fake_image


# Tests that sitagliptin third-generation route names return the third-generation image.
def test_get_reaction_scheme_path_sitagliptin_third_generation(tmp_path, monkeypatch):
    fake_image = tmp_path / "sitagliptin_merck_3rd_gen.png"
    fake_image.write_text("fake image content")

    monkeypatch.setattr("greenroute.WEBSITE.app.REACTION_IMAGE_DIR", tmp_path)

    assert get_reaction_scheme_path("3rd generation route") == fake_image
    assert get_reaction_scheme_path("third generation route") == fake_image

# Tests that get_molecule_summary returns None values when results_df is empty.
def test_get_molecule_summary_empty_results_df(monkeypatch):
    fake_df = pd.DataFrame()

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result == {
        "pathways": None,
        "best_atom_economy": None,
    }


# Tests that get_molecule_summary returns None values when results_df has no drug_name column.
def test_get_molecule_summary_missing_drug_name_column(monkeypatch):
    fake_df = pd.DataFrame({
        "route_name": ["Boots"],
        "display_atom_economy_percent": [77.4],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result == {
        "pathways": None,
        "best_atom_economy": None,
    }


# Tests that get_molecule_summary returns 0 pathways when the molecule is not found.
def test_get_molecule_summary_molecule_not_found(monkeypatch):
    fake_df = pd.DataFrame({
        "drug_name": ["Sertraline"],
        "route_name": ["Pfizer"],
        "display_atom_economy_percent": [80.0],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result == {
        "pathways": 0,
        "best_atom_economy": None,
    }


# Tests that get_molecule_summary counts the number of unique route pathways for a molecule.
def test_get_molecule_summary_counts_unique_pathways(monkeypatch):
    fake_df = pd.DataFrame({
        "drug_name": ["Ibuprofen", "Ibuprofen", "Ibuprofen"],
        "route_name": ["Boots", "BHC", "Boots"],
        "display_atom_economy_percent": [40.0, 77.4, 55.0],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result["pathways"] == 2


# Tests that get_molecule_summary finds the best atom economy value for a molecule.
def test_get_molecule_summary_best_atom_economy(monkeypatch):
    fake_df = pd.DataFrame({
        "drug_name": ["Ibuprofen", "Ibuprofen", "Ibuprofen"],
        "route_name": ["Boots", "BHC", "Flow"],
        "display_atom_economy_percent": [40.0, 77.4, 65.2],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result["best_atom_economy"] == 77.4


# Tests that get_molecule_summary matches molecule names without caring about uppercase or lowercase letters.
def test_get_molecule_summary_case_insensitive_molecule_name(monkeypatch):
    fake_df = pd.DataFrame({
        "drug_name": ["Ibuprofen"],
        "route_name": ["Boots"],
        "display_atom_economy_percent": [40.0],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("IBUPROFEN")

    assert result == {
        "pathways": 1,
        "best_atom_economy": 40.0,
    }


# Tests that get_molecule_summary uses the number of rows as pathways when route_name column is missing.
def test_get_molecule_summary_pathways_without_route_name_column(monkeypatch):
    fake_df = pd.DataFrame({
        "drug_name": ["Ibuprofen", "Ibuprofen", "Ibuprofen"],
        "display_atom_economy_percent": [40.0, 77.4, 65.2],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result["pathways"] == 3


# Tests that get_molecule_summary returns None for best atom economy when the atom economy column is missing.
def test_get_molecule_summary_missing_atom_economy_column(monkeypatch):
    fake_df = pd.DataFrame({
        "drug_name": ["Ibuprofen", "Ibuprofen"],
        "route_name": ["Boots", "BHC"],
    })

    monkeypatch.setattr("greenroute.WEBSITE.app.results_df", fake_df)

    result = get_molecule_summary("Ibuprofen")

    assert result == {
        "pathways": 2,
        "best_atom_economy": None,
    }

# Tests that render_tags shows "No results file" when pathways is None.
def test_render_tags_no_results_file():
    summary = {
        "pathways": None,
        "best_atom_economy": None,
    }

    result = render_tags(summary)

    assert result == (
        '<div class="tag-row">'
        '<span class="tag tag-muted">No results file</span>'
        '</div>'
    )


# Tests that render_tags shows "No pathways available" when pathways is 0.
def test_render_tags_no_pathways_available():
    summary = {
        "pathways": 0,
        "best_atom_economy": None,
    }

    result = render_tags(summary)

    assert result == (
        '<div class="tag-row">'
        '<span class="tag tag-muted">No pathways available</span>'
        '</div>'
    )


# Tests that render_tags shows singular wording when there is exactly 1 pathway.
def test_render_tags_one_pathway():
    summary = {
        "pathways": 1,
        "best_atom_economy": 50.0,
    }

    result = render_tags(summary)

    assert result == (
        '<div class="tag-row">'
        '<span class="tag tag-green">1 pathway</span>'
        '</div>'
    )


# Tests that render_tags shows plural wording when there is more than 1 pathway.
def test_render_tags_multiple_pathways():
    summary = {
        "pathways": 4,
        "best_atom_economy": 80.0,
    }

    result = render_tags(summary)

    assert result == (
        '<div class="tag-row">'
        '<span class="tag tag-green">4 pathways</span>'
        '</div>'
    )

# Tests that render_molecule_card includes the molecule name and formula in the HTML.
def test_render_molecule_card_includes_name_and_formula(monkeypatch):
    fake_summary = {
        "pathways": 1,
        "best_atom_economy": 75.0,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert '<div class="molecule-title">Ibuprofen</div>' in result
    assert '<div class="molecule-formula">C13H18O2</div>' in result


# Tests that render_molecule_card shows a green progress bar when atom economy is 70 or higher.
def test_render_molecule_card_green_bar_for_high_atom_economy(monkeypatch):
    fake_summary = {
        "pathways": 2,
        "best_atom_economy": 75.0,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert 'class="progress-fill-green"' in result
    assert 'style="width:75.0%;"' in result
    assert '<div class="progress-value">75%</div>' in result


# Tests that render_molecule_card shows an orange progress bar when atom economy is below 70.
def test_render_molecule_card_orange_bar_for_low_atom_economy(monkeypatch):
    fake_summary = {
        "pathways": 2,
        "best_atom_economy": 45.0,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert 'class="progress-fill-orange"' in result
    assert 'style="width:45.0%;"' in result
    assert '<div class="progress-value">45%</div>' in result


# Tests that render_molecule_card limits the progress bar width to 100 when atom economy is above 100.
def test_render_molecule_card_progress_width_maximum_100(monkeypatch):
    fake_summary = {
        "pathways": 2,
        "best_atom_economy": 125.0,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert 'style="width:100%;"' in result
    assert '<div class="progress-value">125%</div>' in result


# Tests that render_molecule_card limits the progress bar width to 0 when atom economy is below 0.
def test_render_molecule_card_progress_width_minimum_0(monkeypatch):
    fake_summary = {
        "pathways": 2,
        "best_atom_economy": -10.0,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert 'style="width:0%;"' in result
    assert '<div class="progress-value">-10%</div>' in result


# Tests that render_molecule_card shows a dash and empty progress bar when atom economy is None.
def test_render_molecule_card_no_atom_economy(monkeypatch):
    fake_summary = {
        "pathways": None,
        "best_atom_economy": None,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert 'class="progress-fill-orange"' in result
    assert 'style="width:0%;"' in result
    assert '<div class="progress-value">—</div>' in result


# Tests that render_molecule_card includes the pathway tags from render_tags.
def test_render_molecule_card_includes_rendered_tags(monkeypatch):
    fake_summary = {
        "pathways": 3,
        "best_atom_economy": 80.0,
    }

    fake_formulas = {
        "Ibuprofen": "C13H18O2",
    }

    monkeypatch.setattr("greenroute.WEBSITE.app.get_molecule_summary", lambda molecule: fake_summary)
    monkeypatch.setattr("greenroute.WEBSITE.app.formulas", fake_formulas)

    result = render_molecule_card("Ibuprofen")

    assert '<span class="tag tag-green">3 pathways</span>' in result

# Tests that highlight_best_worst highlights the highest value as best when higher_is_better is True.
def test_highlight_best_worst_higher_is_better():
    series = pd.Series([10, 20, 30])

    result = highlight_best_worst(series, higher_is_better=True)

    assert result == [
        "background-color: #FFF3E0; color: #E65100; font-weight: 600;",
        "",
        "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;",
    ]


# Tests that highlight_best_worst highlights the lowest value as best when higher_is_better is False.
def test_highlight_best_worst_lower_is_better():
    series = pd.Series([10, 20, 30])

    result = highlight_best_worst(series, higher_is_better=False)

    assert result == [
        "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;",
        "",
        "background-color: #FFF3E0; color: #E65100; font-weight: 600;",
    ]


# Tests that highlight_best_worst marks missing values with the grey missing-value style.
def test_highlight_best_worst_missing_values():
    series = pd.Series([10, None, 30])

    result = highlight_best_worst(series, higher_is_better=True)

    assert result == [
        "background-color: #FFF3E0; color: #E65100; font-weight: 600;",
        "background-color: #F5F5F5; color: #9E9E9E;",
        "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;",
    ]


# Tests that highlight_best_worst returns empty styles when all values are missing.
def test_highlight_best_worst_all_values_missing():
    series = pd.Series([None, None, None])

    result = highlight_best_worst(series, higher_is_better=True)


    assert result == ["", "", ""]

# Tests that highlight_best_worst does not mark a worst value when all valid values are the same.
def test_highlight_best_worst_all_valid_values_same():
    series = pd.Series([20, 20, 20])

    result = highlight_best_worst(series, higher_is_better=True)

    assert result == [
        "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;",
        "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;",
        "background-color: #E4EDE0; color: #2D4A22; font-weight: 700;",
    ]


# Tests that highlight_best_worst keeps middle values unstyled.
def test_highlight_best_worst_middle_values_unstyled():
    series = pd.Series([10, 20, 30, 40])

    result = highlight_best_worst(series, higher_is_better=True)

    assert result[1] == ""
    assert result[2] == ""
