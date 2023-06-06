import os
from summary_management import load_summaries, save_summaries
from concurrent.futures import ThreadPoolExecutor
from tkinter import messagebox
import asyncio
import chardet
from gpt_api import makeGpt3APICall

async def process_directory(directory_path, update_gui, initial_prompt):
	try:
		summaries = load_summaries(directory_path)
		if summaries is None:
			await generate_summaries(directory_path, update_gui, initial_prompt)
			summaries = load_summaries(directory_path)
		return summaries
	except Exception as e:
		messagebox.showerror("Error", f"An error occurred: {str(e)}")

async def generate_summaries(directory_path, update_gui, initial_prompt, prompt=""):
	summaries = {}
	total_files = sum([len(files) for r, d, files in os.walk(directory_path)])
	processed_files = 0

	with ThreadPoolExecutor() as executor:
		loop = asyncio.get_event_loop()
		for root, dirs, files in os.walk(directory_path):
			for filename in files:
				file_path = os.path.join(root, filename)
				with open(file_path, "rb") as file:
					raw_data = file.read()
				try:
					detected_encoding = chardet.detect(raw_data)['encoding']
					file_content = raw_data.decode(detected_encoding)
				except Exception as e:
					print(f"Error decoding file {file_path} with encoding {detected_encoding}: {e}")
					continue
				summary = await makeGpt3APICall(file_content, initial_prompt + "\n" + prompt)
				if root not in summaries:
					summaries[root] = {}
				summaries[root][filename] = summary
				processed_files += 1
				update_gui(processed_files, total_files, filename)
	save_summaries(directory_path, summaries)
	return summaries

async def update_summary(file_path, initial_prompt, prompt):
	with open(file_path, "r") as file:
		file_content = file.read()
	new_summary = await makeGpt3APICall(file_content, initial_prompt + "\n" + prompt)
	return new_summary
