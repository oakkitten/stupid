# This work is free. You can redistribute it and/or modify it under the
# terms of the Do What The Fuck You Want To Public License, Version 2,
# as published by Sam Hocevar. See http://www.wtfpl.net/ for more details.

# This is a stupid game written in python and about python
# It currently has 3 stupid levels, latter levels demand knowledge of certain aspects of Python

import sys
from codeop import CommandCompiler
from code import InteractiveInterpreter, softspace

try: import readline
except: pass

# bass class for game objects. doctstring are to be printedw
class Game: pass

# loc/loc2 are placeholder classes for REPL's locals and hidden locals
# docs hold docstrings for objects that don't do them (generators etc)
class Loc: pass
loc, loc2 = Loc(), Loc()
docs = {}

GREEN, END, YELLOW, RED, BLUE = "\033[92m", "\033[0m", "\033[93m", "\033[91m", "\033[94m"

# colors & prints actions (et al)
def f(text, color=GREEN):
    print color + text + END

# colors & returns the objects
def r(text, color=YELLOW):
    return color + text + END

#############################################################################
#############################################################################
#############################################################################

class Interactor(InteractiveInterpreter):
    def __init__(self):
        self.compile = CommandCompiler()

    def interact(self):
        while True:
            try:
                line = raw_input("\n> ")
            except (EOFError, KeyboardInterrupt):
                print
                return

            if not line:
                continue

            try:
                try: code = self.compile(line, "<game>", "eval")
                except SyntaxError: code = self.compile(line, "<game>")
            except (OverflowError, SyntaxError, ValueError):
                self.showsyntaxerror("<game>")
                continue
            
            try:
                res = eval(code, {}, loc.__dict__)
            except SystemExit:
                raise
            except:
                self.showtraceback()
                continue
            else:
                if softspace(sys.stdout, 0):
                    print

            try:
                if res in docs:
                    print r(docs[res])
                elif isinstance(res, Game):
                    print r(res.__doc__)
            except:
                pass

            if res:
                print repr(res)
                loc._ = res

#############################################################################
#############################################################################
#############################################################################

def get_out_of_the_room():
    class Key(Game):
        "A tiny metal key"

    class Knob(Game):
        "A knob with a keyhole"
        def insert_key(self, key):
            if isinstance(key, Key):
                self.key = key
                f("The key slides smoothly into the slot")
            else:
                f("Cannot insert that in the slot")
        def turn_key(self):
            try:
                self.key
            except:
                f("The knob won't turn")
            else:
                self.key = [self.key]
                f("The key turns")

    class Door(Game):
        "A wooden door with a knob"
        def push(self):
            try:
                self.knob.key[0]
            except:
                f("The door won't move an inch")
            else:
                f("You are out!")
                nextlevel()
        def pull(self):
            f("The door won't move")

    class Floor(Game):
        "Wooden floor that is a bit dirty"

    class Room(Game):
        "A room that has one door. Something is glittering on the floor"

    room = Room()
    room.door = Door()
    room.door.knob = Knob()
    room.floor = Floor()
    room.floor.key = Key()
    loc.room = room
    f("\nLevel 0", color=RED)
    f("You find yourself in a room full of shadows. You have to get out...")
    f("Available identifiers: " + r("room"))

#############################################################################

def escape_the_demon():
    class Freedom(Game):
        "The power or right to act, speak, or think as one wants without hindrance or restraint"

    class USA(Freedom):
        "The most influential country in the world.\nIt is based on freedom."

    class Corridor(Game, object):
        "A narrow corridor. A wild demon floats in the air, obstructing your way"

        def _n_fget(self):
            if loc2.free:
                f("""The demon is free already""")
            else:
                f("""As you try to approach the creature, it speaks to you.\n"I've been enslaved in this corridor since the dawn of the world. Plase, *set* me free. Then I can be removed from your way.\"""")
            return loc2.demon

        def _n_fset(self, value):
            if loc2.free:
                f("""The demon is free already""")
            elif isinstance(value, USA) or value == USA:
                f("""As you approach the creature, it says, "It smells right, but it's not quite the freedom I'm looking for\"""")
            elif isinstance(value, Freedom) or value == Freedom:
                loc2.free = True
                f("""The demon thanks you, "I'm free now. You can remove me from your way now.\"""")
            else:
                f("""Angry demon pouts. "What is this? It's not it!\"""")

        def _n_fdel(self):
            if loc2.free:
                f("The demon vanishes into the darkness. You can go further!")
                nextlevel()
            else:
                f("""The demon croaks, "I am not free yet"\"""")

        demon = property(_n_fget, _n_fset, _n_fdel, "A wild creature obstructing your way")


    class Demon(Game):
        "A wild creature who is obstructing your way"
        
    loc.usa = USA()
    loc.corridor = Corridor()
    loc2.free = False
    loc2.demon = Demon()
    docs[Freedom] = Freedom.__doc__
    f("\nLevel 1", color=RED)
    f("As you exit the door and stand in a narrow corridor, you see a wild apparition right in front of you. It seems that it wants to tell you something...")
    f("Available identifiers: " + r("corridor usa"))

#############################################################################

def start_the_generator():
    class Fuel(Game):
        """A bit of liquid smelling like gasoline"""

    def canister():
        for x in range(0, 3):
            yield Fuel()
        f("Canister is empty now")

    class Electricity(Game):
        """Something that could light up a bulb or two"""
        def __init__(self):
            if loc2.switchposition=="on":
                f("Ka-boom! There's a small explosion, and the generator goes down. Did you forget to turn the switch off?")
                loc2.power = False
                raise StopIteration
            else:
                f("The generator roars to life!")
                loc2.power = True
        def lick(self):
            f("You die while licking the wire that comes from the generator. What were you thinking?!")
            raise RuntimeError

    class Switch(Game):
        """A switch on the wall\nIt's written under it, \"Don't power on the generator when the switch is on\""""
        def __init__(self):
            loc2.switchposition = "on"
        def switch(self):
            if loc2.power:
                f("The lights go up!")
                nextlevel()
            else:
                loc2.switchposition = "on" if loc2.switchposition=="off" else "off"
                f("Nothing happens when you flick the switch. The switch is %s now." % loc2.switchposition)

    def generator():
        try:
            for sound in ["phut", "burp", "thump", "whop", "puff"]:
                fuel = yield sound
                if fuel:
                    if isinstance(fuel, Fuel):
                        yield Electricity()
                        return
                    else:
                        f("Engine chokes on something that doesn't appear to be fuel")
            f("Engine stops forever")
        except KeyboardInterrupt:
            f("\nYou kicked at the generator and broke it.")
            yield Exception()


    loc2.power = False
    loc2.switchposition = "on"

    loc.generator = generator()
    docs[loc.generator] = """Old electric generator that works on gasoline. It has no gas, so it's not working.\nBe careful with it: if you try too hard, you will break it"""
    loc.canister = canister()
    docs[loc.canister] = """A canister. It yields something"""
    loc.switch = Switch()
    f("\nLevel 2", color=RED)
    f("You come out of the shadowy room into utter darkness. The only two thigs you can see is a big electric generator and a red canister beside it. There is a wire attached to the generator, it is connected to the switch on the wall. Maybe you can get yourself some light?..")
    f("Available identifiers: " + r("generator canister switch"))

#############################################################################
#############################################################################
#############################################################################

flow = (level for level in [get_out_of_the_room, escape_the_demon, start_the_generator])

def nextlevel():
    global loc, loc2
    try:
        loc, loc2 = Loc(), Loc()
        loc.restart = next(flow)
        loc.restart()
    except StopIteration:
        f("\nCongratulations! You completed all the levels of the game.\nThat's it, really.")
        raise SystemExit

# the next function is a cheat, but it's not likely the player learns about it unless he reads the source
__builtins__.nextlevel = nextlevel
__builtins__.d = lambda *obj: [x for x in dir(*obj) if not x.startswith("_")]

#############################################################################

if __name__ == "__main__":
    f("""Welcome to the python game! A stupid game written in python and about python.\n\n{2}WARNING: This is essentially a python shell and you can potentially damage stuff if you execute dangerous code.{0}\n\nIn this shell, if what you type results in a game object, that object's docstring will be printed in yellow color.\nType {1}restart(){0} to restart current level.\nFunction {1}d(){0} behaves exectly like {1}dir(){0} except it doesn't include underscored stuff.\nRemember that {1}_{0} represents the result of previous expression""".format(GREEN, YELLOW, RED))
    nextlevel()
    f("Good luck!")
    Interactor().interact()
