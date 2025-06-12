import itertools
import math
import time
from copy import deepcopy
import tkinter as tk

def brute_force_packing(shapes, W, H, timeout=10):
    """Algorithme brute force avec backtracking récursif"""
    start_time = time.time()
    best_solution = {'height': float('inf'), 'placements': []}
    n = len(shapes)
    
    # Générer toutes les permutations des formes
    for perm in itertools.permutations(range(n)):
        # Toutes les combinaisons de rotations possibles
        rotations = []
        for i in perm:
            if shapes[i]["type"] == "cercle":
                rotations.append([0])  # Pas de rotation pour les cercles
            else:
                rotations.append([0, math.pi/2, math.pi, 3*math.pi/2])
        
        for rot_combo in itertools.product(*rotations):
            if time.time() - start_time > timeout:
                return best_solution['placements']
                
            placements = []
            current_height = 0
            valid = True
            
            # Essayer de placer chaque forme dans l'ordre
            for idx, (shape_idx, rotation) in enumerate(zip(perm, rot_combo)):
                shape = deepcopy(shapes[shape_idx])
                shape['id'] = idx + 1
                shape['rotation'] = rotation
                
                # Calculer les dimensions après rotation
                if shape["type"] in ["rectangle", "triangle"]:
                    w, h = shape["dimension"]
                    if rotation in [math.pi/2, 3*math.pi/2]:
                        w, h = h, w
                elif shape["type"] == "cercle":
                    w = h = shape["dimension"][0]
                
                # Vérifier si la forme est trop grande
                if w > W or h > H:
                    valid = False
                    break
                
                # Trouver une position valide sans collision
                position_found = False
                for y in range(0, H - int(h) + 1):
                    for x in range(0, W - int(w) + 1):
                        shape['position'] = (x, y)
                        shape['width'] = w
                        shape['height'] = h
                        
                        # Vérifier les collisions
                        collision = False
                        for placed_shape in placements:
                            if shapes_overlap(shape, placed_shape):
                                collision = True
                                break
                        
                        if not collision:
                            placements.append(deepcopy(shape))
                            position_found = True
                            current_height = max(current_height, y + h)
                            break
                    if position_found:
                        break
                
                if not position_found:
                    valid = False
                    break
            
            # Si toutes les formes placées et solution meilleure
            if valid and len(placements) == n:
                if current_height < best_solution['height']:
                    best_solution = {
                        'height': current_height,
                        'placements': deepcopy(placements)
                    }
    
    return best_solution['placements']

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
    """Vérifie si deux formes se superposent (version adaptée pour brute force)"""
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
        r1 = shape1["width"] / 2
        r2 = shape2["width"] / 2
        center_x1 = x1 + r1
        center_y1 = y1 + r1
        center_x2 = x2 + r2
        center_y2 = y2 + r2
        dx = center_x1 - center_x2
        dy = center_y1 - center_y2
        distance = math.sqrt(dx*dx + dy*dy)
        return distance < (r1 + r2)
    
    # Rectangle vs Cercle
    elif shape1["type"] == "rectangle" and shape2["type"] == "cercle":
        rect = {"x": x1, "y": y1, "w": shape1["width"], "h": shape1["height"]}
        circle = {"x": x2 + shape2["width"]/2, 
                 "y": y2 + shape2["width"]/2, 
                 "r": shape2["width"]/2}
        return rect_circle_collision(rect, circle)
    
    # Cercle vs Rectangle (inverse du cas précédent)
    elif shape1["type"] == "cercle" and shape2["type"] == "rectangle":
        circle = {"x": x1 + shape1["width"]/2, 
                 "y": y1 + shape1["width"]/2, 
                 "r": shape1["width"]/2}
        rect = {"x": x2, "y": y2, "w": shape2["width"], "h": shape2["height"]}
        return rect_circle_collision(rect, circle)
    
    # Triangle vs Autre (approximation par rectangle englobant)
    else:
        w1, h1 = shape1["width"], shape1["height"]
        w2, h2 = shape2["width"], shape2["height"]
        return not (x1 + w1 <= x2 or x2 + w2 <= x1 or 
                   y1 + h1 <= y2 or y2 + h2 <= y1)

def dessiner_interface(W, H, placements, scale=40, padding=10):
    fenetre = tk.Tk()
    fenetre.title("Placement Brute Force")
    
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
        shape_id = shape["id"]
        rotation = shape.get("rotation", 0)
        w = shape["width"]
        h = shape["height"]

        x1 = padding + x * scale
        y1 = padding + y * scale
        x2 = x1 + w * scale
        y2 = y1 + h * scale

        if shape_type == "rectangle":
            canvas.create_rectangle(x1, y1, x2, y2, fill="skyblue", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, 
                              text=str(shape_id), font=("Arial", 12, "bold"))

        elif shape_type == "triangle":
            if rotation == 0:
                points = [x1, y2, (x1 + x2) // 2, y1, x2, y2]
            elif rotation == math.pi/2:
                points = [x1, y1, x2, (y1 + y2) // 2, x1, y2]
            elif rotation == math.pi:
                points = [(x1 + x2) // 2, y2, x1, y1, x2, y1]
            elif rotation == 3*math.pi/2:
                points = [x2, y1, x1, (y1 + y2) // 2, x2, y2]
            canvas.create_polygon(points, fill="lightgreen", outline="black")
            canvas.create_text((x1 + x2) // 2, (y1 + y2) // 2, 
                              text=str(shape_id), font=("Arial", 12, "bold"))

        elif shape_type == "cercle":
            radius = (w * scale) / 2
            center_x = x1 + radius
            center_y = y1 + radius
            canvas.create_oval(center_x - radius, center_y - radius,
                               center_x + radius, center_y + radius,
                               fill="salmon", outline="black")
            canvas.create_text(center_x, center_y, 
                              text=str(shape_id), font=("Arial", 12, "bold"))

    # Affichage textuel
    text_resultat = tk.Text(fenetre, height=15, width=80, font=("Consolas", 10))
    text_resultat.pack(pady=10)

    text_resultat.insert(tk.END, "PLACEMENT BRUTE FORCE\n")
    text_resultat.insert(tk.END, f"Bac de dimension: {W} x {H}\n")
    text_resultat.insert(tk.END, f"Formes placées: {len(placements)}/{len(placements)}\n")
    text_resultat.insert(tk.END, "-" * 80 + "\n")
    text_resultat.insert(tk.END, "ID | Type     | Dimensions | Position | Rotation\n")
    text_resultat.insert(tk.END, "-" * 80 + "\n")

    for shape in placements:
        rot_deg = math.degrees(shape.get("rotation", 0))
        dim_str = f"({shape['width']:.1f}, {shape['height']:.1f})"
        text_resultat.insert(
            tk.END,
            f"{shape['id']:2} | {shape['type']:8} | {dim_str:10} | "
            f"{str(shape['position']):9} | {rot_deg:7.1f}°\n"
        )

    text_resultat.config(state="disabled")
    fenetre.mainloop()

# Exemple d'utilisation
if __name__ == "__main__":
    W, H = 10, 10  # Taille du bac

    formes = [
        {"type": "rectangle", "dimension": (7, 3)},  # Forme 1
        {"type": "triangle", "dimension": (4, 6)},    # Forme 2
        {"type": "rectangle", "dimension": (5, 2)},   # Forme 3
        {"type": "cercle", "dimension": (3,)}, 
        {"type": "cercle", "dimension": (3,)},       # Forme 4
        {"type": "rectangle", "dimension": (2, 4)}    # Forme 5
    ]

    print("Calcul des placements par brute force (peut prendre du temps)...")
    placements_brute = brute_force_packing(formes, W, H, timeout=30)
    
    if placements_brute:
        print(f"Solution trouvée avec {len(placements_brute)} formes placées")
        max_height = max([p["position"][1] + p["height"] for p in placements_brute])
        print(f"Hauteur utilisée: {max_height:.1f}/{H}")
    else:
        print("Aucune solution complète trouvée dans le temps imparti")
    
    if placements_brute:
        dessiner_interface(W, H, placements_brute)