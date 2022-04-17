from Game_XO import utils,Game_board
score_dict = {
    'Draw1':-0.1,
    'Draw2':0.3,
    'Win':1,
    'Lose':-1}
weight_path_dict = ('Weight_Player1','Weight_Player2')
myboard = Game_board()
utils.train_with_yourself(myboard,weight_path_dict,score_dict)