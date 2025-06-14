import tkinter as tk
import copy

def NFDH(rectangles, W, H):
    rectangles = sorted(rectangles, key=lambda r: r[1], reverse=True)
    placements = []
    current_shelf_y = 0
    current_shelf_height = 0
    current_x = 0

    for i, (w, h) in enumerate(rectangles):
        if w > W or h > H:
            continue

        if current_x + w > W:
            current_shelf_y += current_shelf_height
            if current_shelf_y + h > H:
                continue
            current_x = 0
            current_shelf_height = h

        placements.append({
            "id": i + 1,
            "position": (current_x, current_shelf_y),
            "dimension": (w, h)
        })
        current_x += w
        current_shelf_height = max(current_shelf_height, h)

    return placements

def FFDH(rectangles, W, H):
    rectangles = sorted(rectangles, key=lambda r: r[1], reverse=True)
    shelves = []  # Chaque étagère = (y_start, height, used_width)
    placements = []

    for i, (w, h) in enumerate(rectangles):
        placed = False
        for shelf in shelves:
            y_start, shelf_height, used_width = shelf
            if h <= shelf_height and used_width + w <= W:
                placements.append({
                    "id": i + 1,
                    "position": (used_width, y_start),
                    "dimension": (w, h)
                })
                shelf[2] += w  # mise à jour largeur utilisée
                placed = True
                break

        if not placed:
            current_y = sum(s[1] for s in shelves)
            if current_y + h > H:
                continue  # impossible à placer
            shelves.append([current_y, h, w])
            placements.append({
                "id": i + 1,
                "position": (0, current_y),
                "dimension": (w, h)
            })

    return placements

def BFDH(rectangles, W, H):
    rectangles = sorted(rectangles, key=lambda r: r[1], reverse=True)
    shelves = []  # Chaque étagère = (y_start, height, used_width)
    placements = []

    for i, (w, h) in enumerate(rectangles):
        best_shelf = None
        min_space_left = float('inf')

        for shelf in shelves:
            y_start, shelf_height, used_width = shelf
            space_left = W - used_width
            if h <= shelf_height and w <= space_left and space_left < min_space_left:
                best_shelf = shelf
                min_space_left = space_left

        if best_shelf:
            y_start, shelf_height, used_width = best_shelf
            placements.append({
                "id": i + 1,
                "position": (used_width, y_start),
                "dimension": (w, h)
            })
            best_shelf[2] += w
        else:
            current_y = sum(s[1] for s in shelves)
            if current_y + h > H:
                continue
            shelves.append([current_y, h, w])
            placements.append({
                "id": i + 1,
                "position": (0, current_y),
                "dimension": (w, h)
            })

    return placements

def brute_force_packing_2d(rectangles, W, H):
    meilleur = {"placements": None, "shelves": None, "nb_shelves": float("inf")}

    def placer(index, placements, shelves):
        if index == len(rectangles):
            if len(shelves) < meilleur["nb_shelves"]:
                meilleur["nb_shelves"] = len(shelves)
                meilleur["placements"] = copy.deepcopy(placements)
                meilleur["shelves"] = copy.deepcopy(shelves)
            return

        w, h = rectangles[index]

        # Essayer de placer le rectangle sur chaque étagère existante
        for i in range(len(shelves)):
            y_start, shelf_height, used_width = shelves[i]
            if h <= shelf_height and used_width + w <= W:
                # Créer nouvelle configuration
                new_placements = copy.deepcopy(placements)
                new_shelves = copy.deepcopy(shelves)
                new_shelves[i][2] += w  # ajouter largeur utilisée
                new_placements.append({
                    "id": index + 1,
                    "position": (used_width, y_start),
                    "dimension": (w, h)
                })
                placer(index + 1, new_placements, new_shelves)

        # Essayer de créer une nouvelle étagère
        current_y = sum(s[1] for s in shelves)
        if current_y + h <= H:
            new_placements = copy.deepcopy(placements)
            new_shelves = copy.deepcopy(shelves)
            new_shelves.append([current_y, h, w])
            new_placements.append({
                "id": index + 1,
                "position": (0, current_y),
                "dimension": (w, h)
            })
            placer(index + 1, new_placements, new_shelves)

    placer(0, [], [])
    return meilleur["placements"]

def dessiner_interface(W, H, placements, scale_x=40, scale_y=15, padding=10):
    fenetre = tk.Tk()
    fenetre.title("Placement NFDH - Grille 2D")

    canvas_width = W * scale_x + padding * 2
    canvas_height = H * scale_y + padding * 2

    canvas = tk.Canvas(fenetre, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(pady=10)

    # Grand rectangle avec bordure
    canvas.create_rectangle(
        padding, padding, 
        W * scale_x + padding, H * scale_y + padding,
        outline="black", width=2
    )

    for rect in placements:
        x, y = rect["position"]
        w, h = rect["dimension"]
        rect_id = rect["id"]

        x1 = padding + x * scale_x
        y1 = padding + y * scale_y
        x2 = padding + (x + w) * scale_x
        y2 = padding + (y + h) * scale_y

        canvas.create_rectangle(x1, y1, x2, y2, fill="skyblue", outline="black")
        canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(rect_id), font=("Arial", 14, "bold"))

    # Affichage du résumé textuel
    text_resultat = tk.Text(fenetre, height=10, width=60, font=("Consolas", 11))
    text_resultat.pack(pady=10)
    text_resultat.insert(tk.END, "Placement des rectangles (méthode NFDH) :\n")
    for rect in placements:
        text_resultat.insert(
            tk.END,
            f"Rectangle {rect['id']} - Taille : {rect['dimension']}, Position : {rect['position']}\n"
        )
    text_resultat.config(state="disabled")

    fenetre.mainloop()

# Exemple d’utilisation
if __name__ == "__main__":
    W, H = 10, 30
    rectangles = [(6,9),(8,9),(2,8),(5,8),(3,5),(5,5),(4,3),(4,3),(3,1)]

    placements = brute_force_packing_2d(rectangles, W, H)
    dessiner_interface(W, H, placements)

    placements = FFDH(rectangles, W, H)
    dessiner_interface(W, H, placements)

    placements = BFDH(rectangles, W, H)
    dessiner_interface(W, H, placements)

    placements = NFDH(rectangles, W, H)
    dessiner_interface(W, H, placements)

    # Zah maka an lisany dem
