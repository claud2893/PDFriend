import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
from pathlib import Path

class PDFTool:
    def __init__(self, root):
        self.root = root
        self.root.title("PDFriend")
        self.files = []

        # UI
        tk.Button(root, text="Add PDFs", command=self.add_files).pack(pady=5)
        tk.Button(root, text="Clear List", command=self.clear_files).pack(pady=5)

        self.listbox = tk.Listbox(root, width=60)
        self.listbox.pack(padx=10, pady=5)

        # Buttons for reordering
        button_frame = tk.Frame(root)
        button_frame.pack(pady=5)

        tk.Button(
            button_frame,
            text="Move Up",
            command=self.move_up,
            bg="#2196F3",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            button_frame,
            text="Move Down",
            command=self.move_down,
            bg="#2196F3",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)

        tk.Button(
            root,
            text="Build your PDF",
            command=self.combine_and_save,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=10)

    def add_files(self):
        selected = filedialog.askopenfilenames(
            filetypes=[("PDF files", "*.pdf")]
        )
        for f in selected:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, Path(f).name)

    def clear_files(self):
        self.files.clear()
        self.listbox.delete(0, tk.END)

    def move_up(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move up.")
            return
        
        index = selection[0]
        if index == 0:
            messagebox.showwarning("Warning", "Item is already at the top.")
            return
        
        # Swap in self.files
        self.files[index], self.files[index - 1] = self.files[index - 1], self.files[index]
        
        # Update listbox
        item = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index - 1, item)
        self.listbox.selection_set(index - 1)

    def move_down(self):
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move down.")
            return
        
        index = selection[0]
        if index == len(self.files) - 1:
            messagebox.showwarning("Warning", "Item is already at the bottom.")
            return
        
        # Swap in self.files
        self.files[index], self.files[index + 1] = self.files[index + 1], self.files[index]
        
        # Update listbox
        item = self.listbox.get(index)
        self.listbox.delete(index)
        self.listbox.insert(index + 1, item)
        self.listbox.selection_set(index + 1)

    def combine_and_save(self):
        if not self.files:
            messagebox.showerror("Error", "No PDF files selected.")
            return

        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not save_path:
            return

        try:
            pdf = pikepdf.Pdf.new()

            for file in self.files:
                with pikepdf.open(file) as src:
                    pdf.pages.extend(src.pages)

            pdf.save(
                save_path,
                compress_streams=True,
                linearize=True
            )

            messagebox.showinfo("Success", "PDF created successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTool(root)
    root.mainloop()
