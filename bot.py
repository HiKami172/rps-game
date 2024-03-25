"""
This module implements a bot model for playing the Rock-Paper-Scissors game.
The model is designed as a class `RPSBot` which uses a Markov chain for prediction.
"""
from typing import List, Optional
import numpy as np


class RPSBot:
    """
    The `RPSBot` class is a bot that plays the Rock-Paper-Scissors game.
    It uses a Markov chain model to predict the next state and generate a counter move.
    """
    def __init__(self, lr=0.01):
        self.states = ('R', 'P', 'S')
        self.lr = lr
        self.transitions = np.random.rand(3, 3)
        self.transitions /= self.transitions.sum(axis=1)[:, np.newaxis]

    def _calculate_stable_distribution(self) -> np.ndarray:
        """Calculate the stable distribution of the transitions' matrix."""
        eigenvalues, eigenvectors = np.linalg.eig(self.transitions.T)
        first_eigen = eigenvectors[:, np.where(np.abs(eigenvalues - 1.0) < 1e-8)[0][0]]
        stable_distribution = np.real(first_eigen)
        stable_distribution /= stable_distribution.sum()
        return stable_distribution

    def train(self, history: List[str]) -> None:
        """Trains the model based on the states history."""
        for i in range(len(history) - 1):
            self.update_transitions(history[i], history[i + 1])

    def update_transitions(self, state: str, new_state: str) -> None:
        """Changes probabilities for transitions from state."""
        if any(s not in self.states for s in [state, new_state]):
            raise ValueError("Invalid state")
        state_index = self.states.index(state)
        new_state_index = self.states.index(new_state)
        self.transitions[state_index] -= self.lr
        self.transitions[state_index, new_state_index] += self.lr * 3

    def predict(self, state: Optional[str] = None) -> str:
        """Predicts the next state based on current and returns counter move."""
        if state is None:
            stable_distribution = self._calculate_stable_distribution()
            response_index = np.argmax(stable_distribution)
            return self.states[response_index]
        if state not in self.states:
            raise ValueError("Invalid state")
        state_index = self.states.index(state)
        response_index = (np.argmax(self.transitions[state_index]) + 1) % 3
        return self.states[response_index]
