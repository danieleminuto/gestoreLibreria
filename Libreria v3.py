import tkinter as tk
from tkinter import messagebox, simpledialog, ttk, filedialog
import json
import os

import requests

# File JSON per salvare i dati
DATA_FILE = 'library_data.json'


def center_popup(popup):
    popup.update_idletasks()
    width = popup.winfo_width()
    height = popup.winfo_height()
    screen_width = popup.winfo_screenwidth()
    screen_height = popup.winfo_screenheight()
    x = (screen_width // 2) - (width // 2)
    y = (screen_height // 2) - (height // 2)
    popup.geometry(f"{width}x{height}+{x}+{y}")


# Funzione per caricare i dati dal file JSON
def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r',encoding='utf-8') as file:
            return json.load(file)
    return {"rooms": {}}


# Funzione per salvare i dati nel file JSON
def save_data(data):
    with open(DATA_FILE, 'w') as file:
        json.dump(data, file, indent=4)


# Funzione per aggiungere un libro allo scaffale
def add_book_to_shelf(shelf, new_book):
    if new_book['isbn']:
        existing_book = next((book for book in shelf if book['isbn'] == new_book['isbn']), None)
    else:
        existing_book = next(
            (book for book in shelf if book['titolo'] == new_book['titolo'] and book['autore'] == new_book['autore']),
            None)

    if existing_book:
        response = messagebox.askyesno("Libro già presente", "Il libro esiste già nello scaffale. Vuoi sovrascriverlo?")
        if response:
            shelf.remove(existing_book)
            shelf.append(new_book)
            messagebox.showinfo("Successo", "Il libro è stato sovrascritto correttamente.")
        else:
            messagebox.showinfo("Annullato", "Il nuovo libro non è stato aggiunto.")
    else:
        shelf.append(new_book)
        messagebox.showinfo("Successo", "Il libro è stato aggiunto correttamente.")


def show_scrollable_info(title, content):
    # Crea una nuova finestra Toplevel
    popup = tk.Toplevel()
    popup.title(title)

    # Imposta la dimensione della finestra
    popup.geometry("400x400")

    # Crea un canvas che conterrà il contenuto
    canvas = tk.Canvas(popup)
    canvas.pack(side="left", fill="both", expand=True)

    # Aggiungi una scrollbar verticale
    scrollbar = tk.Scrollbar(popup, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Crea un frame all'interno del canvas
    scrollable_frame = tk.Frame(canvas)

    # Associa il frame al canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Configura il canvas per funzionare con la scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Aggiungi il testo al frame scrollabile
    label = tk.Label(scrollable_frame, text=content, justify="left", wraplength=380, anchor="w")
    label.pack(fill="both", expand=True)

    # Funzione per aggiornare la regione di scorrimento del canvas
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Funzione per scrollare con il mouse solo nel popup
    def _on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # Associa lo scroll solo al canvas del popup
    canvas.bind("<Enter>", lambda event: canvas.bind("<MouseWheel>", _on_mouse_wheel))
    canvas.bind("<Leave>", lambda event: canvas.unbind("<MouseWheel>"))

    # Pulsante per chiudere il popup
    tk.Button(popup, text="Chiudi", command=popup.destroy).pack(pady=10)


def create_scrollable_frame(parent, bg="gray"):
    # Crea un canvas che conterrà il frame scrollabile
    canvas = tk.Canvas(parent, bg=bg)

    # Aggiungi una scrollbar verticale collegata al canvas
    scrollbar = tk.Scrollbar(parent, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    # Crea un frame all'interno del canvas che conterrà tutti i widget
    scrollable_frame = tk.Frame(canvas, bg=bg)

    # Associa il frame al canvas
    canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")

    # Configura il canvas per funzionare con la scrollbar
    canvas.configure(yscrollcommand=scrollbar.set)

    # Funzione per aggiornare la regione di scorrimento del canvas
    def on_frame_configure(event):
        canvas.configure(scrollregion=canvas.bbox("all"))

    scrollable_frame.bind("<Configure>", on_frame_configure)

    # Funzione per scrollare con il mouse solo nella finestra principale
    def _on_mouse_wheel(event):
        canvas.yview_scroll(-1 * int(event.delta / 120), "units")

    # Associa lo scroll solo al canvas principale
    canvas.bind("<Enter>", lambda event: canvas.bind("<MouseWheel>", _on_mouse_wheel))
    canvas.bind("<Leave>", lambda event: canvas.unbind("<MouseWheel>"))

    # Posiziona il canvas all'interno del layout principale
    canvas.pack(side="left", fill="both", expand=True)

    return scrollable_frame


# Funzione per recuperare i dati del libro tramite ISBN con inserimento manuale dei metadati mancanti
def get_book_data(isbn):
    url = f"https://www.googleapis.com/books/v1/volumes?q=isbn:{isbn}"
    response = requests.get(url)
    book_data = {}
    if response.status_code == 200 and response.json()['totalItems'] > 0:
        volume_info = response.json()['items'][0]['volumeInfo']
        book_data = {
            "isbn": isbn,
            "titolo": volume_info.get("title", None),
            "autore": ', '.join(volume_info.get("authors", [])),
            "casa_editrice": volume_info.get("publisher", "N/A",),
            "data_pubblicazione":volume_info.get('publishedDate', "N/A",)
        }
    else:
        data_popup = tk.Toplevel(window)
        data_popup.title("Inserisci i dati del libro")

        tk.Label(data_popup, text="Titolo:", font=("Arial", 10)).pack()
        title_entry = tk.Entry(data_popup, font=("Arial", 10), width=40)
        title_entry.insert(0, "N/A")
        title_entry.pack()

        tk.Label(data_popup, text="Autore:", font=("Arial", 10)).pack()
        author_entry = tk.Entry(data_popup, font=("Arial", 10), width=40)
        author_entry.insert(0, "N/A")
        author_entry.pack()

        tk.Label(data_popup, text="Casa Editrice:", font=("Arial", 10)).pack()
        publisher_entry = tk.Entry(data_popup, font=("Arial", 10), width=40)
        publisher_entry.insert(0, "N/A")
        publisher_entry.pack()

        tk.Label(data_popup, text="Data di Pubblicazione:", font=("Arial", 10)).pack()
        pub_date_entry = tk.Entry(data_popup, font=("Arial", 10), width=40)
        pub_date_entry.insert(0, "N/A")
        pub_date_entry.pack()

        tk.Label(data_popup, text="ISBN:", font=("Arial", 10)).pack()
        isbn_entry = tk.Entry(data_popup, font=("Arial", 10), width=40)
        isbn_entry.insert(0, isbn)
        isbn_entry.pack()

        def save_data_popup():
            book_data["titolo"] = title_entry.get()
            book_data["autore"] = author_entry.get()
            book_data["casa_editrice"] = publisher_entry.get()
            book_data["data_pubblicazione"] = pub_date_entry.get()
            book_data["isbn"] = isbn_entry.get()
            data_popup.destroy()

        tk.Button(data_popup, text="Salva", command=save_data_popup, font=("Arial", 10)).pack(pady=10)
        window.wait_window(data_popup)

    return book_data


# Funzione per aggiungere un libro manualmente
def add_book_manually(room_name, shelf_name, ripiano_name):
    # Finestra per inserimento manuale
    add_window = tk.Toplevel(window)
    center_popup(add_window)
    add_window.geometry('400x300')
    add_window.title("Aggiungi libro manualmente")

    tk.Label(add_window, text="Titolo:", font=("Arial", 10)).pack()
    title_entry = tk.Entry(add_window, font=("Arial", 10), width=40)

    title_entry.pack()

    tk.Label(add_window, text="Autore:", font=("Arial", 10)).pack()
    author_entry = tk.Entry(add_window, font=("Arial", 10), width=40)

    author_entry.pack()

    tk.Label(add_window, text="Casa Editrice:", font=("Arial", 10)).pack()
    publisher_entry = tk.Entry(add_window, font=("Arial", 10), width=40)
    publisher_entry.pack()

    tk.Label(add_window, text="Data di Pubblicazione:", font=("Arial", 10)).pack()
    pub_date_entry = tk.Entry(add_window, font=("Arial", 10), width=40)
    pub_date_entry.pack()


    tk.Label(add_window, text="ISBN:", font=("Arial", 10)).pack()
    isbn_entry = tk.Entry(add_window, font=("Arial", 10), width=40)
    isbn_entry.insert(0, "N/A")
    isbn_entry.pack()

    def save_book():
        book_data = {
            "titolo": title_entry.get(),
            "autore": author_entry.get(),
            "casa_editrice": publisher_entry.get(),
            "data_pubblicazione": pub_date_entry.get(),
            "isbn": isbn_entry.get()
        }
        data = load_data()
        ripiano = data["rooms"][room_name]["shelves"][shelf_name][ripiano_name]
        add_book_to_shelf(ripiano, book_data)  # Usa la stessa funzione per aggiungere il libro
        save_data(data)
        open_ripiano_view(room_name, shelf_name, ripiano_name)
        add_window.destroy()

        if messagebox.askyesno("Ancora?", "Vuoi inserire un nuovo libro?"):
            add_book_manually(room_name, shelf_name, ripiano_name)

    tk.Button(add_window, text="Salva", command=save_book, font=("Arial", 10)).pack(pady=10)



# Funzione per aggiungere un libro tramite ISBN
def add_book_isbn(room_name, shelf_name, ripiano_name):
    isbn = simpledialog.askstring("Aggiungi libro", "Inserisci il codice ISBN del libro:")
    if isbn:
        book_data = get_book_data(isbn)
        data = load_data()
        ripiano = data["rooms"][room_name]["shelves"][shelf_name][ripiano_name]
        add_book_to_shelf(ripiano, book_data)  # Usa la stessa funzione per aggiungere il libro
        save_data(data)
        open_ripiano_view(room_name, shelf_name, ripiano_name)
        if messagebox.askyesno("Ancora?", "Vuoi inserire un nuovo libro?"):
            add_book_isbn(room_name, shelf_name, ripiano_name)


# Funzione per cercare libri in un ripiano specifico
def search_books(context, room_name=None, shelf_name=None, ripiano_name=None):
    # Creiamo un popup per inserire il termine di ricerca e selezionare il campo
    search_popup = tk.Toplevel(window)
    search_popup.title(f"Cerca nel {context}")
    center_popup(search_popup)
    tk.Label(search_popup, text="Termine di ricerca:", font=("Arial", 10)).pack()
    search_entry = tk.Entry(search_popup, font=("Arial", 10), width=40)
    search_entry.pack()

    # Opzioni per selezionare il campo di ricerca (titolo, autore, casa editrice)
    field_var = tk.StringVar(value="titolo")
    tk.Label(search_popup, text="Cerca per:", font=("Arial", 10)).pack()
    tk.Radiobutton(search_popup, text="Titolo", variable=field_var, value="titolo").pack(anchor="w")
    tk.Radiobutton(search_popup, text="Autore", variable=field_var, value="autore").pack(anchor="w")
    tk.Radiobutton(search_popup, text="Casa Editrice", variable=field_var, value="casa_editrice").pack(anchor="w")

    # Funzione per eseguire la ricerca nel ripiano
    def perform_search(room_name, shelf_name, ripiano_name):
        search_term = search_entry.get().lower()
        search_field = field_var.get()
        data = load_data()
        results = []

        if context == "ripiano" and room_name and shelf_name and ripiano_name:
            ripiano = data["rooms"][room_name]["shelves"][shelf_name][ripiano_name]
            results = [(book, room_name, shelf_name, ripiano_name) for book in ripiano if
                       search_term in book.get(search_field, "").lower()]

        elif context == "scaffale" and shelf_name and room_name:
            # Ricerca in tutti i ripiani di uno scaffale
            for ripiano_name, ripiano in data["rooms"][room_name]["shelves"][shelf_name].items():
                results.extend([(book, room_name, shelf_name, ripiano_name) for book in ripiano if
                                search_term in book.get(search_field, "").lower()])

        elif context == "stanza" and room_name:
            # Ricerca in tutti i scaffali e ripiani di una stanza specifica
            for shelf_name, shelf in data["rooms"][room_name]["shelves"].items():
                for ripiano_name, ripiano in shelf.items():
                    results.extend([(book, room_name, shelf_name, ripiano_name) for book in ripiano if
                                    search_term in book.get(search_field, "").lower()])

        elif context == "casa":
            # Ricerca in tutta la casa
            for room_name, room in data["rooms"].items():
                for shelf_name, shelf in room["shelves"].items():
                    for ripiano_name, ripiano in shelf.items():
                        results.extend([(book, room_name, shelf_name, ripiano_name) for book in ripiano if
                                        search_term in book.get(search_field, "").lower()])

            # Formattiamo i risultati in stringhe leggibili con stanza, scaffale e ripiano
        formatted_results = [
            f"{book.get('titolo', 'N/A')}\nAutore: {book.get('autore', 'N/A')}\nISBN: {book.get('isbn', 'N/A')}\nData di pubblicazione: {book.get('data_pubblicazione', 'N/A')} - Casa editrice: {book.get('casa_editrice', 'N/A')}\nStanza: {room_name} - Scaffale: {shelf_name} - Ripiano: {ripiano_name}\n"
            for book, room_name, shelf_name, ripiano_name in results
        ]

        if formatted_results:
            show_scrollable_info("Risultati", "\n".join(formatted_results))
        else:
            messagebox.showinfo("Nessun risultato", "Nessun libro trovato.")

        search_popup.destroy()

    tk.Button(search_popup, text="Cerca", command=lambda: perform_search(room_name, shelf_name, ripiano_name), font=("Arial", 10)).pack(pady=10)




# Funzione per aggiungere un ripiano a uno scaffale
def add_ripiano(room_name, shelf_name):
    ripiano_name = simpledialog.askstring("Aggiungi Ripiano", "Inserisci il nome del ripiano:")
    if ripiano_name:
        data = load_data()
        if ripiano_name not in data["rooms"][room_name]["shelves"][shelf_name]:
            data["rooms"][room_name]["shelves"][shelf_name][ripiano_name] = []  # Ogni ripiano è una lista di libri
            save_data(data)
            open_shelf_view(room_name, shelf_name)



# Funzione per modificare un ripiano
def edit_ripiano(room_name, shelf_name, ripiano_name):
    new_name = simpledialog.askstring("Modifica Ripiano", f"Rinomina il ripiano '{ripiano_name}'")
    if new_name:
        data = load_data()
        if new_name not in data["rooms"][room_name]["shelves"][shelf_name]:
            data["rooms"][room_name]["shelves"][shelf_name][new_name] = data["rooms"][room_name]["shelves"][
                shelf_name].pop(ripiano_name)
            save_data(data)
            open_shelf_view(room_name, shelf_name)


# Funzione per rimuovere un ripiano
def remove_ripiano(room_name, shelf_name, ripiano_name):
    if messagebox.askyesno("Conferma", f"Sei sicuro di voler rimuovere il ripiano '{ripiano_name}'?"):
        data = load_data()
        if ripiano_name in data["rooms"][room_name]["shelves"][shelf_name]:
            del data["rooms"][room_name]["shelves"][shelf_name][ripiano_name]
            save_data(data)
            open_shelf_view(room_name, shelf_name)


# Funzione per aprire la vista di un ripiano e i libri contenuti
def open_ripiano_view(room_name, shelf_name, ripiano_name):
    for widget in window.winfo_children():
        widget.destroy()

    tk.Label(window, text=f"Ripiano: {ripiano_name}\n\nScaffale: {shelf_name}\n\nLibri", font=("Arial", 12)).pack()
    tk.Button(window, text="Visualizza tutte le stanze", command=initialize_home_view, font=("Arial", 10)).pack(pady=5)
    tk.Button(window, text=f"Visualizza gli scaffali della stanza {room_name} ", command=lambda: open_shelves_view(room_name),
              font=("Arial", 10)).pack(pady=5)

    tk.Button(window, text=f"Visualizza tutti i ripiani dello scaffale {shelf_name} nella stanza {room_name}", command=lambda: open_shelf_view(room_name, shelf_name), font=("Arial", 10)).pack()

    top_buttons_frame = tk.Frame(window)
    top_buttons_frame.pack(pady=10)

    # Bottoni per aggiungere libri manualmente o tramite ISBN
    tk.Button(top_buttons_frame, text="Aggiungi libro manualmente", width=25,
              command=lambda: add_book_manually(room_name, shelf_name, ripiano_name), font=("Arial", 10)).pack(side="left", padx=5)

    tk.Button(top_buttons_frame, text="Aggiungi libro tramite ISBN", width=25,
              command=lambda: add_book_isbn(room_name, shelf_name, ripiano_name), font=("Arial", 10)).pack(side="left", padx=5)

    # Per cercare nei libri contenuti in un ripiano specifico
    tk.Button(top_buttons_frame, text="Cerca nel ripiano", width=25,
              command=lambda: search_books("ripiano", room_name=room_name, shelf_name=shelf_name, ripiano_name=ripiano_name),
              font=("Arial", 10)).pack(side="left", padx=5)

    # Frame per visualizzare i libri
    books_frame = create_scrollable_frame(window, bg="gray")

    # Carica i dati dal ripiano
    data = load_data()
    ripiano = data["rooms"][room_name]["shelves"][shelf_name][ripiano_name]

    for book in ripiano:
        book_frame = tk.Frame(books_frame, bg="lightgray")
        book_frame.pack(padx=10, pady=5, fill="x")

        book_details = tk.Label(book_frame,
                                text=f"{book.get('titolo', 'N/A')}\nAutore: {book.get('autore', 'N/A')} - Casa editrice: {book.get('casa_editrice', 'N/A')}\nData di Pubblicazione:{book.get("data_pubblicazione")} - ISBN: {book.get('isbn', 'N/A')}",
                                font=("Arial", 10))
        book_details.pack(side="left")

        edit_button = tk.Button(book_frame, text="✏️", command=lambda b=book: edit_book(room_name, shelf_name, ripiano_name, b),
                                font=("Arial", 10))
        edit_button.pack(side="left", padx=5)

        delete_button = tk.Button(book_frame, text="🗑️", command=lambda b=book: remove_book(room_name, shelf_name, ripiano_name, b),
                                  font=("Arial", 10))
        delete_button.pack(side="left")


# Funzione per aggiungere uno scaffale a una stanza
def add_shelf(room_name):
    shelf_name = simpledialog.askstring("Aggiungi Scaffale", "Inserisci il nome dello scaffale:")
    if shelf_name:
        data = load_data()
        if shelf_name not in data["rooms"][room_name]["shelves"]:
            data["rooms"][room_name]["shelves"][shelf_name] = {}  # Cambiato da [] a {}
            save_data(data)
            open_shelves_view(room_name)

# Funzione per modificare uno scaffale
def edit_shelf(room_name, shelf_name):
    new_name = simpledialog.askstring("Modifica Scaffale", f"Rinomina lo scaffale '{shelf_name}'")
    if new_name:
        data = load_data()
        if new_name not in data["rooms"][room_name]["shelves"]:
            data["rooms"][room_name]["shelves"][new_name] = data["rooms"][room_name]["shelves"].pop(shelf_name)
            save_data(data)
            open_shelves_view(room_name)

# Funzione per rimuovere uno scaffale
def remove_shelf(room_name, shelf_name):
    if messagebox.askyesno("Conferma", f"Sei sicuro di voler rimuovere lo scaffale '{shelf_name}'?"):
        data = load_data()
        if shelf_name in data["rooms"][room_name]["shelves"]:
            del data["rooms"][room_name]["shelves"][shelf_name]
            save_data(data)
            open_shelves_view(room_name)


def edit_book(room_name, shelf_name, ripiano_name, book):
    # Finestra per modificare i dati del libro
    edit_window = tk.Toplevel(window)
    edit_window.geometry("400x300")
    edit_window.title("Modifica libro")
    center_popup(edit_window)  # Centro il popup

    # Campi per modificare titolo, autore, casa editrice e ISBN
    tk.Label(edit_window, text="Titolo:", font=("Arial", 12)).pack()
    title_entry = tk.Entry(edit_window, font=("Arial", 12), width=40)
    title_entry.insert(0, book.get("titolo", "N/A"))  # Inserisci il valore attuale
    title_entry.pack()

    tk.Label(edit_window, text="Autore:", font=("Arial", 12)).pack()
    author_entry = tk.Entry(edit_window, font=("Arial", 12), width=40)
    author_entry.insert(0, book.get("autore", "N/A"))
    author_entry.pack()

    tk.Label(edit_window, text="Casa Editrice:", font=("Arial", 12)).pack()
    publisher_entry = tk.Entry(edit_window, font=("Arial", 12), width=40)
    publisher_entry.insert(0, book.get("casa_editrice", "N/A"))
    publisher_entry.pack()

    tk.Label(edit_window, text="Data di Pubblicazione:", font=("Arial", 12)).pack()
    pub_date_entry = tk.Entry(edit_window, font=("Arial", 12), width=40)
    pub_date_entry.insert(0, book.get("data_pubblicazione", "N/A"))
    pub_date_entry.pack()

    tk.Label(edit_window, text="ISBN:", font=("Arial", 12)).pack()
    isbn_entry = tk.Entry(edit_window, font=("Arial", 12), width=40)
    isbn_entry.insert(0, book.get("isbn", "N/A"))
    isbn_entry.pack()

    # Funzione per salvare le modifiche
    def save_changes():
        # Aggiorna i valori del libro modificato
        book["titolo"] = title_entry.get()
        book["autore"] = author_entry.get()
        book["casa_editrice"] = publisher_entry.get()
        book["data_pubblicazione"] = pub_date_entry.get()
        book["isbn"] = isbn_entry.get()

        # Salva i cambiamenti nel file JSON
        data = load_data()
        ripiano = data["rooms"][room_name]["shelves"][shelf_name].get(ripiano_name, [])

        # Cerca il libro nel ripiano e sostituisci il vecchio con il nuovo
        for idx, existing_book in enumerate(ripiano):

            if existing_book['isbn'] == "N/A" and existing_book['titolo'] == book['titolo'] and existing_book['autore'] == book['autore']:
                ripiano[idx] = book
            elif existing_book['isbn'] == book['isbn']:
                ripiano[idx] = book
                break

        save_data(data)  # Salva i dati aggiornati

        # Aggiorna la visualizzazione e chiudi la finestra di modifica
        open_ripiano_view(room_name, shelf_name, ripiano_name)
        edit_window.destroy()

    # Pulsante per salvare le modifiche
    tk.Button(edit_window, text="Salva modifiche", command=save_changes, font=("Arial", 12)).pack(pady=10)



# Funzione per rimuovere un libro
def remove_book(room_name, shelf_name, ripiano_name, book):
    # Conferma se l'utente desidera rimuovere il libro
    confirm = messagebox.askyesno("Conferma eliminazione",
                                  f"Sei sicuro di voler eliminare il libro '{book['titolo']}'?")

    if confirm:
        # Carichiamo i dati dal file JSON
        data = load_data()

        # Recuperiamo il ripiano specifico
        ripiano = data["rooms"][room_name]["shelves"][shelf_name].get(ripiano_name, [])

        # Verifichiamo se il libro esiste nel ripiano
        if book in ripiano:
            # Rimuoviamo il libro dal ripiano
            ripiano.remove(book)

            # Salviamo i dati aggiornati
            save_data(data)

            # Aggiorniamo la vista del ripiano per riflettere la modifica
            open_ripiano_view(room_name, shelf_name, ripiano_name)

            messagebox.showinfo("Successo", "Il libro è stato eliminato correttamente.")
        else:
            messagebox.showerror("Errore", "Il libro non è stato trovato nel ripiano.")


# Funzione per aprire la vista di uno scaffale
def open_shelves_view(room_name):
    for widget in window.winfo_children():
        widget.destroy()

    tk.Label(window, text=f"Stanza: {room_name}\n\nScaffali\n", font=("Arial", 12)).pack()

    tk.Button(window, text="Visualizza tutte le stanze", command=initialize_home_view, font=("Arial", 10)).pack(pady=5)

    top_buttons_frame = tk.Frame(window)
    top_buttons_frame.pack(pady=10)


    # Bottoni per aggiungere libri manualmente o tramite ISBN
    tk.Button(top_buttons_frame, text="Aggiungi scaffale", width=25,
              command=lambda: add_shelf(room_name), font=("Arial", 10)).pack(side="left", padx=5)


    tk.Button(top_buttons_frame, text="Cerca nella stanza", width=25, command=lambda: search_books("stanza", room_name),
              font=("Arial", 10)).pack(side="left", padx=5)

    shelves_frame = create_scrollable_frame(window, bg="gray")

    data = load_data()
    for shelf_name in data["rooms"][room_name]["shelves"].keys():
        shelf_frame = tk.Frame(shelves_frame, bg="lightgray")
        shelf_frame.pack(padx=10, pady=5, fill="x")

        shelf_button = tk.Button(shelf_frame, text=f"Scaffale: {shelf_name}",
                                 command=lambda sn=shelf_name: open_shelf_view(room_name, sn), font=("Arial", 10))
        shelf_button.pack(side="left")

        edit_button = tk.Button(shelf_frame, text="✏️", command=lambda sn=shelf_name: edit_shelf(room_name, sn),
                                font=("Arial", 10))
        edit_button.pack(side="left", padx=5)

        delete_button = tk.Button(shelf_frame, text="🗑️", command=lambda sn=shelf_name: remove_shelf(room_name, sn),
                                  font=("Arial", 10))
        delete_button.pack(side="left")

def open_shelf_view(room_name, shelf_name):
    for widget in window.winfo_children():
        widget.destroy()

    tk.Label(window, text=f"Scaffale: {shelf_name}\n\n Ripiani", font=("Arial", 12)).pack()

    tk.Button(window, text="Visualizza tutte le stanze", command=initialize_home_view, font=("Arial", 10)).pack(pady=5)
    tk.Button(window, text=f"Visualizza gli scaffali della stanza {room_name} ", command=lambda: open_shelves_view(room_name),
              font=("Arial", 10)).pack(pady=5)

    top_buttons_frame = tk.Frame(window)
    top_buttons_frame.pack(pady=10)


    # Bottoni per aggiungere libri manualmente o tramite ISBN
    tk.Button(top_buttons_frame, text="Aggiungi ripiano", width=25,
              command=lambda: add_ripiano(room_name, shelf_name), font=("Arial", 10)).pack(side="left", padx=5)


    # Aggiungi il pulsante per cercare in tutto lo scaffale
    tk.Button(top_buttons_frame, text="Cerca nello scaffale", width=25,
              command=lambda: search_books("scaffale", room_name=room_name, shelf_name=shelf_name),
              font=("Arial", 10)).pack(side="left", padx=5)

    # Frame per visualizzare i ripiani
    shelves_frame = create_scrollable_frame(window, bg="gray")

    data = load_data()
    scaffale = data["rooms"][room_name]["shelves"].get(shelf_name, {})

    for ripiano_name, ripiano in scaffale.items():
        ripiano_frame = tk.Frame(shelves_frame, bg="lightgray")
        ripiano_frame.pack(padx=10, pady=5, fill="x")

        # Bottone per vedere i libri nel ripiano
        ripiano_button = tk.Button(ripiano_frame, text=f"Ripiano: {ripiano_name}", command=lambda rn=ripiano_name: open_ripiano_view(room_name, shelf_name, rn), font=("Arial", 10))
        ripiano_button.pack(side="left", padx=5)

        # Aggiungi pulsanti per modificare e rimuovere il ripiano
        edit_button = tk.Button(ripiano_frame, text="✏️", command=lambda rn=ripiano_name: edit_ripiano(room_name, shelf_name, rn),
                                font=("Arial", 10))
        edit_button.pack(side="left", padx=5)

        delete_button = tk.Button(ripiano_frame, text="🗑️", command=lambda rn=ripiano_name: remove_ripiano(room_name, shelf_name, rn),
                                  font=("Arial", 10))
        delete_button.pack(side="left")

# Funzione per aggiornare la vista delle stanze
def refresh_rooms():
    for widget in rooms_frame.winfo_children():
        widget.destroy()

    data = load_data()
    for room_name in data["rooms"].keys():
        room_frame = tk.Frame(rooms_frame, bg="lightgray")
        room_frame.pack(padx=10, pady=5, fill="x")

        room_button = tk.Button(room_frame, text=f"Stanza: {room_name}",
                                command=lambda rn=room_name: open_shelves_view(rn), font=("Arial", 10))
        room_button.pack(side="left")

        edit_button = tk.Button(room_frame, text="✏️", command=lambda rn=room_name: edit_room(rn), font=("Arial", 10))
        edit_button.pack(side="left", padx=5)

        delete_button = tk.Button(room_frame, text="🗑️", command=lambda rn=room_name: remove_room(rn),
                                  font=("Arial", 10))
        delete_button.pack(side="left")

# Funzioni per importare ed esportare il file JSON
def export_data():
    data = load_data()
    file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        with open(file_path, 'w') as file:
            json.dump(data, file, indent=4)
        messagebox.showinfo("Esportazione", "Dati esportati correttamente.")
import os

import os

# Funzione per generare un ID progressivo
def generate_new_id():
    # Cerca i file nella cartella 'backup'
    if not os.path.exists('backup'):
        os.makedirs('backup')  # Crea la cartella se non esiste

    existing_files = [f for f in os.listdir('backup') if f.startswith('library_data_old_') and f.endswith('.json')]
    if existing_files:
        # Estrae gli ID dai nomi dei file esistenti
        ids = [int(f.split('_')[-1].split('.')[0]) for f in existing_files]
        return max(ids) + 1
    return 1  # Se non ci sono file, l'ID iniziale è 1

# Funzione per importare nuovi dati e salvare la libreria esistente come backup nella cartella 'backup'
def import_data():
    file_path = filedialog.askopenfilename(defaultextension=".json", filetypes=[("JSON files", "*.json")])
    if file_path:
        try:
            # Leggi i dati esistenti dalla libreria corrente
            if os.path.exists(DATA_FILE):
                with open(DATA_FILE, 'r') as current_file:
                    current_data = current_file.read()

                # Genera un nuovo ID progressivo
                new_id = generate_new_id()

                # Crea la cartella 'backup' se non esiste già
                backup_folder = 'backup'
                if not os.path.exists(backup_folder):
                    os.makedirs(backup_folder)

                # Salva i dati esistenti nel file di backup nella cartella 'backup'
                backup_file = os.path.join(backup_folder, f'library_data_old_{new_id}.json')
                with open(backup_file, 'w') as backup:
                    backup.write(current_data)
                messagebox.showinfo("Backup creato", f"I dati esistenti sono stati salvati come {backup_file}")

            # Sovrascrivi con i nuovi dati
            with open(file_path, 'r') as new_data_file:
                new_data = new_data_file.read()

            with open(DATA_FILE, 'w') as current_file:
                current_file.write(new_data)

            messagebox.showinfo("Successo", "Nuova libreria importata con successo.")

        except Exception as e:
            messagebox.showerror("Errore", f"Si è verificato un errore durante l'importazione: {e}")
        initialize_home_view()

# Funzione per inizializzare la vista principale (HOME)
def initialize_home_view():
    for widget in window.winfo_children():
        widget.destroy()

    # Creazione del menu
    menu_bar = tk.Menu(window)
    window.config(menu=menu_bar)

    # Aggiungi l'Hamburger Menu
    file_menu = tk.Menu(menu_bar, tearoff=0)
    menu_bar.add_cascade(label="≡", menu=file_menu)
    file_menu.add_command(label="Esporta Libreria", command=export_data)
    file_menu.add_command(label="Importa Libreria", command=import_data)

    top_buttons_frame = tk.Frame(window)
    top_buttons_frame.pack(pady=10)

    tk.Button(top_buttons_frame, text="Aggiungi libro tramite ISBN",
              command=lambda: choose_room_shelf_ripiano_to_add_book("ISBN"), font=("Arial", 10)).pack(side="left", padx=5)
    tk.Button(top_buttons_frame, text="Aggiungi libro manualmente",
              command=lambda: choose_room_shelf_ripiano_to_add_book("manual"), font=("Arial", 10)).pack(side="left", padx=5)
    tk.Button(top_buttons_frame, text="Aggiungi Stanza", command=add_room, font=("Arial", 10)).pack(side="left", padx=5)
    # Per cercare in tutta la casa (non serve passare room_name o shelf_name)
    tk.Button(top_buttons_frame, text="Cerca nella casa", width=25, command=lambda: search_books("casa"),
              font=("Arial", 10)).pack(side="left", padx=5)

    global rooms_frame
    rooms_frame = create_scrollable_frame(window, bg="gray")

    refresh_rooms()



# Funzione per scegliere stanza e scaffale per l'inserimento di un libro
def choose_room_shelf_ripiano_to_add_book(mode):
    data = load_data()
    rooms = list(data["rooms"].keys())

    if not rooms:
        messagebox.showerror("Errore", "Non ci sono stanze disponibili.")
        return

    # Finestra per selezionare stanza, scaffale e ripiano
    selection_window = tk.Toplevel(window)
    selection_window.geometry("230x250")
    selection_window.title("Seleziona stanza, scaffale e ripiano")
    center_popup(selection_window)

    # Creazione del layout
    tk.Label(selection_window, text="Seleziona stanza:", font=("Arial", 10)).pack(padx=20, pady=(5, 5))
    room_var = tk.StringVar(selection_window)
    room_menu = ttk.Combobox(selection_window, textvariable=room_var, values=rooms, width=30)
    room_menu.pack(padx=20, pady=5)

    tk.Label(selection_window, text="Seleziona scaffale:", font=("Arial", 10)).pack(padx=20, pady=(5, 5))
    shelf_var = tk.StringVar(selection_window)
    shelf_menu = ttk.Combobox(selection_window, textvariable=shelf_var, width=30)
    shelf_menu.pack(padx=20, pady=5)

    tk.Label(selection_window, text="Seleziona ripiano:", font=("Arial", 10)).pack(padx=20, pady=(5, 5))
    ripiano_var = tk.StringVar(selection_window)
    ripiano_menu = ttk.Combobox(selection_window, textvariable=ripiano_var, width=30)
    ripiano_menu.pack(padx=20, pady=5)

    # Funzione per aggiornare gli scaffali in base alla stanza selezionata
    def update_shelves(event):
        selected_room = room_var.get()
        shelves = list(data["rooms"][selected_room]["shelves"].keys())
        shelf_menu["values"] = shelves
        ripiano_menu.set('')  # Reset del ripiano quando si cambia lo scaffale

    # Funzione per aggiornare i ripiani in base allo scaffale selezionato
    def update_ripiani(event):
        selected_room = room_var.get()
        selected_shelf = shelf_var.get()
        if selected_shelf:
            ripiani = list(data["rooms"][selected_room]["shelves"][selected_shelf].keys())
            ripiano_menu["values"] = ripiani

    room_menu.bind("<<ComboboxSelected>>", update_shelves)
    shelf_menu.bind("<<ComboboxSelected>>", update_ripiani)

    # Funzione di conferma
    def confirm_selection():
        selected_room = room_var.get()
        selected_shelf = shelf_var.get()
        selected_ripiano = ripiano_var.get()
        if selected_room and selected_shelf and selected_ripiano:
            if mode == "ISBN":
                add_book_isbn(selected_room, selected_shelf, selected_ripiano)
            else:
                add_book_manually(selected_room, selected_shelf, selected_ripiano)
        else:
            messagebox.showerror("Errore", "Seleziona stanza, scaffale e ripiano.")

    tk.Button(selection_window, text="Conferma", command=confirm_selection).pack(pady=15)





# Funzione per modificare il nome di una stanza
def edit_room(room_name):
    new_name = simpledialog.askstring("Modifica Stanza", f"Modifica il nome della stanza '{room_name}'")
    if new_name:
        data = load_data()
        if new_name not in data["rooms"]:
            data["rooms"][new_name] = data["rooms"].pop(room_name)
            save_data(data)
            refresh_rooms()


# Funzione per rimuovere una stanza
def remove_room(room_name):
    if messagebox.askyesno("Conferma", f"Sei sicuro di voler rimuovere la stanza '{room_name}'?"):
        data = load_data()
        if room_name in data["rooms"]:
            del data["rooms"][room_name]
            save_data(data)
            refresh_rooms()


# Funzione per aggiungere una stanza
def add_room():
    room_name = simpledialog.askstring("Aggiungi Stanza", "Inserisci il nome della stanza:")
    if room_name:
        data = load_data()
        if room_name not in data["rooms"]:
            data["rooms"][room_name] = {"shelves": {}}
            save_data(data)
            refresh_rooms()


# Main window setup
window = tk.Tk()
window.state("zoomed")
window.title("Gestione Libreria")
window.geometry("600x400")

initialize_home_view()
window.mainloop()
