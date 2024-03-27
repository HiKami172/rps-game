"""
This module implements a bot model for playing the Rock-Paper-Scissors game.
The model is designed as a class `RPSBot` which uses a Markov chain for prediction.
"""
import os

from typing import List, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import numpy as np


@dataclass
class RPSBot:
    """
    The `RPSBot` class is a bot that plays the Rock-Paper-Scissors game.
    It uses a Markov chain model to predict the next state and generate a counter move.

    Attributes:
        lr: learning rate of the model.
        states: possible states of the model.
        state: current state of the model.
        transitions: transition matrix of the Markov model.
    """

    lr: float = field(default=0.01)
    states: Tuple[str, ...] = field(init=False, default=("R", "P", "S"))
    state: Optional[int] = field(init=False, default=None)
    transitions: np.ndarray = field(init=False)

    def __post_init__(self):
        self.transitions = np.random.rand(3, 3)
        self.transitions /= self.transitions.sum(axis=1)[:, np.newaxis]

    def _calculate_stable_distribution(self) -> np.ndarray:
        """
        Calculate the stable distribution of the transitions' matrix.
        :return: stable distribution of the states.
        """
        eigenvalues, eigenvectors = np.linalg.eig(self.transitions.T)
        first_eigen = eigenvectors[:, np.where(np.abs(eigenvalues - 1.0) < 1e-8)[0][0]]
        stable_distribution = np.real(first_eigen)
        stable_distribution /= stable_distribution.sum()
        return stable_distribution

    def train(self, history: List[str]) -> None:
        """
        Trains the model based on the states' history.
        :param history: states history.
        :return: None
        """
        for i in range(len(history) - 1):
            self.update_transitions(history[i + 1])

    def update_transitions(self, move: str) -> None:
        """
        Sets new state and updates the transitions matrix.
        :param move: next chain state.
        :return: None
        """
        if move not in self.states:
            raise ValueError("Invalid state")
        new_state = self.states.index(move)
        if self.state is None:
            self.state = new_state
            return
        self.transitions[self.state] = np.maximum(
            0.001, self.transitions[self.state] - self.lr
        )
        self.transitions[self.state, new_state] = np.minimum(
            0.999, self.transitions[self.state, new_state] + self.lr * 3
        )
        self.state = new_state

    def predict(self) -> str:
        """
        Predicts the next state based on current and returns a counter move.
        :return: bot move represented by char R/P/S
        """
        if self.state is None:
            stable_distribution = self._calculate_stable_distribution()
            response_index = (np.argmax(stable_distribution) + 1) % 3
        else:
            response_index = (np.argmax(self.transitions[self.state]) + 1) % 3
        return self.states[response_index]

    def reset_state(self) -> None:
        """
        Resets the state of the model.
        :return: None
        """
        self.state = None

    def save_weights(self) -> None:
        """
        Save weights of the model to the file.
        :return: None
        """
        if not os.path.exists('logs'):
            os.makedirs('logs')

        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        with open(f"logs/{timestamp}.txt", "w", encoding="UTF-8") as f:
            np.savetxt(f, self.transitions)

    def load_weights(self, filepath: str) -> None:
        """
        Load model weights from the file.
        :param filepath: filepath of the weights file.
        :return: None
        """
        self.transitions = np.loadtxt(filepath)
