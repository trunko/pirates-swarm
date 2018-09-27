# This is where you build your AI for the Pirates game.

from joueur.base_ai import BaseAI
from colorama import init, Fore, Back, Style
from sys import platform
import os

# <<-- Creer-Merge: imports -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
# you can add additional import(s) here
# <<-- /Creer-Merge: imports -->>

class AI(BaseAI):
    """ The basic AI functions that are the same between games. """

    def get_name(self):
        """ This is the name you send to the server so your AI will control the player named this string.

        Returns
            str: The name of your Player.
        """
        # <<-- Creer-Merge: get-name -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        return "The Senate" # REPLACE THIS WITH YOUR TEAM NAME
        # <<-- /Creer-Merge: get-name -->>

    def start(self):
        """ This is called once the game starts and your AI knows its playerID and game. You can initialize your AI here.
        """
        # <<-- Creer-Merge: start -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        init()
        os.system('clear')
        self.display_map()
        # <<-- /Creer-Merge: start -->>

    def game_updated(self):
        """ This is called every time the game's state updates, so if you are tracking anything you can update it here.
        """
        # <<-- Creer-Merge: game-updated -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        self.display_map()
        # <<-- /Creer-Merge: game-updated -->>

    def end(self, won, reason):
        """ This is called when the game ends, you can clean up your data and dump files here if need be.

        Args:
            won (bool): True means you won, False means you lost.
            reason (str): The human readable string explaining why you won or lost.
        """
        # <<-- Creer-Merge: end -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        os.system('clear')
        self.display_map()
        if won:
            print(Fore.GREEN + '\nI Won!')
            print('Reason: ' + reason + '\n' + Fore.RESET)
        else:
            print(Fore.RED + '\nI Lost!')
            print('Reason: ' + reason + '\n' + Fore.RESET)

        # <<-- /Creer-Merge: end -->>
    def run_turn(self):
        """ This is called every time it is this AI.player's turn.

        Returns:
            bool: Represents if you want to end your turn. True means end your turn, False means to keep your turn going and re-call this function.
        """
        # <<-- Creer-Merge: runTurn -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
        # Put your game logic here for runTurn
        targets = {}

        if self.player.gold >= 800 and self.player.port.tile.unit is None:
            # Spawn a crew if we have the money and there isn't one already
            self.player.port.spawn("crew")
        elif self.player.port.tile.unit is not None and self.player.port.tile.unit.ship_health == 0 and self.player.gold >= 600:
            # Spawn a ship so our crew can sail
            self.player.port.spawn("ship")
        
        for unit in self.player.units:
            if unit.tile is not None:
                if unit.tile == self.player.port.tile and unit.ship_health < self.game.ship_health:
                    unit.rest()
                elif unit._ship_health < self.game._ship_health / 2.0 or unit.gold >= 800:
                    # Heal our unit if the ship is almost dead

                    # Find a path to our port so we can heal
                    path = self.a_star(unit.tile, self.player.port.tile, unit)
                    while unit.moves > 0:
                        if len(path) > 0:
                            # Make sure the port is empty before moving
                            if self.player.port.tile.unit is not None:
                                break
                            # Move along the path if there is one
                            unit.move(path.pop(0))
                        else:
                            # Try to deposit any gold we have while we're here
                            if unit.gold > 0:
                                unit.deposit()
                            # Try to rest
                            unit.rest()
                            break
                else:
                    # Look for the closest ship to attack
                    targets[unit] = None
                    for u in self.game.units:
                        if targets[unit] is None and u._target_port is not None:
                            # Found a merchant ship
                            distance = self.distance(unit.tile, u.tile)
                            if distance is not None and targets[unit] is None:
                                targets[unit] = u
                            elif distance is not None and distance < self.distance(unit.tile, targets[unit].tile) and u not in targets.values():
                                targets[unit] = u
                        elif targets[unit] is None and u.owner == self.player.opponent and u.ship_health <= unit.ship_health and u.tile != self.player.opponent.port.tile:
                            # Found an enemy ship
                            distance = self.distance(unit.tile, u.tile)
                            if distance is not None and targets[unit] is None:
                                targets[unit] = u
                            elif distance is not None and distance < self.distance(unit.tile, targets[unit].tile) and u not in targets.values():
                                targets[unit] = u

                    # If we found a target, move to it, then attack it
                    if targets[unit] is not None:
                        path = self.a_star(unit.tile, targets[unit].tile, unit)
                        # Find a path to this unit's target
                        while unit.moves > 0:
                            if len(path) > 0 and self.distance(unit.tile, targets[unit].tile) > self.game._ship_range:
                                # Move until we're within firing range of the target
                                unit.move(path.pop(0))
                            elif self.distance(unit.tile, targets[unit].tile) <= self.game._ship_range:
                                # Try to attack the ship and break
                                unit.attack(targets[unit].tile, "ship")
                                break
                            else:
                                # If path is not available, just break
                                break

        return True
        # <<-- /Creer-Merge: runTurn -->>

    def find_path(self, start, goal, unit):
        """A very basic path finding algorithm (Breadth First Search) that when given a starting Tile, will return a valid path to the goal Tile.
        Args:
            start (Tile): the starting Tile
            goal (Tile): the goal Tile
            unit (Unit): the Unit that will move
        Returns:
            list[Tile]: A list of Tiles representing the path, the the first element being a valid adjacent Tile to the start, and the last element being the goal.
        """

        if start == goal:
            # no need to make a path to here...
            return []

        # queue of the tiles that will have their neighbors searched for 'goal'
        fringe = []

        # How we got to each tile that went into the fringe.
        came_from = {}

        # Enqueue start as the first tile to have its neighbors searched.
        fringe.append(start)

        # keep exploring neighbors of neighbors... until there are no more.
        while len(fringe) > 0:
            # the tile we are currently exploring.
            inspect = fringe.pop(0)

            # cycle through the tile's neighbors.
            for neighbor in inspect.get_neighbors():
                # if we found the goal, we have the path!
                if neighbor == goal:
                    # Follow the path backward to the start from the goal and return it.
                    path = [goal]

                    # Starting at the tile we are currently at, insert them retracing our steps till we get to the starting tile
                    while inspect != start:
                        path.insert(0, inspect)
                        inspect = came_from[inspect.id]
                    return path
                # else we did not find the goal, so enqueue this tile's neighbors to be inspected

                # if the tile exists, has not been explored or added to the fringe yet, and it is pathable
                if neighbor and neighbor.id not in came_from and neighbor.is_pathable(unit):
                    # add it to the tiles to be explored and add where it came from for path reconstruction.
                    fringe.append(neighbor)
                    came_from[neighbor.id] = inspect

        # if you're here, that means that there was not a path to get to where you want to go.
        #   in that case, we'll just return an empty path.
        return []

    # <<-- Creer-Merge: functions -->> - Code you add between this comment and the end comment will be preserved between Creer re-runs.
    # if you need additional functions for your AI you can add them here
    def a_star(self, start, goal, unit):
        if start == goal:
            return []

        frontier = []
        explored = []

        came_from = {}
        path_cost = {}

        frontier.append(start)
        path_cost[start] = 0

        while len(frontier) > 0:
            inspect = None
            for tile in frontier:
                if inspect is None:
                    inspect = tile
                elif (self.distance(tile, goal) + path_cost[tile]) < (self.distance(inspect, goal) + path_cost[inspect]):
                    inspect = tile
                
            frontier.remove(inspect)
            explored.append(inspect)

            for neighbor in inspect.get_neighbors():
                if neighbor == goal:
                    path = [goal]

                    step = inspect
                    while step != start:
                        path.insert(0, step)
                        step = came_from[step]

                    return path

                if neighbor is not None:
                    if neighbor not in explored and neighbor not in frontier and neighbor.is_pathable(unit):
                        frontier.append(neighbor)
                        came_from[neighbor] = inspect
                        path_cost[neighbor] = path_cost[inspect] + 1
        
        return []

    def distance(self, t1, t2):
        if t1 is not None and t2 is not None:
            return abs(t1.x - t2.x) + abs(t1.y - t2.y)
        else:
            return None

    def display_map(self):
        print('\033[0;0H', end='')

        for y in range(0, self.game.map_height):
            print(' ', end='')
            for x in range(0, self.game.map_width):
                t = self.game.tiles[y * self.game.map_width + x]

                if t.port != None:
                    if t.port.owner == self.player:
                        print(Back.GREEN, end='')
                    elif t.port.owner == self.player.opponent:
                        print(Back.RED, end='')
                    else:
                        print(Back.MAGENTA, end='')
                elif t.type == 'land':
                    print(Back.YELLOW, end='')
                else:
                    print(Back.CYAN, end='')

                foreground = ' '
                print(Fore.WHITE, end='')

                if t.unit != None:
                    if t.unit.owner == self.player:
                        print(Fore.GREEN, end='')
                    elif t.unit.owner == self.player.opponent:
                        print(Fore.RED, end='')
                    else:
                        print(Fore.MAGENTA, end='')

                    if t.unit.ship_health > 0:
                        foreground = 'S'
                    else:
                        foreground = 'C'
                elif t.gold > 0:
                    print(Fore.BLACK, end='')
                    foreground = '$'

                print(foreground + Fore.RESET + Back.RESET, end='')

            if y < 10:
                print(' 0' + str(y))
            else:
                print(' ' + str(y))

        print('\nTurn: ' + str(self.game.current_turn) + ' / ' \
                + str(self.game.max_turns))
        print(Fore.GREEN + 'Infamy: ' + str(self.player.infamy) \
                + '\tGold: ' + str(self.player.gold) + Fore.RESET)
        print(Fore.RED + 'Infamy: ' + str(self.player.opponent.infamy) \
                + '\tGold: ' + str(self.player.opponent.gold) + Fore.RESET)

        return
    # <<-- /Creer-Merge: functions -->>
