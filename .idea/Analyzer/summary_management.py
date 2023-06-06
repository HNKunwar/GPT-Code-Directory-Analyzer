# summary_management.py

import os

SUMMARY_FILE = "summaries.txt"
SUMMARY_DIR = "summary_subdir"

def save_summaries(directory_path, summaries):
	summary_dir = os.path.join(directory_path, SUMMARY_DIR)
	if not os.path.exists(summary_dir):
		os.makedirs(summary_dir)
	summary_file = os.path.join(summary_dir, SUMMARY_FILE)
	with open(summary_file, "w") as file:
		for directory, files in summaries.items():
			file.write(f"{directory}:\n")
			for filename, summary in files.items():
				file.write(f"\t{filename}:\n")
				file.write(f"\t\t{summary}\n")
			file.write("\n")


def load_summaries(directory_path):
	summary_dir = os.path.join(directory_path, SUMMARY_DIR)
	summary_file = os.path.join(summary_dir, SUMMARY_FILE)
	if os.path.exists(summary_file):
		summaries = {}
		current_directory = ""
		with open(summary_file, "r") as file:
			for line in file:
				line = line.strip()
				if line.endswith(":"):
					current_directory = line[:-1]
					summaries[current_directory] = {}
				elif line:
					filename, summary = line.strip().split(": ")
					summaries[current_directory][filename] = summary
		return summaries
	else:
		return None
