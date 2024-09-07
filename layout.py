import tkinter as tk
from tkinter import messagebox

class QuizGameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Quiz Game")

        # Pergunta
        self.question_label = tk.Label(root, text="Pergunta aparecerá aqui", font=('Arial', 16), wraplength=400)
        self.question_label.pack(pady=20)

        # Campo de resposta
        self.answer_entry = tk.Entry(root, font=('Arial', 14), width=40)
        self.answer_entry.pack(pady=10)

        # Botão de envio
        self.submit_button = tk.Button(root, text="Enviar Resposta", command=self.submit_answer, font=('Arial', 14))
        self.submit_button.pack(pady=20)

        # Pontuações
        self.score_frame = tk.Frame(root)
        self.score_frame.pack(pady=10)

        self.score_label = tk.Label(self.score_frame, text="Pontuações", font=('Arial', 14))
        self.score_label.grid(row=0, column=0)

        self.scores = {
            "Player 1": 0,
            "Player 2": 0,
            "Player 3": 0,
            "Player 4": 0,
        }

        self.score_labels = []
        for i, (player, score) in enumerate(self.scores.items()):
            lbl = tk.Label(self.score_frame, text=f"{player}: {score}", font=('Arial', 12))
            lbl.grid(row=i+1, column=0, sticky='w')
            self.score_labels.append(lbl)

    def submit_answer(self):
        answer = self.answer_entry.get()
        if answer.strip() == "":
            messagebox.showwarning("Entrada Inválida", "Por favor, digite uma resposta.")
        else:
            # Aqui você implementaria a lógica para enviar a resposta ao servidor
            print(f"Resposta enviada: {answer}")
            self.answer_entry.delete(0, tk.END)

    def update_question(self, question):
        self.question_label.config(text=question)

    def update_scores(self, scores):
        for i, (player, score) in enumerate(scores.items()):
            self.score_labels[i].config(text=f"{player}: {score}")

if __name__ == "__main__":
    root = tk.Tk()
    app = QuizGameApp(root)
    root.geometry("500x400")
    root.mainloop()
