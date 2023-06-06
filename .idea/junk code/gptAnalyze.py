import os
import openai
import requests
import threading
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from tqdm import tqdm

# Set up your OpenAI API credentials
API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("API_KEY")

# File to store parsed summaries
SUMMARY_FILE = "summaries.txt"

# Function to generate a summary using OpenAI API
def makeGpt3APICall(file_content, prompt, summary_list):
	prompt += f"\n\n{file_content}\n\n"

	headers = {
		"Content-Type": "application/json",
		"Authorization": f"Bearer {API_KEY}"
	}

	data = {
		"model": "gpt-3.5-turbo",
		"messages": [
			{"role": "user", "content": prompt}
		]
	}

	response = requests.post(API_URL, headers=headers, json=data)
	response_data = response.json()
	if 'choices' in response_data:
		message = response_data["choices"][0]["message"]["content"]
		summary_list.append(message)
	else:
		print(f"Error: Response does not include 'choices': {response_data}")

# Function to open file dialog and select directory
def select_directory():
	current_directory = os.path.dirname(os.path.abspath(__file__))
	initial_directory = os.path.abspath(os.path.join(current_directory, os.pardir))
	directory_path = filedialog.askdirectory(initialdir=initial_directory)
	if directory_path:
		process_directory(directory_path)

# Function to process the selected directory
def process_directory(directory_path):
	try:
		summaries = load_summaries(directory_path)
		if summaries is None:
			generate_summaries(directory_path)
			summaries = load_summaries(directory_path)
		display_treeview(summaries)
	except Exception as e:
		messagebox.showerror("Error", f"An error occurred: {str(e)}")

# Function to generate summaries for files in a directory
def generate_summaries(directory_path):
	summaries = {}
	total_files = 0
	parsed_files = 0
	summary_list = []

	for root, dirs, files in os.walk(directory_path):
		summaries[root] = {}
		total_files += len(files)

	executor = ThreadPoolExecutor()
	futures = []

	for root, dirs, files in os.walk(directory_path):
		for filename in files:
			file_path = os.path.join(root, filename)
			with open(file_path, 'r', encoding='utf-8') as file:
				file_content = file.read()
				summaries[root][filename] = ""
				future = executor.submit(partial(makeGpt3APICall, file_content, "", summary_list))
				future.add_done_callback(partial(handle_summary, summaries, root, filename))
				futures.append(future)
				parsed_files += 1
				progress = (parsed_files / total_files) * 100
				print(f"Progress: {progress:.2f}%")
				print(f"Prompt: {file_content}\n")
				print("---------------------------------------")

	# Wait for all the API calls to complete
	for future in tqdm(futures, total=len(futures), desc="Processing Files"):
		future.result()

	# Assign the summaries to the corresponding files
	index = 0
	for root, files in summaries.items():
		for filename in files:
			summaries[root][filename] = summary_list[index]
			index += 1

	# Save the summaries to a file
	save_summaries(directory_path, summaries)

# Function to handle the summary callback
def handle_summary(future, summaries, root, filename):
	try:
		future.result()
	except Exception as e:
		print(f"Error processing {filename}: {str(e)}")

# Function to save the summaries to a file
def save_summaries(directory_path, summaries):
	summary_file = os.path.join(directory_path, SUMMARY_FILE)
	with open(summary_file, "w") as file:
		for directory, files in summaries.items():
			file.write(f"{directory}:\n")
			for filename, summary in files.items():
				file.write(f"\t{filename}:\n")
				file.write(f"\t\t{summary}\n")

# Function to load previously parsed summaries
def load_summaries(directory_path):
	summary_file = os.path.join(directory_path, SUMMARY_FILE)
	if os.path.exists(summary_file):
		summaries = {}
		current_directory = ""
		with open(summary_file, "r") as file:
			for line in file:
				line = line.strip()
				if line.endswith(":"):
					current_directory = line[:-1]
					summaries[current_directory] = {}
				elif line.startswith("\t"):
					filename, summary = line.strip().split(":")
					summaries[current_directory][filename.strip()] = summary.strip()
		return summaries
	else:
		return None

# Function to display the summaries in a tree-like representation
def display_treeview(summaries):
	def toggle_summary(event):
		selected_item = treeview.focus()
		item_text = treeview.item(selected_item, 'text')
		if item_text in summaries:
			child_items = treeview.get_children(selected_item)
			if not child_items:
				for filename, summary in summaries[item_text].items():
					treeview.insert(selected_item, 'end', text=filename, tags=('file',), values=(summary,))
			else:
				treeview.delete(*child_items)

	def show_summary(event):
		selected_item = treeview.focus()
		item_text = treeview.item(selected_item, 'text')
		if item_text not in summaries:
			summary = treeview.item(selected_item, 'values')[0]
			messagebox.showinfo("File Summary", summary)

	window = tk.Tk()
	window.title("gptAnalyze")
	window.geometry("800x600")

	treeview = ttk.Treeview(window)
	treeview.pack(fill='both', expand=True)
	treeview.tag_configure('file', font=('TkDefaultFont', 10))
	treeview.bind('<Double-1>', show_summary)
	treeview.bind('<Button-1>', toggle_summary)

	for directory, files in summaries.items():
		parent_item = treeview.insert('', 'end', text=directory)
		for filename in files:
			treeview.insert(parent_item, 'end', text=filename, tags=('file',), values=(summaries[directory][filename],))

	window.mainloop()


# Create the Tkinter GUI window
window = tk.Tk()
window.title("gptAnalyze")
window.geometry("300x200")

# Create a button to select the directory
select_button = tk.Button(window, text="Select Directory", command=select_directory)
select_button.pack(pady=20)

# Run the Tkinter event loop
window.mainloop()
