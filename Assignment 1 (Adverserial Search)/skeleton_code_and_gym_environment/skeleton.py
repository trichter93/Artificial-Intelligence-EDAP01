import gym
import random
import requests
import numpy as np
import argparse
import sys
import copy
from operator import itemgetter
from graphviz import Digraph
from gym_connect_four import ConnectFourEnv

env: ConnectFourEnv = gym.make("ConnectFour-v0")

#SERVER_ADRESS = "http://localhost:8000/"
SERVER_ADRESS = "https://vilde.cs.lth.se/edap01-4inarow/"
API_KEY = 'nyckel'
STIL_ID = ["tfy14tri"] # TODO: fill this list with your stil-id's

def call_server(move):
   res = requests.post(SERVER_ADRESS + "move",
                       data={
                           "stil_id": STIL_ID,
                           "move": move, # -1 signals the system to start a new game. any running game is counted as a loss
                           "api_key": API_KEY,
                       })
   # For safety some respose checking is done here
   if res.status_code != 200:
      print("Server gave a bad response, error code={}".format(res.status_code))
      exit()
   if not res.json()['status']:
      print("Server returned a bad status. Return message: ")
      print(res.json()['msg'])
      exit()
   return res

def check_stats():
   res = requests.post(SERVER_ADRESS + "stats",
                       data={
                           "stil_id": STIL_ID,
                           "api_key": API_KEY,
                       })

   stats = res.json()
   return stats

"""
You can make your code work against this simple random agent
before playing against the server.
It returns a move 0-6 or -1 if it could not make a move.
To check your code for better performance, change this code to
use your own algorithm for selecting actions too
"""
def opponents_move(env):
   env.change_player() # change to oppoent
   avmoves = env.available_moves()
   if not avmoves:
      env.change_player() # change back to student before returning
      return -1

   # TODO: Optional? change this to select actions with your policy too
   # that way you get way more interesting games, and you can see if starting
   # is enough to guarrantee a win
   print(list(avmoves)) # There are almost always available moves
   action = random.choice(list(avmoves))

   state, reward, done, _ = env.step(action)
   if done:
      if reward == 1: # reward is always in current players view
         reward = -1
   env.change_player() # change back to student before returning
   return state, reward, done

# Create some tree for which every node is a new game state and edges are possible moves
# Implement DFS (Depth first search) 

# Implement some quiescence search

# def evaluation_function(state):
    
#     # Do something based on board to return -1,...,1 with some
#     # Implement some linear weighted function
    
#     return 0

def evaluation_function(state):
        evaluation_table = np.array([[3, 4, 5, 7, 5, 4, 3], 
                           [4, 6, 8, 10, 8, 6, 4],
                           [5, 8, 11, 13, 11, 8, 5], 
                           [5, 8, 11, 13, 11, 8, 5],
                           [4, 6, 8, 10, 8, 6, 4],
                           [3, 4, 5, 7, 5, 4, 3]])
        utility = 138
        sum = 0
        for i in range(6):
            for j in range(7):
                if state[i,j] == 1:
                    sum += evaluation_table[i,j]
                elif state[i,j] == -1:
                    sum -= evaluation_table[i,j]
        return utility + sum

def student_move(env, state = np.zeros((6, 7), dtype=int)):
   """
   TODO: Implement your min-max alpha-beta pruning algorithm here.
   Give it whatever input arguments you think are necessary
   (and change where it is called).
   The function should return a move from 0-6
   """
   tree = search_tree(env, state, 5)
   # This is where we should use a search tree, a evaluation function and alphabeta pruning in making the next move
   
   # evaluate all the positions at the bottom of the tree and choose move with highest evaluation
   # evaluations = {}
   # for node in tree.leaf_nodes:
   #     evaluations[tree.leaf_nodes.sequence] = evaluation_function(tree.node.state)
   # if tree.max_depth % 2 == 0: # 
   #     max_key = max(evaluations, key=evaluations.get)
   #     return list(max_key)[0]
   # max_key = max(evaluations, key=evaluations.get)
   # return list(max_key)[0]
   return tree.optimal()

def play_game(vs_server = True):
   """
   The reward for a game is as follows. You get a
   botaction = random.choice(list(avmoves)) reward from the
   server after each move, but it is 0 while the game is running
   loss = -1
   win = +1
   draw = +0.5
   error = -10 (you get this if you try to play in a full column)
   Currently the player always makes the first move
   """

   # default state
   state = np.zeros((6, 7), dtype=int)
   # env has methods available_moves, reset, step, 
   # setup new game
   if vs_server:
      # Start a new game
      res = call_server(-1) # -1 signals the system to start a new game. any running game is counted as a loss

      # This should tell you if you or the bot starts
      print(res.json()['msg'])
      botmove = res.json()['botmove']
      state = np.array(res.json()['state'])
      env.reset(board=state)
   else:
      # reset game to starting state
      env.reset(board=None)
      # determine first player
      student_gets_move = random.choice([True, False])
      if student_gets_move:
         print('You start!')
         print()
      else:
         print('Bot starts!')
         print()

   # Print current gamestate
   #print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
   #print(state)
   #print()

   done = False
   while not done:
      # Select your move
      stmove = student_move(env, state) # TODO: change input here

      # make both student and bot/server moves
      if vs_server:
         # Send your move to server and get response
         res = call_server(stmove)
         print(res.json()['msg'])

         # Extract response values
         result = res.json()['result']
         botmove = res.json()['botmove']
         state = np.array(res.json()['state'])
         print("state : \n" + str(state))
         env.reset(board=state)
      else:
         if student_gets_move:
            # Execute your move
            avmoves = env.available_moves()
            if stmove not in avmoves:
               print("You tried to make an illegal move! Games ends.")
               break
            state, result, done, _ = env.step(stmove)
            print("state : \n" + str(state))

         student_gets_move = True # student only skips move first turn if bot starts

         # print or render state here if you like

         # select and make a move for the opponent, returned reward from students view
         if not done:
            state, result, done = opponents_move(env)

      # Check if the game is over
      if result != 0:
         done = True
         if not vs_server:
            print("Game over. ", end="")
            # print("state : \n" + str(state))
         if result == 1:
            print("You won!")
            #print("state : \n" + str(state))
         elif result == 0.5:
            print("It's a draw!")
            # print("state : \n" + str(state))
         elif result == -1:
            print("You lost!")
            # print("state : \n" + str(state))
         elif result == -10:
            print("You made an illegal move and have lost!")
         else:
            print("Unexpected result result={}".format(result))
         if not vs_server:
            print("Final state (1 are student discs, -1 are servers, 0 is empty): ")
      else:
         #print("Current state (1 are student discs, -1 are servers, 0 is empty): ")
         pass
      # Print current gamestate
      #print(state)
      #print()

def main():
   # Parse command line arguments
   for i in range(1 ):
       parser = argparse.ArgumentParser()
       group = parser.add_mutually_exclusive_group()
       group.add_argument("-l", "--local", help = "Play locally", action="store_true")
       group.add_argument("-o", "--online", help = "Play online vs server", action="store_true")
       parser.add_argument("-s", "--stats", help = "Show your current online stats", action="store_true")
       args = parser.parse_args()
    
       # Print usage info if no arguments are given
       if len(sys.argv)==1:
          parser.print_help(sys.stderr)
          sys.exit(1)
    
       if args.local:
          play_game(vs_server = False)
       elif args.online:
          play_game(vs_server = True)
    
       if args.stats:
          stats = check_stats()
          print(stats)

   # TODO: Run program with "--online" when you are ready to play against the server
   # the results of your games there will be logged
   # you can check your stats bu running the program with "--stats"
class search_tree:
    # Each game board has row amount of rows and col amount of cols. 6 and 7 respectively for our game
    # self.final_positions = []
    def __init__(self, env,  state = np.zeros((6, 7), dtype=int), max_depth = 3):
        self.total_nodes = 0
        self.max_depth = max_depth
        self.env = copy.deepcopy(env)
        self.__dot = Digraph('Search-Tree', comment='A search tree')
        self.ground_state = state
        self.root = Node(self.env, 0, self.ground_state)
        self.leaf_nodes = []
        self.expand_tree(self.root, 0)
        self.minimax(self.leaf_nodes)
        
        
        
    def expand_tree(self, node, done):
        if done == True or node.depth == self.max_depth:
            # if done == True:
                #print(done)
            self.add_node_to_graph(node, done, node.parent_node.id)
            self.leaf_nodes.append(node)
            return node
        if node.parent_node != -1:
            self.add_node_to_graph(node, False, node.parent_node.id)
        else:
            self.add_node_to_graph(node, False, node.parent_node)
        for move in node.env.available_moves():
            tempenv = copy.deepcopy(node.env)
            sequence = copy.copy(node.operator_sequence)
            #print(f"depth : {node.depth}, move : {move}")
            state, reward, done, _ = tempenv.step(move)
            tempenv.change_player()
            #print(state)
            self.total_nodes += 1
            next_node = Node(tempenv, self.total_nodes, state, node, move, sequence, node.depth+1, node.path_cost + 10)
            node.children.append(self.expand_tree(next_node, done))
        return node
            
    # Problemet är att jag vill inte göra moves i det faktiska environmentet,
    # jag vill bara spara nya kopior av statet efter hypotetiska moves och se om de resulterar i ett result != 0
    # env.step(action) ger mig statet (Kan bara göras på det sättet), env.available_moves ger mängden görbara moves
    def add_node_to_graph(self, node, done, parentid=-1):
        if node.operator == -1:
            node_string = "id : " + str(node.id) + "\n parent : " + str(node.parent_node)  + "\n operator sequence : " + str(node.operator_sequence) + "\n path cost : " + str(node.path_cost) + "\n state : \n " + str(node.state)
        elif node.depth == self.max_depth or done==True:
            node_string = "id : " + str(node.id) + ", eval : " + str(evaluation_function(node.state)) + " \n operator : " + str(node.operator) + "\n parent : " + str(node.parent_node.id) + "\n operator sequence : " + str(node.operator_sequence) + "\n path cost : " + str(node.path_cost) + "\n state : \n " + str(node.state) 
        else:
            node_string = "id : " + str(node.id) + ", eval : " + str(evaluation_function(node.state)) + " \n operator : " + str(node.operator) + "\n parent : " + str(node.parent_node.id) + "\n operator sequence : " + str(node.operator_sequence) + "\n path cost : " + str(node.path_cost) + "\n state : \n " + str(node.state) 
        self.__dot.node(str(node.id), label=node_string)
        if (parentid != -1):
            self.__dot.edge(str(node.parent_node.id), str(node.id))

        # print(nodeString)

        return
    def optimal(self):
        #Returns minimax decision, traverse tree and find the optimal decision
        operator_evaluations = {}
        for child in self.root.children:
            operator_evaluations[child.operator] = child.evaluation
        return max(operator_evaluations, key=operator_evaluations.get)
            # split leaf nodes into groups with same parent node
            # take min value of these nodes evaluations and put it as evaluation of parent node
            # do the same with parent nodes and go up till root
            
            
    def minimax(self, list_of_nodes):
        parent_nodes = []
        #nodes_per_parent = {}
        for node in list_of_nodes:
            if node.parent_node != -1:
                parent_nodes.append(node.parent_node)
            else:
                parent_nodes.append(node)
        parent_nodes = list(set(parent_nodes))
        for parent_node in parent_nodes:
            if parent_node is not self.root or not isinstance(parent_node, int):
                evaluations = [child.evaluation for child in parent_node.children]
                if parent_node.depth % 2 == 1:
                    parent_node.evaluation = min(evaluations)
                else:
                    parent_node.evaluation = max(evaluations)
        #copy.copy(parent_nodes)
        if len(parent_nodes) != 1:
            self.minimax(parent_nodes)
    def max_value():
        pass
    
    def min_value():
        pass
            
        
    def make_dot_data(self) :
        return self.__dot
class Node:
    
    def __init__(self, env, id, state = np.zeros((6, 7), dtype=int), parent_node=-1, operator = -1, operator_sequence = [], depth = 0, path_cost = 0): # Operator is an int that took us from the previous state to the node stat
        self.parent_node = parent_node
        self.id = id
        self.operator = operator
        self.operator_sequence = operator_sequence
        if self.operator != -1:
            self.operator_sequence.append(operator)
        self.env = env
        self.state = state
        self.children = []
        self.depth = depth
        self.evaluation = evaluation_function(self.state)
        self.path_cost = path_cost
        #print(self.id)
    # def change_state(self,state):
    #     rows = 5 # max number
    #     for i in range(rows,-1,-1):
    #         if state[i][self.operator] == 0:
    #             state[i][self.operator] = 1
    #             return state
            
   
# state, reward, done, _ = env.step(2)

if __name__ == "__main__":
    main()
# There are almost always 6 edges from each node
# The changes to the state happen automatically,
# but I need to keep an internal respresentation at each node and depth to evaluate how good a move is

# class Node:
#     """Contains the information of the node and another nodes of the Decision Tree."""

#     def __init__(self, id, parentId=0):
#         self.parentId = parentId
#         self.id = id
 
#         self.value = None
#         #self.next = None
#         self.children = []
#     def has_children(self):
#         return self.children != None
        
        
# dot.render(directory='/Users/trichter/Artificial-Intelligence-EDAP01/Assignment 1 (Adverserial Search)).replace('\\', '/')
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        