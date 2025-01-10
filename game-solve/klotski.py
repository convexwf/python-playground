# !/usr/bin/python3
# -*- coding: utf-8 -*-
# @Project : python-playground
# @FileName : game-solve/klotski.py
# @Author : convexwf@gmail.com
# @CreateDate : 2025-01-10 09:28
# @UpdateTime : 2025-01-10 09:28

import numpy as np
import copy
from collections import deque


class block:
    def __init__(self, x1, y1, x2, y2, dx=True, dy=True, goal=(-1, -1)):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2
        self.w = y2 - y1
        self.h = x2 - x1
        self.dx = dx
        self.dy = dy
        self.goal = goal

    def __repr__(self):
        return f"block({self.x1}, {self.y1}, {self.x2}, {self.y2})"

    def __hash__(self):
        return hash((self.x1, self.y1, self.x2, self.y2, self.dx, self.dy))

    def __eq__(self, other):
        if isinstance(other, block):
            return (self.x1, self.y1, self.x2, self.y2) == (
                other.x1,
                other.y1,
                other.x2,
                other.y2,
            )
        return False

    def __lt__(self, other):
        if isinstance(other, block):
            return (self.x1, self.y1) < (
                other.x1,
                other.y1,
            )
        return False

    def move(self, delta_x, delta_y):
        if self.dx:
            self.x1 += delta_x
            self.x2 += delta_x
        if self.dy:
            self.y1 += delta_y
            self.y2 += delta_y

    def check(self):
        return (self.x1, self.y1) == self.goal


class klotski:
    def __init__(self, board_size, block_list):
        self.board_size = board_size
        self.block_list = copy.deepcopy(block_list)

        self.board = np.zeros((board_size[0], board_size[1]), dtype=int)
        for i, block in enumerate(block_list):
            self.board[block.x1 : block.x2 + 1, block.y1 : block.y2 + 1] = i + 1
        self.history = []

    def move(self):
        next_states = []
        for block in self.block_list:
            if block.dx:
                if (
                    block.x1 > 0
                    and self.board[block.x1 - 1, block.y1 : block.y2 + 1].sum() == 0
                ):
                    block.move(-1, 0)
                    next_states.append(klotski(self.board_size, self.block_list))
                    block.move(1, 0)
                if (
                    block.x2 < self.board_size[0] - 1
                    and self.board[block.x2 + 1, block.y1 : block.y2 + 1].sum() == 0
                ):
                    block.move(1, 0)
                    next_states.append(klotski(self.board_size, self.block_list))
                    block.move(-1, 0)
            if block.dy:
                if (
                    block.y1 > 0
                    and self.board[block.x1 : block.x2 + 1, block.y1 - 1].sum() == 0
                ):
                    block.move(0, -1)
                    next_states.append(klotski(self.board_size, self.block_list))
                    block.move(0, 1)
                if (
                    block.y2 < self.board_size[1] - 1
                    and self.board[block.x1 : block.x2 + 1, block.y2 + 1].sum() == 0
                ):
                    block.move(0, 1)
                    next_states.append(klotski(self.board_size, self.block_list))
                    block.move(0, -1)
        return next_states

    def __hash__(self):
        block_tuple = tuple(sorted(self.block_list))
        return hash(block_tuple)


if __name__ == "__main__":
    block_list = [
        block(0, 1, 1, 1, dx=True, dy=False),
        block(0, 2, 0, 3, dx=False, dy=True),
        block(0, 4, 0, 5, dx=False, dy=True),
        block(1, 2, 3, 2, dx=True, dy=False),
        block(1, 3, 1, 5, dx=False, dy=True),
        block(2, 0, 2, 1, dx=False, dy=True, goal=(2, 4)),
        block(2, 3, 3, 3, dx=True, dy=False),
        block(3, 4, 3, 5, dx=False, dy=True),
        block(4, 0, 5, 0, dx=True, dy=False),
        block(4, 5, 5, 5, dx=True, dy=False),
        block(5, 2, 5, 4, dx=False, dy=True),
    ]

    klotski_instance = klotski((6, 6), block_list)

    state_set = set()
    state_set.add(klotski_instance.__hash__())
    kqueue = deque()
    kqueue.append(klotski_instance)

    step = 0
    while len(kqueue) > 0:
        current_state = kqueue.popleft()
        next_states = current_state.move()
        is_found = False
        for state in next_states:
            # print(state.board)
            # print(state.__hash__())
            if state.__hash__() not in state_set:
                state_set.add(state.__hash__())
                state.history = current_state.history.copy() + [current_state]
                kqueue.append(state)
                if state.block_list[5].check():
                    print("Found a solution!")
                    is_found = True
                    break
        if is_found:
            print("Solution path:")
            for s in state.history:
                print(s.board)
            break
        step += 1
        print(f"Step: {step}, Queue size: {len(kqueue)}")

    # next_states = klotski_instance.move()
    # for state in next_states:
    #     print(state.board)
