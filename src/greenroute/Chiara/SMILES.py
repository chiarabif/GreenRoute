from rdkit import Chem
from rdkit.Chem import AllChem, Draw

# Use better coordinate generator (but not aggressive styling)
Chem.rdDepictor.SetPreferCoordGen(True)

# Molecules
ibuprofen = Chem.MolFromSmiles("CC(C)CC1=CC=C(C(C(O)=O)C)C=C1")
artemisinin = Chem.MolFromSmiles("O=C1OC2CC3CCC(C)(O3)OC2(C)C1")
sertraline = Chem.MolFromSmiles("CN[C@H]1CC[C@@H](C2=CC=CC=C2)C1")
sitagliptin = Chem.MolFromSmiles("FC1=CC(C[C@@H](N)CC(N2CCN3C=NN=C3C2)=O)=C(F)C=C1F")

# Function to improve layout but keep chemistry correct
def draw_clean(mol):
    AllChem.Compute2DCoords(mol)  # improves layout ONLY

    img = Draw.MolToImage(
        mol,
        size=(500, 500),
        kekulize=True,
        wedgeBonds=True   # keeps stereochemistry wedges
    )
    img.show()

# Show molecules separately
draw_clean(ibuprofen)
draw_clean(artemisinin)
draw_clean(sertraline)
draw_clean(sitagliptin)