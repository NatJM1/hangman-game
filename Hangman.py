"""
Hangman Game
Developed with Pygame
This game features:
- Subject selection (Science, Geography, English)
- Visual hangman progression
- Letter button interface
- Hint system
- Win/lose conditions
"""

import pygame
import math
import random
import os
import sys

# Initialize Pygame library
pygame.init()

# ======================================================================
# CONSTANTS AND GAME SETTINGS
# ======================================================================

# Game window dimensions
WIDTH, HEIGHT = 800, 500

# Create game window with specified dimensions
win = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Hangman Game!")  # Window title

# Colors (RGB values)
WHITE = (255, 255, 255)  # Background color
BLACK = (0, 0, 0)        # Text and drawing color

# ======================================================================
# LETTER BUTTON SETUP
# ======================================================================

# Button appearance settings
RADIUS = 20    # Radius of each letter button
GAP = 15       # Space between buttons
letters = []   # Will store all letter button data

# Starting position for the letter buttons grid
startx = round((WIDTH - (RADIUS * 2 + GAP) * 13) / 2)  # Centered horizontally
starty = 400  # Vertical position

# ASCII value for 'A' - used to generate letters
A = 65

# Create letter buttons in a grid (2 rows of 13 letters each)
for i in range(26):
    # Calculate x position (13 letters per row)
    x = startx + GAP * 2 + ((RADIUS * 2 + GAP) * (i % 13))
    # Calculate y position (second row starts after 13 letters)
    y = starty + ((i // 13) * (GAP + RADIUS * 2))
    # Store button info: [x, y, letter, visible?]
    letters.append([x, y, chr(A + i), True])

# ======================================================================
# FONT SETTINGS
# ======================================================================

# Different fonts for various text elements
LETTER_FONT = pygame.font.SysFont('comicsans', 40)  # Letter buttons
WORD_FONT = pygame.font.SysFont('comicsans', 60)    # Word display
TITLE_FONT = pygame.font.SysFont('comicsans', 70)   # Game title
HINT_FONT = pygame.font.SysFont('comicsans', 25)    # Hint text

# ======================================================================
# HANGMAN IMAGE HANDLING
# ======================================================================

def generate_hangman_images():
    """
    Creates simple hangman images programmatically.
    Returns a list of 7 Pygame surfaces showing progressive hangman states.
    """
    images = []
    
    for status in range(7):
        # Create blank image surface
        image = pygame.Surface((200, 250))
        image.fill(WHITE)  # White background
        
        # Draw gallows (always visible)
        pygame.draw.rect(image, BLACK, (50, 30, 100, 10))  # Top beam
        pygame.draw.rect(image, BLACK, (50, 30, 10, 200))  # Vertical post
        pygame.draw.rect(image, BLACK, (20, 230, 100, 10))  # Base
        
        # Progressive drawing of hangman based on wrong guesses
        if status >= 1:  # Head
            pygame.draw.circle(image, BLACK, (100, 60), 20, 2)
        if status >= 2:  # Body
            pygame.draw.line(image, BLACK, (100, 80), (100, 140), 2)
        if status >= 3:  # Left arm
            pygame.draw.line(image, BLACK, (100, 100), (70, 120), 2)
        if status >= 4:  # Right arm
            pygame.draw.line(image, BLACK, (100, 100), (130, 120), 2)
        if status >= 5:  # Left leg
            pygame.draw.line(image, BLACK, (100, 140), (70, 180), 2)
        if status >= 6:  # Right leg
            pygame.draw.line(image, BLACK, (100, 140), (130, 180), 2)
        
        images.append(image)
    
    return images

# Try to load images from folder, otherwise generate them
images = []
image_folder = "hangman_images"  # Folder name for custom images

try:
    # Check if image folder exists
    if os.path.exists(image_folder):
        images_loaded = True
        # Try to load all 7 images (hangman0.png to hangman6.png)
        for i in range(7):
            image_path = os.path.join(image_folder, f"hangman{i}.png")
            if os.path.exists(image_path):
                img = pygame.image.load(image_path)
                images.append(img)
            else:
                images_loaded = False
                break
        
        # If any image is missing, use generated ones instead
        if not images_loaded:
            images = generate_hangman_images()
    else:
        # Folder doesn't exist - use generated images
        images = generate_hangman_images()
except Exception as e:
    # If any error occurs, use generated images
    print(f"Error loading images: {e}")
    images = generate_hangman_images()

# ======================================================================
# GAME DATA
# ======================================================================

# Word lists organized by subject
word_lists = {
    "Science": ["GRAVITY", "PHOTOSYNTHESIS", "ATOM"],
    "Geography": ["MOUNTAIN", "RIVER", "DESERT"],
    "English": ["METAPHOR", "ALLITERATION", "SONNET"]
}

# Game state variables
hangman_status = 0    # Tracks wrong guesses (0-6)
guessed = []          # Letters that have been guessed
hint_visible = False  # Whether hint is currently shown
subject_selected = False  # Whether player has chosen a subject
subject = ""          # Current subject (Science/Geography/English)
word = ""             # The word to guess
hint = ""             # Hint for current word

# ======================================================================
# BUTTON DEFINITIONS
# ======================================================================

# Game control buttons (position, width, height)
hint_button = pygame.Rect(600, 100, 100, 40)    # Shows/hides hint
quit_button = pygame.Rect(600, 160, 100, 40)    # Exits game
restart_button = pygame.Rect(600, 220, 100, 40) # Restarts game

# Subject selection buttons
science_button = pygame.Rect(300, 200, 200, 50)
geography_button = pygame.Rect(300, 270, 200, 50)
english_button = pygame.Rect(300, 340, 200, 50)

# ======================================================================
# DRAWING FUNCTIONS
# ======================================================================

def draw_text_wrapped(text, font, color, rect):
    """
    Draws text that automatically wraps within a given rectangle.
    Args:
        text: The text to display
        font: Pygame font object
        color: Text color
        rect: Pygame Rect defining boundaries
    """
    words = text.split(" ")  # Split text into words
    space_width = font.size(" ")[0]  # Get width of space character
    x, y = rect.topleft  # Starting position
    
    for word in words:
        word_surface = font.render(word, True, color)
        word_width, word_height = word_surface.get_size()
        
        # If word doesn't fit, move to next line
        if x + word_width >= rect.x + rect.width:
            x = rect.x  # Return to left edge
            y += word_height  # Move down
            
        # Draw the word
        win.blit(word_surface, (x, y))
        x += word_width + space_width  # Move right for next word

def draw():
    """Main drawing function - renders all game elements"""
    win.fill(WHITE)  # Clear screen with white
    
    if not subject_selected:
        # ==============================================================
        # SUBJECT SELECTION SCREEN
        # ==============================================================
        
        # Draw title
        text = TITLE_FONT.render("Select a Subject", 1, BLACK)
        win.blit(text, (WIDTH/2 - text.get_width()/2, 50))
        
        # Draw subject buttons with centered text
        pygame.draw.rect(win, BLACK, science_button, border_radius=5)
        text = HINT_FONT.render("Science", 1, WHITE)
        win.blit(text, (
            science_button.x + (science_button.width - text.get_width())/2,
            science_button.y + (science_button.height - text.get_height())/2
        ))
        
        pygame.draw.rect(win, BLACK, geography_button, border_radius=5)
        text = HINT_FONT.render("Geography", 1, WHITE)
        win.blit(text, (
            geography_button.x + (geography_button.width - text.get_width())/2,
            geography_button.y + (geography_button.height - text.get_height())/2
        ))
        
        pygame.draw.rect(win, BLACK, english_button, border_radius=5)
        text = HINT_FONT.render("English", 1, WHITE)
        win.blit(text, (
            english_button.x + (english_button.width - text.get_width())/2,
            english_button.y + (english_button.height - text.get_height())/2
        ))
    else:
        # ==============================================================
        # MAIN GAME SCREEN
        # ==============================================================
        
        # Draw game title
        text = TITLE_FONT.render("HANGMAN GAME", 1, BLACK)
        win.blit(text, (WIDTH/2 - text.get_width()/2, 20))
        
        # Draw word with blanks for unguessed letters
        display_word = ""
        for letter in word:
            if letter in guessed:
                display_word += letter + " "  # Show guessed letters
            else:
                display_word += "_ "         # Show blank for unguessed
        text = WORD_FONT.render(display_word, 1, BLACK)
        win.blit(text, (WIDTH/2 - text.get_width()/2, 200))
        
        # Draw letter buttons (only visible ones)
        for letter in letters:
            x, y, ltr, visible = letter
            if visible:
                # Button circle
                pygame.draw.circle(win, BLACK, (x, y), RADIUS, 3)
                # Letter text (centered)
                text = LETTER_FONT.render(ltr, 1, BLACK)
                win.blit(text, (x - text.get_width()/2, y - text.get_height()/2))
        
        # Draw control buttons
        pygame.draw.rect(win, BLACK, hint_button, border_radius=5)
        text = HINT_FONT.render("Hint", 1, WHITE)
        win.blit(text, (
            hint_button.x + (hint_button.width - text.get_width())/2,
            hint_button.y + (hint_button.height - text.get_height())/2
        ))
        
        pygame.draw.rect(win, BLACK, quit_button, border_radius=5)
        text = HINT_FONT.render("Quit", 1, WHITE)
        win.blit(text, (
            quit_button.x + (quit_button.width - text.get_width())/2,
            quit_button.y + (quit_button.height - text.get_height())/2
        ))
        
        pygame.draw.rect(win, BLACK, restart_button, border_radius=5)
        text = HINT_FONT.render("Restart", 1, WHITE)
        win.blit(text, (
            restart_button.x + (restart_button.width - text.get_width())/2,
            restart_button.y + (restart_button.height - text.get_height())/2
        ))
        
        # Show hint popup if enabled
        if hint_visible:
            hint_rect = pygame.Rect(250, 100, 300, 100)
            pygame.draw.rect(win, WHITE, hint_rect)
            pygame.draw.rect(win, BLACK, hint_rect, 3)
            draw_text_wrapped(f"Hint: {hint}", HINT_FONT, BLACK, hint_rect)
        
        # Draw current hangman image based on wrong guesses
        win.blit(images[hangman_status], (100, 100))
    
    # Update the display
    pygame.display.update()

# ======================================================================
# GAME LOGIC FUNCTIONS
# ======================================================================

def display_message(message):
    """
    Shows a message screen for 3 seconds.
    Used for win/lose notifications.
    """
    pygame.time.delay(1000)  # Short pause
    win.fill(WHITE)  # Clear screen
    
    # Render message centered
    text = pygame.font.SysFont('comicsans', 50).render(message, 1, BLACK)
    win.blit(text, (WIDTH/2 - text.get_width()/2, HEIGHT/2 - text.get_height()/2))
    
    pygame.display.update()
    pygame.time.delay(3000)  # Show for 3 seconds

def reset_game():
    """Resets game state for a new round"""
    global hangman_status, word, guessed, hint_visible
    
    hangman_status = 0  # Reset wrong guesses
    word = random.choice(word_lists[subject])  # Pick new word
    
    # Set appropriate hint based on subject
    hint = f"A {subject} term." if subject != "English" else f"An {subject} term."
    
    guessed = []          # Clear guessed letters
    hint_visible = False  # Hide hint
    
    # Reset all letter buttons to visible
    for letter in letters:
        letter[3] = True

# ======================================================================
# MAIN GAME LOOP
# ======================================================================

def main():
    """Main game loop controlling the game flow"""
    global hangman_status, guessed, hint_visible
    global subject_selected, subject, word, hint
    
    clock = pygame.time.Clock()
    run = True
    
    while run:
        clock.tick(60)  # Cap at 60 FPS
        
        # ==============================================================
        # EVENT HANDLING
        # ==============================================================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            
            if event.type == pygame.MOUSEBUTTONDOWN:
                m_x, m_y = pygame.mouse.get_pos()
                
                if not subject_selected:
                    # ==================================================
                    # SUBJECT SELECTION
                    # ==================================================
                    if science_button.collidepoint(m_x, m_y):
                        subject = "Science"
                        word = random.choice(word_lists["Science"])
                        hint = "A Science term."
                        subject_selected = True
                    elif geography_button.collidepoint(m_x, m_y):
                        subject = "Geography"
                        word = random.choice(word_lists["Geography"])
                        hint = "A Geography term."
                        subject_selected = True
                    elif english_button.collidepoint(m_x, m_y):
                        subject = "English"
                        word = random.choice(word_lists["English"])
                        hint = "An English term."
                        subject_selected = True
                else:
                    # ==================================================
                    # GAME CONTROLS
                    # ==================================================
                    if hint_button.collidepoint(m_x, m_y):
                        hint_visible = not hint_visible  # Toggle hint
                    
                    if quit_button.collidepoint(m_x, m_y):
                        pygame.quit()
                        return
                    
                    if restart_button.collidepoint(m_x, m_y):
                        reset_game()
                    
                    # ==================================================
                    # LETTER BUTTON HANDLING
                    # ==================================================
                    for letter in letters:
                        x, y, ltr, visible = letter
                        if visible:
                            # Calculate distance from click to button center
                            dis = math.sqrt((x - m_x)**2 + (y - m_y)**2)
                            
                            if dis < RADIUS:  # Click was on this button
                                letter[3] = False  # Hide button
                                guessed.append(ltr.upper())  # Add to guesses
                                
                                if ltr.upper() not in word:  # Wrong guess
                                    hangman_status += 1
        
        # ==============================================================
        # DRAW CURRENT GAME STATE
        # ==============================================================
        draw()
        
        # ==============================================================
        # WIN/LOSE CONDITIONS
        # ==============================================================
        if subject_selected:
            # Check if all letters in word have been guessed
            won = all(letter in guessed for letter in word)
            
            if won:
                display_message("You WON!")
                reset_game()
            
            # Check if hangman is complete (6 wrong guesses)
            if hangman_status == 6:
                display_message(f"You LOST! Word: {word}")
                reset_game()

# Start the game when script is run
if __name__ == "__main__":
    main()