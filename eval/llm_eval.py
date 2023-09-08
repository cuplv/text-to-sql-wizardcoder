import time
from datasets import load_dataset
from tqdm.notebook import tqdm
from gradio_client import Client

client = Client("https://richardr1126-sql-skeleton-codellama-demo.hf.space/")

dataset = load_dataset("richardr1126/spider-context-validation", split="validation")