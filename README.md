# Chatbot Partie RAG 

Ce projet fait partie d'un système de Retrieval-Augmented Generation (RAG) pour un Chatbot.
L'objectif est de fournir des réponses contextuelles précises en utilisant des informations extraitesà partir de données externes.

## 📌 Prérequis
Clé API OpenAI
Vous devez disposer d'une clé API valide d'OpenAI.

## Build et Lancer l'application avec Docker

  1.Cloner le dépôt :

    
        git clone [lien du dépôt]

  2. Accéder au répertoire du projet :
       ```bash
       cd repertoire/de/projet
       
  4. Environnement Virtuel :
     Créez un fichier .env à la racine du projet avec la clé sous la forme suivante :
       ```bash
       OPENAI_API_KEY="SECRET_KEY"

  5.Builder le container avec Docker Compose :

   
     docker-compose up --build -d

  6.Lancer le projet :
  si le projet deja builder il suffiit de le lancer avec la cmd suivante :
  
    
    docker-compose up 

    

  


  
    
     





