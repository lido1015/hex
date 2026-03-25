from solution import HexBoard, SmartPlayer, RandomPlayer

player1 = SmartPlayer(1)
player2 = SmartPlayer(2)

hex = HexBoard(11)

hex.play_game(player1,player2,verbose=True)