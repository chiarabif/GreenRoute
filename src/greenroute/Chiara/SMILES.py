import io
import os
import matplotlib.pyplot as plt
from PIL import Image
from rdkit import Chem
from rdkit.Chem import AllChem, Draw
from rdkit.Chem.Draw import rdMolDraw2D

Chem.rdDepictor.SetPreferCoordGen(True)

def _clean_hs(smi):
    mol = Chem.RWMol(Chem.RemoveHs(Chem.MolFromSmiles(smi)))
    for atom in mol.GetAtoms():
        atom.SetNumExplicitHs(0)
        atom.SetNoImplicit(False)
    mol = mol.GetMol()
    Chem.SanitizeMol(mol)
    return mol

molecules = {
    "ibuprofen": Chem.MolFromSmiles("CC(C)CC1=CC=C(C(C(O)=O)C)C=C1"),
    "artemisinin": _clean_hs("C[C@]1(O2)CC[C@@]3([H])[C@H](C)CC[C@@]4([H])[C@@H](C)C(O[C@@]2([H])[C@]43OO1)=O"),
    "sertraline": Chem.MolFromSmiles("CN[C@H]1CC[C@@H](C2=CC=C(Cl)C(Cl)=C2)C3=C1C=CC=C3"),
    "sitagliptin": Chem.MolFromSmiles("FC1=CC(C[C@@H](N)CC(N2CCN3C=NN=C3C2)=O)=C(F)C=C1F"),
}

output_dir = os.path.dirname(os.path.abspath(__file__))

fig, axes = plt.subplots(1, 4, figsize=(20, 5))

for ax, (name, mol) in zip(axes, molecules.items()):
    AllChem.Compute2DCoords(mol)
    if name == "artemisinin":
        mol_prep = Draw.PrepareMolForDrawing(mol, addChiralHs=False, wedgeBonds=True)
        drawer = rdMolDraw2D.MolDraw2DCairo(500, 500)
        drawer.drawOptions().prepareMolsBeforeDrawing = False
        drawer.DrawMolecule(mol_prep)
        drawer.FinishDrawing()
        img = Image.open(io.BytesIO(drawer.GetDrawingText()))
    else:
        img = Draw.MolToImage(mol, size=(500, 500), kekulize=True, wedgeBonds=True)
    img.save(os.path.join(output_dir, f"{name}.png"))
    ax.imshow(img)
    ax.axis("off")
    ax.set_title(name, fontsize=14)

plt.tight_layout()
plt.show()