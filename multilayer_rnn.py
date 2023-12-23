"""
Minimal character-level Vanilla RNN model. Written by Kyle DeProw
BSD License
"""
import numpy as np
from optimizers import *

class RNN():
  def __init__(self,hidden_size):
    self.hidden_size = 100 # size of hidden layer of neurons
    print("init")
    self.data = open('/Users/eduardoleao/Documents/NN/rnn/data/way_of_kings.txt', 'r').read() # should be simple plain text file
    chars = list(set(self.data))
    data_size, self.vocab_size = len(self.data), len(chars)
    print('data has {} characters, {} unique.'.format(data_size, self.vocab_size))
    self.char_to_ix = { ch:i for i,ch in enumerate(chars) }
    self.ix_to_char = { i:ch for i,ch in enumerate(chars) }
 

    self.Wxh = {}
    self.Whh = {}
    self.Why = {}
    self.Whu = {}

    self.bh = {}
    self.by = {}
    self.bu = {}


    self.Wxh[0] = np.random.randn(hidden_size, self.vocab_size)/np.sqrt(self.vocab_size) # input to hidden
    self.Whh[0] = np.random.randn(hidden_size, hidden_size)/np.sqrt(hidden_size) # hidden to hidden
    self.Why[0] = np.random.randn(self.vocab_size, hidden_size)/np.sqrt(hidden_size) # hidden to output
    self.Whu[0] = np.random.randn(self.vocab_size, hidden_size)/np.sqrt(hidden_size) # hidden to output

    self.bh[0] = np.zeros((hidden_size, 1)) # hidden bias
    self.by[0] = np.zeros((self.vocab_size, 1)) # output bias
    self.bu[0] = np.zeros((self.vocab_size, 1)) # inter layer bias


    self.Wxh[1] = np.random.randn(hidden_size, self.vocab_size)/np.sqrt(self.vocab_size) # input to hidden
    self.Whh[1] = np.random.randn(hidden_size, hidden_size)/np.sqrt(hidden_size) # hidden to hidden
    self.Why[1] = np.random.randn(self.vocab_size, hidden_size)/np.sqrt(hidden_size) # hidden to output
    self.Whu[0] = np.random.randn(self.vocab_size, hidden_size)/np.sqrt(hidden_size) # hidden to output

    self.bh[1] = np.zeros((hidden_size, 1)) # hidden bias
    self.by[1] = np.zeros((self.vocab_size, 1)) # output bias
    self.bu[1] = np.zeros((self.vocab_size, 1)) # inter layer bias


    
  
  def lossFun(self, inputs, targets, hprev):
    """
    inputs,targets are both list of integers.
    hprev is Hx1 array of initial hidden state
    returns the loss, gradients on model parameters, and last hidden state
    """
    xs, hs, ys, ps = {}, {0:{},1:{}}, {}, {}
    hs[0][-1], hs[1][-1] = np.copy(hprev), np.copy(hprev)
    loss = 0
    # forward pass
    for t in range(len(inputs)):
      xs[t] = np.zeros((self.vocab_size,1)) # encode in 1-of-k representation
      xs[t][inputs[t]] = 1
      hs[0][t] = np.tanh(np.dot(self.Wxh, xs[t]) + np.dot(self.Whh, hs[0][t-1]) + self.bh) # hidden state
    
    for t in range(len(inputs)):
      hs[1][t] = np.tanh(np.dot(self.Whh, hs[1][t-1]) + self.bh + np.dot(self.Whu, hs[0][t]) + self.bu) # hidden state
      ys[t] = np.dot(self.Why, hs[0][t]) + self.by # unnormalized log probabilities for next chars
      ps[t] = np.exp(ys[0][t]) / np.sum(np.exp(ys[0][t])) # probabilities for next chars
      loss += -np.log(ps[0][t][targets[t],0]) # softmax (cross-entropy loss)

    # backward pass: compute gradients going backwards
    dWxh, dWhh, dWhy, dWhu = np.zeros_like(self.Wxh), np.zeros_like(self.Whh), np.zeros_like(self.Why), np.zeros_like(self.Whu)
    dbh, dby, dbu = np.zeros_like(self.bh), np.zeros_like(self.by), np.zeros_like(self.bu)
    dhnext = np.zeros_like(hs[0][0])
    dh = {}
    dhraw = {}


    for t in reversed(range(len(inputs))):
      dy = np.copy(ps[0][t])
      dy[targets[t]] -= 1 # backprop into y. see http://cs231n.github.io/neural-networks-case-study/#grad if confused here
      dWhy += np.dot(dy, hs[t].T)
      dby += dy
      dh[1] = np.dot(self.Why.T, dy) + dhnext # backprop into h
      dhraw[1] = (1 - hs[0][t] * hs[0][t]) * dh[1] # backprop through tanh nonlinearity
      dbh[1] += dhraw[1]
      dWxh += np.dot(dhraw[1], xs[t].T)
      dWhh += np.dot(dhraw[1], hs[0][t-1].T)
      dhnext = np.dot(self.Whh.T, dhraw[1])

      
    for t in reversed(range(len(inputs))):
      dy = np.copy(ps[0][t])
      dy[targets[t]] -= 1 # backprop into y. see http://cs231n.github.io/neural-networks-case-study/#grad if confused here
      dWhy += np.dot(dy, hs[t].T)
      dby += dy
      dh[1] = np.dot(self.Why.T, dy) + dhnext # backprop into h
      dhraw[1] = (1 - hs[0][t] * hs[0][t]) * dh[1] # backprop through tanh nonlinearity
      dbh[1] += dhraw[1]
      dWxh += np.dot(dhraw[1], xs[t].T)
      dWhh += np.dot(dhraw[1], hs[0][t-1].T)
      dhnext = np.dot(self.Whh.T, dhraw[1])


    for dparam in [dWxh, dWhh, dWhy, dbh, dby]:
      np.clip(dparam, -5, 5, out=dparam) # clip to mitigate exploding gradients
    return loss, dWxh, dWhh, dWhy, dbh, dby, hs[0][len(inputs)-1]

  def sample(self,h, seed_ix, n):
    """ 
    sample a sequence of integers from the model 
    h is memory state, seed_ix is seed letter for first time step
    """
    x = np.zeros((self.vocab_size, 1))
    x[seed_ix] = 1
    ixes = []
    for t in range(n):
      h = np.tanh(np.dot(self.Wxh, x) + np.dot(self.Whh, h) + self.bh)
      y = np.dot(self.Why, h) + self.by
      p = np.exp(y) / np.sum(np.exp(y))
      ix = np.random.choice(range(self.vocab_size), p=p.ravel())
      x = np.zeros((self.vocab_size, 1))
      x[ix] = 1
      ixes.append(ix)
    return ixes

  def train(self,seq_length, learning_rate = 1e-2 ,regularization = 1e-5,patience = 6):
    # Optimizer configration
    self.config = {'learning_rate': learning_rate,
                       'regularization': regularization,
                       'beta1': .9,
                       'beta2':.99,
                       'epsilon':1e-8,
                       'm_Wxh':np.zeros(self.Wxh.shape), 'v_Wxh':np.zeros(self.Wxh.shape),
                       'm_Whh':np.zeros(self.Whh.shape), 'v_Whh':np.zeros(self.Whh.shape),
                       'm_Wha':np.zeros(self.Why.shape), 'v_Wha':np.zeros(self.Why.shape),
                       'm_bh':np.zeros(self.bh.shape), 'v_bh':np.zeros(self.bh.shape),
                       'm_ba':np.zeros(self.by.shape), 'v_ba':np.zeros(self.by.shape),
                       't':30}
    n, p, decay_counter = 0, 0, 0
    losses = []
    #mWxh, mWhh, mWhy = np.zeros_like(self.Wxh), np.zeros_like(self.Whh), np.zeros_like(self.Why)
    #mbh, mby = np.zeros_like(self.bh), np.zeros_like(self.by) # memory variables for Adagrad
    smooth_loss = -np.log(1.0/self.vocab_size)*seq_length # loss at iteration 0
    while True:
      # prepare inputs (we're sweeping from left to right in steps seq_length long)
      if p+seq_length+1 >= len(self.data) or n == 0: 
        hprev = np.zeros((hidden_size,1)) # reset RNN memory
        p = 0 # go from start of data
      inputs = [self.char_to_ix[ch] for ch in self.data[p:p+seq_length]]
      targets = [self.char_to_ix[ch] for ch in self.data[p+1:p+seq_length+1]]

      # sample from the model now and then
      if n % 1000 == 0:
        sample_ix = self.sample(hprev, inputs[0], 200)
        txt = ''.join(self.ix_to_char[ix] for ix in sample_ix)
        print('----\n{} \n----'.format(txt, ))
        print('iter {}, loss: {}'.format(n, smooth_loss)) # print progress
        losses.append(smooth_loss)
        if smooth_loss > max(losses[-patience:]) and decay_counter >= patience:
          self.config['learning_rate'] *= 0.9
          print("learning_rate: {}".format(learning_rate))
          decay_counter = 0
      # forward seq_length characters through the net and fetch gradient
      loss, dWxh, dWhh, dWhy, dbh, dby, hprev = self.lossFun(inputs, targets, hprev)
      smooth_loss = smooth_loss * 0.999 + loss * 0.001
      
      # perform parameter update with Adagrad
      self.Wxh, self.Whh, self.Why, self.bh, self.by, self.config = Adam(self.Wxh, self.Whh, self.Why, self.bh, self.by, dWxh, dWhh, dWhy, dbh, dby, self.config)
      #for param, dparam, mem in zip([self.Wxh, self.Whh, self.Why, self.bh, self.by], 
      #                              [dWxh, dWhh, dWhy, dbh, dby], 
      #                              [mWxh, mWhh, mWhy, mbh, mby]):
      #  mem += dparam * dparam
      #  param += -learning_rate * dparam / np.sqrt(mem + 1e-8) # adagrad update

      p += seq_length # move data pointer
      n += 1 # iteration counter 
      decay_counter += 1
seq_length = 25
learning_rate = 3e-4
regularization = 1e-7
hidden_size = 100

model = RNN(hidden_size)
model.train(seq_length,learning_rate = learning_rate,regularization = regularization)