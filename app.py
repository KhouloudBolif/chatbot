from flask import Flask, request, jsonify
from pymongo import MongoClient
from RAG import query_documents, generate_response , index_documents
from datetime import datetime

import uuid

app = Flask(__name__)

# Connexion à MongoDB Atlas
client = MongoClient("mongodb+srv://developer:Chatbot123@cluster0.exyhx.mongodb.net/chatbot?retryWrites=true&w=majority&appName=Cluster0")
db = client["chatbot"]  # Remplacez par le nom de votre base de données
collection = db["questions_answers"] 
sessions_collection = db["sessions"]

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
    
@app.route('/user_history', methods=['POST'])
def get_user_history():
    try:
        # Récupérer l'ID utilisateur depuis le corps de la requête
        data = request.get_json()
        user_id = data.get('user_id', '')

        if not user_id:
            return jsonify({"error": "L'ID utilisateur est requis."}), 400

        # Rechercher toutes les sessions pour cet utilisateur
        sessions = list(sessions_collection.find({"user_id": user_id}, {"_id": 0}))

        if not sessions:
            return jsonify({"message": "Aucune session trouvée pour cet utilisateur."}), 404

        # Ajouter les messages de chaque session
        user_history = []
        for session in sessions:
            session_id = session['session_id']
            messages = list(collection.find({"session_id": session_id}, {"_id": 0}))
            session['messages'] = messages
            user_history.append(session)

        return jsonify({"user_id": user_id, "history": user_history})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)