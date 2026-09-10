import pygame
import sys
import os
import math
import game

pygame.init()

has_audio = False
try:
    if not pygame.mixer.get_init():
        pygame.mixer.init()
    has_audio = True
except Exception:
    print("Audio driver unavailable. Playing without sound.")

display_screen = pygame.display.set_mode((1280, 720), pygame.RESIZABLE)
WIDTH, HEIGHT = 1280, 720
screen = pygame.Surface((WIDTH, HEIGHT))
pygame.display.set_caption("Bao Bonanza")

BASE_DIR = os.path.dirname(__file__)
IMG_DIR = os.path.join(BASE_DIR, "assets", "images")
AUDIO_DIR = os.path.join(BASE_DIR, "assets", "audio")

if has_audio:
    music_path = os.path.join(AUDIO_DIR, "bg.mp3")
    if os.path.exists(music_path):
        if not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)

bg_raw = pygame.image.load(os.path.join(IMG_DIR, "background.png")).convert()
bg_img = pygame.transform.scale(bg_raw, (WIDTH, HEIGHT))

# Load NPC and scale
npc_raw = pygame.image.load(os.path.join(IMG_DIR, "npc.png")).convert_alpha()
npc_h_menu = int(HEIGHT * 0.65)
npc_w_menu = int(npc_raw.get_width() * (npc_h_menu / npc_raw.get_height()))
npc_menu_img = pygame.transform.smoothscale(npc_raw, (npc_w_menu, npc_h_menu))

# ── Fonts — pixel style ───────────────────────────────────────────────────────
_pix_candidates = ["Press Start 2P", "Courier New", "Courier", "monospace"]


def _best_font(size, bold=False):
    for name in _pix_candidates:
        try:
            f = pygame.font.SysFont(name, size, bold=bold)
            if f:
                return f
        except Exception:
            pass
    return pygame.font.SysFont("arial", size, bold=bold)


font_title_lg = _best_font(int(HEIGHT * 0.075), bold=True)
font_btn = _best_font(int(HEIGHT * 0.040), bold=True)
font_about_hd = _best_font(int(HEIGHT * 0.045), bold=True)
font_about_bod = _best_font(int(HEIGHT * 0.026), bold=False)


def pixel_text(font, text, color):
    """Render then scale with no smoothing for chunky pixel look."""
    surf = font.render(text, False, color)
    w, h = surf.get_size()
    return pygame.transform.scale(surf, (w, h))


# ── Colours ───────────────────────────────────────────────────────────────────
WOOD_DARK = (101, 65, 27)
WOOD_MID = (140, 90, 38)
WOOD_LIGHT = (185, 130, 65)
WOOD_GRAIN = (160, 108, 44)
BORDER_GOLD = (218, 175, 80)
BORDER_DK = (160, 120, 40)
TXT_CREAM = (255, 245, 210)
TXT_GOLD = (240, 200, 80)
SCROLL_CLR = (200, 155, 70)

clock = pygame.time.Clock()

# ── Layout constants ──────────────────────────────────────────────────────────
cx = WIDTH // 2
btn_w, btn_h = int(WIDTH * 0.28), int(HEIGHT * 0.13)
gap = int(HEIGHT * 0.03)

start_btn_rect = pygame.Rect(cx - btn_w // 2, int(HEIGHT * 0.28), btn_w, int(btn_h * 1.15))
about_btn_rect = pygame.Rect(cx - btn_w // 2, start_btn_rect.bottom + gap, btn_w, btn_h)
exit_btn_rect = pygame.Rect(cx - btn_w // 2, about_btn_rect.bottom + gap, btn_w, btn_h)

# About panel dimensions
_pw = int(WIDTH * 0.6)
_ph = int(HEIGHT * 0.72)
_panel = pygame.Rect((WIDTH - _pw) // 2, (HEIGHT - _ph) // 2, _pw, _ph)
BACK_BTN_RECT = pygame.Rect(cx - 100, _panel.bottom - 70, 200, 50)


# ── Drawing helpers ───────────────────────────────────────────────────────────

def draw_wood_sign(surface, rect, highlight=False, corner_r=14):
    shadow_surf = pygame.Surface((rect.w + 8, rect.h + 8), pygame.SRCALPHA)
    pygame.draw.rect(shadow_surf, (0, 0, 0, 100), shadow_surf.get_rect(), border_radius=corner_r + 4)
    surface.blit(shadow_surf, (rect.x + 4, rect.y + 4))

    base_col = WOOD_LIGHT if highlight else WOOD_MID
    pygame.draw.rect(surface, base_col, rect, border_radius=corner_r)

    for i in range(3):
        gy = rect.y + rect.h // 4 * (i + 1)
        pygame.draw.line(surface, WOOD_GRAIN, (rect.x + 12, gy), (rect.x + rect.w - 12, gy), 1)

    bevel = rect.inflate(-6, -6)
    pygame.draw.rect(surface, WOOD_DARK, bevel, width=3, border_radius=corner_r - 2)
    pygame.draw.rect(surface, BORDER_GOLD, rect, width=3, border_radius=corner_r)
    inner = rect.inflate(-10, -10)
    pygame.draw.rect(surface, BORDER_DK, inner, width=2, border_radius=corner_r - 4)


def draw_scroll_ornament(surface, cx_pos, y, width=120):
    pts = []
    for i in range(61):
        t = i / 60
        px = cx_pos - width // 2 + int(t * width)
        py = y + int(math.sin(t * math.pi * 4) * 4)
        pts.append((px, py))
    if len(pts) > 1:
        pygame.draw.lines(surface, SCROLL_CLR, False, pts, 2)


def draw_button(surface, rect, label, hovered=False):
    draw_wood_sign(surface, rect, highlight=hovered)
    txt_col = TXT_GOLD if hovered else TXT_CREAM
    txt = pixel_text(font_btn, label, txt_col)
    surface.blit(txt, txt.get_rect(center=rect.center))
    draw_scroll_ornament(surface, rect.centerx, rect.bottom - int(rect.h * 0.22), width=int(rect.w * 0.55))


def draw_about_panel(surface, mouse_pos):
    dim = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    dim.fill((0, 0, 0, 170))
    surface.blit(dim, (0, 0))

    draw_wood_sign(surface, _panel, corner_r=18)

    hdr = pixel_text(font_about_hd, "- About -", TXT_GOLD)
    surface.blit(hdr, hdr.get_rect(center=(cx, _panel.y + int(_ph * 0.10))))

    divider_y = _panel.y + int(_ph * 0.18)
    pygame.draw.line(surface, BORDER_GOLD, (_panel.x + 30, divider_y), (_panel.right - 30, divider_y), 2)

    about_lines = [
        ("Developer", "Crystelle Faith Gorgonio"),
        ("", ""),
        ("Game Title", "Bao Bonanza"),
        ("Genre", "Puzzle / Arcade"),
        ("Platform", "PC (Python / Pygame)"),
        ("", ""),
        ("How to Play", "Watch the ball, pick the right cup!"),
        ("", "Every 10 pts: +1 cup & faster speed"),
        ("Max Cups", "5 cups"),
        ("", ""),
        ("", "(c) 2025  Crystelle Faith Gorgonio"),
    ]

    ly = divider_y + int(_ph * 0.06)
    lh = int(_ph * 0.075)
    for label, value in about_lines:
        if label == "" and value == "":
            ly += lh // 2
            continue
        if label:
            lbl_s = pixel_text(font_about_bod, label + ":", TXT_GOLD)
            surface.blit(lbl_s, (_panel.x + 40, ly))
        val_s = pixel_text(font_about_bod, value, TXT_CREAM)
        surface.blit(val_s, (_panel.x + int(_pw * 0.40), ly))
        ly += lh

    hov_back = BACK_BTN_RECT.collidepoint(mouse_pos)
    draw_button(surface, BACK_BTN_RECT, "BACK", hovered=hov_back)


# ── Main menu loop ────────────────────────────────────────────────────────────

def main_menu():
    global display_screen
    showing_about = False

    while True:
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
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, getattr(pygame, 'K_AC_BACK', 1073742094)):
                if showing_about:
                    showing_about = False
                # Do not auto exit on back button on main menu

            # ── TOUCH & MOUSE SUPPORT ─────────────────────────────────────────
            if (event.type == pygame.MOUSEBUTTONDOWN and event.button == 1) or event.type == pygame.FINGERDOWN:
                if event.type == pygame.FINGERDOWN:
                    raw_input = (int(event.x * win_w), int(event.y * win_h))
                else:
                    raw_input = event.pos
                
                touch_pos = (
                    int((raw_input[0] - x_offset) / scale),
                    int((raw_input[1] - y_offset) / scale)
                )

                if showing_about:
                    if BACK_BTN_RECT.collidepoint(touch_pos):
                        showing_about = False
                else:
                    if start_btn_rect.collidepoint(touch_pos):
                        res = game.run_game()
                        if res == "quit":
                            pygame.quit()
                            sys.exit()

                    elif about_btn_rect.collidepoint(touch_pos):
                        showing_about = True

                    elif exit_btn_rect.collidepoint(touch_pos):
                        pygame.quit()
                        sys.exit()

        # ── Draw ──────────────────────────────────────────────────────────────
        screen.blit(bg_img, (0, 0))

        if not showing_about:
            time_ms = pygame.time.get_ticks()
            breathe_offset = ((time_ms // 600) % 2) * 2

            npc_x = int(WIDTH * 0.82)
            npc_bottom_y = int(HEIGHT * 0.76) + breathe_offset

            npc_menu_rect = npc_menu_img.get_rect(midbottom=(npc_x, npc_bottom_y))
            screen.blit(npc_menu_img, npc_menu_rect)

            shadow_t = pixel_text(font_title_lg, "BAO BONANZA", (60, 30, 0))
            big_t = pixel_text(font_title_lg, "BAO BONANZA", TXT_GOLD)
            screen.blit(shadow_t, shadow_t.get_rect(center=(cx + 3, int(HEIGHT * 0.14) + 3)))
            screen.blit(big_t, big_t.get_rect(center=(cx, int(HEIGHT * 0.14))))

            hov_start = start_btn_rect.collidepoint(mouse_pos)
            hov_about = about_btn_rect.collidepoint(mouse_pos)
            hov_exit = exit_btn_rect.collidepoint(mouse_pos)

            draw_button(screen, start_btn_rect, "START GAME", hovered=hov_start)
            draw_button(screen, about_btn_rect, "ABOUT", hovered=hov_about)
            draw_button(screen, exit_btn_rect, "EXIT", hovered=hov_exit)
        else:
            draw_about_panel(screen, mouse_pos)

        display_screen.fill((0, 0, 0))
        if new_w > 0 and new_h > 0:
            scaled_surf = pygame.transform.scale(screen, (new_w, new_h))
            display_screen.blit(scaled_surf, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    main_menu()