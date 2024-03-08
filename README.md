[![forthebadge](https://forthebadge.com/images/badges/made-with-python.svg)](https://forthebadge.com)
# Gudlft
---
Fork : https://github.com/OpenClassrooms-Student-Center/Python_Testing

### Pré-requis
Avoir un OS **Linux** avec **Python 3.12** installé  
<br/>

### Installation
Executer ces commandes dans un terminal **bash**
pour installer installer le projet
```bash
git clone git@github.com:Jeremie-Silva/Gudlft.git
cd Gudlft
virtualenv -p3.12 .venv
source .venv/bin/activate
pip install -r requirements.txt
```

<br/>

lancer l'application en local :
```bash
export FLASK_APP=server.py
flask run
```
lancer les tests de performance en local :
```bash
locust -f tests/tests_perform_tests/locustfile.py -H http://127.0.0.1:5000 --users 5 --spawn-rate 5
google-chrome http://0.0.0.0:8089/
```
lancer les tests unitaires en local :
```bash
pytest --cov=server --cov-report=html tests/tests_unit_tests/tests_server.py
google-chrome http://localhost:63342/Gudlft/htmlcov/index.html
```
