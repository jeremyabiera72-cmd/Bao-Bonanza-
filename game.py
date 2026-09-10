import pygame
import math
import sys
import os
import random
from assets.data.npc_dialogue import get_random_dialogue, get_win_dialogue, get_lose_dialogue


# ── Pixel font helper ─────────────────────────────────────────────────────────
def _make_pixel_font(size, bold=False):
    for name in ["Press Start 2P", "Courier New", "Courier", "monospace"]:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.SysFont("arial", size, bold=bold)


def pix(font, text, color):
    """No-antialias render for crisp pixel look."""
    return font.render(text, False, color)


# ── Wood sign drawing helpers ─────────────────────────────────────────────────
WOOD_MID = (140, 90, 38)
WOOD_LIGHT = (185, 130, 65)
WOOD_DARK = (101, 65, 27)
WOOD_GRAIN = (160, 108, 44)
BORDER_GOLD = (218, 175, 80)
BORDER_DK = (160, 120, 40)
TXT_CREAM = (255, 245, 210)
TXT_GOLD = (240, 200, 80)
SCROLL_CLR = (200, 155, 70)


def draw_wood_panel(surface, rect, highlight=False, corner_r=12):
    shadow = pygame.Surface((rect.w + 6, rect.h + 6), pygame.SRCALPHA)
    pygame.draw.rect(shadow, (0, 0, 0, 100), shadow.get_rect(), border_radius=corner_r + 3)
    surface.blit(shadow, (rect.x + 3, rect.y + 3))
    base = WOOD_LIGHT if highlight else WOOD_MID
    pygame.draw.rect(surface, base, rect, border_radius=corner_r)
    for i in range(2):
        gy = rect.y + rect.h // 3 * (i + 1)
        pygame.draw.line(surface, WOOD_GRAIN, (rect.x + 8, gy), (rect.x + rect.w - 8, gy), 1)
    pygame.draw.rect(surface, WOOD_DARK, rect.inflate(-4, -4), width=2, border_radius=corner_r - 2)
    pygame.draw.rect(surface, BORDER_GOLD, rect, width=3, border_radius=corner_r)
    pygame.draw.rect(surface, BORDER_DK, rect.inflate(-8, -8), width=2, border_radius=corner_r - 3)


def draw_scroll(surface, cx, y, width=100):
    pts = []
    for i in range(61):
        t = i / 60
        px = cx - width // 2 + int(t * width)
        py = y + int(math.sin(t * math.pi * 4) * 3)
        pts.append((px, py))
    if len(pts) > 1:
        pygame.draw.lines(surface, SCROLL_CLR, False, pts, 2)


def draw_wood_button(surface, rect, font, label, hovered=False):
    draw_wood_panel(surface, rect, highlight=hovered, corner_r=10)
    col = TXT_GOLD if hovered else TXT_CREAM
    txt = pix(font, label, col)
    surface.blit(txt, txt.get_rect(center=rect.center))
    draw_scroll(surface, rect.centerx, rect.bottom - int(rect.h * 0.22), width=int(rect.w * 0.5))


def draw_speech_bubble(surface, font, text, cx, top_y, screen_w):
    padding_x, padding_y = 18, 12
    txt_surf = pix(font, text, (255, 255, 255))
    tw, th = txt_surf.get_size()
    bw = tw + padding_x * 2
    bh = th + padding_y * 2
    tail = 12

    bx = cx - bw // 2
    by = top_y - bh - tail - 6

    bx = max(10, min(bx, screen_w - bw - 10))

    box_rect = pygame.Rect(bx, by, bw, bh)
    draw_wood_panel(surface, box_rect, corner_r=8)
    surface.blit(txt_surf, txt_surf.get_rect(center=box_rect.center))

    tail_cx = cx
    tail_top = by + bh
    pts = [(tail_cx - 8, tail_top), (tail_cx + 8, tail_top), (tail_cx, tail_top + tail)]
    pygame.draw.polygon(surface, WOOD_MID, pts)
    pygame.draw.polygon(surface, BORDER_GOLD, pts, 2)


# ── Pause Overlay ─────────────────────────────────────────────────────────────
def draw_pause_menu(surface, font_title, font_btn, resume_rect, quit_rect, mouse_pos, w, h):
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 160))
    surface.blit(dim, (0, 0))

    panel = pygame.Rect(w // 2 - 200, h // 2 - 160, 400, 320)
    draw_wood_panel(surface, panel, corner_r=16)

    title = pix(font_title, "NATIGIL", TXT_GOLD)
    surface.blit(title, title.get_rect(center=(w // 2, panel.y + 55)))
    pygame.draw.line(surface, BORDER_GOLD, (panel.x + 20, panel.y + 95), (panel.right - 20, panel.y + 95), 2)

    draw_wood_button(surface, resume_rect, font_btn, "TULOY", hovered=resume_rect.collidepoint(mouse_pos))
    draw_wood_button(surface, quit_rect, font_btn, "BACK TO MENU", hovered=quit_rect.collidepoint(mouse_pos))


def draw_try_again_menu(surface, font_btn, try_again_rect, mouse_pos, w, h):
    dim = pygame.Surface((w, h), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 160))
    surface.blit(dim, (0, 0))

    panel = pygame.Rect(w // 2 - 180, h // 2 - 90, 360, 180)
    draw_wood_panel(surface, panel, corner_r=16)

    draw_wood_button(surface, try_again_rect, font_btn, "TRY AGAIN", hovered=try_again_rect.collidepoint(mouse_pos))


# ─────────────────────────────────────────────────────────────────────────────

def run_game():
    pygame.init()

    has_audio = False
    try:
        if not pygame.mixer.get_init():
            pygame.mixer.init()
        has_audio = True
    except (NotImplementedError, AttributeError, Exception):
        print("Audio driver unavailable. Playing without sound.")

    display_screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
    WIDTH, HEIGHT = 1280, 720
    screen = pygame.Surface((WIDTH, HEIGHT))
    pygame.display.set_caption("Bao Bonanza")

    BASE_DIR = os.path.dirname(__file__)
    IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
    AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")

    bg_img = pygame.image.load(os.path.join(IMG_DIR, "background.png")).convert()
    bg_img = pygame.transform.scale(bg_img, (WIDTH, HEIGHT))
    npc_img = pygame.image.load(os.path.join(IMG_DIR, "npc.png")).convert_alpha()
    npc_smile = pygame.image.load(os.path.join(IMG_DIR, "npcSmiling.png")).convert_alpha()
    npc_shy = pygame.image.load(os.path.join(IMG_DIR, "shyNPC.png")).convert_alpha()

    npc_h = int(HEIGHT * 0.65)
    npc_w = int(npc_img.get_width() * (npc_h / npc_img.get_height()))
    npc_img = pygame.transform.smoothscale(npc_img, (npc_w, npc_h))
    npc_smile = pygame.transform.smoothscale(npc_smile, (npc_w, npc_h))
    npc_shy = pygame.transform.smoothscale(npc_shy, (npc_w, npc_h))

    cup_w, cup_h = int(WIDTH * 0.16), int(HEIGHT * 0.30)
    raw_cup = pygame.image.load(os.path.join(IMG_DIR, "cupAsset.png")).convert_alpha()
    cup_sprite = pygame.transform.smoothscale(raw_cup, (cup_w, cup_h))
    raw_up = pygame.image.load(os.path.join(IMG_DIR, "upCupAsset.png")).convert_alpha()
    up_cup_sprite = pygame.transform.smoothscale(raw_up, (cup_w, cup_h))

    raw_ball = pygame.image.load(os.path.join(IMG_DIR, "shellball.png")).convert_alpha()
    ball_size = int(cup_w * 0.55)
    ball_sprite = pygame.transform.smoothscale(raw_ball, (ball_size, ball_size))

    music_path = os.path.join(AUDIO_DIR, "bg.mp3")
    if has_audio and os.path.exists(music_path):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)

    # Fonts
    font_score = _make_pixel_font(int(HEIGHT * 0.035), bold=True)
    font_dialogue = _make_pixel_font(int(HEIGHT * 0.028), bold=True)
    font_btn = _make_pixel_font(int(HEIGHT * 0.032), bold=True)
    font_pause_hd = _make_pixel_font(int(HEIGHT * 0.048), bold=True)

    # Interface Buttons
    menu_btn_rect = pygame.Rect(WIDTH - 140, 14, 120, 44)
    resume_rect = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 - 30, 260, 60)
    quit_rect = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 + 50, 260, 60)
    try_again_rect = pygame.Rect(WIDTH // 2 - 130, HEIGHT // 2 - 20, 260, 60)

    score = 0
    current_npc_img = npc_img
    current_dialogue = get_random_dialogue()
    paused = False

    def get_game_settings(sc):
        num_cups = min(5, 3 + (sc // 10))
        spd = min(0.1, 0.035 + (sc // 10) * 0.01)
        return num_cups, spd

    def get_spots(nc):
        spot_y = int(HEIGHT * 0.8)
        spacing = int(WIDTH / (nc + 1))
        return [(spacing * (i + 1), spot_y) for i in range(nc)]

    class CupShell:
        def __init__(self, idx, is_win=False, spots=None, spd=0.035):
            self.spot_index = idx
            self.is_winning_cup = is_win
            self.spots = spots
            self.x, self.y = spots[idx]
            self.start_x = self.x
            self.start_y = self.y
            self.target_x = self.x
            self.target_y = self.y
            self.anim_progress = 1.0
            self.anim_speed = spd
            self.is_lifted = False
            self.lift_offset = 0.0

        def move_to_spot(self, new_idx):
            self.spot_index = new_idx
            self.start_x, self.start_y = self.x, self.y
            self.target_x, self.target_y = self.spots[new_idx]
            self.anim_progress = 0.0
            self.is_lifted = False

        def update(self):
            if self.anim_progress < 1.0:
                self.anim_progress = min(1.0, self.anim_progress + self.anim_speed)
                t = self.anim_progress
                st = t * t * (3 - 2 * t)
                self.x = self.start_x + (self.target_x - self.start_x) * st
                by = self.start_y + (self.target_y - self.start_y) * st
                self.y = by - math.sin(t * math.pi) * cup_h * 0.3
            if self.is_lifted:
                if self.lift_offset > -cup_h * 0.8:
                    self.lift_offset -= cup_h * 0.06
            else:
                if self.lift_offset < 0.0:
                    self.lift_offset += cup_h * 0.06

        def draw(self, surface):
            if self.is_winning_cup and self.lift_offset < -cup_h * 0.2:
                ball_bottom_y = int(self.y + cup_h * 0.45)
                ball_rect = ball_sprite.get_rect(midbottom=(int(self.x), ball_bottom_y))
                surface.blit(ball_sprite, ball_rect)
            sprite = up_cup_sprite if self.is_lifted else cup_sprite
            rect = sprite.get_rect(center=(int(self.x), int(self.y + self.lift_offset)))
            surface.blit(sprite, rect)
            return rect

    num_cups, anim_speed = get_game_settings(score)
    SPOTS = get_spots(num_cups)
    winning_spot = random.randint(0, num_cups - 1)
    shells = [CupShell(i, is_win=(winning_spot == i), spots=SPOTS, spd=anim_speed) for i in range(num_cups)]
    for s in shells:
        s.is_lifted = True

    def swap_shells(a, b):
        sa, sb = shells[a].spot_index, shells[b].spot_index
        shells[a].move_to_spot(sb)
        shells[b].move_to_spot(sa)

    clock = pygame.time.Clock()
    game_state = "STARTING"
    state_timer = 90
    shuffle_count = 0

    while True:
        clock.tick(60)
        win_w, win_h = display_screen.get_size()
        scale = min(win_w / WIDTH, win_h / HEIGHT)
        new_w, new_h = int(WIDTH * scale), int(HEIGHT * scale)
        x_offset = (win_w - new_w) // 2
        y_offset = (win_h - new_h) // 2

        raw_mouse = pygame.mouse.get_pos()
        mouse_pos = (
            int((raw_mouse[0] - x_offset) / scale),
            int((raw_mouse[1] - y_offset) / scale)
        )

        for event in pygame.event.get():
            if event.type == pygame.VIDEORESIZE:
                if event.w > 0 and event.h > 0 and (event.w, event.h) != display_screen.get_size():
                    display_screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
            if event.type == pygame.QUIT:
                return "quit"

            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, getattr(pygame, 'K_AC_BACK', 1073742094)):
                paused = not paused

            # Handle both Mouse and Touch inputs
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.FINGERDOWN:
                if event.type == pygame.FINGERDOWN:
                    raw_input = (int(event.x * win_w), int(event.y * win_h))
                else:
                    raw_input = event.pos
                
                input_pos = (
                    int((raw_input[0] - x_offset) / scale),
                    int((raw_input[1] - y_offset) / scale)
                )

                if paused:
                    if resume_rect.collidepoint(input_pos):
                        paused = False
                    elif quit_rect.collidepoint(input_pos):
                        return "menu"
                else:
                    if menu_btn_rect.collidepoint(input_pos):
                        paused = True
                    elif game_state == "WAITING":
                        for shell in shells:
                            rect = cup_sprite.get_rect(center=(int(shell.x), int(shell.y)))
                            if rect.collidepoint(input_pos):
                                shell.is_lifted = True
                                if shell.is_winning_cup:
                                    current_dialogue = get_win_dialogue()
                                    current_npc_img = npc_smile
                                    score += 1
                                    game_state = "REVEALING"
                                    state_timer = 120
                                else:
                                    current_dialogue = get_lose_dialogue()
                                    current_npc_img = npc_shy
                                    for s in shells:
                                        if s.is_winning_cup:
                                            s.is_lifted = True
                                    game_state = "LOST"
                                break

                    elif game_state == "LOST":
                        if try_again_rect.collidepoint(input_pos):
                            score = 0
                            num_cups, anim_speed = get_game_settings(score)
                            SPOTS = get_spots(num_cups)
                            winning_spot = random.randint(0, num_cups - 1)
                            shells = [CupShell(i, is_win=(winning_spot == i), spots=SPOTS, spd=anim_speed) for i in range(num_cups)]
                            for s in shells:
                                s.is_lifted = True
                            game_state = "STARTING"
                            state_timer = 90
                            current_dialogue = get_random_dialogue()
                            current_npc_img = npc_img

        # ── Game Logic Updates ────────────────────────────────────────────────
        if not paused:
            if game_state == "STARTING":
                state_timer -= 1
                if state_timer <= 0:
                    for s in shells:
                        s.is_lifted = False
                    game_state = "SHUFFLING"
                    shuffle_count = random.randint(5 + score, 10 + score)
                    current_dialogue = "Hinahaluin..."

            elif game_state == "SHUFFLING":
                if all(s.anim_progress >= 1.0 for s in shells) and all(s.lift_offset >= 0.0 for s in shells):
                    if shuffle_count > 0:
                        a, b = random.sample(range(num_cups), 2)
                        swap_shells(a, b)
                        shuffle_count -= 1
                    else:
                        game_state = "WAITING"
                        current_dialogue = "Saan ang bola? Hula na!"

            elif game_state == "REVEALING":
                state_timer -= 1
                if state_timer <= 0:
                    num_cups, anim_speed = get_game_settings(score)
                    SPOTS = get_spots(num_cups)
                    winning_spot = random.randint(0, num_cups - 1)
                    shells = [CupShell(i, is_win=(winning_spot == i), spots=SPOTS, spd=anim_speed) for i in range(num_cups)]
                    for s in shells:
                        s.is_lifted = True
                    game_state = "STARTING"
                    state_timer = 90
                    current_dialogue = get_random_dialogue()
                    current_npc_img = npc_img

            for s in shells:
                s.update()

        # ── Render ────────────────────────────────────────────────────────────
        screen.blit(bg_img, (0, 0))

        time_ms = pygame.time.get_ticks()
        breathe_offset = ((time_ms // 600) % 2) * 2
        table_y = int(HEIGHT * 0.755)
        npc_rect = current_npc_img.get_rect(midbottom=(WIDTH // 2, table_y + breathe_offset))
        screen.blit(current_npc_img, npc_rect)

        table_strip = pygame.Rect(0, table_y, WIDTH, HEIGHT - table_y)
        screen.blit(bg_img, (0, table_y), table_strip)

        for s in shells:
            s.draw(screen)

        score_surf = pix(font_score, f"Score: {score}", TXT_GOLD)
        sc_bg = score_surf.get_rect(topleft=(14, 14)).inflate(20, 12)
        draw_wood_panel(screen, sc_bg, corner_r=8)
        screen.blit(score_surf, score_surf.get_rect(center=sc_bg.center))

        draw_wood_button(screen, menu_btn_rect, font_btn, "MENU", hovered=menu_btn_rect.collidepoint(mouse_pos))

        npc_head_y = npc_rect.top + int(npc_h * 0.15)
        draw_speech_bubble(screen, font_dialogue, current_dialogue, WIDTH // 2, npc_head_y, WIDTH)

        if paused:
            draw_pause_menu(screen, font_pause_hd, font_btn, resume_rect, quit_rect, mouse_pos, WIDTH, HEIGHT)
        elif game_state == "LOST":
            draw_try_again_menu(screen, font_btn, try_again_rect, mouse_pos, WIDTH, HEIGHT)

        # Scale virtual screen to display
        display_screen.fill((0, 0, 0))
        if new_w > 0 and new_h > 0:
            scaled_surf = pygame.transform.scale(screen, (new_w, new_h))
            display_screen.blit(scaled_surf, (x_offset, y_offset))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run_game()