import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
from directory_parser import process_directory, update_summary
from pathlib import Path
import os
import asyncio

def update_gui(window, processed_files, total_files, filename):
	window.progress_var.set(processed_files)
	window.progress_bar['maximum'] = total_files
	window.progress_bar['value'] = processed_files
	window.file_var.set(f"Processing: {filename}")

def add_to_treeview(tree, parent, directory):
	for path in sorted(directory.iterdir()):
		item_id = tree.insert(parent, 'end', text=path.name)
		if path.is_dir():
			add_to_treeview(tree, item_id, path)

async def select_directory(window):
	script_directory = Path(__file__).resolve().parent
	initial_directory = script_directory.parent

	directory = filedialog.askdirectory(initialdir=initial_directory)
	if directory:
		window.treeview.delete(*window.treeview.get_children())
		directory_path = Path(directory)
		add_to_treeview(window.treeview, '', directory_path)
		initial_prompt = "Give an Overview of the code's function, then under Functions list the functions and what they do, list what dependencies they use and what functions they evoke"
		window.queue.put(process_directory(directory_path, lambda processed_files, total_files, filename: update_gui(window, processed_files, total_files, filename), initial_prompt))

async def select_file(window):
	file_path = filedialog.askopenfilename(initialdir=os.path.dirname(__file__))
	if file_path:
		parent_id = window.treeview.insert('', 'end', text=os.path.dirname(file_path))
		window.treeview.insert(parent_id, 'end', text=os.path.basename(file_path))
		initial_prompt = "<YOUR_INITIAL_PROMPT>"
		prompt = simpledialog.askstring("Prompt", "Enter a prompt for GPT-3", parent=window)
		if prompt:
			window.queue.put(update_summary(file_path, initial_prompt, prompt))

def create_window(queue):
	window = tk.Tk()
	window.title("gptAnalyze")
	window.configure(bg="black")

	window.queue = queue

	window.treeview = ttk.Treeview(window, style="Custom.Treeview")
	window.treeview.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

	window.progress_var = tk.DoubleVar()
	window.progress_bar = ttk.Progressbar(window, variable=window.progress_var, style="Custom.Horizontal.TProgressbar")
	window.progress_bar.pack(side=tk.BOTTOM, fill=tk.X)

	file_button = ttk.Button(window, text="Select File", command=lambda: window.queue.put(select_file(window)))
	file_button.pack(side=tk.TOP, padx=5, pady=5)

	directory_button = ttk.Button(window, text="Select Directory", command=lambda: window.queue.put(select_directory(window)))
	directory_button.pack(side=tk.TOP, padx=5, pady=5)

	window.file_var = tk.StringVar()
	window.file_label = ttk.Label(window, textvariable=window.file_var, style="Custom.TLabel")
	window.file_label.pack(side=tk.BOTTOM, fill=tk.X)

	return window


