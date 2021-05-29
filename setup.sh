git clone https://github.com/takenl2021/python_asa
cd ./python_asa
pip install -e .
cd ../
git clone https://github.com/yuce/pyswip.git
cd ./pyswip
pip install -e .
cd ../
pip install fastapi
pip install prolog
apt-get install software-properties-common -y
apt-add-repository ppa:swi-prolog/stable
apt-get update
apt-get install swi-prolog -y