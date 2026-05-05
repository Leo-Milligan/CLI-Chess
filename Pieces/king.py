#!/usr/bin/env python3

class king:
    def __init__(self,  colour) -> None:
        self.colour = colour

    def __str__(self) -> str:
        return f"{self.colour}_{self.__class__.__name__}"
