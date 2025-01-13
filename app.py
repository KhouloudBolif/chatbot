from flask import Flask, request, jsonify , send_file
from pymongo import MongoClient
from RAG import query_documents, generate_response , index_documents
from datetime import datetime
import joblib
import networkx as nx
from NetworkModel.model import GCN
import matplotlib.pyplot as plt
from io import BytesIO
import uuid
from NetworkModel.Graph import linear_threshold
from flask_cors import CORS
import base64
from PIL import Image
import traceback
from bson.objectid import ObjectId
import io
app = Flask(__name__)
# Autoriser les requêtes de localhost:4200
CORS(app, origins=["http://localhost:4200"])
# Connexion à MongoDB Atlas
client = MongoClient("mongodb+srv://developer:Chatbot123@cluster0.exyhx.mongodb.net/chatbot?retryWrites=true&w=majority&appName=Cluster0")
db = client["chatbot"]  # Remplacez par le nom de votre base de données
collection = db["questions_answers"] 
sessions_collection = db["sessions"]
collection = db["graph_images"] 
#Model de Graph network 

# Charger le modèle et la fonction
model_data = joblib.load('NetworkModel\model_menace.pkl')
model = model_data['model']
linear_threshold = model_data['linear_threshold']

# Endpoint pour ajouter Data dans RAG 
@app.route('/index', methods=['POST'])
def index_documents_api():
    try:
        # Extraire le chemin du dossier depuis la requête
        data = request.get_json()
        #folder_path = data.get("folder_path")
        folder_path="./data"
        if not folder_path:
            return jsonify({"error": "Le chemin du dossier est requis."}), 400
        
        # Appeler la fonction pour indexer les documents
        index_documents(folder_path)
        
        return jsonify({"message": f"Les documents du dossier '{folder_path}' ont été indexés avec succès."})
    except Exception as e:
        return jsonify({"error": f"Erreur inattendue : {str(e)}"}), 500
    
# Endpoint pour démarrer une nouvelle session
@app.route('/start_session', methods=['POST'])
def start_session():
    try:
        data = request.get_json()
        user_id = data.get('user_id', '')

        if not user_id:
            return jsonify({"error": "L'ID utilisateur est requis."}), 400

        # Générer un ID de session unique
        session_id = str(uuid.uuid4())

        # Enregistrer la session dans MongoDB
        session = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.utcnow()
        }
        sessions_collection.insert_one(session)

        return jsonify({"message": "Session démarrée avec succès.", "session_id": session_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint pour poser une question
@app.route('/ask', methods=['POST'])
def ask_question():
    try:
    
          # Extraire la question et l'ID utilisateur du corps de la requête
        data = request.get_json()
        session_id = data.get('session_id', '')
        question = data.get('question', '')
        #user_id = data.get('user_id', '')  # ID utilisateur envoyé dans la requête

        if not question:
            return jsonify({"error": "La question est requise."}), 400
        
        if not session_id or not question:
            return jsonify({"error": "L'ID de session et la question sont requis."}), 400
        
        # Vérifier si la session existe
        session = sessions_collection.find_one({"session_id": session_id})
        if not session:
            return jsonify({"error": "Session invalide."}), 404
       # if not user_id:
        #    return jsonify({"error": "L'ID utilisateur est requis."}), 400

        # Utiliser les fonctions pour générer une réponse
        relevant_chunks = query_documents(question)
        answer = generate_response(question, relevant_chunks)

        timestamp = datetime.utcnow()  # Heure actuelle en UTC
        # Stocker la question, la réponse, et l'ID utilisateur dans MongoDB
        record = {
            "session_id": session_id,
            "question": question,
            "answer": answer.content,
            #"relevant_chunks": relevant_chunks,
            "timestamp": timestamp # Heure en UTC
        }
        collection.insert_one(record)
       
        return jsonify({"question": question, "answer": answer.content , "session_id": session_id , "timestamp": timestamp.isoformat()   })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    

# Endpoint pour récupérer l'historique d'une session
@app.route('/session_history', methods=['POST'])
def get_session_history():
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')

        if not session_id:
            return jsonify({"error": "L'ID de session est requis."}), 400

        # Récupérer tous les messages associés à cette session
        history = list(collection.find({"session_id": session_id}, {"_id": 0}))

        if not history:
            return jsonify({"message": "Aucun message trouvé pour cette session."}), 404

        return jsonify({"session_id": session_id, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/allhistory', methods=['POST'])
def history():
    try:
        data = request.get_json()
        session_id = data.get('session_id', '')

        if not session_id:
            return jsonify({"error": "L'ID de session est requis."}), 400

        # Récupérer tous les messages associés à cette session, triés par timestamp décroissant, et limiter à 3 messages
        history = list(collection.find({"session_id": session_id}, {"_id": 0}).sort("timestamp", -1).limit(3))

        if not history:
            return jsonify({"message": "Aucun message trouvé pour cette session."}), 404

        return jsonify({"session_id": session_id, "history": history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Charger les données du graphe
    edges = data['edges']
    initial_infected = data['initial_infected']
    node_thresholds = data['node_thresholds']

    # Construire le graphe
    G = nx.Graph()
    for src, dst, weight in edges:
        G.add_edge(src, dst, weight=weight)

    # Appliquer la fonction linear_threshold
    infected_nodes = linear_threshold(G, initial_infected, node_thresholds)

    return jsonify({'infected_nodes': list(infected_nodes)})

@app.route('/visualize', methods=['POST'])
def visualize():
    # Récupérer les données JSON envoyées par le client
    data = request.get_json()

    edges = data['edges']
    initial_infected = data['initial_infected']
    node_thresholds = data['node_thresholds']

    # Construire le graphe
    G = nx.Graph()
    for src, dst, weight in edges:
        G.add_edge(src, dst, weight=weight)

    # Déterminer les nœuds infectés
    infected_nodes = linear_threshold(G, initial_infected, node_thresholds)

    # Générer le graphe avec NetworkX et Matplotlib
    pos = nx.spring_layout(G)
    node_colors = ['red' if node in infected_nodes else 'skyblue' for node in G.nodes]

    plt.figure(figsize=(8, 6))
    nx.draw(
        G,
        pos,
        with_labels=True,
        node_color=node_colors,
        edge_color='gray',
        node_size=2000,
        font_size=12,
        font_weight='bold'
    )
    plt.title("Propagation des menaces dans le réseau")

    # Encoder l'image en Base64
    from io import BytesIO
    buffer = BytesIO()
    plt.savefig(buffer, format="png")
    plt.close()
    buffer.seek(0)
    image_base64 = base64.b64encode(buffer.read()).decode('utf-8')
    buffer.close()

    # Sauvegarder dans MongoDB
    image_data = {
        'name': 'graph_image.png',
        'image_base64': image_base64
    }
    collection.insert_one(image_data)

    return jsonify({"message": "Image saved successfully.", "image_base64": image_base64})

# Fonction de propagation (exemple simplifié, à personnaliser selon vos besoins)
def linear_threshold(G, initial_infected, node_thresholds):
    # Exemple de logique simplifiée pour la propagation
    infected = set(initial_infected)
    for node in G.nodes:
        if node not in infected and G.degree[node] > node_thresholds.get(node, 1):
            infected.add(node)
    return infected

@app.route('/upload', methods=['POST'])
def upload_image():
    try:
        # Récupérer les données de l'image du corps de la requête
        data = request.get_json()
        if 'image' not in data:
            return jsonify({"message": "Missing 'image' field in the request body."}), 400
        
        # Décoder l'image encodée en Base64
        image_data = base64.b64decode(data['image'])
        
        # Convertir les données binaires en PNG avec Pillow
        image = Image.open(io.BytesIO(image_data))
        output = io.BytesIO()
        image.save(output, format="PNG")
        output.seek(0)

        # Enregistrer l'image dans MongoDB
        image_record = {"image": output.getvalue()}
        result = collection.insert_one(image_record)

        # Retourner l'image en réponse
        output.seek(0)  # Réinitialiser le pointeur pour lecture
        return send_file(output, mimetype='image/png')
    except Exception as e:
        traceback.print_exc()  # Pour débogage
        return jsonify({"message": "An error occurred while processing the image.", "error": str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)