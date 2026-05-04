import tkinter as tk
from tkinter import ttk, messagebox
import requests
import json
import os

# Файл для хранения избранных пользователей
FAVORITES_FILE = "favorites.json"


class GitHubUserFinder:
    def __init__(self, root):
        self.root = root
        self.root.title("GitHub User Finder")
        self.root.geometry("800x600")
        self.root.resizable(True, True)

        # Загрузка избранных пользователей
        self.favorites = self.load_favorites()

        # Поле ввода для поиска
        tk.Label(root, text="Введите имя пользователя GitHub:").pack(pady=5)
        self.search_entry = tk.Entry(root, width=50)
        self.search_entry.pack(pady=5)
        self.search_entry.bind("<Return>", lambda event: self.search_users())

        # Кнопка поиска
        self.search_button = tk.Button(root, text="Поиск", command=self.search_users)
        self.search_button.pack(pady=5)

        # Таблица результатов поиска
        self.results_tree = ttk.Treeview(root, columns=("login", "id"), show="headings")
        self.results_tree.heading("login", text="Логин")
        self.results_tree.heading("id", text="ID")
        self.results_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Кнопка добавления в избранное
        self.fav_button = tk.Button(
            root, text="Добавить выбранного в избранное", command=self.add_to_favorites
        )
        self.fav_button.pack(pady=5)

        # Список избранных пользователей
        tk.Label(root, text="Избранные пользователи:").pack()
        self.favorites_listbox = tk.Listbox(root, height=8)
        self.favorites_listbox.pack(fill=tk.X, padx=10, pady=5)
        self.update_favorites_listbox()

        # Кнопка удаления из избранного
        self.remove_fav_button = tk.Button(
            root, text="Удалить выбранного из избранного", command=self.remove_from_favorites
        )
        self.remove_fav_button.pack(pady=5)

    def load_favorites(self):
        """Загружает избранное из JSON-файла"""
        if os.path.exists(FAVORITES_FILE):
            try:
                with open(FAVORITES_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return []
        return []

    def save_favorites(self):
        """Сохраняет избранное в JSON-файл"""
        try:
            with open(FAVORITES_FILE, "w", encoding="utf-8") as f:
                json.dump(self.favorites, f, indent=4, ensure_ascii=False)
        except IOError as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить избранное: {e}")

    def update_favorites_listbox(self):
        """Обновляет отображение списка избранных"""
        self.favorites_listbox.delete(0, tk.END)
        for user in self.favorites:
            self.favorites_listbox.insert(tk.END, f"{user['login']} (ID: {user['id']})")

    def search_users(self):
        """Поиск пользователей через GitHub API"""
        query = self.search_entry.get().strip()
        
        # Проверка на пустое поле
        if not query:
            messagebox.showwarning("Ошибка ввода", "Поле поиска не должно быть пустым.")
            return

        # Очистка предыдущих результатов
        for row in self.results_tree.get_children():
            self.results_tree.delete(row)

        # Запрос к GitHub API
        try:
            url = f"https://api.github.com/search/users?q={query}&per_page=30"
            response = requests.get(url)
            response.raise_for_status()
            data = response.json()

            users = data.get("items", [])
            if not users:
                messagebox.showinfo("Результаты", "Пользователи не найдены.")
                return

            for user in users:
                self.results_tree.insert("", tk.END, values=(user["login"], user["id"]))

        except requests.exceptions.RequestException as e:
            messagebox.showerror("Ошибка API", f"Не удалось выполнить запрос:\n{e}")

    def add_to_favorites(self):
        """Добавляет выбранного пользователя в избранное"""
        selected = self.results_tree.selection()
        if not selected:
            messagebox.showwarning("Нет выбора", "Выберите пользователя из результатов поиска.")
            return

        login = self.results_tree.item(selected[0])["values"][0]
        user_id = self.results_tree.item(selected[0])["values"][1]

        # Проверка, не в избранном ли уже
        for fav in self.favorites:
            if fav["id"] == user_id:
                messagebox.showinfo("Уже в избранном", f"Пользователь {login} уже в избранном.")
                return

        self.favorites.append({"login": login, "id": user_id})
        self.save_favorites()
        self.update_favorites_listbox()
        messagebox.showinfo("Добавлено", f"{login} добавлен в избранное.")

    def remove_from_favorites(self):
        """Удаляет выбранного пользователя из избранного"""
        selected_index = self.favorites_listbox.curselection()
        if not selected_index:
            messagebox.showwarning("Нет выбора", "Выберите пользователя в списке избранных.")
            return

        removed = self.favorites.pop(selected_index[0])
        self.save_favorites()
        self.update_favorites_listbox()
        messagebox.showinfo("Удалено", f"{removed['login']} удалён из избранного.")


if __name__ == "__main__":
    root = tk.Tk()
    app = GitHubUserFinder(root)
    root.mainloop()
