import tkinter as tk
from tkinter import filedialog, messagebox, ttk, scrolledtext
import os
import re
import concurrent.futures
import threading
import queue
import time

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Email and Password Extractor")
        self.root.geometry("800x950")
        self.root.resizable(False, False)

        # Set gradient background
        self.canvas = tk.Canvas(root, width=800, height=950)
        self.canvas.pack(fill=tk.BOTH, expand=True)
        self.draw_gradient(0, 0, 800, 950, "#2C3E50", "#4CA1AF")

        self.style = ttk.Style()
        self.style.theme_use('clam')

        self.queue = queue.Queue()  # Queue for thread-safe communication
        self.create_widgets()
        self.check_queue()  # Start checking the queue for updates

    def draw_gradient(self, x1, y1, x2, y2, color1, color2):
        """Draw a gradient background."""
        for i in range(y1, y2):
            ratio = (i - y1) / (y2 - y1)
            r = int(int(color1[1:3], 16) * (1 - ratio) + int(color2[1:3], 16) * ratio)
            g = int(int(color1[3:5], 16) * (1 - ratio) + int(color2[3:5], 16) * ratio)
            b = int(int(color1[5:7], 16) * (1 - ratio) + int(color2[5:7], 16) * ratio)
            color = f'#{r:02x}{g:02x}{b:02x}'
            self.canvas.create_line(x1, i, x2, i, fill=color)

    def create_widgets(self):
        # Frame for the header
        header_frame = ttk.Frame(self.root)
        header_frame.place(relx=0.5, rely=0.1, anchor=tk.CENTER)

        ttk.Label(header_frame, text="Email and Password Extractor", font=('Helvetica', 16, 'bold'), background="#2C3E50", foreground="white").pack()

        # Frame for folder selection
        folder_frame = ttk.Frame(self.root)
        folder_frame.place(relx=0.5, rely=0.2, anchor=tk.CENTER)

        ttk.Label(folder_frame, text="Select Folder:", background="#2C3E50", foreground="white").pack(side=tk.LEFT)
        self.folder_path = tk.StringVar()
        ttk.Entry(folder_frame, textvariable=self.folder_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_frame, text="Browse", command=self.browse_folder, style="Gradient.TButton").pack(side=tk.LEFT)

        # Frame for keyword input
        keyword_frame = ttk.Frame(self.root)
        keyword_frame.place(relx=0.5, rely=0.3, anchor=tk.CENTER)

        ttk.Label(keyword_frame, text="Enter Keywords:", background="#2C3E50", foreground="white").pack(side=tk.LEFT)
        self.keywords_input = tk.StringVar()
        ttk.Entry(keyword_frame, textvariable=self.keywords_input, width=50).pack(side=tk.LEFT, padx=5)

        # Frame for the process button
        process_frame = ttk.Frame(self.root)
        process_frame.place(relx=0.5, rely=0.4, anchor=tk.CENTER)

        ttk.Button(process_frame, text="Start Processing", command=self.start_processing, style="Gradient.TButton").pack()

        # Frame for the progress bar
        progress_frame = ttk.Frame(self.root)
        progress_frame.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        self.progress_canvas = tk.Canvas(progress_frame, width=760, height=20, bg='white')
        self.progress_canvas.pack()

        # Frame for the log box
        log_frame = ttk.Frame(self.root)
        log_frame.place(relx=0.5, rely=0.7, anchor=tk.CENTER)

        self.log_box = scrolledtext.ScrolledText(log_frame, height=20, width=90, wrap=tk.WORD, bg="#34495E", fg="white", insertbackground="white")
        self.log_box.pack(fill=tk.BOTH, expand=True)

        # Frame for the copy button
        copy_frame = ttk.Frame(self.root)
        copy_frame.place(relx=0.5, rely=0.9, anchor=tk.CENTER)

        ttk.Button(copy_frame, text="Copy Results", command=self.copy_results, style="Gradient.TButton").pack()

        # Custom button style
        self.style.configure("Gradient.TButton", background="#3498DB", foreground="white", font=('Helvetica', 10, 'bold'))
        self.style.map("Gradient.TButton", background=[('active', '#2980B9')])

    def browse_folder(self):
        folder_selected = filedialog.askdirectory()
        if folder_selected:
            self.folder_path.set(folder_selected)
            self.log("Folder selected: " + folder_selected, "info")

    def start_processing(self):
        folder_path = self.folder_path.get()
        if not folder_path:
            messagebox.showerror("Error", "Please select a folder first.")
            self.log("Error: No folder selected.", "error")
            return

        keywords_input = self.keywords_input.get()
        if not keywords_input:
            messagebox.showerror("Error", "Please enter at least one keyword.")
            self.log("Error: No keywords entered.", "error")
            return

        keywords = [keyword.strip() for keyword in keywords_input.split(',')]
        file_paths = [os.path.join(folder_path, f) for f in os.listdir(folder_path) if f.endswith('.txt')]

        if not file_paths:
            messagebox.showerror("Error", "No .txt files found in the selected folder.")
            self.log("Error: No .txt files found in the selected folder.", "error")
            return

        self.log("Processing... Please wait.", "info")
        self.update_progress(0)
        self.root.update_idletasks()

        # Start processing in a separate thread to keep the UI responsive
        threading.Thread(target=self.process_files, args=(file_paths, keywords), daemon=True).start()

    def process_files(self, file_paths, keywords):
        start_time = time.time()  # Start the timer
        total_files = len(file_paths)
        processed_files = 0

        for keyword in keywords:
            output_file = f"{keyword}_output.txt"
            total_lines_extracted, unique_lines_saved = find_and_save_lines_with_keyword(file_paths, keyword, output_file, self.queue)
            duplicates_removed = total_lines_extracted - unique_lines_saved

            self.queue.put(f"Keyword '{keyword}': {total_lines_extracted} lines extracted, {duplicates_removed} duplicates removed, {unique_lines_saved} unique lines saved in {output_file}")

            processed_files += 1
            self.update_progress((processed_files / total_files) * 100)
            self.root.update_idletasks()

        end_time = time.time()  # End the timer
        process_time = end_time - start_time
        self.queue.put(f"Process Completed Successfully in {process_time:.2f} seconds.")

        # Ask the user if they want to save the output file
        save_file = messagebox.askyesno("Save Output", "Do you want to save the output file?")
        if save_file:
            save_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
            if save_path:
                with open(output_file, 'r', encoding='utf-8') as source, open(save_path, 'w', encoding='utf-8') as destination:
                    destination.write(source.read())
                self.log(f"Output saved to {save_path}", "info")

    def update_progress(self, value):
        self.progress_canvas.delete("progress")
        width = self.progress_canvas.winfo_width()
        height = self.progress_canvas.winfo_height()
        for i in range(int(width * value / 100)):
            color = self.get_gradient_color(i, width)
            self.progress_canvas.create_rectangle(i, 0, i + 1, height, fill=color, outline=color, tags="progress")

    def get_gradient_color(self, x, width):
        # Gradient from red to green
        r = int(255 * (1 - x / width))
        g = int(255 * (x / width))
        b = 0
        return f'#{r:02x}{g:02x}{b:02x}'

    def log(self, message, message_type="info"):
        if message_type == "info":
            self.log_box.insert(tk.END, "[INFO] " + message + "\n", "info")
        elif message_type == "error":
            self.log_box.insert(tk.END, "[ERROR] " + message + "\n", "error")
        elif message_type == "success":
            self.log_box.insert(tk.END, "[SUCCESS] " + message + "\n", "success")
        self.log_box.see(tk.END)  # Auto-scroll to the bottom

    def copy_results(self):
        results = self.log_box.get("1.0", tk.END)
        if results.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(results)
            self.log("Results copied to clipboard.", "info")
        else:
            self.log("No results to copy.", "info")

    def check_queue(self):
        """Check the queue for updates and log them."""
        try:
            while True:
                message = self.queue.get_nowait()
                self.log(message, "info")
        except queue.Empty:
            pass
        self.root.after(100, self.check_queue)  # Check the queue every 100ms

def format_email_pass(line):
    pattern = r'(\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b)[:;,\s](\S+)'
    match = re.search(pattern, line)
    if match:
        # Ensure we ignore anything after the first colon in the password
        password_part = match.group(2).split(':')[0]
        return f"{match.group(1)}:{password_part}"
    return None

def extract_email_pass(file_path, keyword, encodings, queue):
    unique_lines = set()
    total_lines_found = 0
    for encoding in encodings:
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                for line in file:
                    if keyword.lower() in line.lower():
                        formatted_line = format_email_pass(line)
                        if formatted_line:
                            total_lines_found += 1
                            unique_lines.add(formatted_line)
                            queue.put(f"Found: {formatted_line} in {file_path}")
            break  # Exit after the first successful encoding
        except UnicodeDecodeError:
            continue  # Try the next encoding
    return unique_lines, total_lines_found

def process_file(file_path, keyword, encodings, queue):
    return extract_email_pass(file_path, keyword, encodings, queue)

def find_and_save_lines_with_keyword(file_paths, keyword, output_file, queue):
    encodings = ['utf-8', 'latin-1', 'cp1252', 'utf-16', 'utf-8-sig']
    total_lines_extracted = 0
    all_unique_lines = set()

    with concurrent.futures.ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
        futures = [executor.submit(process_file, file_path, keyword, encodings, queue) for file_path in file_paths]
        for future in concurrent.futures.as_completed(futures):
            unique_lines, lines_found = future.result()
            all_unique_lines.update(unique_lines)
            total_lines_extracted += lines_found

    with open(output_file, 'w', encoding='utf-8') as output:
        for line in all_unique_lines:
            output.write(line + '\n')

    return total_lines_extracted, len(all_unique_lines)

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()