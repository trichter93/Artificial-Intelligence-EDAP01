#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 12 20:44:23 2022

@author: trichter
"""
import gym
import random
import requests
import numpy as np
import argparse
import sys
import copy
from graphviz import Digraph
from gym_connect_four import ConnectFourEnv
from skeleton import search_tree, evaluation_function


env: ConnectFourEnv = gym.make("ConnectFour-v0")
env.reset()
for i in range(6):
    if i % 2 == 0:
        state, result, done, _ = env.step(3)
        env.change_player()
    else:
        state, result, done, _ = env.step(0)
        env.change_player()
tree = search_tree(env, state, 2)
dot = tree.make_dot_data()
dot.render(directory='/Users/trichter/Artificial-Intelligence-EDAP01/Assignment 1 (Adverserial Search)'.replace('\\', '/'))


evaluations = {}
#evaluations[sequence] = evaluation_function(tree.final_positions[sequence])
for i, node in enumerate(tree.leaf_nodes):
    print("final pos " + str(i) + " : \n")
    print(str(node.operator_sequence) + '\n')
    print(str(node.state)+"\n")
    print(node.evaluation)

    

# 3, 6 max_key => gives 125
# 