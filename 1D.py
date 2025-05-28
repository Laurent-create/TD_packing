import tkinter as tk
from tkinter import ttk, messagebox

def first_fit(objects, bin_capacity):
    bins = []
    placements = []

    for i, obj in enumerate(objects):
        placed = False
        for j in range(len(bins)):
            if sum(item[1] for item in bins[j]) + obj <= bin_capacity:
                bins[j].append((i + 1, obj))
                placements.append((i + 1, obj, j + 1))
                placed = True
                break
        if not placed:
            bins.append([(i + 1, obj)])
            placements.append((i + 1, obj, len(bins)))

    return bins, placements

def best_fit(objects, bin_capacity):
    bins = []
    placements = []

    for i, obj in enumerate(objects):
        best_index = -1
        min_space_left = bin_capacity + 1

        for j, bin in enumerate(bins):
            space_left = bin_capacity - sum(item[1] for item in bin)
            if obj <= space_left and space_left < min_space_left:
                best_index = j
                min_space_left = space_left

        if best_index != -1:
            bins[best_index].append((i + 1, obj))
            placements.append((i + 1, obj, best_index + 1))
        else:
            bins.append([(i + 1, obj)])
            placements.append((i + 1, obj, len(bins)))

    return bins, placements

def worst_fit(objects, bin_capacity):
    bins = []
    placements = []

    for i, obj in enumerate(objects):
        worst_index = -1
        max_space_left = -1

        for j, bin in enumerate(bins):
            space_left = bin_capacity - sum(item[1] for item in bin)
            if obj <= space_left and space_left > max_space_left:
                worst_index = j
                max_space_left = space_left

        if worst_index != -1:
            bins[worst_index].append((i + 1, obj))
            placements.append((i + 1, obj, worst_index + 1))
        else:
            bins.append([(i + 1, obj)])
            placements.append((i + 1, obj, len(bins)))

    return bins, placements

class PackingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("1D Bin Packing")

        self.objects = []
        self.bin_capacity = tk.IntVar(value=10)

        self.setup_ui()

    def setup_ui(self):
        # Paramètres
        frame_top = tk.Frame(self.root)
        frame_top.pack(pady=10)

        tk.Label(frame_top, text="Capacité d’un bac :").grid(row=0, column=0)
        tk.Entry(frame_top, textvariable=self.bin_capacity, width=5).grid(row=0, column=1)

        tk.Label(frame_top, text="Taille d’un objet :").grid(row=0, column=2)
        self.obj_entry = tk.Entry(frame_top, width=5)
        self.obj_entry.grid(row=0, column=3)

        tk.Button(frame_top, text="Ajouter Objet", command=self.ajouter_objet).grid(row=0, column=4, padx=10)

        self.objets_label = tk.Label(self.root, text="Objets : []")
        self.objets_label.pack()

        # Boutons méthode
        frame_buttons = tk.Frame(self.root)
        frame_buttons.pack(pady=10)

        tk.Button(frame_buttons, text="First Fit", command=lambda: self.appliquer("FF")).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Best Fit", command=lambda: self.appliquer("BF")).pack(side="left", padx=5)
        tk.Button(frame_buttons, text="Worst Fit", command=lambda: self.appliquer("WF")).pack(side="left", padx=5)

        # Résultats
        self.resultats = tk.Text(self.root, width=70, height=15, state="disabled")
        self.resultats.pack(pady=10)
        
        # canva 
        self.canvas = tk.Canvas(self.root, width=500, height=250, bg="white")
        self.canvas.pack(pady=10)


    def ajouter_objet(self):
        try:
            taille = int(self.obj_entry.get())
            if taille <= 0:
                raise ValueError
            self.objects.append(taille)
            self.obj_entry.delete(0, tk.END)
            self.update_affichage_objets()
        except ValueError:
            messagebox.showerror("Erreur", "Veuillez entrer un entier positif.")

    def update_affichage_objets(self):
        texte = "Objets : [" + ", ".join(map(str, self.objects)) + "]"
        self.objets_label.config(text=texte)

    def appliquer(self, methode):
        if not self.objects:
            messagebox.showwarning("Attention", "Aucun objet à placer.")
            return

        capacity = self.bin_capacity.get()
        if methode == "FF":
            bins, placements = first_fit(self.objects, capacity)
        elif methode == "BF":
            bins, placements = best_fit(self.objects, capacity)
        else:
            bins, placements = worst_fit(self.objects, capacity)

        self.afficher_resultats(bins, placements, capacity)

    def afficher_representations_1D(self, bins, capacity):
        self.canvas.delete("all")
        width_unit = 400 / capacity  # pixels par unité de taille
        height = 30
        padding = 10

        colors = ["#FF9999", "#99CCFF", "#99FF99", "#FFFF99", "#FFCC99", "#CCCCFF", "#FF66CC"]

        for i, bin in enumerate(bins):
            y_top = 20
            y_top += i * (height + padding)
            x = 10
            for j, (idx, taille) in enumerate(bin):
                w = taille * width_unit
                color = colors[j % len(colors)]
                self.canvas.create_rectangle(x, y_top, x + w, y_top + height, fill=color, outline="black")
                self.canvas.create_text(x + w/2, y_top + height/2, text=f"O{idx}(T:{taille})", font=("Arial", 8))
                x += w
            # Dessin de la bordure totale du bac
            self.canvas.create_rectangle(10, y_top, 410, y_top + height, outline="black")
            self.canvas.create_text(415, y_top + height/2, text=f"Bac {i+1}", anchor="w", font=("Arial", 9, "bold"))

    def afficher_resultats(self, bins, placements, capacity):
        self.resultats.config(state="normal")
        self.resultats.delete(1.0, tk.END)

        self.resultats.insert(tk.END, f"Capacité d’un bac : {capacity}\n")
        self.resultats.insert(tk.END, f"Nombre total de bacs utilisés : {len(bins)}\n\n")

        for i, contenu in enumerate(bins, 1):
            total = sum(t for (_, t) in contenu)
            ligne = f"Bac {i} (rempli = {total}) : "
            ligne += ", ".join([f"Objet {idx} (taille = {taille})" for (idx, taille) in contenu])
            self.resultats.insert(tk.END, ligne + "\n")

        self.afficher_representations_1D(bins, capacity)
        self.resultats.config(state="disabled")


# Lancement de l’application
if __name__ == "__main__":
    root = tk.Tk()
    app = PackingApp(root)
    root.mainloop()
