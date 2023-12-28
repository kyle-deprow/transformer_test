#!/bin/bash
echo "Initializing training of NLP model..."
python3 run.py --fine_tune /Users/ubuntu/Documents/ML/NN/rnn/config.json /Users/ubuntu/Documents/ML/NN/rnn/data/bee_gees.txt /Users/ubuntu/Documents/ML/NN/rnn/models/model_bee_gees.json
