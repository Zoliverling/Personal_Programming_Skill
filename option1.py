from tkinter import *
from tkinter import messagebox, simpledialog

from option2 import *


def create_players(n_players):
    players = []
    for p in range(n_players+1):
        _player = Player(p)
        players.append(_player)
    return players


def start_game():
    def do_bet(round):
        '''bot players bet smartly'''
        others_bet = []
        text_str = ''
        for i in game.players_id:
            p = players[i]
            if i == 0:
                text_str += f'You : rank {p.rank}, bet {bet}\n'
                me.bag -= bet
                game.bet += bet
                others_bet += [bet]
            else:
                if round == 1:
                    # get score based on pokers and others bet
                    score = enum_score(p.hand, game.table,
                                       game.pokers, others_bet)  # (0,1]

                else:
                    # get score based on others bet
                    score = others_bet_score(others_bet)
                _bet = int(p.bag * score)
                if _bet == p.bag:
                    _bet -= 1
                if _bet == 0:
                    _bet += 1
                text_str += f'Player {p.name}: rank {p.rank}, bet {_bet}\n'
                p.bag -= _bet
                game.bet += _bet
                others_bet += [_bet]
        text.set(text_str)
    game = Game(len(players))
    for i in game.players_id:
        p = players[i]
        p.hand = game.draw(2)
    me = players[0]
    game_id = me.game_id
    show_cards(canvas, me.hand)
    text.set(
        f'Your cards: {me.hand[0][0]}{me.hand[0][1]} {me.hand[1][0]}{me.hand[1][1]}')
    # You will input your action
    action = messagebox.askquestion(title='input your action', message='bet?')
    if action == 'yes':
        bet = simpledialog.askinteger('First Bet', 'Input bet:', initialvalue=1,
                                      minvalue=1, maxvalue=me.bag-2, parent=root)
    else:
        me.game_id = quit_game(game_id)
        return
    # 3 community cards will be randomly drawn
    game.start()
    show_cards(canvas, me.hand, game.table)
    # You will input your action
    action = messagebox.askquestion(title='input your action', message='bet?')
    if action == 'yes':
        bet += simpledialog.askinteger('Second Bet', 'Input bet:', initialvalue=1,
                                       minvalue=1, maxvalue=me.bag-1, parent=root)
    else:
        me.game_id = quit_game(game_id)
        return
    # players fold
    fold = []
    text_str = ''
    for i in game.players_id:
        p = players[i]
        p.rank = get_rank(p.hand + game.table)
        if i != 0 and p.rank > 8:
            fold.append(i)
            text_str += f'Player {i}: fold\n'
    for i in fold:
        game.players_id.remove(i)
        if len(game.players_id) == 1:
            game.end = 1
            break
    # players’ actions will be displayed
    if game.end:
        text.set(text_str +
                 f'——————Results——————\nYou win\n——————End of Game {game_id}——————')
        me.game_id = end_game(game_id)
        return
    else:
        do_bet(round=1)

    # Another 2 community cards will be randomly drawn
    game.table += game.draw(2)
    show_cards(canvas, me.hand, game.table)
    # You will input your action
    action = messagebox.askquestion(title='input your action', message='bet?')
    if action == 'yes':
        bet = simpledialog.askinteger('Third Bet', 'Input bet:', initialvalue=1,
                                      minvalue=1, maxvalue=me.bag, parent=root)
    else:
        me.game_id = quit_game(game_id)
        return
    # get rank
    for id in game.players_id:
        p = players[id]
        p.rank = 10
        for three in combinations(game.table, 3):
            _rank = get_rank(p.hand + list(three))
            if p.rank > _rank:
                p.rank = _rank
                p.best = p.hand + list(three)
    # players fold
    fold = []
    text_str = ''
    for i in game.players_id:
        p = players[i]
        if i != 0 and (p.rank > 8 or p.bag < 1):
            fold.append(i)
            text_str += f'Player {i}: fold\n'
    for i in fold:
        game.players_id.remove(i)
        if len(game.players_id) == 1:
            game.end = 1
            break
    # players’ actions will be displayed
    if game.end:
        text.set(text_str +
                 f'——————Results——————\nYou win\n——————End of Game {game_id}——————')
        me.game_id = end_game(game_id)
        return
    else:
        do_bet(round=2)
    # the results will be displayed
    winners = get_winner(players, game.players_id)
    text_str = '——————Results——————\n'
    if len(winners) == 1 and winners[0] == 0:
        text_str += 'You win\n'
    else:  # tie
        text_str += 'Winner: ' + \
            ' '.join([f'Player {i}' for i in winners]) + '\n'
    # give money to winners
    for p in players:
        if p.name in winners:
            p.bag += game.bet / len(winners)
    for id in game.players_id:
        p = players[id]
        if id == 0:
            text_str += f'You : ${p.bag}\n'
        else:
            text_str += f'Player {p.name}: ${p.bag}\n'
    print(f'——————End of Game {game_id}——————')
    text.set(text_str)

    # bot player who does not have any money left will be removed
    quit = []
    for p in players:
        if p.bag < 2:
            quit.append(p)
            print(f'player {p.name} left')
    for p in quit:
        players.remove(p)
    # you will be asked whether you want to continue
    if me.bag < 2:
        messagebox.showinfo(
            title='game end', message='Your money is not enough')
        root.quit()
        return
    me.game_id = end_game(game_id)
    return


def end_game(game_id):
    action = messagebox.askquestion(
        title=f'End of Game {game_id}', message='Continue?')
    if action == 'yes':
        show_cards(canvas)
        text.set('Click Start')
    else:
        root.quit()
    return game_id+1


def quit_game(game_id):
    show_cards(canvas)
    text.set('Click Start')
    messagebox.showinfo(title='game end', message='You quit')
    return game_id+1


def pokers_idx(poker):
    number = range(2, 14)
    color = ['S', 'H', 'C', 'D']
    pokers = []
    for c in color:
        pokers.append([c, 14])
    for n in number:
        for c in color:
            pokers.append([c, n])
    return pokers.index(poker)+1


def show_cards(canvas, hand=[], table=[]):
    global img_list
    img_list = []  # store PhotoImage
    for i, card in enumerate(table):
        img = PhotoImage(file=f'img/{pokers_idx(card)}.GIF')
        img_list.append(img)
        canvas.create_image((i*150+100, 100), image=img)
    for i, card in enumerate(hand):
        img = PhotoImage(file=f'img/{pokers_idx(card)}.GIF')
        img_list.append(img)
        canvas.create_image((i*200+200, 300), image=img)


if __name__ == "__main__":
    root = Tk()
    root.title("Texas Hold'em")
    W, H = root.winfo_screenwidth(), root.winfo_screenheight()
    w, h = 800, 600
    root.geometry(f'{w}x{h}+{int((W-w)/2)}+{int((H-h)/2)}')
    root.resizable(0, 0)
    root.withdraw()
    root.update_idletasks()
    n_player = simpledialog.askinteger('Start', 'Input num of bot players:',
                                       initialvalue=3, minvalue=1, parent=root)
    players = create_players(n_player)
    # ---------- Widgets ----------
    canvas = Canvas(root, width=800, height=400, bg='lightgreen')
    canvas.pack()
    text = StringVar()
    screen = Label(root, text='screen', textvariable=text,
                   width=100, height=8, bg='lightblue')
    screen.pack()
    start_btn = Button(root, text='Start', width=10, height=2, bg='white',
                       command=start_game)
    start_btn.pack()
    root.deiconify()
    root.mainloop()
