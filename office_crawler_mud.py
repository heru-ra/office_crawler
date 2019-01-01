from datetime import datetime
from json import load, loads, dump
from os import system, path
from random import randint, choice
import socket
from textwrap import TextWrapper as textwrapper, fill
from threading import Timer as timer, Thread, Event, Lock as lock
from time import time

# terminal colors
red = '\033[31m'
lred = '\033[91m'
green = '\033[32m'
lgreen = '\033[92m'
yellow = '\033[33m'
lyellow = '\033[93m'
blue = '\033[34m'
lblue = '\033[94m'
magenta = '\033[35m'
lmagenta = '\033[95m'
cyan = '\033[36m'
lcyan = '\033[96m'
lgray = '\033[37m'
dgray = '\033[90m'
white = '\033[97m'
black = '\033[30m'
decolor = '\033[0m\033[49m'
bold = '\033[1m'
unbold = '\033[22m'

clients = {}

lock = lock()


class Resources:

    prompt = f"> "

    # if you spawn in this office/room, it means your office_map.json file is
    # missing or incorrectly formatted
    office = {
        1: {'name': "In a Dream State",
            'exits': {'north': 1, 'south': 1, 'west': 1, 'east': 1},
            'desc': "Your mind is blank, but carefree. You're in a warm, " +
            "happy place... Wait, did you sleep through your alarm?"
            },
    }

    npc = {
        'Jay': {'prefix': "",
                'desc': "sits at his desk, coding.",
                'look': "He's very smart and handsome. You are filled with " +
                "an overwhelming desire to be his friend.",
                'current_room': 1,
                'allowed_rooms': (1, 2, 3, 4),
                'move_die': (20, 10),
                'phrases': (
                    "tells you a really lame dad joke.",
                    "glances at you out of the corner of his eye.",
                    "mumbles, \"There's got to be a better way to do this...\""
                ),
                'phrase_die': (30, 20),
                },
    }


class Dice:

    @classmethod
    def roll(cls, sides: int, mod: int):

        if randint(1, sides) <= (sides / mod):
            return True
        else:
            return False


class Ticker:

    def loop(self):

        self.function(self.interval)
        self.thread = timer(self.interval, self.loop)
        self.thread.start()

    def _start(self, interval: int, function):

        self.interval = interval
        self.function = function
        self.thread = timer(self.interval, self.loop)
        self.thread.start()

    def _stop(self):

        self.thread.cancel()


class Output:

    @classmethod
    def cmd_prompt(cls, player: str):

        output = f"\n{Resources.prompt}"
        clients[player]['session'].socket.send(output.encode())

    @classmethod
    def _local(cls, room: int, msg: str, prefix: str = '', suffix: str = '', player_mute: str = None):

        # room-dependant, locally-announced messages

        for player in clients.keys():
            if clients[player]['current_rm'] == room:
                output = f"{prefix}{cls.wordwrap(msg)}{suffix}"

                if player_mute != None and player_mute == player:
                    pass
                else:

                    clients[player]['session'].socket.send(
                        output.encode())

                    cls.cmd_prompt(player)

    @classmethod
    def motd(cls, player: str):

        out = \
            f" {cyan}╒════════════════════════════════════════════════════════════════════════════╕\n" \
            f" {cyan}│                                                                            │\n" \
            f" {cyan}│{dgray}                          .,,uod8B8bou,,.                                   {cyan}│\n" \
            f" {cyan}│{dgray}                 ..,uod8BBBBBBBBBBBBBBBBRPFT?l!i:.                          {cyan}│\n" \
            f" {cyan}│{dgray}            ,=m8BBBBBBBBBBBBBBBRPFT?!||||||||||||||                         {cyan}│\n" \
            f" {cyan}│{dgray}            !...:!TVBBBRPFT||||||||||!!^^\"\"'   ||||                         {cyan}│\n" \
            f" {cyan}│{dgray}            !.......:!?|||||!!^^\"\"'            ||||                         {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||   {white}____ ____ ____ ____ ____ ____                  {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||  {white}||O |||F |||F |||I |||C |||E ||                 {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||  {white}||__|||__|||__|||__|||__|||__||                 {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||  {white}|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|                 {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||     {white}____ ____ ____ ____ ____ ____ ____           {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||    {white}||C |||R |||A |||W |||L |||E |||R ||          {cyan}│\n" \
            f" {cyan}│{dgray}            !.........||||    {white}||__|||__|||__|||__|||__|||__|||__||          {cyan}│\n" \
            f" {cyan}│{dgray}            `.........||||    {white}|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|          {cyan}│\n" \
            f" {cyan}│{dgray}             `........||||                    ,╷╷╷╷                         {cyan}│\n" \
            f" {cyan}│{dgray}              .;......||||               _.-!{red}███╗{dgray}|{red}  ███╗██╗   ██╗██████╗    {cyan}│\n" \
            f" {cyan}│{dgray}      .,uodWBBBBb.....||||       _.-!!|||||||{red}████╗{dgray}b{red}████║██║   ██║██╔══██╗   {cyan}│\n" \
            f" {cyan}│{dgray}   !YBBBBBBBBBBBBBBb..!|||:..-!!|||||||!iof68{red}██╔████╔██║██║   ██║██║  ██║   {cyan}│\n" \
            f" {cyan}│{dgray}   !..YBBBBBBBBBBBBBBb!!||||||||!iof68BBBBBBR{red}██║╚██╔╝██║██║   ██║██║  ██║   {cyan}│\n" \
            f" {cyan}│{dgray}   !....YBBBBBBBBBBBBBBbaaitf68BBBBBBRPFT?!::{red}██║{dgray}:{red}╚═╝ ██║╚██████╔╝██████╔╝   {cyan}│\n" \
            f" {cyan}│{dgray}   !......YBBBBBBBBBBBBBBBBBBBRPFT?!::::::;:!{red}╚═╝{dgray}`;::{red} ╚═╝ ╚═════╝ ╚═════╝    {cyan}│\n" \
            f" {cyan}│{dgray}   !........YBBBBBBBBBBRPFT?!::::::::::^''...::::::;                        {cyan}│\n" \
            f" {cyan}│{dgray}   `..........YBRPFT?!::::::::::::::::::::::::;iof68bo                      {cyan}│\n" \
            f" {cyan}│{dgray}     `..........:::::::::::::::::::::::;iof68888888888b.                    {cyan}│\n" \
            f" {cyan}│{dgray}       `........::::::::::::::::;iof688888888888888888888b.                 {cyan}│\n" \
            f" {cyan}│{dgray}         `......:::::::::;iof688888888888888888888888888888b.               {cyan}│\n" \
            f" {cyan}│{dgray}           `....:::;iof688888888888888888888888888888888899fT!              {cyan}│\n" \
            f" {cyan}│{dgray}             `..::!8888888888888888888888888888888899fT|!^\"'                {cyan}│\n" \
            f" {cyan}│{dgray}               `' !!988888888888888888888888899fT|!^\"'                      {cyan}│\n" \
            f" {cyan}│{dgray}                   `!!8888888888888888899fT|!^\"'                            {cyan}│\n" \
            f" {cyan}│{dgray}                     `!988888888899fT|!^\"'                                  {cyan}│\n" \
            f" {cyan}│{dgray}                       `!9899fT|!^\"'                                        {cyan}│\n" \
            f" {cyan}│{dgray}                         `!^\"'                                              {cyan}│\n" \
            f" {cyan}│                                                                            │\n" \
            f" {cyan}╘════════════════════════════════════════════════════════════════════════════╛{decolor}\n\n"

        clients[player]['session'].socket.send(str("\n").encode())
        clients[player]['session'].socket.send(out.encode())

    @classmethod
    def private(cls, player: str, msg: str, prefix: str = '', suffix: str = '', nowrap: bool = False):

        # non-room dependant, player-isolated messages
        if nowrap:
            output = f"{msg}"
        else:
            output = f"{prefix}{cls.wordwrap(msg)}{suffix}"

        clients[player]['session'].socket.send(output.encode())

    @property
    def timestamp(self):

        return datetime.fromtimestamp(time()).strftime('%Y-%m-%d %H:%M:%S')

    @classmethod
    def wordwrap(cls, string: str):

        # wrap our print output at 80 char
        wrapper = textwrapper(
            width=76, replace_whitespace=False, drop_whitespace=True, initial_indent='  ', subsequent_indent='  ')

        return wrapper.fill(text=string)


class Action(Output):

    def __init__(self):

        super().__init__()

        self.directions = {
            'north': ('n', 'north'),
            'south': ('s', 'south'),
            'east': ('e', 'east'),
            'west': ('w', 'west')
        }

        self.direction_aliases = tuple(item for
                                       sublist in self.directions.values() for
                                       item in sublist)

        # aliases and their commands
        self.commands = {
            'move': {
                'aliases': self.direction_aliases,
                'command': self.move
            },
            'look': {
                'aliases': ('l', 'look'),
                'command': self.look
            },
            'quit': {
                'aliases': ('exit', 'close', 'quit', 'leave', 'log', 'logout'),
                'command': self.quit
            },
            '_help': {
                'aliases': ('cmd', 'commands', 'help'),
                'command': self._help
            },
            'debug': {
                'aliases': ('debug',),
                'command': self.debug
            },
            '_map': {
                'aliases': ('map',),
                'command': self._map
            },
        }

    def debug(self, player: str, cmd_line: str):

        self._local(clients[player]['current_rm'],
               "You run some tests", "\0337\033[2F\n", "\0338")

    def exits(self, room: int, long: bool = False):

        total_exits = None

        if not long:
            # concatenate available exits
            for key in Resources.office[room]['exits']:
                if Resources.office[room]['exits'][key]:
                    if not total_exits:
                        total_exits = f"{key}"
                    else:
                        total_exits = f"{total_exits}, {key}"

            # pluralize exit/s
            if len(Resources.office[room]['exits']) > 1:
                exit_plural = "Exits"
            else:
                exit_plural = "Exit"

            return f"{green}{exit_plural}:{decolor} {total_exits}"

    def _help(self, player: str, cmd_line: str):

        self.private(player,
                     f"{bold}Available Commands:{unbold}", "\n", "\n")

        self.private(player,
                     f" north\n   south\n   east\n   west\n   look [direction or npc]\n   quit", "\n", "\n")

        self.cmd_prompt(player)

    def look(self, player: str, cmd_line: str):

        if " " in cmd_line:

            result = False

            cmd_line = cmd_line[cmd_line.index(" ")+1:]

            cmd_line = next((key for key, value in self.directions.items()
                             if cmd_line in value), cmd_line)

            # look <direction>
            if cmd_line in Resources.office[clients[player]['current_rm']]['exits'] and \
                    Resources.office[clients[player]['current_rm']]['exits'][cmd_line]:
                result = True

                room = Resources.office[clients[player]['current_rm']
                                        ]['exits'][str(cmd_line)]
                direction = cmd_line

                self.private(player,
                             f"To the {direction} you see:", "\n", "\n\n")

                self.private(player,
                             f"  {blue}{Resources.office[room]['name']}{decolor}", "", "\n")

                # present players
                for other_player in clients.keys():
                    if clients[other_player]['current_rm'] == room:
                        self.private(player,
                                     f"  {cyan}{clients[other_player]['name']} is standing here.{decolor}", "", "\n")

                # present NPCs
                for key in Resources.npc.keys():
                    if room == Resources.npc[key]['current_room']:
                        self.private(player,
                                     f"  {yellow}{key} {Resources.npc[key]['desc']}" +
                                     f"{decolor}", "", "\n")

            # look <NPC>
            for key in Resources.npc.keys():
                if cmd_line in str(key).lower() and \
                        Resources.npc[key]['current_room'] == \
                        clients[player]['current_rm']:

                    result = True

                    self.private(
                        player, f"  {Resources.npc[key]['look']}", "\n", "\n")

            # no valid look target
            if not result:
                self.private(player,
                             f"You see nothing.", "\n", "\n")

            self.cmd_prompt(player)

        else:
            self.room_desc(player, clients[player]['current_rm'])

    def _map(self, player: str, cmd_line: str):

        if " " in cmd_line:
            cmd_line = cmd_line[cmd_line.index(" ")+1:]

        map_width = 22
        line1 = line2 = line3 = ""
        default_drawing = {
            'nw': f"┼", 'n': f"───", 'ne': f"┼",
            'w': f"│", 'c': "   ", 'e': f"│",
            'sw': f"┼", 's': f"───", 'se': f"┼"
        }

        self.drawing = dict(default_drawing)

        if len(Resources.office.keys()) < map_width:
            map_width = len(Resources.office.keys())

        for room in Resources.office.keys():
            if cmd_line == "num":
                self.drawing['c'] = str(room).zfill(3)

            for wall, num in Resources.office[room]['exits'].items():
                if num:
                    if wall == 'north':
                        self.drawing['n'] = "   "
                    elif wall == 'south':
                        self.drawing['s'] = "   "
                    elif wall == 'west':
                        self.drawing['w'] = " "
                    elif wall == 'east':
                        self.drawing['e'] = " "

            if self.drawing['n'] == "───" and self.drawing['s'] == "───" and \
                    self.drawing['w'] == "│" and self.drawing['e'] == "│":
                self.drawing['c'] = " ╳ "

            if room == clients[player]['current_rm']:
                self.drawing['c'] = f"{red}YOU{decolor}"

            if 'regions' in Resources.office[room]:
                for num in Resources.office[room]['regions']:
                    if cmd_line == "num":
                        if num == 0:
                            color = white
                        if num == 1:
                            color = blue
                        if num in (2, 3, 4):
                            color = f"\033[44m{white}"
                        if num == 5:
                            color = green
                        if num in (6, 7, 8, 9):
                            color = f"\033[42m{white}"
                        if num == 10:
                            color = cyan
                        if num in (11, 12, 13, 14, 15):
                            color = f"\033[46m{white}"
                        if num == 16:
                            color = magenta
                        if num in (17, 18, 19, 20, 21):
                            color = f"\033[45m{white}"
                        if num == 22:
                            color = f"\033[43m{black}"
                        if num == 23:
                            color = red
                        if num == 24:
                            color = f"\033[41m{white}"
                    else:
                        color = dgray
            else:
                color = dgray

            line1 = f"{line1}\b{self.drawing['nw']}{self.drawing['n']}{self.drawing['ne']}"
            line2 = f"{line2}\b{self.drawing['w']}{color}{self.drawing['c']}{decolor}{self.drawing['e']}"
            line3 = f"{line3}\b{self.drawing['sw']}{self.drawing['s']}{self.drawing['se']}"

            self.drawing = dict(default_drawing)

            if room % map_width == 0:
                self.private(
                    player, f"\033[F{line1}\n{line2}\n{line3}", "", "", True)
                line1 = line2 = line3 = ""

    def move(self, player: str, cmd_line: str):

        cmd_line = next(key for key, value in self.directions.items()
                        if cmd_line in value)

        # if direction leads to adjacent room, move player
        if cmd_line in Resources.office[clients[player]['current_rm']]['exits'] and \
                Resources.office[clients[player]['current_rm']]['exits'][cmd_line]:

            # locally announce departure
            for direction, num in Resources.office[clients[player]['current_rm']]['exits'].items():
                if Resources.office[clients[player]['current_rm']]['exits'][cmd_line] == num:
                    self._local(clients[player]['current_rm'],
                                f"{clients[player]['name']} left to the {direction}.", "\r", "\n", player)

            # move rooms
            clients[player]['current_rm'] = Resources.office[clients[player]['current_rm']
                                                             ]['exits'][cmd_line]

            # locally announce entry
            self._local(clients[player]['current_rm'],
                        f"{clients[player]['name']} enters the room.", "\r", "\n", player)

            self.room_desc(player, clients[player]['current_rm'])
        else:
            self.private(player,
                         f"You cannot move that direction.", "\n", "\n")

            self.cmd_prompt(player)

    def quit(self, player: str, cmd_line: str):

        self.private(player,
                     f"You log your hours and leave the office...", "\n", "\n\n")

    def room_desc(self, player: str, room: int):

        entities = False
        newline = ""

        self.private(
            player, f"{blue}{Resources.office[room]['name']}{decolor}", "\n", "\n")

        self.private(
            player, f"  {Resources.office[room]['desc']}", "\n", "\n\n")

        # present players
        for other_player in clients.keys():
            if clients[other_player]['current_rm'] == room and other_player != player:
                entities = True
                self.private(player,
                             f"{cyan}{clients[other_player]['name']} is standing here.{decolor}", "", "\n")

        # present NPCs
        for key in Resources.npc.keys():
            if room == Resources.npc[key]['current_room']:
                entities = True
                self.private(player,
                             f"{yellow}{key} {Resources.npc[key]['desc']}{decolor}", "", "\n")

        if entities:
            newline = "\n"

        # available exits
        self.private(player, f"{self.exits(room)}", f"{newline}", "\n")

        self.cmd_prompt(player)

    def spawn(self, player: str):

        self.private(player,
                     f"You arrive at the office, to begin your shift...", "", "\n")

        self._local(clients[player]['current_rm'],
                    f"{clients[player]['name']} arrives to work.", "\r", "\n", player)

        self.room_desc(player, clients[player]['current_rm'])


class Session(Thread, Action):

    def __init__(self, socket, address: tuple):

        Thread.__init__(self)
        Action.__init__(self)

        self.socket = socket
        self.address = address
        self.player = str(self.address)

    def run(self):

        lock.acquire()
        clients[self.player] = {
            'session': self, 'name': f"Employee {randint(1, 100)}", 'current_rm': 1}
        lock.release()

        print(
            f"{self.timestamp} ({self.address[0]}) {cyan}{clients[self.player]['name']}{decolor} <CONNECTED>")

        self.motd(self.player)
        self.spawn(self.player)

        connected = True

        while connected and self.player in clients.keys():
            try:
                data = self.socket.recv(1024)
            except OSError:
                break

            if not data:
                # client connection remotely terminated
                break

            if isinstance(data, bytes):
                data = data.decode('utf-8').rstrip()
                if "\x04" not in data:
                    print(
                        f"{self.timestamp} ({self.address[0]}) {cyan}{clients[self.player]['name']}{decolor} '{data}'")

                    user_input = data
                    valid_command = False

                    # check player command against known aliases/commands
                    for key, value in self.commands.items():
                        if " " in user_input:
                            if user_input[:user_input.index(" ")] in value['aliases']:
                                valid_command = True
                                self.commands[str(key)]['command'](
                                    self.player, user_input)
                        else:
                            if user_input in value['aliases']:
                                valid_command = True
                                if user_input in self.commands['quit']['aliases']:
                                    connected = False
                                self.commands[str(key)]['command'](
                                    self.player, user_input)

                    if not valid_command:
                        self.cmd_prompt(self.player)

        if self.player in clients.keys():
            self.socket.close()

            self._local(clients[self.player]['current_rm'],
                        f"{clients[self.player]['name']} clocks out and leaves the office.", "\r", "\n", str(self.address))

            print(
                f"{self.timestamp} ({self.address[0]}) {cyan}{clients[self.player]['name']}{decolor} <DISCONNECTED>")

            lock.acquire()
            clients.pop(self.player, None)
            lock.release()


class Server(Dice, Output, Ticker):

    def __init__(self):

        # super().__init__()

        self.HOST = ''
        self.PORT = 51234

        self.server_running = False

    def listen(self):

        print(
            f"{self.timestamp} {green}SERVER{decolor}: LISTENING ON PORT {white}{bold}{self.PORT}{unbold}{decolor}")

        while True:
            try:
                client, addr = self.server_socket.accept()
                Session(client, addr).start()
            except OSError:
                break

    def load_state(self):

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: LOADING OFFICE MAP...")

        if path.exists(f"{path.dirname(__file__)}/config/office_map.json"):
            with open(f"{path.dirname(__file__)}/config/office_map.json", 'r') as json_file:
                try:
                    Resources.office = load(json_file)
                except ValueError:
                    print(
                        f"{self.timestamp} {red}ERROR{decolor}: OFFICE MAP FAILED TO LOAD!")
                    print(
                        f"{self.timestamp} {blue}SERVER{decolor}: GENERATING DEFAULT MAP...")

            # JSON format wraps room number keys in double-quotes and our game
            # then thinks they are strings (not int) -- this solves that
            old_office = list(Resources.office.items())
            Resources.office.clear()
            for key, value in old_office:
                Resources.office[int(key)] = value

            print(
                f"{self.timestamp} {green}SERVER{decolor}: {bold}{white}{len(Resources.office.keys())}{unbold}{decolor} ROOMS LOADED SUCCESSFULLY")

            # if path.exists('save'):
            #     with open('save', 'r') as json_file:
            #         try:
            #             self.player = load(json_file)
            #         except ValueError:
            #             pass
        else:
            print(
                f"{self.timestamp} {red}ERROR{decolor}: OFFICE MAP FAILED TO LOAD")
            print(
                f"{self.timestamp} {blue}SERVER{decolor}: GENERATING DEFAULT MAP...")

    def run(self):

        while True:
            user_input = input().lower()

            if user_input == "start" and not self.server_running:
                self.server_socket = socket.socket(
                    socket.AF_INET, socket.SOCK_STREAM)
                self.server_socket.setsockopt(
                    socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                self.server_socket.bind(
                    (socket.gethostbyname('localhost'), self.PORT))
                self.server_socket.listen(4)

                self.server_running = True

                startthread = Thread(
                    target=self.start_server, args=[])
                startthread.start()
            elif user_input == "start" and self.server_running:
                print(
                    f"{self.timestamp} {yellow}ALERT{decolor}: SERVER ALREADY RUNNING")

            if user_input == "stop" and self.server_running:
                self.server_running = False

                self.stop_server()

            elif user_input == "stop" and not self.server_running:
                print(
                    f"{self.timestamp} {yellow}ALERT{decolor}: NO SERVER CURRENTLY RUNNING")

    def save_state(self):

        pass

        # with open('save', 'w') as outfile:
        #     dump(self.player, outfile)

    def start_server(self):

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: INITIALIZING...")

        self.load_state()

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: STARTING TICK TIMERS...")

        self.tick_2s = Ticker()
        self.tick_2s._start(2, self.tick)
        self.tick_6s = Ticker()
        self.tick_6s._start(6, self.tick)

        self.listen()

    def stop_server(self):

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: STOPPING SERVER...")

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: DISCONNECTING {white}{bold}{len(clients.keys())}{unbold}{decolor} PLAYERS...")

        lock.acquire()

        for player in clients.keys():
            self.private(
                player, f"{red}THE SERVER IS SHUTTING DOWN{decolor}", "\r", "\n")
            self.private(
                player, f"YOUR PROGRESS WILL BE SAVED", "", "\n")
            self.private(
                player, f"{white}{bold}GOODBYE{unbold}{decolor}", "\n", "\n\n")

            clients[player]['session'].socket.close()

        clients.clear()

        lock.release()

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: STOPPING TICK TIMERS...")
        self.tick_2s._stop()
        self.tick_6s._stop()

        print(
            f"{self.timestamp} {blue}SERVER{decolor}: CLOSING SOCKET...")

        self.server_socket.close()

        print(
            f"{self.timestamp} {green}SERVER{decolor}: SERVER IS OFFLINE")

        # self.save_state()

    def tick(self, interval: int):

        # 2s tick
        if interval == 2:

            # NPC rolls
            for key in Resources.npc.keys():

                # NPC movement
                if self.roll(Resources.npc[key]['move_die'][0],
                             Resources.npc[key]['move_die'][1]):

                    # randomly choose an adjacent room
                    try:
                        room_choice = choice(tuple(Resources.office[
                            Resources.npc[key]['current_room']]['exits'].values()))

                        if room_choice in Resources.npc[key]['allowed_rooms']:
                            # verified within NPC's allowed path
                            for direction, num in Resources.office[Resources.npc[key]['current_room']]['exits'].items():
                                if room_choice == num:
                                    self._local(Resources.npc[key]['current_room'],
                                                f"{key} left to the {direction}.", "\r", "\n")

                            # update NPC's current room
                            Resources.npc[key]['current_room'] = room_choice

                            # locally echo NPC entry
                            self._local(room_choice,
                                        f"{key} enters the room.", "\r", "\n")

                    except KeyError:
                        print(
                            f"{self.timestamp} {red}ERROR{decolor}: NPC {bold}{key}{unbold} MOVEMENT ROLL FAILED")

        # 6s tick
        if interval == 6:

            # NPC rolls
            for key in Resources.npc.keys():

                # NPC speech (phrases)
                if self.roll(Resources.npc[key]['phrase_die'][0],
                             Resources.npc[key]['phrase_die'][1]):

                    phrase_choice = choice(Resources.npc[key]['phrases'])

                    self._local(Resources.npc[key]['current_room'],
                                f"{key} {phrase_choice}", "\r", "\n")


if __name__ == '__main__':

    system('clear')

    logo = \
        f" {cyan}╒════════════════════════════════════════════════════════════════════════════╕\n" \
        f" {cyan}│    {white}____ ____                                                               {cyan}│\n" \
        f" {cyan}│   {white}||O |||C ||{red}▒╗   ███╗██╗   ██╗██████╗                                     {cyan}│\n" \
        f" {cyan}│   {white}||__|||__||{red}▒█╗ ████║██║   ██║██╔══██╗                                    {cyan}│\n" \
        f" {cyan}│   {white}|/__\\|/__\\|{red}╔████╔██║██║   ██║██║  ██║   {white}____ ____ ____ ____ ____ ____    {cyan}│\n" \
        f" {cyan}│            {red}▒▒║╚██╔╝██║██║   ██║██║  ██║  {white}||S |||E |||R |||V |||E |||R ||   {cyan}│\n" \
        f" {cyan}│            {red}██║ ╚═╝ ██║╚██████╔╝██████╔╝  {white}||__|||__|||__|||__|||__|||__||   {cyan}│\n" \
        f" {cyan}│            {red}╚═╝     ╚═╝ ╚═════╝ ╚═════╝   {white}|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|   {cyan}│\n" \
        f" {cyan}│                                                                            │\n" \
        f" {cyan}╞════════════════════════════════════════════════════════════════════════════╡\n" \
        f" {cyan}│                                                                            │\n" \
        f" {cyan}│{decolor}  ver        {bold}{white}1.0{unbold}                                                            {cyan}│\n" \
        f" {cyan}│{decolor}  author     {bold}{white}Jay Snyder{unbold}                                                     {cyan}│\n" \
        f" {cyan}│{decolor}  ~          {bold}{white}https://github.com/heru-ra/{unbold}                                    {cyan}│\n" \
        f" {cyan}│                                                                            │\n" \
        f" {cyan}╞════════════════════════════════════════════════════════════════════════════╡\n" \
        f" {cyan}│                                                                            │\n" \
        f" {cyan}│{decolor}  * Type {bold}{green}start{decolor}{unbold} to start the server                                          {cyan}│\n" \
        f" {cyan}│{decolor}  * Once started, type {bold}{red}stop{decolor}{unbold} to shutdown                                     {cyan}│\n" \
        f" {cyan}│{decolor}  * For a list of more commands, type {bold}{blue}help{decolor}{unbold}                                  {cyan}│\n" \
        f" {cyan}│                                                                            │\n" \
        f" {cyan}╘════════════════════════════════════════════════════════════════════════════╛{decolor}\n"

    print(logo)

    Server().run()
