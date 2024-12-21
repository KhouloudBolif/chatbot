from flask import Flask, request, jsonify
from RAG import query_documents, generate_response , index_documents

app = Flask(__name__)


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

@app.route('/ask', methods=['POST'])
def ask_question():
    try:
        # Extraire la question du corps de la requête
        data = request.get_json()
        question = data.get('question', '')

        if not question:
            return jsonify({"error": "La question est requise."}), 400

        # Utiliser les fonctions pour générer une réponse
        relevant_chunks = query_documents(question)
        answer = generate_response(question, relevant_chunks)

        return jsonify({"question": question, "answer": answer.content})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host="0.0.0.0",debug=True)