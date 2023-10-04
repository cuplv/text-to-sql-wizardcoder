[![Open in HF Spaces](https://huggingface.co/datasets/huggingface/badges/raw/main/open-in-hf-spaces-lg-dark.svg)](https://huggingface.co/spaces/richardr1126/sql-skeleton-wizardcoder-demo)

# Introduction
This project aims to use off-the-shelf large language models for text-to-SQL program sysnthesis tasks. After experimenting with various models, fine-tuning hyperparameters, and training datasets an optimal solution was identified by fine-tuning the [WizardLM/WizardCoder-15B-V1.0](https://huggingface.co/WizardLM/WizardCoder-15B-V1.0) base model using QLoRA techniques on [this](https://huggingface.co/datasets/richardr1126/spider-context-validation) customized Spider training dataset. The resultant model, [richardr1126/spider-skeleton-wizard-coder-merged](richardr1126/spider-skeleton-wizard-coder-merged), demonstrates **63.7% execution accuracy** when evaluated. The project utilizes a custom validation dataset that incorporates database context into the question. A live demonstration of the model is available on Hugging Face Space, facilitated by the Gradio library for user-friendly GUI.

### Spider Skeleton WizardCoder - [test-suite-sql-eval](https://github.com/taoyds/test-suite-sql-eval) Results
With temperature set to 0.0, top_p set to 0.9, and top_k set to 0, the model achieves **63.7% execution accuracy** on the Spider dev set w/ database context.

<img src="https://raw.githubusercontent.com/cuplv/text-to-sql-wizardcoder/main/eval/plots/spiderwizard-plus-chatgpt.svg" height="300">
<img src="https://raw.githubusercontent.com/cuplv/text-to-sql-wizardcoder/main/eval/plots/spiderwizard-vs-chatgpt.svg" height="300">

Note:
- ChatGPT was evaluated with the default hyperparameters and with the system message `You are a sophisticated AI assistant capable of converting text into SQL queries. You can only output SQL, don't add any other text.`
- Both models were evaluated with `--plug_value` in `evaluation.py` using the Spider dev set with database context.
  - `--plug_value`: If set, the gold value will be plugged into the predicted query. This is suitable if your model does not predict values. This is set to `False` by default.
### Spider Dataset

[Spider](https://arxiv.org/abs/1809.08887) is a large-scale complex and cross-domain semantic parsing and text-to-SQL dataset annotated by 11 Yale students
The goal of the Spider challenge is to develop natural language interfaces to cross-domain databases.

This dataset was used to finetune this model.

# Usage

## Cloning the repo
```bash
git lfs install && \
git clone https://github.com/cuplv/text-to-sql-wizardcoder.git
```
#### Download the HuggingFace Spaces demo submodule
```bash
cd text-to-sql-wizardcoder/sql-skeleton-wizardcoder-demo && \
git submodule update --init --recursive
```

## Running the GGML model locally (need at least 16GB of RAM)
- The best way to run this model locally is to use the [4-bit GGML version](https://huggingface.co/richardr1126/spider-skeleton-wizard-coder-ggml) on [koboldcpp](https://github.com/LostRuins/koboldcpp), with CuBlas support.
- With 8GB of GPU-VRAM on an NVIDIA GPU and 16GB of CPU-RAM, I stabley offloaded 20 layers, half of the model into VRAM, which helps the prompt processing speed tremendously.
- Using `koboldcpp` will create a local REST API that you can use to generate predictions. If you want to use a sepeerate computer to generate predictions, you can use [Ngrok](https://ngrok.com/) to create a public URL for your local REST API.

## Evaluating the model on [Spider](https://arxiv.org/abs/1809.08887) validation set

### Installing Dependencies

To install the necessary dependencies, you should create a new Conda environment and install the required packages using the `requirements.txt` file.:
#### With Conda

```bash
conda create -n text-to-sql && \
conda activate text-to-sql && \
pip install -r requirements.txt
```
#### No Conda
```pip install -r requirements.txt```

The `requirements.txt` file contains the following packages:

```bash
transformers
datasets
tqdm
torch
numpy
scipy
gradio_client
python-dotenv
```

### Generate Training and Validation Data

The `generate-finetune-data.py` script is a Python script that generates fine-tuning data for the model. 

This script allows you to select the mode of data generation (`train`, `validation`, `both`), the SQL type (`natsql`, `sql`), and whether to use the SQL skeleton in the output sequence. 

#### Usage

```bash
python generate-finetune-data.py --mode [MODE] --sql_type [SQL_TYPE] --skeleton
```

#### Options

- `--mode [MODE]`: Specifies the mode of data generation. Replace `[MODE]` with one of `train`, `validation`, or `both`. By default, the mode is set to `both`.
- `--sql_type [SQL_TYPE]`: Specifies the SQL type used. Replace `[SQL_TYPE]` with either `natsql` or `sql`.
- `--skeleton`: Use SQL skeleton in the output sequence.

#### Examples

Generate training and validation data for a `natsql` type model with skeleton:

```bash
python generate-finetune-data.py --mode both --sql_type natsql --skeleton
```

Generate training data for a `sql` type model without skeleton:

```bash
python generate-finetune-data.py --mode train --sql_type sql
```

### Generate Predictions with HuggingFace Space API

Use the `gen_predictions_hf_spaces.ipynb` notebook to generate predictions from **spider-skeleton-wizard-coder** model using the Hugging Face space API.

### Generate Predictions with a REST API

Use the `gen_predictions_koboldcpp.ipynb` notebook to generate predictions from a model using a local Ngrok REST API.

### Evaluate the Predictions

The `evaluation.py` script is used to evaluate the quality of the predictions generated by the model. To evaluate your predictions, use the following command:

```bash
cd eval
python evaluation.py --plug_value --input predictions/temp0_skeleton_best.txt
```
### Command-line options for `evaluation.py`

- `--input`: Specifies the path to the input file that contains the predicted queries. This argument is required.
  
- `--gold`: Specifies the path to the gold queries. This argument is optional and defaults to an empty string.
  
- `--db`: Specifies the directory that contains all the databases and test suites. By default, it points to the `./data/database` directory.
  
- `--table`: Specifies the `tables.json` schema file. By default, this argument is an empty string.
  
- `--etype`: Specifies the evaluation type. It can be `all`, `exec` for test suite accuracy, or `match` for the original exact set match accuracy. The default value is `exec`.
  
- `--plug_value`: If set, the gold value will be plugged into the predicted query. This is suitable if your model does not predict values. This is set to `False` by default.
  
- `--keep_distinct`: If set, the DISTINCT keyword will be kept during evaluation. This is set to `False` by default.
  
- `--progress_bar_for_each_datapoint`: If set, a progress bar for running test inputs for each datapoint will be displayed. This is set to `False` by default.
  
- `--natsql`: If set, the script will convert natsql to SQL and evaluate the converted SQL. This is set to `False` by default.

Based on the input file name, if it contains "natsql", the `--natsql` flag will be automatically set to True. Also, if `--natsql` is true, the output file path is prepared by appending "2sql" before ".txt", and gold and table paths are adjusted accordingly.

If `--natsql` is true, the predicted queries are first converted to SQL by running the `convert_natsql_to_sql.py` script in a subprocess.

# Citations

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