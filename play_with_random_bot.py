from Game_XO import Game_board,agent

def play_with_random(you_go_first = True): 
    isEnd = False
    player_turn = you_go_first
    token = 1
    #Wrong,isEnd,isDraw
    Board = Game_board()
    if you_go_first:
        my_agent = agent('p2',er = 0,lr = 0,decay = 0)
        my_agent.loadWeight('Weight_Player2')
    else:
        my_agent = agent('p1',er = 0,lr = 0,decay = 0,token=1)
        my_agent.loadWeight('Weight_Player1')
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
        else:
            winner = 'O'
        print(f'{winner} is win')
    else:
        print('Draw')
    

play_with_random()
