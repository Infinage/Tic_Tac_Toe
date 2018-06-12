#!/usr/bin/python3

"""
A Tic Tac Toe game with python :)
Implementation of AI - thinks one step ahead to prevent the user from winning & implementation of sockets module
to play the game over a network - the choice which the user makes is transmitted over the socket connection - More of a peer
to peer N/w

Source: https://www.wikihow.com/Win-at-Tic-Tac-Toe

Coded By:
    Naresh J
    
"""

import random

class TcError(Exception):
    pass

def onlymissingno(list1, list2, list3):
    'Returns a no. in list1 not in list2 and is also in list3, if no such no exists returns None'
    lst = list(set(list1) - set(list2))
    if len(lst) == 1 and lst[0] in list3:
        return lst[0]

def aipick(board, aisym):
    'Prioritze winning over making making the game a draw, if no such moves possible it returns a random pick'
    
    oppsym = 'X' if aisym == 'O' else 'O'
    nfilled = [i for i in board if board[i] == ' '] # Positions vacant
    aifill = [i for i in board if board[i] == aisym] # Positions filled by AI
    oppfill = [i for i in board if board[i] == oppsym] # Positions filled by Player

    #Check for winning possibilities, "I can win by picking this."
    for i in ((1, 2, 3), (4, 5, 6), (7, 8, 9), (1, 4, 7), (2, 5, 8), (3, 6, 9), (1, 5, 9), (3, 5, 7)):
        ch = onlymissingno(i, aifill, nfilled)
        if ch:
            return ch

    #Check for the opponents winning moves, "I will lose if don't pick this"
    for i in ((1, 2, 3), (4, 5, 6), (7, 8, 9), (1, 4, 7), (2, 5, 8), (3, 6, 9), (1, 5, 9), (3, 5, 7)):
        ch = onlymissingno(i, oppfill, nfilled)
        if ch:
            return ch

    if board[5] == ' ': # Priortize the center spot
        return 5
    else: # prioritize the corner spots next
        picklist = [i for i in nfilled if i in (1, 3, 5, 7)]
        if picklist: # If any corner spot is free, pick it
            return random.choice(picklist)
        else:
            return random.choice(nfilled) 

class tic_tac_toe(object):
    def __init__(self):
        
        self.board = {i : ' ' for i in range(1, 10)} # TIC TAC TOE board
        self.nfilled = [i for i in range(1, 10)] # values that hasn't been filled yet
        self.winner = None # No winners yet

    def playb(self, against, sym='X'):

        self.printb(empty=True) # prints an empty board with positional values
        turn = sym # by default the player is given 'X', & the player gets to start first
        
        while not(self.winner) and self.nfilled:
            ch = int(input("\nTurn for '" + str(turn) + "'. Where would you place your mark : "))
            
            try:
                if ch not in self.nfilled: # If player picks a value that's already been picked
                    raise board_already_filled
                elif (1 > ch) or (ch > 9): # If player picks a no out of range
                    raise board_value_error

            except TcError as e:
                print (e.args[0])

            else: # If no errors have been encountered

                self.board[ch] = turn
                self.nfilled.remove(ch)
                self.printb()
                self.winner = self.gameovercheck(turn)
                
                turn = 'X' if turn == 'O' else 'O' # Alternating the turns, for the computer

                if self.winner == None and self.nfilled: # If player hasn't already won
                    if against == 'BOT':
                        ch = random.choice(self.nfilled)
                        print ("\nIt's Oviya's turn. She has marked at : ", ch)

                    elif against == 'AI':
                        ch = aipick(self.board, aisym=turn)
                        print ("\nIt's Sophia's turn. She has marked at : ", ch)                    
                    
                    self.board[ch] = turn
                    self.nfilled.remove(ch)
                    self.printb()
                    self.winner = self.gameovercheck(turn)
                    turn = 'X' if turn == 'O' else 'O'
                
        else: # Winner has been decided
            print ("\nGame over!!\n" + str(self.winner), "has won the game.")

    def play(self, hosting):
        '''Play against another player over the network'''

        def findnfilled(self):
            '''A function to find nfilled automatically with the obtained self.board'''
            self.nfilled = [i for i in self.board if self.board[i] == ' ']

        import pickle, socket, time
        host = input("Enter the client's IP address to connect with: ")
        port = 5001 # Change port if required
        sock = socket.socket()

        if hosting:
            sock.bind((host, port))
            sock.listen(1) # Serves atmost one request
            sock, addr = sock.accept()
            
            sym = input("X/O : ").upper() # Only the person hosting the game can decide the symbols
            sock.send(sym.encode())
            turn = sym
            self.sent = True # A class variable that tracks the most recent process - sent/received
            
        else:
            sock.connect((host, port))
            turn = sock.recv(1024).decode()
            sym = 'X' if turn == 'O' else 'O'
            self.sent = False # Recently received
            
        print ("Connection established! Connected to : ", sock.getpeername())
        print ("You are : '" + sym + "'")
        self.printb(True) # Printing the positional values

        while not(self.winner) and self.nfilled:

            turn = 'X' if turn == 'O' else 'O'
            print("\nTurn for '" + str(turn) + "'.")
            
            if not self.sent: # If recently received, then its your turn                
                while True: # Until 
                    ch = int(input("Where would you place your mark : "))
            
                    try:
                        if ch not in self.nfilled: # If player picks a value that's already been picked
                            raise board_already_filled
                        elif (1 > ch) or (ch > 9): # If player picks a no out of range
                            raise board_value_error

                    except TcError as e:
                        print (e.args[0], "\nTry again!")

                    except:
                        print ("\nTry again!")

                    else: # If no errors have been encountered

                        self.board[ch] = turn
                        self.nfilled.remove(ch)
                        data = pickle.dumps(self.board)
                        sock.send(data)
                        break

            else: # If recently received, then its the opponents turn
                self.board = pickle.loads(sock.recv(1024))
                findnfilled(self)

            self.winner = self.gameovercheck(turn)
            self.sent = not self.sent # Inverting the value
            self.printb()

        else: # winner has been decided
            print ("\nGame over!!\n" + str(self.winner), "has won the game.")
            sock.close()
            
    def gameovercheck(self, turn):
        'Game over yet? Returns "Turn" if the person has one'

        if self.board[1] == self.board[2] == self.board[3] and self.board[1] == turn or\
           self.board[4] == self.board[5] == self.board[6] and self.board[4] == turn or\
           self.board[7] == self.board[8] == self.board[9] and self.board[7] == turn : # Checking horizontally
            return turn
        elif self.board[1] == self.board[5] == self.board[9] and self.board[1] == turn  or\
             self.board[3] == self.board[5] == self.board[7] and self.board[3] == turn : # Checking diagnol wise
            return turn
        elif self.board[1] == self.board[4] == self.board[7] and self.board[1] == turn  or\
           self.board[2] == self.board[5] == self.board[8] and self.board[2] == turn  or\
           self.board[3] == self.board[6] == self.board[9] and self.board[3] == turn : # Checking horizontally
            return turn
        else:
            return None

    def printb(self, empty=False):
        'A function that prints the board out to user or alternatively prints an empty* board with positional values'        

        board = {i : i for i in range(1, 10)} if empty else self.board
        
        print ('\n{0: ^3} | {1: ^3} | {2: ^3}'.format(board[1], board[2], board[3]))
        print ('-' * 16)
        print ('{0: ^3} | {1: ^3} | {2: ^3}'.format(board[4], board[5], board[6]))
        print ('-' * 16)
        print ('{0: ^3} | {1: ^3} | {2: ^3}'.format(board[7], board[8], board[9]))


# Defining the custom errors

board_value_error = TcError("Please enter values only between 1 - 9.")
board_already_filled = TcError("A value already exists. Try a different location.")


# ====================== MAIN PROGRAM ======================== #

game = tic_tac_toe()
against = input("Who do you wish to play against (AI/BOT/FRND) : ").upper()
if against == "AI" or against == "BOT":
    game.playb(against)
else:
    hosting = True if input("Do you wish to Host (Y/N): ").upper() == 'Y' else False
    game.play(hosting)
