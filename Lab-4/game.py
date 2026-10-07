import random
from words import WORDS, HINTS
from stats import SessionStats

# name: (lives, score multiplier)
DIFFICULTIES = {
    "easy": (8, 1),
    "medium": (6, 2),
    "hard": (4, 3),
}
BASE_POINTS = 5
HINT_PENALTY = 2


class HangmanGame:
    def __init__(self):
        # Session state: lasts for the whole run.
        self.score = 0
        self.streak = 0
        self.stats = SessionStats()
        self.category = "technology"
        self.difficulty = "medium"
        # Round state: reset by start_round().
        self.secret = ""
        self.guessed = set()
        self.wrong = set()
        self.lives = 6
        self.hint_used = False

    def start_round(self):
        """Reset round-specific state only; session state is untouched."""
        self.secret = random.choice(WORDS[self.category])
        self.guessed.clear()
        self.wrong.clear()
        self.lives, self.multiplier = DIFFICULTIES[self.difficulty]
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        """Apply one guess. Invalid or repeated input never changes state."""
        if not letter:
            return "Enter a letter."
        if len(letter) != 1:
            return "Enter only one letter at a time."
        if not ("a" <= letter <= "z"):
            return "Letters a-z only."
        if letter in self.guessed or letter in self.wrong:
            return "Already guessed."
        if letter in self.secret:
            self.guessed.add(letter)
            return "Correct."
        self.wrong.add(letter)
        self.lives -= 1
        return "Wrong."

    def use_hint(self):
        if self.hint_used:
            return None
        self.hint_used = True
        hint = HINTS.get(self.secret, "No hint available.")
        return hint + f" (-{HINT_PENALTY} from this round's reward)"

    def round_points(self):
        """Win reward: (base + streak - hint penalty), floored at 0, times multiplier."""
        penalty = HINT_PENALTY if self.hint_used else 0
        return max(0, BASE_POINTS + self.streak - penalty) * self.multiplier

    def finish_round(self, won):
        """Update streak, score and session stats for a completed round.

        Returns the points earned this round."""
        points = 0
        if won:
            self.streak += 1
            points = self.round_points()
            self.score += points
        else:
            self.streak = 0
        self.stats.record(won, self.streak)
        return points

    def play_round(self):
        """Play one round. Returns False if the player quit mid-round."""
        self.start_round()
        show_board = True
        while self.lives > 0 and not self.won():
            # Redraw the board only when something changed, so invalid
            # input gets one short message instead of a repeated board.
            if show_board:
                self.print_board()
            raw = input("Letter, /hint, or /quit: ").strip().lower()
            if raw == "/quit":
                return False
            if raw == "/hint":
                hint = self.use_hint()
                print(hint if hint else "Hint already used.")
                show_board = False
                continue
            if raw.startswith("/"):
                print("Unknown command. Use /hint or /quit.")
                show_board = False
                continue
            result = self.guess(raw)
            print(result)
            show_board = result in ("Correct.", "Wrong.")

        won = self.won()
        points = self.finish_round(won)
        if won:
            print("Solved:", self.secret, f"(+{points} points)")
        else:
            print("Out of lives. The word was:", self.secret)
        return True

    def print_board(self):
        print("\nWord:", self.masked())
        print("Wrong:", " ".join(sorted(self.wrong)) or "-")
        print("Lives:", self.lives, "Score:", self.score, "Streak:", self.streak,
              f"[{self.category}, {self.difficulty}]")

    @staticmethod
    def pick(options, raw):
        """Match raw input to an option by name or 1-based number, else None."""
        if raw in options:
            return raw
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        return None

    def choose_category(self):
        """Return a category name, or None if the player chose to quit."""
        names = list(WORDS)
        print("\nCategories:")
        for i, name in enumerate(names, 1):
            print(f"  {i}. {name}")
        while True:
            raw = input("Choose category (name or number) or q: ").strip().lower()
            if raw == "q":
                return None
            choice = self.pick(names, raw)
            if choice:
                return choice
            print("Unknown category.")

    def choose_difficulty(self):
        names = list(DIFFICULTIES)
        for i, name in enumerate(names, 1):
            lives, mult = DIFFICULTIES[name]
            print(f"  {i}. {name}: {lives} lives, x{mult} points")
        while True:
            raw = input("Choose difficulty (name or number): ").strip().lower()
            choice = self.pick(names, raw)
            if choice:
                return choice
            print("Unknown difficulty.")

    def ask_again(self):
        while True:
            raw = input("Another round? [y/n]: ").strip().lower()
            if raw in ("y", "yes"):
                return True
            if raw in ("n", "no"):
                return False
            print("Please answer y or n.")

    def print_summary(self):
        print("\n--- Session summary ---")
        print("Rounds played:", self.stats.rounds)
        print("Rounds won:   ", self.stats.wins)
        print("Best streak:  ", self.stats.best_streak)
        print("Final score:  ", self.score)

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        try:
            self.session_loop()
        except (EOFError, KeyboardInterrupt):
            print("\nGame interrupted.")
        self.print_summary()

    def session_loop(self):
        while True:
            category = self.choose_category()
            if category is None:
                return
            self.category = category
            self.difficulty = self.choose_difficulty()
            if not self.play_round():
                return
            print("Rounds:", self.stats.rounds, "Wins:", self.stats.wins,
                  "Best streak:", self.stats.best_streak)
            if not self.ask_again():
                return
