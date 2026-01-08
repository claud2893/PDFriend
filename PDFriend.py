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

        self.compress_var = tk.BooleanVar(value=True)
        tk.Checkbutton(
            root,
            text="Compress / Shrink Output PDF",
            variable=self.compress_var
        ).pack(pady=5)

        tk.Button(
            root,
            text="Generate a merged/compressed PDF",
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

            if self.compress_var.get():
                pdf.save(
                    save_path,
                    optimize_streams=True, #this does not work - deleting it does not compress PDFs
                    compress_streams=True,
                    linearize=True
                )
            else:
                pdf.save(save_path)

            messagebox.showinfo("Success", "PDF created successfully!")

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTool(root)
    root.mainloop()
