"""Interfaccia desktop: python app.py."""
import json
import os
import queue
import threading
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from analisi import analizza


def main():
    root = tk.Tk()
    root.title('Coerenza immagini · IA → JSON')
    root.geometry('800x700')
    frame = ttk.Frame(root, padding=20)
    frame.pack(fill='both', expand=True)
    path, key, model = tk.StringVar(), tk.StringVar(value=os.getenv('OPENROUTER_API_KEY', '')), tk.StringVar(value=os.getenv('OPENROUTER_MODEL', ''))
    ttk.Label(frame, text='Coerenza immagini', font=('', 20, 'bold')).pack(anchor='w')
    ttk.Label(frame, text='Carica una foto e ricevi una valutazione in JSON.').pack(anchor='w', pady=8)
    def scegli():
        selected = filedialog.askopenfilename(filetypes=[('Immagini', '*.jpg *.jpeg *.png *.webp')])
        if selected:
            path.set(selected)
    ttk.Button(frame, text='Scegli immagine', command=scegli).pack(anchor='w')
    ttk.Label(frame, textvariable=path, wraplength=740).pack(anchor='w', pady=5)
    for label, variable, mask in [('Chiave OpenRouter (solo in memoria)', key, '*'), ('Modello (vuoto = gratuito compatibile)', model, '')]:
        ttk.Label(frame, text=label).pack(anchor='w', pady=(8, 0))
        ttk.Entry(frame, textvariable=variable, show=mask).pack(fill='x')
    ttk.Label(frame, text='Descrizione attesa (facoltativa, massimo 4000 caratteri)').pack(anchor='w', pady=(12, 0))
    description = tk.Text(frame, height=3)
    description.pack(fill='x')
    ttk.Label(frame, text='Analizza invia la foto a OpenRouter e al provider del modello.\nLa valutazione può sbagliare e non certifica se la foto è vera o generata.', wraplength=740).pack(anchor='w', pady=10)
    output = tk.Text(frame, height=14, wrap='word')
    events = queue.Queue()
    result = None
    def start():
        nonlocal result
        if not path.get():
            messagebox.showerror('Immagine mancante', 'Scegli prima una foto.')
            return
        values = (path.get(), description.get('1.0', 'end').strip(), key.get().strip(), model.get().strip())
        result = None
        save.configure(state='disabled')
        run.configure(state='disabled')
        output.delete('1.0', 'end')
        output.insert('end', 'Analisi in corso…')
        def worker():
            try:
                events.put((True, analizza(*values)))
            except Exception as exc:
                events.put((False, str(exc)))
        threading.Thread(target=worker, daemon=True).start()
    def poll():
        nonlocal result
        try:
            ok, value = events.get_nowait()
            output.delete('1.0', 'end')
            output.insert('end', json.dumps(value, ensure_ascii=False, indent=2) if ok else 'Errore: ' + value)
            result = value if ok else None
            save.configure(state='normal' if ok else 'disabled')
            run.configure(state='normal')
        except queue.Empty:
            pass
        root.after(100, poll)
    def export():
        target = filedialog.asksaveasfilename(defaultextension='.json', initialfile='analisi.json', filetypes=[('JSON', '*.json')])
        if target and result is not None:
            try:
                with open(target, 'w', encoding='utf-8') as file:
                    json.dump(result, file, ensure_ascii=False, indent=2)
            except OSError as exc:
                messagebox.showerror('Salvataggio fallito', str(exc))
    run = ttk.Button(frame, text='Analizza immagine', command=start)
    run.pack(anchor='w', pady=5)
    output.pack(fill='both', expand=True)
    save = ttk.Button(frame, text='Salva JSON', command=export, state='disabled')
    save.pack(anchor='w', pady=10)
    poll()
    root.mainloop()


if __name__ == '__main__':
    main()
