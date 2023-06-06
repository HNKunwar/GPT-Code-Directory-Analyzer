

import sys
import os

# Append the directory containing gptAnalyze.py to the sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

import gptAnalyze

if __name__ == '__main__':
	gptAnalyze.main()

