import pygame
import math
import random
import os
import sys

# Initialize Pygame
pygame.init()

# Constants for the game window
WIDTH, HEIGHT = 800, 500
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game!")

# Button variables
RADIUS = 20  # Radius of the letter buttons
GAP = 15     # Gap between buttons
letters = []  # List to store letter button positions and states
startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)  # Starting x-coordinate for buttons
starty = 400  # Starting y-coordinate for buttons
A = 65  # ASCII value for 'A'

# Create letter buttons
for i in range(26):
    x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))  # Calculate x position
    y = starty + ((i // 13) * (GAP + RADIUS * 2))  # Calculate y position
    letters.append([x, y, chr(A + i), True])  # Store button position, letter, and visibility

# Fonts for the game
LETTER_FONT = pygame.font.SysFont('comicsans', 40)  # Font for letter buttons
WORD_FONT = pygame.font.SysFont('comicsans', 60)    # Font for the word display
TITLE_FONT = pygame.font.SysFont('comicsans', 70)   # Font for the title
HINT_FONT = pygame.font.SysFont('comicsans', 25)    # Smaller font for buttons

# Load hangman images
image_folder = r"C:\Py codes"  # Your image path
images = []

try:
    for i in range(7):  # Load 7 images (0-6)
        image_path = os.path.join(image_folder, f"hangman{i}.png")
        if not os.path.exists(image_path):
            print(f"Error: Image not found at {image_path}")
            pygame.quit()
            sys.exit()
        image = pygame.image.load(image_path)
        images.append(image)
except Exception as e:
    print(f"Error loading images: {e}")
    pygame.quit()
    sys.exit()

# Word lists for each subject
word_lists = {
    "Science": ["GRAVITY", "PHOTOSYNTHESIS", "ATOM"],
    "Geography": ["MOUNTAIN", "RIVER", "DESERT"],
    "English": ["METAPHOR", "ALLITERATION", "SONNET"]
}

# Game variables
hangman_status = 0  # Tracks the number of incorrect guesses
guessed = []  # List to store guessed letters
hint_visible = False  # Tracks if the hint popup is visible
subject_selected = False  # Tracks if a subject has been selected
subject = ""  # Stores the selected subject
word = ""  # Stores the selected word
hint = ""  # Stores the hint for the selected word

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# Buttons
hint_button = pygame.Rect(600, 100, 100, 40)  # Hint button (smaller and moved up)
quit_button = pygame.Rect(600, 160, 100, 40)  # Quit button (smaller and moved up)
restart_button = pygame.Rect(600, 220, 100, 40)  # Restart button (smaller and moved up)
science_button = pygame.Rect(300, 200, 200, 50)  # Science subject button
geography_button = pygame.Rect(300, 270, 200, 50)  # Geography subject button
english_button = pygame.Rect(300, 340, 200, 50)  # English subject button

def draw_text_wrapped(text, font, color, rect):
    """Draws text wrapped within a given rectangle."""
    words = text.split(" ")  # Split the hint into words
    space_width, _ = font.size(" ")  # Width of a space character
    x, y = rect.topleft  # Starting position for the text
    max_width = rect.width  # Maximum width of the rectangle

    for word in words:
        word_surface = font.render(word, True, color)
        word_width, word_height = word_surface.get_size()

        # If the word exceeds the max width, move to the next line
        if x + word_width >= rect.x + max_width:
            x = rect.x  # Reset x to the left edge
            y += word_height  # Move y to the next line

        # Draw the word
        win.blit(word_surface, (x, y))
        x += word_width + space_width  # Move x to the right for the next word

def draw():
    """Draws all game elements on the screen."""
    win.fill(WHITE)  # Clear the screen with white

    if not subject_selected:
        # Draw subject selection screen
        text = TITLE_FONT.render("Select a Subject", 1, BLACK)
        win.blit(text, (WIDTH / 2 - text.get_width() / 2, 50))

        # Draw subject buttons
        pygame.draw.rect(win, BLACK, science_button, border_radius=5)
        science_text = HINT_FONT.render("Science", 1, WHITE)
        text_x = science_button.x + (science_button.width - science_text.get_width()) // 2
        text_y = science_button.y + (science_button.height - science_text.get_height()) // 2
        win.blit(science_text, (text_x, text_y))

        pygame.draw.rect(win, BLACK, geography_button, border_radius=5)
        geography_text = HINT_FONT.render("Geography", 1, WHITE)
        text_x = geography_button.x + (geography_button.width - geography_text.get_width()) // 2
        text_y = geography_button.y + (geography_button.height - geography_text.get_height()) // 2
        win.blit(geography_text, (text_x, text_y))

        pygame.draw.rect(win, BLACK, english_button, border_radius=5)
        english_text = HINT_FONT.render("English", 1, WHITE)
        text_x = english_button.x + (english_button.width - english_text.get_width()) // 2
        text_y = english_button.y + (english_button.height - english_text.get_height()) // 2
        win.blit(english_text, (text_x, text_y))
    else:
        # Draw title
        text = TITLE_FONT.render("DEVELOPER HANGMAN", 1, BLACK)
        win.blit(text, (WIDTH / 2 - text.get_width() / 2, 20))

        # Draw the word with guessed letters
        display_word = ""
        for letter in word:
            if letter in guessed:
                display_word += letter + " "
            else:
                display_word += "_ "
        text = WORD_FONT.render(display_word, 1, BLACK)
        win.blit(text, (WIDTH / 2 - text.get_width() / 2, 200))

        # Draw letter buttons
        for letter in letters:
            x, y, ltr, visible = letter
            if visible:
                pygame.draw.circle(win, BLACK, (x, y), RADIUS, 3)  # Draw button outline
                text = LETTER_FONT.render(ltr, 1, BLACK)
                win.blit(text, (x - text.get_width() / 2, y - text.get_height() / 2))
        
        # Draw hint button
        pygame.draw.rect(win, BLACK, hint_button, border_radius=5)
        hint_text = HINT_FONT.render("Hint", 1, WHITE)
        text_x = hint_button.x + (hint_button.width - hint_text.get_width()) // 2
        text_y = hint_button.y + (hint_button.height - hint_text.get_height()) // 2
        win.blit(hint_text, (text_x, text_y))

        # Draw quit button
        pygame.draw.rect(win, BLACK, quit_button, border_radius=5)
        quit_text = HINT_FONT.render("Quit", 1, WHITE)
        text_x = quit_button.x + (quit_button.width - quit_text.get_width()) // 2
        text_y = quit_button.y + (quit_button.height - quit_text.get_height()) // 2
        win.blit(quit_text, (text_x, text_y))

        # Draw restart button
        pygame.draw.rect(win, BLACK, restart_button, border_radius=5)
        restart_text = HINT_FONT.render("Restart", 1, WHITE)
        text_x = restart_button.x + (restart_button.width - restart_text.get_width()) // 2
        text_y = restart_button.y + (restart_button.height - restart_text.get_height()) // 2
        win.blit(restart_text, (text_x, text_y))

        # Display hint popup if visible
        if hint_visible:
            hint_rect = pygame.Rect(250, 100, 300, 100)  # Larger box for wrapped hint text
            pygame.draw.rect(win, WHITE, hint_rect)
            pygame.draw.rect(win, BLACK, hint_rect, 3)
            draw_text_wrapped(f"Hint: {hint}", HINT_FONT, BLACK, hint_rect)

        # Draw hangman image
        win.blit(images[hangman_status], (100, 100))
    pygame.display.update()

def display_message(message):
    """Displays a message on the screen for a few seconds."""
    pygame.time.delay(1000)  # Wait for 1 second
    win.fill(WHITE)  # Clear the screen

    # Adjust font size for long messages
    font = pygame.font.SysFont('comicsans', 50)
    text = font.render(message, 1, BLACK)
    win.blit(text, (WIDTH / 2 - text.get_width() / 2, HEIGHT / 2 - text.get_height() / 2))

    pygame.display.update()
    pygame.time.delay(3000)  # Display the message for 3 seconds

def reset_game():
    """Resets the game variables for a new round."""
    global hangman_status, word, guessed, letters, hint_visible, hint, subject_selected
    hangman_status = 0
    word, hint = random.choice(list(words.items()))  # Choose a new word and hint
    guessed = []  # Clear guessed letters
    hint_visible = False  # Reset hint visibility
    subject_selected = False  # Reset subject selection
    for letter in letters:
        letter[3] = True  # Reset visibility of all letter buttons

def main():
    """Main game loop."""
    global hangman_status, word, guessed, letters, hint_visible, subject_selected, subject, hint

    FPS = 60  # Frames per second
    clock = pygame.time.Clock()
    run = True

    while run:
        clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:  # Handle window close event
                pygame.quit()
                return

            if event.type == pygame.MOUSEBUTTONDOWN:  # Handle mouse clicks
                m_x, m_y = pygame.mouse.get_pos()

                if not subject_selected:
                    # Subject selection screen
                    if science_button.collidepoint(m_x, m_y):
                        subject = "Science"
                        word = random.choice(word_lists["Science"])
                        hint = f"A {subject} term."
                        subject_selected = True
                    elif geography_button.collidepoint(m_x, m_y):
                        subject = "Geography"
                        word = random.choice(word_lists["Geography"])
                        hint = f"A {subject} term."
                        subject_selected = True
                    elif english_button.collidepoint(m_x, m_y):
                        subject = "English"
                        word = random.choice(word_lists["English"])
                        hint = f"An {subject} term."
                        subject_selected = True
                else:
                    # Hint button (toggle hint visibility)
                    if hint_button.collidepoint(m_x, m_y):
                        hint_visible = not hint_visible  # Toggle hint visibility

                    # Quit button
                    if quit_button.collidepoint(m_x, m_y):
                        pygame.quit()
                        return

                    # Restart button
                    if restart_button.collidepoint(m_x, m_y):
                        reset_game()

                    # Letter buttons
                    for letter in letters:
                        x, y, ltr, visible = letter
                        if visible:
                            dis = math.sqrt((x - m_x) ** 2 + (y - m_y) ** 2)  # Distance to button

                            if dis < RADIUS:  # If clicked
                                letter[3] = False  # Hide the button
                                guessed.append(ltr.upper())  # Add the letter to guessed list

                                if ltr.upper() not in word:  # Incorrect guess
                                    hangman_status += 1
        
        draw()  # Draw the game state

        # Check for win or lose
        if subject_selected:
            won = all(letter in guessed for letter in word)  # Check if all letters are guessed
            if won:
                display_message("You WON!")
                reset_game()

            if hangman_status == 6:  # Check if hangman is fully drawn
                display_message(f"You LOST! Word: {word}")
                reset_game()

# Run the game
if __name__ == "__main__":
    main()