import copy

def bin_packing_all_combinations(objets, capacite):
    meilleur_resultat = {"bacs": None, "nb": len(objets)}

    def placer(index, bacs):
        if index == len(objets):
            if len(bacs) < meilleur_resultat["nb"]:
                meilleur_resultat["nb"] = len(bacs)
                meilleur_resultat["bacs"] = bacs
            return

        obj = objets[index]

        # Essayer d'ajouter l'objet à chaque bac existant
        for i in range(len(bacs)):
            if sum(bacs[i]) + obj <= capacite:
                nouveaux_bacs = copy.deepcopy(bacs)
                nouveaux_bacs[i].append(obj)
                placer(index + 1, nouveaux_bacs)

        # Essayer de créer un nouveau bac
        nouveaux_bacs = copy.deepcopy(bacs)
        nouveaux_bacs.append([obj])
        placer(index + 1, nouveaux_bacs)

    placer(0, [])
    return meilleur_resultat["nb"], meilleur_resultat["bacs"]

# Exemple d'utilisation
if __name__ == "__main__":
    objets = [5, 2, 6, 2 , 5]
    capacite = 10
    nb_bacs, agencement = bin_packing_all_combinations(objets, capacite)

    print(f"Nombre minimal de bacs : {nb_bacs}")
    for i, bac in enumerate(agencement, 1):
        print(f"Bac {i} : {bac}")
