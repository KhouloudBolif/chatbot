# Chatbot de Sécurité

Ce projet consiste à développer un chatbot de sécurité qui répond aux besoins de cybersécurité, tout en intégrant des fonctionnalités avancées comme l'authentification des utilisateurs, la génération de graphes, et la gestion des menaces en réseau.

## Table des matières
- [À propos](#à-propos)
- [Fonctionnalités](#fonctionnalités)
- [Architecture](#architecture)
- [Prérequis](#prérequis)
- [lancer project](#lancer_projet)


---

## À propos

Le chatbot de sécurité repose sur une architecture modulaire qui combine des technologies modernes pour assurer une communication fluide et sécurisée. Il utilise des frameworks comme Angular pour le front-end et Flask/Spring pour le back-end.

---

## Fonctionnalités

1. **Authentification utilisateur** (Spring + MongoDB).
2. **Support de chat conversationnel** basé sur des modèles de langage avancés.
3. **Analyse et diffusion des menaces en réseau** avec des graphes.
4. **Génération d'images à partir de texte** pour des visualisations enrichies.

---

## Architecture

Voici une vue détaillée de l'architecture :
![WhatsApp Image 2025-01-13 à 18 33 44_fcbd4739](https://github.com/user-attachments/assets/a70df869-fe95-46b1-bff4-84875064d501)


- **Front-End** : Angular, exécuté dans un conteneur Docker.
- **Back-End** : Flask pour la gestion des modèles (chat, graphe et images) et Spring pour l'authentification.
- **Base de données** : MongoDB pour stocker les informations.
- **Modèles** : Intégration de modèles pour la diffusion des menaces en réseau, la génération d'images, et le chat conversationnel.

---
## Prérequis

- **Node.js** et **npm** pour Angular.
- **Python 3.8+** pour Flask.
- **Java 11+** pour Spring.
- **Docker** pour la conteneurisation.
- **MongoDB** installé localement ou en conteneur.



# Pour Lancer le Projet :

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

    

  ## Contributeurs

Ce projet a été réalisé par :
- **Bolif Khouloud**
- **El Bannouri Khaoula**
- **Abderrazzak el Bourkadi**
- **Ayoub Touybi**

---


  
    
     





