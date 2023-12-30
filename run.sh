#!/bin/bash
echo "Initializing training of NLP model..."
<<<<<<< HEAD
python3 run.py --train config.json shakespeare.txt -to_path shakespeare.json -from_path model_params_large.json
=======
python3 run.py --train config.json shakespeare.txt -to_path shakespeare.json -from_path sanderson.json
>>>>>>> 5bfbb29... fixed LSTM for torch
