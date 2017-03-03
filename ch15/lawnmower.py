# File: lawnmower.py
#    from chapter 15 of _Genetic Algorithms with Python_
#
# Author: Clinton Sheppard <fluentcoder@gmail.com>
# Copyright (c) 2016 Clinton Sheppard
#
# Licensed under the Apache License, Version 2.0 (the "License").
# You may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or
# implied.  See the License for the specific language governing
# permissions and limitations under the License.

from enum import Enum


class FieldContents(Enum):
    Grass = ' #'
    Mowed = ' .'
    Mower = 'M'

    def __str__(self):
        return self.value


class Direction:
    def __init__(self, index, xOffset, yOffset, symbol):
        self.Index = index
        self.XOffset = xOffset
        self.YOffset = yOffset
        self.Symbol = symbol

    def move_from(self, location, distance=1):
        return Location(location.X + distance * self.XOffset,
                        location.Y + distance * self.YOffset)


class Directions(Enum):
    North = Direction(0, 0, -1, '^')
    East = Direction(1, 1, 0, '>')
    South = Direction(2, 0, 1, 'v')
    West = Direction(3, -1, 0, '<')

    @staticmethod
    def get_direction_after_turn_left_90_degrees(direction):
        newIndex = direction.Index - 1 \
            if direction.Index > 0 \
            else len(Directions) - 1
        newDirection = next(i for i in Directions
                            if i.value.Index == newIndex)
        return newDirection.value

    @staticmethod
    def get_direction_after_turn_right_90_degrees(direction):
        newIndex = direction.Index + 1 \
            if direction.Index < len(Directions) - 1 \
            else 0
        newDirection = next(i for i in Directions
                            if i.value.Index == newIndex)
        return newDirection.value


class Location:
    def __init__(self, x, y):
        self.X, self.Y = x, y

    def move(self, xOffset, yOffset):
        return Location(self.X + xOffset,
                        self.Y + yOffset)


class Mower:
    def __init__(self, location, direction):
        self.Location = location
        self.Direction = direction
        self.StepCount = 0

    def turn_left(self):
        self.StepCount += 1
        self.Direction = Directions\
            .get_direction_after_turn_left_90_degrees(self.Direction)

    def mow(self, field):
        newLocation = self.Direction.move_from(self.Location)
        newLocation, isValid = field.fix_location(newLocation)
        if isValid:
            self.Location = newLocation
            self.StepCount += 1
            field.set(self.Location, self.StepCount
                if self.StepCount > 9
                else " {}".format(self.StepCount))

    def jump(self, field, forward, right):
        newLocation = self.Direction.move_from(self.Location, forward)
        rightDirection = Directions\
            .get_direction_after_turn_right_90_degrees(self.Direction)
        newLocation = rightDirection.move_from(newLocation, right)
        newLocation, isValid = field.fix_location(newLocation)
        if isValid:
            self.Location = newLocation
            self.StepCount += 1
            field.set(self.Location, self.StepCount
                if self.StepCount > 9
                else " {}".format(self.StepCount))


class Field:
    def __init__(self, width, height, initialContent):
        self.Field = [[initialContent] * width for _ in range(height)]
        self.Width = width
        self.Height = height

    def set(self, location, symbol):
        self.Field[location.Y][location.X] = symbol

    def count_mowed(self):
        return sum(1 for row in range(self.Height)
                   for column in range(self.Width)
                   if self.Field[row][column] != FieldContents.Grass)

    def display(self, mower):
        for rowIndex in range(self.Height):
            if rowIndex != mower.Location.Y:
                row = ' '.join(map(str, self.Field[rowIndex]))
            else:
                r = self.Field[rowIndex][:]
                r[mower.Location.X] = "{}{}".format(
                    FieldContents.Mower, mower.Direction.Symbol)
                row = ' '.join(map(str, r))
            print(row)


class ValidatingField(Field):
    def __init__(self, width, height, initialContent):
        super().__init__(width, height, initialContent)

    def fix_location(self, location):
        if location.X >= self.Width or \
                        location.X < 0 or \
                        location.Y >= self.Height or \
                        location.Y < 0:
            return None, False
        return location, True


class ToroidField(Field):
    def __init__(self, width, height, initialContent):
        super().__init__(width, height, initialContent)

    def fix_location(self, location):
        newLocation = Location(location.X, location.Y)
        if newLocation.X < 0:
            newLocation.X += self.Width
        elif newLocation.X >= self.Width:
            newLocation.X %= self.Width

        if newLocation.Y < 0:
            newLocation.Y += self.Height
        elif newLocation.Y >= self.Height:
            newLocation.Y %= self.Height

        return newLocation, True
