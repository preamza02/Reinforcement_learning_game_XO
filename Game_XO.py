import numpy as np
import random
import pickle


## token or state -1 is X 
#              and 1 is O
#                  o is empty

class Game_board:
    def __init__(self):#figsize (3*3)
        self.board = np.zeros((3,3))

    def getAvailable(self):
        available = tuple(map(tuple, np.transpose(np.array(np.where(self.board==0)))))
        return available

    def reset(self):
        self.board = np.zeros((3,3))

    def get_hash(self):
        return utils.create_hash(self.board)
        
    def showBoard(self):
        for rows in self.board:
            for state in rows:
                if state == -1:
                    symbol  = 'X'
                elif state == 1:
                    symbol = 'O'
                else:
                    symbol = '-'
                print(symbol ,end=' ')
            print('\n')

    def action(self,token,index): #token -1,1
        state = self.board[index]
        if state != 0:
            Wrong = True
        else:
            Wrong = False
            self.board[index] = token
        isEnd,isDraw = self.check()
        return Wrong,isEnd,isDraw
        
    def check(self):
        isEnd = False
        isDraw = None
        #chenck rows
        rows_sum = np.abs(np.sum(self.board,axis = 1))
        #chenck rows
        col_sum = np.abs(np.sum(self.board,axis = 0))
        #chenck diagonal
        diagonal1_sum = np.abs(self.board[0][0] +self.board[1][1] + self.board[2][2])
        diagonal2_sum = np.abs(self.board[0][2] +self.board[1][1] + self.board[2][0])
        if (rows_sum == 3).any() or (col_sum == 3).any() or diagonal1_sum == 3 or diagonal2_sum == 3:
            isEnd = True
            isDraw = False
        elif not (self.board == 0).any():
            isEnd = True
            isDraw = True
        return isEnd,isDraw

class agent:
    def __init__(self,name,token = -1,er = 0.4,lr = 1,decay = 0.9):
        self.name = name
        self.token = token
        self.er = er                #explore rate
        self.lr = lr                #learning rate
        self.decay = decay         #decay of future reward
        self.boardScore = {}         #{Board hash : score for this board hash}
        self.history = []           #[hashboard]
    
    def generate_aciton(self,board,show_random = False):
        if np.random.uniform(0, 1) <= self.er:
            action = random.choice(board.getAvailable())
            next_board = board.board.copy()
            next_board[action] = self.token
            action_boardhash = utils.create_hash(next_board)
            self.history.append(action_boardhash)
            if show_random:
                print('this is random')
        else:
            max_val = -99
            for position in board.getAvailable():
                next_board = board.board.copy()
                next_board[position] = self.token
                action_boardhash = utils.create_hash(next_board)
                value = 0 if self.boardScore.get(action_boardhash) is None else self.boardScore.get(action_boardhash)
                if value >= max_val:
                    max_val = value
                    action = position
                    total_hash = action_boardhash
            self.history.append(total_hash)
        return action
        
    def update_boardScore(self,reward):
        for hashboard in self.history[::-1]:
            if self.boardScore.get(hashboard) is None:
                self.boardScore[hashboard] = 0
            add_score  = self.lr * (self.decay * reward - self.boardScore[hashboard])
            self.boardScore[hashboard] += add_score
            reward = self.boardScore[hashboard]
        
    def reset(self):
        self.history = []

    
    def saveWeight(self):
        file = open('Weight_' + str(self.name), 'wb')
        pickle.dump(self.boardScore, file)
        file.close()

    def loadWeight(self, file_path):
        file = open(file_path, 'rb')
        self.boardScore = pickle.load(file)
        file.close()
    
            
            
class utils:
    def create_hash(board):
        board
        hash = str(board.reshape(9))
        return hash
    def train_RL(board,p1,p2,score_dict,er1 = 0.3,er2 = 0.3,lr = 0.7,epoch = 1000,show_log = True,log_every = 100,test = False): #p1 always go first
        p1.er = er1
        p2.er = er2
        p1.lr = lr
        p2.lr = lr
        p1_win = 0
        p2_win = 0
        draw = 0
        for num_game in range(epoch):
            if test or (show_log and ((num_game % log_every) == 0)):
                print(f'epoch : {num_game} Starting')
                total = p1_win + p2_win + draw if (p1_win + p2_win + draw) != 0 else 1
                print(f'P1 win : {p1_win} ({100* p1_win/total}%) P2 win {p2_win} ({100*p2_win/total}%) Draw : {draw} ({100*draw/total}%)')
            isEnd = False
            p1_turn = True
            while not isEnd:
                if p1_turn:
                    action = p1.generate_aciton(board,show_random=test)
                    Wrong,isEnd,isDraw = board.action(p1.token,action)
                else:
                    action = p2.generate_aciton(board,show_random=test)
                    Wrong,isEnd,isDraw = board.action(p2.token,action)
                if Wrong:
                    print('There is some thing wrong Pream find them NOW!!')
                p1_turn = not p1_turn
                if test:
                    board.showBoard()
                    print('\n')
            if isDraw:
                p1_reward = score_dict['Draw1']
                p2_reward = score_dict['Draw2']
                draw += 1
                if test:
                    print('draw')
            elif not p1_turn:
                p1_reward = score_dict['Win']
                p2_reward = score_dict['Lose']
                p1_win +=1
                if test:
                    print('P1')
            else:
                p1_reward = score_dict['Lose']
                p2_reward = score_dict['Win']
                p2_win += 1
                if test:
                    print('P2')
            p1.update_boardScore(p1_reward)
            p1.reset()
            p2.update_boardScore(p2_reward)
            p2.reset()
            board.reset()
        p1.saveWeight()
        p2.saveWeight()

    def train_with_yourself(board,weight_path_dict,score_dict,you_go_first = True,epochs = 1): 
        for _ in range(epochs):
            isEnd = False
            player_turn = you_go_first
            token = 1
            #Wrong,isEnd,isDraw
            Board = Game_board()
            if you_go_first:
                my_agent = agent('Player2',er = 0,lr = 0.8,decay = 0.9)
                my_agent.loadWeight(weight_path_dict[1])
            else:
                my_agent = agent('Player1',er = 0,lr = 0.8,decay = 0.9,token=1)
                my_agent.loadWeight(weight_path_dict[0])
            print('Input foramt is row,col for (row,col)')
            print('ex. if you want to chose (0,0) please enter 0,0')
            Board.showBoard()
            while not isEnd:
                if player_turn:
                    print("Enter Your positon : ",end='')
                    Input = input()
                    if Input == 'q':
                        break
                    try:
                        position = tuple([int(x) for x in Input.split(',')])
                    except:
                        print('Error Wrong format')
                        break
                else:
                    position = my_agent.generate_aciton(Board)
                    print(f'bot go for {position}')
                Wrong,isEnd,isDraw = Board.action(token,position)
                Board.showBoard()
                if Wrong:
                    print('Wrong position please Enter again')
                else:
                    token = -1*token
                    player_turn = not player_turn
            end_token = -1*token
            if not isDraw:
                if end_token == -1:
                    winner = 'X'
                    agent_reward = score_dict['Win'] if you_go_first else score_dict['Lose']
                    my_agent.update_boardScore(agent_reward)
                else:
                    winner = 'O'
                    agent_reward = score_dict['Lose'] if you_go_first else score_dict['Win']
                    my_agent.update_boardScore(agent_reward)
                print(f'{winner} is win')
            else:
                print('Draw')
                agent_reward = score_dict['Draw2'] if you_go_first else score_dict['Draw1']
                my_agent.update_boardScore(agent_reward)
        my_agent.saveWeight()