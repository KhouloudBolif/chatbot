from flask import Flask, request, jsonify, send_file
import joblib
import networkx as nx
from NetworkModel.model import GCN
import matplotlib.pyplot as plt
from io import BytesIO
#installation 
#pip install torch torchvision torchaudio
#pip install torch-geometric
# pip install networkx
#pip install joblib
#pip install matplotlib
def linear_threshold(G, initial_infected, node_thresholds):
    # Initialiser les ensembles de nœuds infectés
    newly_infected = set(initial_infected)  # Nœuds récemment infectés
    total_infected = set(initial_infected)  # Tous les nœuds infectés
    influence = {node: 0.0 for node in G.nodes}  # Influence exercée sur chaque nœud

    # Boucle jusqu'à ce qu'il n'y ait plus de propagation
    while newly_infected:
        next_infected = set()  # Liste des nœuds à infecter au prochain tour
        
        # Pour chaque nœud récemment infecté
        for node in newly_infected:
            # Examiner tous les voisins
            for neighbor in G.neighbors(node):
                if neighbor not in total_infected:  # Si le voisin n'est pas déjà infecté
                    # Ajouter l'influence basée sur le poids de l'arête
                    influence[neighbor] += G[node][neighbor]['weight']
                    
                    # Vérifier si le voisin a un seuil dans node_thresholds
                    if neighbor in node_thresholds:
                        # Si l'influence atteint ou dépasse le seuil du voisin, il devient infecté
                        if influence[neighbor] >= node_thresholds[neighbor]:
                            next_infected.add(neighbor)
                    else:
                        # Si le seuil du voisin est manquant, retourner une erreur ou utiliser un seuil par défaut
                        print(f"Warning: No threshold for neighbor {neighbor}, using default threshold.")
                        default_threshold = 0.5  # Ex: seuil par défaut
                        if influence[neighbor] >= default_threshold:
                            next_infected.add(neighbor)

        # Mettre à jour les ensembles de nœuds infectés
        total_infected.update(next_infected)
        newly_infected = next_infected  # Nouveaux nœuds infectés pour le prochain tour

    # Retourner la liste de tous les nœuds infectés
    return total_infected


