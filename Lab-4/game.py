import random
from words import WORDS, HINTS
from stats import SessionStats


class HangmanGame:
    def __init__(self):
        # Session state: lasts for the whole run.
        self.score = 0
        self.streak = 0
        self.stats = SessionStats()
        self.category = "technology"
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
        self.lives = 6
        self.hint_used = False

    def masked(self):
        return " ".join(ch if ch in self.guessed else "_" for ch in self.secret)

    def won(self):
        return all(ch in self.guessed for ch in set(self.secret))

    def guess(self, letter):
        if len(letter) != 1 or not letter.isalpha():
            return "Enter one letter."
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
        self.score = max(0, self.score - 1)
        return HINTS.get(self.secret, "No hint available.")

    def finish_round(self, won):
        """Update streak, score and session stats for a completed round."""
        if won:
            self.streak += 1
            self.score += 5 + self.streak
        else:
            self.streak = 0
        self.stats.record(won, self.streak)

    def play_round(self):
        """Play one round. Returns False if the player quit mid-round."""
        self.start_round()
        while self.lives > 0 and not self.won():
            print("\nWord:", self.masked())
            print("Wrong:", " ".join(sorted(self.wrong)) or "-")
            print("Lives:", self.lives, "Score:", self.score, "Streak:", self.streak)
            raw = input("Letter, /hint, or /quit: ").strip().lower()
            if raw == "/quit":
                return False
            if raw == "/hint":
                hint = self.use_hint()
                print(hint if hint else "Hint already used.")
                continue
            print(self.guess(raw))

        won = self.won()
        self.finish_round(won)
        if won:
            print("Solved:", self.secret)
        else:
            print("Out of lives. The word was:", self.secret)
        return True

    def print_summary(self):
        print("\n--- Session summary ---")
        print("Rounds played:", self.stats.rounds)
        print("Rounds won:   ", self.stats.wins)
        print("Best streak:  ", self.stats.best_streak)
        print("Final score:  ", self.score)

    def run(self):
        print("Hangman Challenge")
        print("A session consists of multiple rounds.")
        self.session_loop()
        self.print_summary()

    def session_loop(self):
        while True:
            print("\nCategories:", ", ".join(WORDS))
            raw = input("Choose category or q: ").strip().lower()
            if raw == "q":
                return
            if raw not in WORDS:
                print("Unknown category.")
                continue
            self.category = raw
            if not self.play_round():
                return
            print("Rounds:", self.stats.rounds, "Wins:", self.stats.wins,
                  "Best streak:", self.stats.best_streak)
            again = input("Another round? [y/n]: ").strip().lower()
            if again != "y":
                return
