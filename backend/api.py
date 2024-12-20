from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import json

app = Flask(__name__)
CORS(app)  # Activer CORS pour toutes les routes
socketio = SocketIO(app, cors_allowed_origins="*")  # Initialiser SocketIO

# Chargement des identifiants depuis un fichier JSON
with open("users.json", "r") as file:
    USERS = json.load(file)

# Variable pour stocker la dernière donnée reçue
dernieres_donnees = {}

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        email = data.get('email')
        password = data.get('password')

        # Vérification des identifiants pour plusieurs utilisateurs
        user = next((user for user in USERS if user['email'] == email and user['password'] == password), None)

        if user:
            return jsonify({"success": True, "message": "Connexion réussie."}), 200
        return jsonify({"success": False, "message": "Email ou mot de passe incorrect."}), 401

    except Exception as e:
        print(f"Erreur lors de la connexion : {e}")
        return jsonify({"success": False, "message": "Erreur interne du serveur."}), 500

@app.route('/api/site-state', methods=['POST', 'GET'])
def site_state():
    global dernieres_donnees
    if request.method == 'POST':
        try:
            data = request.json
            if not data or 'parameter' not in data:
                return jsonify({"error": "Le champ 'parameter' est requis."}), 400

            dernieres_donnees = data  # Stocker les données reçues
            print(f"Data reçue : {data}")
            
            # Envoyer les données via WebSocket à tous les clients connectés
            socketio.emit('update', {"message": f"Nouvelles données : {data['parameter']}"})
            
            return jsonify({"message": "Requête POST traitée avec succès."}), 200

        except Exception as e:
            print(f"Erreur lors de la requête POST : {e}")
            return jsonify({"error": "Erreur lors du traitement des données."}), 500

    elif request.method == 'GET':
        try:
            print(f"Requête GET reçue sur /api/site-state")
            if dernieres_donnees and 'parameter' in dernieres_donnees:
                return jsonify({"message": f"Dernières données reçues : {dernieres_donnees['parameter']}"}), 200
            else:
                return jsonify({"message": "Aucune donnée disponible."}), 200

        except Exception as e:
            print(f"Erreur lors de la requête GET : {e}")
            return jsonify({"error": "Erreur interne du serveur."}), 500

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5001, debug=True)