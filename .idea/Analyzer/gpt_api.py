# gpt_api.py
import aiohttp
import asyncio
import math
import os

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("API_KEY")  # Get the API key from an environment variable
MAX_TOKENS = 4096  # Setting to a bit less than actual limit for safety

async def makeGpt3APICall(file_content, initial_prompt):
	total_length = len(initial_prompt) + len(file_content)
	num_chunks = math.ceil(total_length / MAX_TOKENS)
	chunk_size = len(file_content) // num_chunks

	summaries = []
	async with aiohttp.ClientSession() as session:
		for i in range(num_chunks):
			chunk_start = i * chunk_size
			chunk_end = chunk_start + chunk_size if i != num_chunks - 1 else len(file_content)
			file_chunk = file_content[chunk_start:chunk_end]

			prompt_chunk = f"{initial_prompt}\n\n{file_chunk}\n\n"
			headers = {
				"Content-Type": "application/json",
				"Authorization": f"Bearer {API_KEY}"
			}
			data = {
				"model": "gpt-3.5-turbo",
				"messages": [
					{"role": "system", "content": "You are a language model that summarizes code."},
					{"role": "user", "content": prompt_chunk}
				]
			}
			async with session.post(API_URL, headers=headers, json=data) as response:
				response_data = await response.json()

				if 'choices' in response_data:
					message = response_data["choices"][0]["message"]["content"]
					summaries.append(message)
				else:
					error_message = response_data.get('error', {}).get('message')
					summaries.append("Error: No response choices")
	return ' '.join(summaries)
