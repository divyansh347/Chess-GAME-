import os
import pygame
import chess
import chess.engine

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 800
SQUARE_SIZE = WIDTH // 8
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
DARK_BROWN = (139, 69, 19)
LIGHT_BROWN = (222, 184, 135)

# Path to Stockfish
engine_path = r"C:\\Users\\divya\\OneDrive\\Desktop\\Chess game\\stockfish.exe"

# Check if Stockfish exists
if not os.path.isfile(engine_path):
    print(f"Stockfish not found at the specified path: {engine_path}")
    exit()

# Initialize the screen
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Function to load chess piece images or use placeholders
def load_images():
    pieces = ["K", "Q", "R", "B", "N", "P"]
    colors = ["w", "b"]
    images = {}
    for color in colors:
        for piece in pieces:
            try:
                img = pygame.image.load(f"images/{color}{piece}.png")
                img = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))
                images[f"{color}{piece}"] = img
            except pygame.error:
                placeholder = pygame.Surface((SQUARE_SIZE, SQUARE_SIZE))
                placeholder.fill((255, 0, 0) if color == "w" else (0, 0, 255))  # Red for white, blue for black
                images[f"{color}{piece}"] = placeholder
    return images

# Draw the chessboard
def draw_board(board, images, player_color, selected_square=None):
    for row in range(8):
        for col in range(8):
            if player_color == chess.BLACK:
                display_row = 7 - row
                display_col = 7 - col
            else:
                display_row = row
                display_col = col

            color = LIGHT_BROWN if (row + col) % 2 == 0 else DARK_BROWN
            square_rect = pygame.Rect(display_col * SQUARE_SIZE, display_row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE)
            pygame.draw.rect(screen, color, square_rect)

            if selected_square == row * 8 + col:
                pygame.draw.rect(screen, (0, 255, 0), square_rect, 3)

            piece = board.piece_at(row * 8 + col)
            if piece:
                piece_color = 'w' if piece.color == chess.WHITE else 'b'
                piece_type = piece.symbol().upper()
                image = images.get(f"{piece_color}{piece_type}")
                if image:
                    screen.blit(image, (display_col * SQUARE_SIZE, display_row * SQUARE_SIZE))

# Add hologram to the background
def draw_hologram():
    font = pygame.font.Font(None, 72)
    text = font.render("Made by Divyansh Rajput", True, (200, 200, 200, 50))
    text_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    text_surface.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    screen.blit(text_surface, (0, 0))

# Display game over message
def show_message(message):
    font = pygame.font.Font(None, 64)
    text = font.render(message, True, BLACK)
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    pygame.time.wait(3000)

# Get the square under the mouse click
def get_square_under_mouse():
    x, y = pygame.mouse.get_pos()
    return y // SQUARE_SIZE, x // SQUARE_SIZE

# Ask for user preferences
def get_user_preferences():
    font = pygame.font.Font(None, 36)
    selected_color = None
    selected_level = None

    while selected_color is None or selected_level is None:
        screen.fill(WHITE)
        draw_hologram()

        color_text = font.render("Choose your color: W for White, B for Black", True, BLACK)
        level_text = font.render("Choose level: 1 (Beginner), 2 (Intermediate), 3 (Difficult), 4 (GOAT)", True, BLACK)

        screen.blit(color_text, (WIDTH // 2 - color_text.get_width() // 2, HEIGHT // 3 - color_text.get_height() // 2))
        screen.blit(level_text, (WIDTH // 2 - level_text.get_width() // 2, HEIGHT // 2 - level_text.get_height() // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w:
                    selected_color = chess.WHITE
                elif event.key == pygame.K_b:
                    selected_color = chess.BLACK
                elif event.key == pygame.K_1:
                    selected_level = "Beginner"
                elif event.key == pygame.K_2:
                    selected_level = "Intermediate"
                elif event.key == pygame.K_3:
                    selected_level = "Difficult"
                elif event.key == pygame.K_4:
                    selected_level = "GOAT"

    return selected_color, selected_level

# Main game function
def play_game():
    clock = pygame.time.Clock()
    board = chess.Board()
    images = load_images()

    difficulty_levels = {"Beginner": 2.0, "Intermediate": 1.0, "Difficult": 0.5, "GOAT": 0.01}
    player_color, level = get_user_preferences()
    selected_square = None

    engine = chess.engine.SimpleEngine.popen_uci(engine_path)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                engine.quit()
                pygame.quit()
                return
            if event.type == pygame.MOUSEBUTTONDOWN:
                row, col = get_square_under_mouse()
                clicked_square = row * 8 + col

                if selected_square is None:
                    piece = board.piece_at(clicked_square)
                    if piece and piece.color == board.turn:
                        selected_square = clicked_square
                else:
                    move = chess.Move(selected_square, clicked_square)
                    if move in board.legal_moves:
                        board.push(move)

                        if board.is_checkmate():
                            show_message("Sorry, you lost! Better luck next time.")
                            engine.quit()
                            pygame.quit()
                            return

                        if board.is_check():
                            print("Check!")

                        if not board.is_game_over() and board.turn != player_color:
                            result = engine.play(board, chess.engine.Limit(time=difficulty_levels[level]))
                            board.push(result.move)

                            if board.is_checkmate():
                                show_message("Congratulations, you won!")
                                engine.quit()
                                pygame.quit()
                                return

                    selected_square = None

        screen.fill(WHITE)
        draw_hologram()
        draw_board(board, images, player_color, selected_square)
        pygame.display.flip()
        clock.tick(FPS)

if __name__ == "__main__":
    play_game()
