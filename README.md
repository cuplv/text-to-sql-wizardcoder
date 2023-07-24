## Prerequisites

- Ensure that you have Python installed on your system.
- Install the required Python packages listed in the `requirements.txt` file, if not already done.

## Generate Training and Validation Data

The `generate_finetuning_data.py` script is a Python script that generates fine-tuning data for the model. 

This script allows you to select the mode of data generation (`train`, `validation`, `both`), the SQL type (`natsql`, `sql`), and whether to use the SQL skeleton in the output sequence. 

### Usage

```shell
python generate_finetuning_data.py --mode [MODE] --sql_type [SQL_TYPE] --skeleton
```

#### Options

- `--mode [MODE]`: Specifies the mode of data generation. Replace `[MODE]` with one of `train`, `validation`, or `both`. By default, the mode is set to `both`.
- `--sql_type [SQL_TYPE]`: Specifies the SQL type used. Replace `[SQL_TYPE]` with either `natsql` or `sql`.
- `--skeleton`: Use SQL skeleton in the output sequence.

#### Examples

Generate training and validation data for a `natsql` type model with skeleton:

```shell
python generate_finetuning_data.py --mode both --sql_type natsql --skeleton
```

Generate training data for a `sql` type model without skeleton:

```shell
python generate_finetuning_data.py --mode train --sql_type sql
```

## Convert Hugging Face Model to GGML Format

The `convert-hf-to-ggml.py` script allows you to convert a model from Hugging Face to GGML format.

Here is how to convert a model:

```shell
python convert-hf-to-ggml.py [HF_MODEL_NAME]
```

Replace `[HF_MODEL_NAME]` with the name of the Hugging Face model you want to convert.

## Quantize WizardCoder

You can use the `starcoder-quantize` script to quantize the model. 

Here is an example:

```shell
./starcoder-quantize ./models/[HF_MODEL_NAME]-ggml.bin [HF_MODEL_NAME]-q4_0.bin 2
```

Replace `[HF_MODEL_NAME]` with the name of the GGML model you want to quantize.

## Generate Predictions with HuggingFace Space API

Use the `gen_predictions_hf_spaces.ipynb` notebook to generate predictions from your model using the Hugging Face space API.

## Generate Predictions with a REST API

Use the `generate_predict_eval.ipynb` notebook to generate predictions from your model using a REST API.

## Evaluate the Predictions

The `evaluation.py` script is used to evaluate the quality of the predictions generated by the model. It offers a flexible set of parameters to customize your evaluation according to your requirements.

To evaluate your predictions, navigate to the `eval` directory and use the following command:

```shell
cd eval
python evaluation.py --input [NatSQL skeleton + predicted NatSQL file]
```

Replace `[NatSQL skeleton + predicted NatSQL file]` with the path to the input file containing the NatSQL skeleton and the predicted NatSQL. 

### Command-line options for `evaluation.py`

Here is an overview of the command-line arguments you can use with `evaluation.py`:

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

In the case of evaluating exact match accuracy (`etype` 'all' or 'match'), the foreign key map is built from the provided table JSON file. The script asserts that the table argument must not be None if exact set match is evaluated.

If `--natsql` is true, the predicted queries are first converted to SQL by running the `convert_natsql_to_sql.py` script in a subprocess.

Finally, the script calls the `evaluate` function to evaluate the predicted SQL queries.
