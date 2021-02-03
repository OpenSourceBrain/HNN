set -e
cd NeuroML2
cd nmllite
python GenerateNetwork.py -single -jnmlnrn
python GenerateNetwork.py -jnmlnrn

omv all -V
