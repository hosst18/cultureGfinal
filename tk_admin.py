from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from bot.core.questions_store import (
    add_question,
    get_categories,
    load_questions,
)


class QuestionAdminApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CultureG - Admin Questions (Tkinter)")
        self.geometry("800x550")

        cats = get_categories()
        if not cats:
            # Catégories par défaut si aucun fichier trouvé
            cats = [
                "sport",
                "esport",
                "culture",
                "histoire",
                "geographie",
                "science",
                "technologie",
                "musique",
                "cinema",
                "litterature",
                "jeux_video",
            ]
        self.categories = cats

        self.create_widgets()
        self.refresh_question_list()

    def create_widgets(self):
        # --- Frame haut : sélection catégorie + liste ---
        top_frame = ttk.Frame(self)
        top_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        ttk.Label(top_frame, text="Catégorie :").grid(row=0, column=0, sticky="w")
        self.category_var = tk.StringVar(value=self.categories[0])
        self.category_combo = ttk.Combobox(
            top_frame,
            textvariable=self.category_var,
            values=self.categories,
            state="readonly",
        )
        self.category_combo.grid(row=0, column=1, sticky="w", padx=5)
        self.category_combo.bind("<<ComboboxSelected>>", lambda e: self.refresh_question_list())

        self.listbox = tk.Listbox(top_frame, height=12)
        self.listbox.grid(row=1, column=0, columnspan=4, sticky="nsew", pady=5)

        top_frame.rowconfigure(1, weight=1)
        top_frame.columnconfigure(3, weight=1)

        # --- Frame bas : ajout de question ---
        bottom = ttk.LabelFrame(self, text="Ajouter une question")
        bottom.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(bottom, text="Question :").grid(row=0, column=0, sticky="w")
        self.q_entry = ttk.Entry(bottom, width=90)
        self.q_entry.grid(row=0, column=1, columnspan=3, sticky="w", pady=2)

        self.choice_vars = []
        for i, label in enumerate(["A", "B", "C", "D"]):
            ttk.Label(bottom, text=f"Réponse {label} :").grid(row=i + 1, column=0, sticky="w")
            var = tk.StringVar()
            entry = ttk.Entry(bottom, textvariable=var, width=50)
            entry.grid(row=i + 1, column=1, sticky="w", pady=2)
            self.choice_vars.append(var)

        ttk.Label(bottom, text="Bonne réponse :").grid(row=1, column=2, sticky="e")
        self.good_var = tk.StringVar(value="A")
        good_combo = ttk.Combobox(
            bottom,
            textvariable=self.good_var,
            values=["A", "B", "C", "D"],
            width=5,
            state="readonly",
        )
        good_combo.grid(row=1, column=3, sticky="w")

        ttk.Label(bottom, text="Nouvelle catégorie (optionnel) :").grid(row=2, column=2, sticky="e")
        self.new_cat_var = tk.StringVar()
        new_cat_entry = ttk.Entry(bottom, textvariable=self.new_cat_var, width=20)
        new_cat_entry.grid(row=2, column=3, sticky="w")

        ttk.Label(bottom, text="Difficulté :").grid(row=3, column=2, sticky="e")
        self.diff_var = tk.StringVar(value="facile")
        diff_combo = ttk.Combobox(
            bottom,
            textvariable=self.diff_var,
            values=["facile", "moyen", "difficile"],
            width=10,
            state="readonly",
        )
        diff_combo.grid(row=3, column=3, sticky="w")

        add_btn = ttk.Button(bottom, text="Ajouter la question", command=self.on_add)
        add_btn.grid(row=4, column=3, sticky="e", pady=5)

    def refresh_question_list(self):
        current_cat = self.category_var.get()
        questions = load_questions(current_cat)
        self.listbox.delete(0, tk.END)
        for q in questions:
            text = q.get("q", "")[:100]
            if len(q.get("q", "")) > 100:
                text += "..."
            self.listbox.insert(tk.END, text)

    def on_add(self):
        q_text = self.q_entry.get().strip()
        choices = [v.get().strip() for v in self.choice_vars]
        if not q_text or any(c == "" for c in choices):
            messagebox.showerror("Erreur", "Question et toutes les réponses doivent être remplies.")
            return

        good_map = {"A": 0, "B": 1, "C": 2, "D": 3}
        answer_index = good_map.get(self.good_var.get(), 0)

        category = self.new_cat_var.get().strip() or self.category_var.get()
        difficulty = self.diff_var.get()

        add_question(category, q_text, choices, answer_index, difficulty=difficulty)

        messagebox.showinfo("OK", f"Question ajoutée dans la catégorie '{category}'.")

        if category not in self.categories:
            self.categories.append(category)
            self.category_combo["values"] = self.categories
            self.category_var.set(category)

        self.q_entry.delete(0, tk.END)
        for v in self.choice_vars:
            v.set("")
        self.new_cat_var.set("")
        self.refresh_question_list()


if __name__ == "__main__":
    app = QuestionAdminApp()
    app.mainloop()
