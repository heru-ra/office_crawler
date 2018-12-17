from json import load, loads, dump
from os import system, path
from random import randint, choice
from textwrap import TextWrapper as textwrapper, fill
from threading import Timer as timer, Thread, Event


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


class Resources:

    prompt = f"\n> "

    player = {
        'name': "Employee",
        'current_rm': 1,
    }

    # if you spawn in this office/room, it means your office_map file is
    # missing or incorrectly formatted
    office = {
        1: {'name': "In a Dream State",
            'exits': {'north': None, 'south': None, 'west': None, 'east': None},
            'desc': "Your mind is blank, but carefree. You're in a warm, " +
            "happy place... Wait, did you sleep through your alarm?"
            },
    }

    npc = {
        'Jay': {'prefix': "",
                'desc': "sits at his desk, coding.",
                'look': "He's very smart and handsome. You are filled with " +
                "an overwhelming desire to be his friend.",
                'current_room': 6,
                'allowed_rooms': (6, 7, 29, 51, 73, 74, 52, 30, 31, 32, 33, 34, 35),
                'move_die': (20, 20),
                'phrases': (
                    "tells you a really lame dad joke.",
                    "glances at you out of the corner of his eye.",
                    "mumbles, \"There's got to be a better way to do this...\""
                ),
                'phrase_die': (20, 20),
                },
    }


class Dice:

    def roll(self, sides: int, mod: int):

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


class Output(Resources):

    def local(self, room: int, msg: str):

        # local (same-room) echoes
        if room == self.player['current_rm']:
            print(f"\r{self.wordwrap(msg)}")
            print(self.prompt, end='')

    def motd(self):

        print(
            f"                     ____ ____ ____ ____ ____ ____\n" +
            f"                    ||O |||F |||F |||I |||C |||E ||\n" +
            f"                    ||__|||__|||__|||__|||__|||__||\n" +
            f"                    |/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|\n" +
            f"                       ____ ____ ____ ____ ____ ____ ____\n" +
            f"                      ||C |||R |||A |||W |||L |||E |||R ||\n" +
            f"                      ||__|||__|||__|||__|||__|||__|||__||\n" +
            f"                      |/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|/__\\|\n\n" +
            f"              {yellow}a MUD-like, rogue-like, dungeon-crawler-esque game{decolor}\n\n" +
            f"------------------------------------------------------------------------------\n"
        )

    def private(self, msg: str):

        # non-room dependant messages
        print(f"\n{self.wordwrap(msg)}")

    def wordwrap(self, string: str):

        # wrap our print output at 80 char
        wrapper = textwrapper(
            width=80, replace_whitespace=False, drop_whitespace=True)

        return wrapper.fill(text=string)


class Action(Output):

    def __init__(self):

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

    def debug(self, cmd_line: str):

        pass

    def exits(self, room: int, long: bool = False):

        total_exits = None

        if not long:
            # concatenate available exits
            for key in self.office[room]['exits']:
                if self.office[room]['exits'][key]:
                    if not total_exits:
                        total_exits = f"{key}"
                    else:
                        total_exits = f"{total_exits}, {key}"

            # pluralize exit/s
            if len(self.office[room]['exits']) > 1:
                exit_plural = "Exits"
            else:
                exit_plural = "Exit"

            return f"{green}{exit_plural}:{decolor} {total_exits}"

    def _help(self, cmd_line: str):

        self.private(
            f"{bold}Available Commands:{unbold}")

        self.private(
            f"  north\n  south\n  east\n  west\n  look [direction or npc]\n  quit")

    def look(self, cmd_line: str):

        if " " in cmd_line:

            result = False

            cmd_line = cmd_line[cmd_line.index(" ")+1:]

            cmd_line = next((key for key, value in self.directions.items()
                             if cmd_line in value), cmd_line)

            # look <direction>
            if cmd_line in self.office[self.player['current_rm']]['exits'] and \
                    self.office[self.player['current_rm']]['exits'][cmd_line]:
                result = True

                room = self.office[self.player['current_rm']
                                   ]['exits'][str(cmd_line)]
                direction = cmd_line

                self.private(
                    f"To the {direction} you see:")

                self.private(
                    f"  {blue}{self.office[room]['name']}{decolor}")

                for key in self.npc.keys():
                    if room == self.npc[key]['current_room']:
                        self.private(
                            f"  {cyan}{key} {self.npc[key]['desc']}" +
                            f"{decolor}")

            # look <NPC>
            for key in self.npc.keys():
                if cmd_line in str(key).lower() and \
                        self.npc[key]['current_room'] == \
                        self.player['current_rm']:

                    result = True

                    self.private(f"  {self.npc[key]['look']}")

            # no valid look target
            if not result:
                self.private(
                    f"You see nothing.")

        else:
            self.room_desc(self.player['current_rm'])

    def _map(self, cmd_line: str):

        if " " in cmd_line:
            cmd_line = cmd_line[cmd_line.index(" ")+1:]

        map_width = 22
        line1 = line2 = line3 = ""
        room = self.player['current_rm']
        default_drawing = {
            'nw': f"┼", 'n': f"───", 'ne': f"┼",
            'w': f"│", 'c': "   ", 'e': f"│",
            'sw': f"┼", 's': f"───", 'se': f"┼"
        }

        self.drawing = dict(default_drawing)

        for room in self.office.keys():
            if cmd_line == "num":
                self.drawing['c'] = str(room).zfill(3)

            for wall, num in self.office[room]['exits'].items():
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

            if room == self.player['current_rm']:
                self.drawing['c'] = f"{red}YOU{decolor}"

            if 'regions' in self.office[room]:
                for num in self.office[room]['regions']:
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
                print(f"\033[F{line1}\n{line2}\n{line3}")
                line1 = line2 = line3 = ""

    def move(self, cmd_line: str):

        cmd_line = next(key for key, value in self.directions.items()
                        if cmd_line in value)

        # if direction leads to adjacent room, move player
        if cmd_line in self.office[self.player['current_rm']]['exits'] and \
                self.office[self.player['current_rm']]['exits'][cmd_line]:
            self.player['current_rm'] = self.office[self.player['current_rm']
                                                    ]['exits'][cmd_line]
            self.room_desc(self.player['current_rm'])
        else:
            self.private(
                f"You cannot move that direction.")

    def quit(self, cmd_line: str):

        self.private(
            f"You log your hours and leave the office...")
        print(f"\n")

        exit()

    def room_desc(self, room: int):

        self.private(f"{blue}{self.office[room]['name']}{decolor}")

        self.private(f"  {self.office[room]['desc']}")

        # present NPCs
        for key in self.npc.keys():
            if room == self.npc[key]['current_room']:
                self.private(
                    f"{cyan}{key} {self.npc[key]['desc']}{decolor}")

        # available exits
        self.private(f"{self.exits(room)}")

    def spawn(self, start_rm: int = 1):

        self.player['current_rm'] = start_rm

        self.private(
            f"You arrive at your office, to begin your shift...")

        self.room_desc(self.player['current_rm'])


class Game(Action, Dice, Ticker, Resources):

    def __init__(self):

        super().__init__()

    def listen(self):

        while True:
            user_input = input(self.prompt).lower()

            # check player command against known aliases/commands
            for key, value in self.commands.items():
                if " " in user_input:
                    if user_input[:user_input.index(" ")] in value['aliases']:
                        self.commands[str(key)]['command'](user_input)
                else:
                    if user_input in value['aliases']:
                        if user_input in self.commands['quit']['aliases']:
                            self.quit_game()
                        self.commands[str(key)]['command'](user_input)

    def load_state(self):

        if path.exists('save'):
            with open('save', 'r') as json_file:
                try:
                    self.player = load(json_file)
                except ValueError:
                    pass

        if path.exists('office_map'):
            with open('office_map', 'r') as json_file:
                try:
                    self.office = load(json_file)
                except ValueError:
                    pass

            # JSON format wraps room number keys in double-quotes and our game
            # then thinks they are strings (not int) -- this solves that
            old_office = list(self.office.items())
            self.office.clear()
            for key, value in old_office:
                self.office[int(key)] = value

    def new_game(self):

        system('clear')

        self.load_state()
        self.motd()
        self.spawn(self.player['current_rm'])

        self.tick_2s = Ticker()
        self.tick_2s._start(2, self.tick)

        self.tick_6s = Ticker()
        self.tick_6s._start(6, self.tick)

        self.listen()

    def save_state(self):

        with open('save', 'w') as outfile:
            dump(self.player, outfile)

    def tick(self, interval: int):

        # 2s tick
        if interval == 2:

            # NPC rolls
            for key in self.npc.keys():

                # NPC movement
                if self.roll(self.npc[key]['move_die'][0],
                             self.npc[key]['move_die'][1]):

                    # randomly choose an adjacent room
                    room_choice = choice(tuple(self.office[
                        self.npc[key]['current_room']]['exits'].values()))

                    if room_choice in self.npc[key]['allowed_rooms']:
                        # verified within NPC's allowed path
                        for direction, num in self.office[self.player[
                                'current_rm']]['exits'].items():

                            if room_choice == num:
                                self.local(self.npc[key]['current_room'],
                                           f"{key} left to the {direction}.")

                        # update NPC's current room
                        self.npc[key]['current_room'] = room_choice

                        # locally echo NPC entry
                        self.local(self.npc[key]['current_room'],
                                   f"{key} enters the room.")

        # 6s tick
        if interval == 6:

            # NPC rolls
            for key in self.npc.keys():

                # NPC speech (phrases)
                if self.roll(self.npc[key]['phrase_die'][0],
                             self.npc[key]['phrase_die'][1]):

                    phrase_choice = choice(self.npc[key]['phrases'])

                    self.local(self.npc[key]['current_room'],
                               f"{key} {phrase_choice}")

    def quit_game(self):

        self.tick_2s._stop()
        self.tick_6s._stop()
        self.save_state()


if __name__ == '__main__':

    Game().new_game()
