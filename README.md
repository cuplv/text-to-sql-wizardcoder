#### Generate training data command:
```
python generate_finetuning_data.py --mode both
```

#### Convert HF to GGML command:
```
python convert-hf-to-ggml.py [HF_MODEL_NAME]
```

#### Quantize WizardCoder model command:
```
./starcoder-quantize ./models/[HF_MODEL_NAME]-ggml.bin [HF_MODEL_NAME]-q4_0.bin 2
```

#### Evaluate:
- Use the `generate_predict_eval.ipynb` notebook to generate predictions.
```
cd eval
python evaluation.py --input [NatSQL skeleton + predicted NatSQL file]
```