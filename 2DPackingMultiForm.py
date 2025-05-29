import tkinter as tk
import math
from copy import deepcopy

def test_rotations(shape, W, H):
    """Teste les différentes rotations et retourne la meilleure configuration"""
    if shape["type"] == "cercle":
        return shape  # Les cercles ne changent pas avec la rotation

    best_rotation = 0
    best_w, best_h = shape["dimension"]
    best_area = best_w * best_h
    best_fit = False

    for rotation in [0, math.pi/2, math.pi, 3*math.pi/2]:
        temp_w, temp_h = shape["dimension"]
        if rotation in [math.pi/2, 3*math.pi/2]:
            temp_w, temp_h = temp_h, temp_w

        if temp_w <= W and temp_h <= H:
            temp_area = temp_w * temp_h
            if (not best_fit) or (temp_h < best_h) or (temp_h == best_h and temp_area < best_area):
                best_fit = True
                best_rotation = rotation
                best_w, best_h = temp_w, temp_h
                best_area = temp_area

    optimized_shape = deepcopy(shape)
    optimized_shape["rotation"] = best_rotation
    return optimized_shape

def NFDH(shapes, W, H):
    optimized_shapes = [test_rotations(s, W, H) for s in shapes]

    def shape_height(s):
        if s["type"] == "cercle":
            return s["dimension"][0]
        w, h = s["dimension"]
        if s.get("rotation", 0) in [math.pi/2, 3*math.pi/2]:
            return w
        return h

    optimized_shapes.sort(key=shape_height, reverse=True)

    placements = []
    current_shelf_y = 0
    current_shelf_height = 0
    current_x = 0

    for i, shape in enumerate(optimized_shapes):
        if shape["type"] in ["rectangle", "triangle"]:
            w, h = shape["dimension"]
            if shape.get("rotation", 0) in [math.pi/2, 3*math.pi/2]:
                w, h = h, w
        elif shape["type"] == "cercle":
            diameter = shape["dimension"][0]
            w = h = diameter

        # Vérification stricte des dimensions
        if w > W or h > H:
            continue

        if current_x + w > W:
            current_shelf_y += current_shelf_height
            current_x = 0
            current_shelf_height = 0

        # Vérification de la hauteur disponible
        if current_shelf_y + h > H:
            continue

        placements.append({
            "id": i + 1,
            "type": shape["type"],
            "position": (current_x, current_shelf_y),
            "dimension": shape["dimension"],
            "rotation": shape.get("rotation", 0)
        })

        current_x += w
        current_shelf_height = max(current_shelf_height, h)

    return placements

def FFDH(shapes, W, H):
    """First-Fit Decreasing Height algorithm with rotation support"""
    
    # 1. Test all possible rotations for each shape
    optimized_shapes = [test_rotations(s, W, H) for s in shapes]
    
    # 2. Sort shapes by decreasing height (with rotation applied)
    def get_height(s):
        if s["type"] == "cercle":
            return s["dimension"][0]
        w, h = s["dimension"]
        if s.get("rotation", 0) in [math.pi/2, 3*math.pi/2]:
            return w
        return h
    
    optimized_shapes.sort(key=get_height, reverse=True)
    
    # 3. Initialize shelves
    placements = []
    shelves = []  # List of (y_position, remaining_width, shelf_height)
    
    for i, shape in enumerate(optimized_shapes):
        # Get dimensions after rotation
        if shape["type"] in ["rectangle", "triangle"]:
            w, h = shape["dimension"]
            if shape.get("rotation", 0) in [math.pi/2, 3*math.pi/2]:
                w, h = h, w
        elif shape["type"] == "cercle":
            w = h = shape["dimension"][0]
        
        # Skip if too large for the bin
        if w > W or h > H:
            continue
        
        placed = False
        
        # 4. Try to place in existing shelves (First-Fit)
        for shelf in shelves:
            y, remaining_width, shelf_height = shelf
            
            # Check if fits in current shelf
            if remaining_width >= w and shelf_height >= h:
                # Place shape
                placements.append({
                    "id": i + 1,
                    "type": shape["type"],
                    "position": (W - remaining_width, y),
                    "dimension": shape["dimension"],
                    "rotation": shape.get("rotation", 0)
                })
                
                # Update shelf
                shelf[1] -= w  # Reduce remaining width
                placed = True
                break
        
        # 5. If not placed, create new shelf if possible
        if not placed:
            # Find current max y position
            max_y = shelves[-1][0] + shelves[-1][2] if shelves else 0
            
            if max_y + h <= H:
                # Create new shelf
                shelves.append([max_y, W - w, h])
                
                placements.append({
                    "id": i + 1,
                    "type": shape["type"],
                    "position": (0, max_y),
                    "dimension": shape["dimension"],
                    "rotation": shape.get("rotation", 0)
                })
    
    return placements

def rect_circle_collision(rect, circle):
    """Vérifie la collision entre un rectangle et un cercle"""
    # Trouver le point le plus proche du cercle dans le rectangle
    closest_x = max(rect["x"], min(circle["x"], rect["x"] + rect["w"]))
    closest_y = max(rect["y"], min(circle["y"], rect["y"] + rect["h"]))
    
    # Calculer la distance
    dx = circle["x"] - closest_x
    dy = circle["y"] - closest_y
    distance = math.sqrt(dx*dx + dy*dy)
    
    return distance < circle["r"]

def shapes_overlap(shape1, shape2):
    """Vérifie si deux formes se superposent"""
    x1, y1 = shape1["position"]
    x2, y2 = shape2["position"]
    
    # Rectangle vs Rectangle
    if shape1["type"] == "rectangle" and shape2["type"] == "rectangle":
        w1, h1 = shape1["width"], shape1["height"]
        w2, h2 = shape2["width"], shape2["height"]
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or 
                   y1 + h1 <= y2 or y2 + h2 <= y1)
    
    # Cercle vs Cercle
    elif shape1["type"] == "cercle" and shape2["type"] == "cercle":
        r1 = shape1["dimension"][0] / 2
        r2 = shape2["dimension"][0] / 2
        dx = x1 - x2
        dy = y1 - y2
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (r1 + r2)
    
    # Rectangle vs Cercle
    elif shape1["type"] == "rectangle" and shape2["type"] == "cercle":
        rect = {"x": x1, "y": y1, "w": shape1["width"], "h": shape1["height"]}
        circle = {"x": x2, "y": y2, "r": shape2["dimension"][0]/2}
        return rect_circle_collision(rect, circle)
    
    # Cercle vs Rectangle (inverse du cas précédent)
    elif shape1["type"] == "cercle" and shape2["type"] == "rectangle":
        circle = {"x": x1, "y": y1, "r": shape1["dimension"][0]/2}
        rect = {"x": x2, "y": y2, "w": shape2["width"], "h": shape2["height"]}
        return rect_circle_collision(rect, circle)
    
    # Triangle vs Autre (approximation par rectangle englobant)
    elif shape1["type"] == "triangle" or shape2["type"] == "triangle":
        # Pour simplifier, on utilise le rectangle englobant
        w1, h1 = shape1["width"], shape1["height"]
        w2, h2 = shape2["width"], shape2["height"]
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or 
                   y1 + h1 <= y2 or y2 + h2 <= y1)
    
    # Cas par défaut (pas de collision)
    return False

def merge_overlapping_spaces(spaces):
    """Fusionne les espaces vides qui se chevauchent"""
    merged = True
    while merged:
        merged = False
        new_spaces = []
        spaces.sort(key=lambda s: (s["x"], s["y"]))
        
        i = 0
        while i < len(spaces):
            current = spaces[i]
            j = i + 1
            while j < len(spaces):
                other = spaces[j]
                # Vérifier si les espaces se chevauchent
                if (current["x"] < other["x"] + other["w"] and
                    current["x"] + current["w"] > other["x"] and
                    current["y"] < other["y"] + other["h"] and
                    current["y"] + current["h"] > other["y"]):
                    
                    # Fusionner les deux espaces
                    x = min(current["x"], other["x"])
                    y = min(current["y"], other["y"])
                    w = max(current["x"] + current["w"], other["x"] + other["w"]) - x
                    h = max(current["y"] + current["h"], other["y"] + other["h"]) - y
                    
                    current = {"x": x, "y": y, "w": w, "h": h}
                    del spaces[j]
                    merged = True
                else:
                    j += 1
            new_spaces.append(current)
            i += 1
        
        spaces = new_spaces
    
    return spaces

def BestFit(shapes, W, H):
    """Algorithme Best-Fit pour le bin packing 2D avec support de rotation et vérification des collisions"""
    # 1. Tester toutes les rotations possibles et trier par aire décroissante
    optimized_shapes = []
    for s in shapes:
        rotated = test_rotations(s, W, H)
        if rotated["dimension"]:  # Vérifier qu'une rotation valide existe
            optimized_shapes.append(rotated)
    
    # Calculer l'aire pour le tri
    for shape in optimized_shapes:
        if shape["type"] in ["rectangle", "triangle"]:
            w, h = shape["dimension"]
            shape["area"] = w * h
        elif shape["type"] == "cercle":
            r = shape["dimension"][0] / 2
            shape["area"] = math.pi * r * r
    
    optimized_shapes.sort(key=lambda s: s["area"], reverse=True)
    
    # 2. Initialiser les espaces vides
    empty_spaces = [{"x": 0, "y": 0, "w": W, "h": H}]
    placements = []
    
    for i, shape in enumerate(optimized_shapes):
        # Déterminer les dimensions après rotation
        if shape["type"] in ["rectangle", "triangle"]:
            w, h = shape["dimension"]
            if shape.get("rotation", 0) in [math.pi/2, 3*math.pi/2]:
                w, h = h, w
        elif shape["type"] == "cercle":
            w = h = shape["dimension"][0]
        
        # Passer si trop grand pour le conteneur
        if w > W or h > H:
            continue
        
        # 3. Trouver le meilleur emplacement
        best_fit = None
        best_space_idx = -1
        min_residual = float('inf')
        
        for idx, space in enumerate(empty_spaces):
            if space["w"] >= w and space["h"] >= h:
                residual = (space["w"] - w) * (space["h"] - h)
                
                # Seulement considérer si meilleur résidu
                if residual < min_residual:
                    # Créer un placement potentiel
                    potential_placement = {
                        "id": i + 1,
                        "type": shape["type"],
                        "position": (space["x"], space["y"]),
                        "dimension": shape["dimension"],
                        "rotation": shape.get("rotation", 0),
                        "width": w,
                        "height": h
                    }
                    
                    # Vérifier les collisions avec les placements existants
                    collision = False
                    for placed in placements:
                        if shapes_overlap(potential_placement, placed):
                            collision = True
                            break
                    
                    if not collision:
                        min_residual = residual
                        best_fit = {
                            "x": space["x"],
                            "y": space["y"],
                            "w": w,
                            "h": h
                        }
                        best_space_idx = idx
        
        # 4. Si un emplacement valide est trouvé, mettre à jour les espaces
        if best_fit:
            # Placer la forme
            placements.append({
                "id": i + 1,
                "type": shape["type"],
                "position": (best_fit["x"], best_fit["y"]),
                "dimension": shape["dimension"],
                "rotation": shape.get("rotation", 0),
                "width": w,
                "height": h
            })
            
            # Découper l'espace restant
            used_space = empty_spaces.pop(best_space_idx)
            new_spaces = []
            
            # Espace à droite
            if used_space["w"] > w:
                new_spaces.append({
                    "x": used_space["x"] + w,
                    "y": used_space["y"],
                    "w": used_space["w"] - w,
                    "h": h
                })
            
            # Espace au-dessus
            if used_space["h"] > h:
                new_spaces.append({
                    "x": used_space["x"],
                    "y": used_space["y"] + h,
                    "w": used_space["w"],
                    "h": used_space["h"] - h
                })
            
            # Espace coin supérieur droit
            if used_space["w"] > w and used_space["h"] > h:
                new_spaces.append({
                    "x": used_space["x"] + w,
                    "y": used_space["y"] + h,
                    "w": used_space["w"] - w,
                    "h": used_space["h"] - h
                })
            
            # Ajouter et fusionner les nouveaux espaces
            empty_spaces.extend(new_spaces)
            empty_spaces = merge_overlapping_spaces(empty_spaces)
    
    return placements


def dessiner_interface(W, H, placements, scale=40, padding=10):
    fenetre = tk.Tk()
    fenetre.title("Placement optimal avec rotation automatique")

    canvas_width = W * scale + padding * 2
    canvas_height = H * scale + padding * 2

    canvas = tk.Canvas(fenetre, width=canvas_width, height=canvas_height, bg="white")
    canvas.pack(pady=10)

    # Dessiner le bac
    canvas.create_rectangle(
        padding, padding,
        W * scale + padding, H * scale + padding,
        outline="black", width=3
    )

    for shape in placements:
        x, y = shape["position"]
        shape_type = shape["type"]
        rect_id = shape["id"]
        rotation = shape.get("rotation", 0)

        x1 = padding + x * scale
        y1 = padding + y * scale

        if shape_type == "rectangle":
            w, h = shape["dimension"]
            if rotation in [math.pi/2, 3*math.pi/2]:
                w, h = h, w
            x2 = x1 + w * scale
            y2 = y1 + h * scale
            canvas.create_rectangle(x1, y1, x2, y2, fill="skyblue", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(rect_id), font=("Arial", 12, "bold"))

        elif shape_type == "triangle":
            base, height = shape["dimension"]
            if rotation in [math.pi/2, 3*math.pi/2]:
                base, height = height, base
            x2 = x1 + base * scale
            y2 = y1 + height * scale

            if rotation == 0:
                points = [x1, y2, (x1 + x2) / 2, y1, x2, y2]
            elif rotation == math.pi/2:
                points = [x1, y1, x2, (y1 + y2) / 2, x1, y2]
            elif rotation == math.pi:
                points = [(x1 + x2) / 2, y2, x1, y1, x2, y1]
            elif rotation == 3*math.pi/2:
                points = [x2, y1, x1, (y1 + y2) / 2, x2, y2]

            canvas.create_polygon(points, fill="lightgreen", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, text=str(rect_id), font=("Arial", 12, "bold"))

        elif shape_type == "cercle":
            diameter = shape["dimension"][0]
            radius = diameter * scale / 2
            center_x = x1 + radius
            center_y = y1 + radius
            canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               fill="salmon", outline="black")
            canvas.create_text(center_x, center_y, text=str(rect_id), font=("Arial", 12, "bold"))

    # Affichage textuel
    text_resultat = tk.Text(fenetre, height=15, width=80, font=("Consolas", 10))
    text_resultat.pack(pady=10)

    text_resultat.insert(tk.END, "PLACEMENT OPTIMAL AVEC ROTATION AUTOMATIQUE\n")
    text_resultat.insert(tk.END, f"Bac de dimension: {W} x {H}\n")
    text_resultat.insert(tk.END, "-" * 80 + "\n")
    text_resultat.insert(tk.END, "ID | Type     | Dimensions   | Position     | Rotation\n")
    text_resultat.insert(tk.END, "-" * 80 + "\n")

    for shape in placements:
        rot_deg = math.degrees(shape.get("rotation", 0))
        text_resultat.insert(
            tk.END,
            f"{shape['id']:2} | {shape['type']:8} | {str(shape['dimension']):12} | "
            f"{str(shape['position']):12} | {rot_deg:7.1f}°\n"
        )

    text_resultat.config(state="disabled")
    fenetre.mainloop()

# Exemple d'utilisation avec vérification des bords
if __name__ == "__main__":
    W, H = 10, 9  # Taille du bac

    formes = [
    {"type": "rectangle", "dimension": (7, 3)},  # Forme 1
    {"type": "triangle", "dimension": (4, 6)},   # Forme 2
    {"type": "rectangle", "dimension": (5, 2)},  # Forme 3
    {"type": "cercle", "dimension": (3,)},       # Forme 4
    {"type": "rectangle", "dimension": (2, 4)}   # Forme 5
]

    placements_nfdh = NFDH(formes, W, H)
    placements_ffdh = FFDH(formes, W, H)
    placements_bf = BestFit(formes, W, H)
    
    print("NFDH:", len(placements_nfdh), "/5 - Hauteur utilisée:", max([p["position"][1] + (p["dimension"][1] if p["type"] != "cercle" else p["dimension"][0]) for p in placements_nfdh]))
    print("FFDH:", len(placements_ffdh), "/5 - Hauteur utilisée:", max([p["position"][1] + (p["dimension"][1] if p["type"] != "cercle" else p["dimension"][0]) for p in placements_ffdh]))
    print("Best-Fit:", len(placements_bf), "/5 - Hauteur utilisée:", max([p["position"][1] + (p["dimension"][1] if p["type"] != "cercle" else p["dimension"][0]) for p in placements_bf]))
    
    dessiner_interface(W, H, placements_nfdh)
    dessiner_interface(W, H, placements_ffdh) 
    dessiner_interface(W, H, placements_bf)