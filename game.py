import json
import random
import pygame
import socket
import threading

# Initialize pygame for audio
pygame.init()
pygame.mixer.init()

# ANSI color codes
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    RESET = '\033[0m'

# Game state
class GameState:
    def __init__(self):
        self.player = None
        self.score = 0
        self.current_location = "CBD"
        self.resources = {
            "personnel": 100,
            "equipment": 100,
            "public_support": 50,
            "morale": 75
        }
        self.events = []

# Player class
class Player:
    def __init__(self, background):
        self.background = background
        if background == "Veteran Officer":
            self.strengths = ["Experienced", "High morale boost", "Better negotiation"]
            self.weaknesses = ["Old-fashioned thinking", "Slower physical abilities"]
        elif background == "Rookie Officer":
            self.strengths = ["High energy", "Quick to respond", "Innovative thinking"]
            self.weaknesses = ["Lack of experience", "Lower trust from senior officers"]
        elif background == "Community Liaison":
            self.strengths = ["High trust from citizens", "Good communication skills"]
            self.weaknesses = ["Limited combat training", "Viewed as too lenient"]
        else:  # Tactical Expert
            self.strengths = ["Strategic thinking", "Excellent in crisis management"]
            self.weaknesses = ["Poor interpersonal skills", "Sometimes too aggressive"]

# Main game class
class NairobiPoliceGame:
    def __init__(self):
        self.game_state = GameState()
        self.load_high_score()
        self.locations = ["CBD", "Kibera", "Mathare", "Uhuru Park", "City Hall", "Nairobi Hospital"]
        self.current_day = 1
        self.max_days = 30
        # Initialize sounds
        self.buzz_sound = pygame.mixer.Sound("buzz-buzz-95806.mp3")

    def load_high_score(self):
        try:
            with open("high_score.json", "r") as f:
                self.high_score = json.load(f)["high_score"]
        except FileNotFoundError:
            self.high_score = 0

    def save_high_score(self):
        with open("high_score.json", "w") as f:
            json.dump({"high_score": max(self.high_score, self.game_state.score)}, f)

    def start_game(self):
        self.character_creation()
        self.main_game_loop()

    def character_creation(self):
        print("Welcome to the Nairobi Police and Citizens Protests Adventure!")
        print("Choose your character background:")
        print("1. Veteran Officer")
        print("2. Rookie Officer")
        print("3. Community Liaison")
        print("4. Tactical Expert")

        while True:
            choice = input("Enter your choice (1-4): ")
            if choice in ["1", "2", "3", "4"]:
                backgrounds = ["Veteran Officer", "Rookie Officer", "Community Liaison", "Tactical Expert"]
                self.game_state.player = Player(backgrounds[int(choice) - 1])
                print(f"\nYou have chosen: {self.game_state.player.background}")
                print("Strengths:", ", ".join(self.game_state.player.strengths))
                print("Weaknesses:", ", ".join(self.game_state.player.weaknesses))
                break
            else:
                self.buzz_sound.play()  # Play buzzing sound for invalid choice
                print("Invalid choice. Please enter a number between 1 and 4.")

    def main_game_loop(self):
        while self.current_day <= self.max_days:
            print(f"\n--- Day {self.current_day} of {self.max_days} ---")
            self.display_game_state()
            self.handle_location_event()
            self.handle_random_event()
            self.handle_player_action()
            self.update_game_state()
            if self.check_game_over():
                break
            self.current_day += 1
        self.end_game()

    def display_game_state(self):
        print(f"\nCurrent Location: {self.game_state.current_location}")
        print(f"Score: {self.game_state.score}")
        print("Resources:")
        for resource, value in self.game_state.resources.items():
            print(f"  {resource.capitalize()}: {value}")

    def handle_location_event(self):
        events = {
            "CBD": ["Traffic congestion due to protests", "Business owners complaining about lost revenue"],
            "Kibera": ["Reports of unrest in informal settlements", "Community leaders requesting a meeting"],
            "Mathare": ["Youth groups organizing peaceful demonstrations", "Rumors of potential violence"],
            "Uhuru Park": ["Large gathering for a political rally", "Environmental activists staging a sit-in"],
            "City Hall": ["Government officials demanding action", "Protesters attempting to enter the building"],
            "Nairobi Hospital": ["Injured protesters seeking treatment", "Staff overwhelmed by the influx of patients"]
        }
        event = random.choice(events[self.game_state.current_location])
        print(f"\nLocation Update: {event}")
        self.handle_location_specific_challenge(event)

    def handle_location_specific_challenge(self, event):
        print("\nHow do you want to respond to this situation?")
        print("1. Take immediate action")
        print("2. Gather more information")
        print("3. Delegate to a specialized team")
        choice = input("Enter your choice (1-3): ")
        
        if choice == "1":
            success = random.random() < 0.5
            if success:
                self.print_success("Your quick action resolved the situation effectively.")
                self.update_score(15)
            else:
                self.print_failure("Your hasty decision led to complications.")
                self.update_score(-10)
        elif choice == "2":
            self.print_success("You gained valuable insights by gathering more information.")
            self.update_score(5)
            self.game_state.resources["public_support"] += 3
        elif choice == "3":
            success = random.random() < 0.7
            if success:
                self.print_success("The specialized team handled the situation well.")
                self.update_score(10)
            else:
                self.print_failure("The team struggled to manage the situation effectively.")
                self.update_score(-5)
        else:
            self.buzz_sound.play()  # Play buzzing sound for invalid choice
            self.print_failure("Invalid choice. Opportunity lost.")
            self.update_score(-5)

    def handle_random_event(self):
        events = [
            self.peaceful_protest_event,
            self.media_scrutiny_event,
            self.natural_disaster_event,
            self.political_interference_event,
            self.resource_shortage_event
        ]
        random.choice(events)()

    def peaceful_protest_event(self):
        print("\nA peaceful protest has started in Uhuru Park.")
        success = random.random() < 0.6
        if success:
            self.print_success("The protest remained peaceful, thanks to your effective crowd control.")
            self.update_score(10)
        else:
            self.print_failure("The protest turned violent despite your efforts.")
            self.update_score(-15)

    def media_scrutiny_event(self):
        print("\nThe media is scrutinizing police actions.")
        success = random.random() < 0.7
        if success:
            self.print_success("The media reports were favorable, boosting public support.")
            self.update_score(10)
            self.game_state.resources["public_support"] += 5
        else:
            self.print_failure("The media portrayed the police negatively, causing public backlash.")
            self.update_score(-10)
            self.game_state.resources["public_support"] -= 5

    def natural_disaster_event(self):
        print("\nA natural disaster has struck, complicating the situation.")
        success = random.random() < 0.5
        if success:
            self.print_success("Your team effectively managed the disaster, earning public praise.")
            self.update_score(20)
        else:
            self.print_failure("The disaster response was inadequate, causing further chaos.")
            self.update_score(-20)

    def political_interference_event(self):
        print("\nThere is political interference affecting police operations.")
        success = random.random() < 0.6
        if success:
            self.print_success("You successfully navigated the political challenges.")
            self.update_score(15)
        else:
            self.print_failure("Political interference hampered your efforts, leading to setbacks.")
            self.update_score(-15)

    def resource_shortage_event(self):
        print("\nA shortage of resources is limiting police effectiveness.")
        self.print_failure("You need to allocate your resources wisely to overcome this challenge.")
        self.update_score(-10)
        self.game_state.resources["equipment"] -= 10

    def handle_player_action(self):
        print("\nChoose your action:")
        print("1. Address the crowd with a calming speech")
        print("2. Deploy a small, visible police presence")
        print("3. Organize a dialogue with community leaders")
        print("4. Allow protests to proceed with minimal intervention")
        choice = input("Enter your choice (1-4): ")

        if choice == "1":
            success = random.random() < 0.7
            if success:
                self.print_success("Your speech calmed the crowd, reducing tension.")
                self.update_score(10)
                self.game_state.resources["public_support"] += 5
            else:
                self.print_failure("The crowd reacted negatively to your speech.")
                self.update_score(-10)
        elif choice == "2":
            success = random.random() < 0.5
            if success:
                self.print_success("The visible police presence deterred potential violence.")
                self.update_score(10)
                self.game_state.resources["personnel"] -= 5
            else:
                self.print_failure("The presence escalated tensions.")
                self.update_score(-10)
        elif choice == "3":
            success = random.random() < 0.8
            if success:
                self.print_success("Dialogue with leaders was successful in easing tensions.")
                self.update_score(15)
            else:
                self.print_failure("The dialogue failed to achieve its goals.")
                self.update_score(-5)
        elif choice == "4":
            success = random.random() < 0.4
            if success:
                self.print_success("Allowing the protests to proceed peacefully was a wise decision.")
                self.update_score(5)
            else:
                self.print_failure("The lack of intervention led to unrest.")
                self.update_score(-15)
        else:
            self.buzz_sound.play()  # Play buzzing sound for invalid choice
            self.print_failure("Invalid choice. No action taken.")
            self.update_score(-5)

    def update_game_state(self):
        self.update_resources()

    def update_resources(self):
        # Randomly adjust resources to simulate real-world changes
        self.game_state.resources["personnel"] += random.randint(-5, 5)
        self.game_state.resources["equipment"] += random.randint(-5, 5)
        self.game_state.resources["public_support"] += random.randint(-5, 5)
        self.game_state.resources["morale"] += random.randint(-5, 5)

        # Ensure resources are within valid bounds
        for key in self.game_state.resources:
            self.game_state.resources[key] = max(0, min(self.game_state.resources[key], 100))

    def print_success(self, message):
        print(f"{Colors.GREEN}{message}{Colors.RESET}")

    def print_failure(self, message):
        print(f"{Colors.RED}{message}{Colors.RESET}")

    def update_score(self, points):
        self.game_state.score += points

    def check_game_over(self):
        if self.game_state.resources["personnel"] <= 0:
            print("\nGame Over: All personnel have been exhausted.")
            return True
        if self.game_state.resources["equipment"] <= 0:
            print("\nGame Over: All equipment has been lost.")
            return True
        if self.game_state.resources["public_support"] <= 0:
            print("\nGame Over: Public support has been lost.")
            return True
        if self.game_state.resources["morale"] <= 0:
            print("\nGame Over: Morale is too low to continue.")
            return True
        return False

    def end_game(self):
        print(f"\nGame Over! Your final score is {self.game_state.score}.")
        if self.game_state.score > self.high_score:
            print(f"Congratulations! You've set a new high score: {self.game_state.score}")
            self.high_score = self.game_state.score
            self.save_high_score()

# Multiplayer functionality (simplified example)
class MultiplayerManager:
    def __init__(self, game):
        self.game = game
        self.server = None
        self.client = None

    def host_game(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("0.0.0.0", 9999))
        self.server.listen(1)
        print("Waiting for a player to join...")
        self.client, _ = self.server.accept()
        print("Player joined! Starting the game...")
        self.start_multiplayer_game()

    def join_game(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.client.connect(("localhost", 9999))
        print("Connected to the host! Starting the game...")
        self.start_multiplayer_game()

    def start_multiplayer_game(self):
        threading.Thread(target=self.handle_client, args=(self.client,)).start()
        self.game.start_game()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if data:
                    print(f"Received: {data.decode()}")
            except:
                print("Connection lost.")
                break

# Main execution
if __name__ == "__main__":
    game = NairobiPoliceGame()
    print("Do you want to play multiplayer? (y/n)")
    if input().lower() == 'y':
        multiplayer = MultiplayerManager(game)
        print("Do you want to (1) host or (2) join a game?")
        if input() == '1':
            multiplayer.host_game()
        else:
            multiplayer.join_game()
    game.start_game()
