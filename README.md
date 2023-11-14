[![Open in HF Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-lg-dark.svg)](https://huggingface.co/spaces/richardr1126/sql-skeleton-wizardcoder-demo)

#### Finetune Datasets
- [spider](https://huggingface.co/datasets/spider)
- [richardr1126/spider-context-instruct](https://huggingface.co/datasets/richardr1126/spider-context-instruct?row=0)
- [richardr1126/spider-natsql-skeleton-context-instruct](https://huggingface.co/datasets/richardr1126/spider-natsql-skeleton-context-instruct)
- [richardr1126/spider-skeleton-context-instruct](https://huggingface.co/datasets/richardr1126/spider-skeleton-context-instruct)

#### Validation Datasets
- [spider](https://huggingface.co/datasets/spider)
- [richardr1126/spider-context-validation](https://huggingface.co/datasets/richardr1126/spider-context-validation)
- [richardr1126/spider-natsql-context-validation](https://huggingface.co/datasets/richardr1126/spider-natsql-context-validation)
- [richardr1126/spider-context-validation-ranked-schema](https://huggingface.co/datasets/richardr1126/spider-context-validation-ranked-schema)

#### Local Large Language Models
- [richardr1126/sql-guanaco-13b-merged](https://huggingface.co/richardr1126/sql-guanaco-13b-merged)
- [richardr1126/spider-natsql-wizard-coder-merged](https://huggingface.co/richardr1126/spider-natsql-wizard-coder-merged)
- [richardr1126/spider-skeleton-wizard-coder-merged](https://huggingface.co/richardr1126/spider-skeleton-wizard-coder-merged)

# Summer 2023 Approaches
### 1. SQL Guanaco 13B
- This was my first attempt at fine-tuning an LLM
- I used the guanaco 13b (based from llama13b) model as the base model, and I fine tuned it on a guanaco style spider dataset that was premade.
- I never ran a full evaluation for this model because it was performing so poorly.

### 2. Spider Wizard Coder
- Switch to **WizardCoder-15B** (based from StarCoder) as the base model for fine-tuning for my text-to-sql model
- This model was fine-tuned on the [richardr1126/spider-context-instruct](https://huggingface.co/datasets/richardr1126/spider-context-instruct?row=0) dataset, which includes the database context in the fine-tuning data
- The results for this model were okay, but sub par. Around ~50%

### 3. Spider NatSQL Skeleton WizardCoder
- [NatSQL](https://arxiv.org/abs/2109.05153) is an intermediate representation for SQL that simplifies the queries and reduces the mismatch between natural language and SQL. NatSQL preserves the core functionalities of SQL, but removes some clauses and keywords that are hard to infer from natural language descriptions. NatSQL also makes schema linking easier by reducing the number of schema items to predict. NatSQL can be easily converted to executable SQL queries and can improve the performance of text-to-SQL models.
- This model was fine-tuned on the [richardr1126/spider-natsql-skeleton-context-instruct](https://huggingface.co/datasets/richardr1126/spider-natsql-skeleton-context-instruct) dataset, it is the same as spider-context-instruct except it has the NatSQL output in the response instead of the NormSQL. This dataset also used the **skeleton** formatting for better outputs
- **Skeleton formatting:**
	- `select count ( _ ) from _ where _ | select count ( * ) from head where age > 56`
- Theoretically if the model doesn't have to write as much it should do better, NatSQL reduces the length of queries and simplifies joining tables a lot.
- **56.5%** execution accuracy
- The results for this model were less than expected. Most likely because WizardCoder-15B already knows some SQL so trying to fine-tune it on a different SQL language might have confused the model.

### 4. Spider Skeleton Wizard Coder
- Stopped using NatSQL and went back to NormSQL. However I kept the skeleton formatting
- This model was fine-tuned using the [richardr1126/spider-skeleton-context-instruct](https://huggingface.co/datasets/richardr1126/spider-skeleton-context-instruct) dataset. This is still the best performing dataset I have created for fine-tunes.
- **Skeleton formatting:**
	- `select count ( _ ) from _ where _ | select count ( * ) from head where age > 56`
- Results: **61%** execution accuracy
- Beats ChatGPT zero-shot with a simple system prompt and no examples
- This was the best model that I fine-tuned during the summer 2023 for Text-to-SQL tasks.
- The model does very well for a local large language model at Text-to-SQL

### 5. ChatGPT
- To compare my model against something. I ran basic prediction for the spider dataset using ChatGPT.
- The validation dataset I used was the same one I used for Spider Skeleton Wizard Coder
- ChatGPT was evaluated with the default hyperparameters and with the system message `You are a sophisticated AI assistant capable of converting text into SQL queries. You can only output SQL, don't add any other text.`
- Results: **57.6%**.
- This is what the accuracy would be if you were using the ChatGPT GUI and only asking it to convert natural language to SQL with database context.
- ChatGPT's capabilities vary so much depending on the input, later on in my approaches I use a more complex ChatGPT setup to achieve the highest accuracy yet.

# Fall 2023 Approaches

### 1. Spider Skeleton Wizard Coder + ChatGPT Ranked Schema
- In this approach I use the same model Spider Skeleton Wizard Coder for predicting the SQL queries
- **ChatGPT Ranked Schema**
	- I asked ChatGPT to rank the validation dataset's database context by placing tables that are more relevant to the question higher in the database context string. I also ask it to remove tables that it doesn't think it will need in the final prediction. This created the [spider-context-validation-ranked-schema](https://huggingface.co/datasets/richardr1126/spider-context-validation-ranked-schema) dataset.
- The good thing about this approach was that I only needed to run the rankings for the schema through ChatGPT one time. Then I had the file with the rankings forever.
- I didn't change anything about the model, I just reran the predictions using this newly ranked dataset.
- Results: **63.7%**. This is now the ==best performing approach using Local Large Language models==
- This only provided a **2.7%** increase in accuracy.

### 2. Spider Skeleton Wizard Coder + 5 Beams + ChatGPT Ranked Schema
- In this approach I decided to make my local model Spider Skeleton Wizard Coder use **5 beams** in it's generation arguments instead of greedy decoding.
- **5 beams**
	- The model will go down 5 different paths when trying to predict the SQL. I then return 4 of the 5 beams as multiple SQL queries
- With 4 returned SQLs from the model for each dataset question I chose the correct query by choosing the first 1 out of the 4 that doesn't have an execution error in the SQL.
- Results: **60%**
- This approach actually brought the execution accuracy down, which was not expected
- Probably due to the fact that I was keeping basically correct queries from making it into the final result if they had an execution error, and the fact that I took away greedy decoding

### 3. Spider Skeleton Wizard Coder + 5 Beams + ChatGPT Choose Best SQL + ChatGPT Ranked Schema
- The only thing that changed with this approach was that I tried to ask ChatGPT to choose the best SQL for the question out of the 4 return SQLs from my local llm.
- **ChatGPT chooses the best query out of 4**
- Results: **58.5%**
- The results went down even further with this approach indicating that asking ChatGPT to reason about SQL is not going to work.
- It is odd that ChatGPT made the accuracy worse because in the next few approaches I use, asking ChatGPT to do similar things on SQL that ChatGPT itself predicted works just fine, and gives the best results I have ever gotten.

### 4. ChatGPT + Alignment + Clear Context
- This approach does not use a local large language models at all. Relies on **gpt3.5-turbo-16k** from the OpenAI API.
- **Alignment**
	- To align ChatGPT to give better responses I use 5 predefined input sequences that load into ChatGPT before the SQL question I am trying to ask
	- It is not multi-shot as I am not giving it example queries, I just give it tips and rules to follow and confirmation of those rules by ChatGPT.
	- [See below for the ChatGPT Alignment Prompt format](https://github.com/cuplv/text-to-sql-wizardcoder#chatgpt-alignment-prompt-format)
- **Clear Context:**
	- I reformatted the database context to be easier for the model to parse, with each table on a different line and the columns in parentheses
	- I also asked ChatGPT to rank the tables by putting tables that are more relevant higher in the context, I did the same for the columns of each table as well
```
		# singer ( singer_id, name, country, age )
		# stadium ( capacity, highest, lowest, average )
		# concert ( theme, year, concert_id, concert_name )
		# singer_in_concert ( concert_id, singer_id )
		# concert.stadium_id = stadium.stadium_id
		# singer_in_concert.singer_id = singer.singer_id
		# singer_in_concert.concert_id = concert.concert_id
```
- Results: **68.2%**

### 5. ChatGPT + Alignment + Clear Context + Error Correction
- I added was another section to the ChatGPT prediction script that looks for errors in the SQL and tries to correct them using ChatGPT.
- **Error Correction:**
	- run the predicted SQL query from ChatGPT on an actual database corresponding to the question, and if there is an execution error in the sqlparse library when executing the query ask chatGPT to fix it
	- `I am getting an error when executing that on a dummy database. Please try to fix it. The error is:`
- Results: None. I didn't do prediction for just the error correction

### 6. (SQLChatGPT) ChatGPT + Alignment + Clear Context + Error Correction + Example Driven Correction
- In this approach I added Example driven correction to the prediction script for ChatGPT, which comes after error correction section.
- **Example driven correction**:
	- `That is incorrect. Please try again. The resulting table from the query is not what it should be. The correct result table is below. Don't try to match exactly to the result table I give, I want these to work for any content in a larger database. Please try to fix you original query as best you can with the new information.`
- Results: **72%** (or **75.5%** on my simple evaluation tool)
- I am dubbing this approach **SQLChatGPT** becuase there are so many different parts to it.

### 7. SQLChatGPT + SELECT and WHERE Clause Repair
- This approach builds off of the previous approach, SQLChatGPT.
- I introduced a simple mutation based repair in my simple_eval.py tool. It will try to repair the SELECT and WHERE clauses of the SQL query if they are incorrect using the gold (ground truth) SQL's result table (or just input-output examples). It will try to repair the SELECT clause by adding or removing columns from the SELECT clause, and it will try to repair the WHERE clause by adding or removing conditions from the WHERE clause. Tries all combinations of adding and removing columns and conditions.
- Results: **74.6%** (or **79.11%** on my simple evaluation tool)

### 7. Finetuned SQLChatGPT + SELECT and WHERE Clause Repair
- In this approach I decided to finetune ChatGPT (gpt-3.5-turbo-1106, this model has 16k context) on the Spider dataset using OpenAI's API.
- I use the finetuned model for the initial SQL query prediction and the Example Driven correction, but I use gpt-4 for the Error driven correction.
- Results: **80.7%** (or **83.46%** on my simple evaluation tool)
- This is currently the best approach I have taken for Text-to-SQL

# ChatGPT Alignment Prompt format:
**Role: SYSTEM**  
**Content:**  
You are now an excellent SQL writer, first I’ll give you some tips and examples, and I need you to remember the tips, and do not make same mistakes.

**Role: USER**
**Content:**  
Tips 1:  
Question: Which A has most number of B?  
Gold SQL: select A from B group by A order by count ( * ) desc limit 1;
Notice that the Gold SQL doesn’t select COUNT(*) because the question only wants to know the A and the number should be only used in ORDER BY clause, there are many questions asks in this way, and I need you to remember this in the the following questions.

**Role: ASSISTANT**  
**Content:**  
Thank you for the tip! I’ll keep in mind that when the question only asks for a certain field, I should not include the COUNT(*) in the SELECT statement, but instead use it in the ORDER BY clause to sort the results based on the count of that field.

**Role: USER**  
**Content:**  
Tips 2:  
Don’t use "IN", "OR", "LEFT JOIN" as it might cause extra results, use "INTERSECT" or "EXCEPT" instead, and remember to use "DISTINCT" or "LIMIT" when necessary.  
For example,  
Question: Who are the A who have been nominated for both B award and C award?  
Gold SQL should be: select A from X where award = ’B’ intersect select A from X where award = ’C’;

**Role: ASSISTANT**  
**Content:**  
Thank you for the tip! I’ll remember to use "INTERSECT" or "EXCEPT" instead of "IN", "NOT IN", or "LEFT JOIN" when I want to find records that match or don’t match across two tables. Additionally, I’ll make sure to use "DISTINCT" or "LIMIT" when necessary to avoid repetitive results or limit the number of results returned.

**Role: USER**  (Actual prompt)
**Content:**  
```markdown
### Complete sqlite SQL query only and with no explanation, and do not select extra columns that are not explicitly requested in the query.
### Sqlite SQL tables, with their properties:
#
# singer ( singer_id, name, country, age )
# stadium ( capacity, highest, lowest, average )
# concert ( theme, year, concert_id, concert_name )
# singer_in_concert ( concert_id, singer_id )
# concert.stadium_id = stadium.stadium_id
# singer_in_concert.singer_id = singer.singer_id
# singer_in_concert.concert_id = concert.concert_id
#


### How many singers do we have?
SELECT
```

# Citations

```bibtex
@misc{dong2023c3,
      title={C3: Zero-shot Text-to-SQL with ChatGPT}, 
      author={Xuemei Dong and Chao Zhang and Yuhang Ge and Yuren Mao and Yunjun Gao and lu Chen and Jinshu Lin and Dongfang Lou},
      year={2023},
      eprint={2307.07306},
      archivePrefix={arXiv},
      primaryClass={cs.CL}
}
```
```bibtex
@misc{luo2023wizardcoder,
      title={WizardCoder: Empowering Code Large Language Models with Evol-Instruct}, 
      author={Ziyang Luo and Can Xu and Pu Zhao and Qingfeng Sun and Xiubo Geng and Wenxiang Hu and Chongyang Tao and Jing Ma and Qingwei Lin and Daxin Jiang},
      year={2023},
}
```
```bibtex
@article{yu2018spider,
  title={Spider: A large-scale human-labeled dataset for complex and cross-domain semantic parsing and text-to-sql task},
  author={Yu, Tao and Zhang, Rui and Yang, Kai and Yasunaga, Michihiro and Wang, Dongxu and Li, Zifan and Ma, James and Li, Irene and Yao, Qingning and Roman, Shanelle and others},
  journal={arXiv preprint arXiv:1809.08887},
  year={2018}
}
```
```bibtex
@inproceedings{gan-etal-2021-natural-sql,
    title = "Natural {SQL}: Making {SQL} Easier to Infer from Natural Language Specifications",
    author = "Gan, Yujian  and
      Chen, Xinyun  and
      Xie, Jinxia  and
      Purver, Matthew  and
      Woodward, John R.  and
      Drake, John  and
      Zhang, Qiaofu",
    booktitle = "Findings of the Association for Computational Linguistics: EMNLP 2021",
    month = nov,
    year = "2021",
    address = "Punta Cana, Dominican Republic",
    publisher = "Association for Computational Linguistics",
    url = "https://aclanthology.org/2021.findings-emnlp.174",
    doi = "10.18653/v1/2021.findings-emnlp.174",
    pages = "2030--2042",
}
```
```bibtex
@article{dettmers2023qlora,
  title={QLoRA: Efficient Finetuning of Quantized LLMs},
  author={Dettmers, Tim and Pagnoni, Artidoro and Holtzman, Ari and Zettlemoyer, Luke},
  journal={arXiv preprint arXiv:2305.14314},
  year={2023}
}
```
```bibtex
@inproceedings{li2022resdsql,
  author = {Haoyang Li and Jing Zhang and Cuiping Li and Hong Chen},
  title = "RESDSQL: Decoupling Schema Linking and Skeleton Parsing for Text-to-SQL",
  booktitle = "AAAI",
  year = "2023"
}
```