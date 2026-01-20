import tkinter as tk
from tkinter import filedialog, messagebox
import pikepdf
from pathlib import Path

class PDFTool:
    """Intializes the PDF manipulation tool GUI and functionality."""
    def __init__(self, root):
        self.root = root
        self.root.title("PDFriend")
        self.files = []
        self.temporary_files = set()  # Track temporary files created by add_pages_from_file

        # Buttons for file operations
        tk.Button(root, text="Add PDFs", command=self.add_files).pack(pady=5)
        tk.Button(root, text="Select page(s) from a PDF", command=self.add_pages_from_file).pack(pady=5)
        tk.Button(root, text="Clear List", command=self.clear_files).pack(pady=5)

        # Listbox to display selected files
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


        # Button to combine and save PDFs
        tk.Button(
            root,
            text="Build your PDF",
            command=self.combine_and_save,
            bg="#4CAF50",
            fg="white"
        ).pack(pady=10)

    def add_files(self):
        """Opens a file dialog to select PDF files and adds them to the list."""
        selected = filedialog.askopenfilenames(
            filetypes=[("PDF files", "*.pdf")]
        )
        for f in selected:
            if f not in self.files:
                self.files.append(f)
                self.listbox.insert(tk.END, Path(f).name)

    def add_pages_from_file(self):
        """Opens a file dialog to select a PDF file, then allows selecting specific pages to add to the list."""
        
        # Open file dialog to select a PDF
        file_path = filedialog.askopenfilename(
            filetypes=[("PDF files", "*.pdf")]
        )
        if not file_path:
            return
        
        # Open the selected PDF to get page count
        try:
            with pikepdf.open(file_path) as pdf:
                page_count = len(pdf.pages)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
            return
        
        # Create a dialog to input page numbers
        page_input = tk.Toplevel(self.root)
        page_input.title("Select Pages")
        page_input.geometry("400x250")
        
        # Instructions label
        tk.Label(
            page_input,
            text=f"Enter page numbers (PDF has {page_count} pages):\n\n"
                 "Examples:\n"
                 "  - Single page: 5\n"
                 "  - Range: 1-10\n"
                 "  - Multiple: 1,3,5-7,10",
            justify=tk.LEFT
        ).pack(padx=10, pady=10)
        
        # Text entry for page numbers
        entry = tk.Entry(page_input, width=40)
        entry.pack(padx=10, pady=5)
        entry.focus()
        
        def validate_and_add():
            """Validates input and extracts selected pages."""
            input_str = entry.get().strip()
            if not input_str:
                messagebox.showwarning("Warning", "Please enter at least one page number.")
                return
            
            # Parse page numbers
            try:
                pages = self._parse_page_numbers(input_str, page_count)
                if not pages:
                    messagebox.showwarning("Warning", "No valid pages entered.")
                    return
            except ValueError as e:
                messagebox.showerror("Error", str(e))
                return
            
            # Extract pages from PDF
            try:
                with pikepdf.open(file_path) as pdf:
                    new_pdf = pikepdf.Pdf.new()
                    for page_num in pages:
                        new_pdf.pages.append(pdf.pages[page_num - 1])
                
                # Generate temporary file name with page info
                original_name = Path(file_path).stem
                pages_str = self._format_pages_for_name(pages)
                temp_filename = f"{original_name}_{pages_str}.pdf"
                
                # Save to temporary location
                temp_path = Path(file_path).parent / temp_filename
                new_pdf.save(temp_path)
                
                # Add to files list
                if str(temp_path) not in self.files:
                    self.files.append(str(temp_path))
                    self.temporary_files.add(str(temp_path))  # Mark as temporary
                    self.listbox.insert(tk.END, temp_filename)
                
                messagebox.showinfo("Success", f"Added {len(pages)} page(s) from PDF.")
                page_input.destroy()
                
            except Exception as e:
                messagebox.showerror("Error", f"Could not extract pages: {str(e)}")
        
        # Buttons
        button_frame = tk.Frame(page_input)
        button_frame.pack(pady=10)
        
        tk.Button(
            button_frame,
            text="Add",
            command=validate_and_add,
            bg="#4CAF50",
            fg="white"
        ).pack(side=tk.LEFT, padx=5)
        
        tk.Button(
            button_frame,
            text="Cancel",
            command=page_input.destroy
        ).pack(side=tk.LEFT, padx=5)

    def _parse_page_numbers(self, input_str, max_page):
        """Parses page number input and returns a sorted list of unique page numbers.
        
        Supports:
        - Single pages: "5"
        - Ranges: "1-10"
        - Multiple entries: "1,3,5-7,10"
        
        Args:
            input_str: String with page numbers
            max_page: Maximum page number in the PDF
            
        Returns:
            Sorted list of unique valid page numbers
            
        Raises:
            ValueError: If input contains invalid page numbers or formats
        """
        pages = set()
        
        # Split by comma
        for part in input_str.split(','):
            part = part.strip()
            if not part:
                continue
            
            # Check if it's a range (contains dash)
            if '-' in part:
                range_parts = part.split('-')
                if len(range_parts) != 2:
                    raise ValueError(f"Invalid range format: {part}")
                
                try:
                    start = int(range_parts[0].strip())
                    end = int(range_parts[1].strip())
                except ValueError:
                    raise ValueError(f"Invalid page numbers in range: {part}")
                
                if start < 1 or end < 1:
                    raise ValueError("Page numbers must be greater than 0.")
                if start > max_page or end > max_page:
                    raise ValueError(f"Page number exceeds PDF page count ({max_page}).")
                if start > end:
                    raise ValueError(f"Invalid range: start ({start}) must be <= end ({end}).")
                
                pages.update(range(start, end + 1))
            else:
                # Single page
                try:
                    page_num = int(part)
                except ValueError:
                    raise ValueError(f"Invalid page number: {part}")
                
                if page_num < 1:
                    raise ValueError("Page numbers must be greater than 0.")
                if page_num > max_page:
                    raise ValueError(f"Page {page_num} exceeds PDF page count ({max_page}).")
                
                pages.add(page_num)
        
        return sorted(list(pages))

    def _format_pages_for_name(self, pages):
        """Formats a list of page numbers into a compact string for the filename.
        
        Args:
            pages: Sorted list of page numbers
            
        Returns:
            Formatted string (e.g., "1-3_5_7-10")
        """
        if not pages:
            return "pages"
        
        groups = []
        start = pages[0]
        end = pages[0]
        
        for page in pages[1:]:
            if page == end + 1:
                end = page
            else:
                if start == end:
                    groups.append(str(start))
                else:
                    groups.append(f"{start}-{end}")
                start = page
                end = page
        
        # Add the last group
        if start == end:
            groups.append(str(start))
        else:
            groups.append(f"{start}-{end}")
        
        return "_".join(groups)

    def _cleanup_temporary_files(self):
        """Deletes temporary PDF files created by add_pages_from_file."""
        for temp_file in self.temporary_files:
            try:
                temp_path = Path(temp_file)
                if temp_path.exists():
                    temp_path.unlink()  # Delete the file
            except Exception as e:
                # Log error but don't interrupt workflow
                print(f"Warning: Could not delete temporary file {temp_file}: {str(e)}")
        
        # Clear the temporary files tracking
        self.temporary_files.clear()
        self.files.clear()
        self.listbox.delete(0, tk.END)

    def clear_files(self):
        """Clears the list of selected PDF files."""
        self.files.clear()
        self.temporary_files.clear()
        self.listbox.delete(0, tk.END)

    def move_up(self):
        """Moves the selected file up in the list."""
    
        # Get index of selected item
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move up.")
            return
        
        # Show warning if already at the top
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
        """Moves the selected file down in the list."""

        # Get index of selected item
        selection = self.listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select an item to move down.")
            return
        
        # Show warning if already at the bottom
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
        """Generates the combined PDF according to the list order and saves it to a specified location."""
        
        # Check if there are files to combine
        if not self.files:
            messagebox.showerror("Error", "No PDF files selected.")
            return

        # Prompt user for save location
        save_path = filedialog.asksaveasfilename(
            defaultextension=".pdf",
            filetypes=[("PDF files", "*.pdf")]
        )
        if not save_path:
            return

        # Try to combine PDFs and save, otherwise show error message
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
            
            # Delete temporary files after successful save
            self._cleanup_temporary_files()

        except Exception as e:
            messagebox.showerror("Error", str(e))


if __name__ == "__main__":
    root = tk.Tk()
    app = PDFTool(root)
    root.mainloop()
