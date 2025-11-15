from curses import *
import random
from time import time as T

DEFAULT_WORDS_PER_RUN = 25

tgtWords = open("neuromancer.txt").read().split()
clrEnd = 12 * " "

WORD_OPTIONS = [5, 10, 15, 20, 25]

def split_text_to_lines(text, max_lines):
    words = text.split()
    lines = []
    cur = []
    approx = (len(text) // max_lines) + 5

    for word in words:
        if len(lines) == max_lines:
            break
        if len(cur) == 0:
            cur.append(word)
        else:
            tmp = " ".join(cur) + " " + word
            if len(tmp) <= approx:
                cur.append(word)
            else:
                line = " ".join(cur)
                lines.append(line)
                cur = [word]

    if len(lines) < max_lines and len(cur) > 0:
        last = " ".join(cur)
        lines.append(last)

    while len(lines) < max_lines:
        lines.append("")

    return lines[:max_lines]

def show_main_menu(stdscr, theme=None, words_per_run=25):
    while True:
        stdscr.clear()
        
        height, width = stdscr.getmaxyx()
        
        ascii_art = [
            "     _____             __  ",
            "    / ___/______ _____/ /__",
            "   / /__/ __/ _ `/ __/  '_/",
            "   \\___/_/  \\_,_/\\__/_/\\_\\ ",
            "     / _ )___ __________ __",
            "    / _  / -_) __/ __/ // /",
            "   /____/\\__/_/ /_/  \\_, / ",
            "                    /___/  "
        ]
        
        art_width = len(ascii_art[0])
        art_height = len(ascii_art)
        start_col = max(0, (width - art_width) // 2)
        start_row = max(0, (height - art_height - 8) // 2)
        
        for i, line in enumerate(ascii_art):
            row_pos = start_row + i
            if 0 <= row_pos < height and 0 <= start_col < width:
                try:
                    stdscr.addstr(row_pos, start_col, line)
                except:
                    pass
        
        menu_options = [
            "w - white theme",
            "b - black theme", 
            "s - words: " + str(words_per_run).rjust(2),
            "",
            "esc to exit"
        ]
        
        menu_start_row = start_row + art_height + 2
        
        for i, option in enumerate(menu_options):
            row_pos = menu_start_row + i
            if 0 <= row_pos < height:
                option_center = max(0, (width - len(option)) // 2)
                try:
                    stdscr.addstr(row_pos, option_center, option)
                except:
                    pass
        
        stdscr.refresh()
        
        try:
            key = stdscr.getkey().lower()
        except:
            continue
            
        if key == "\x1B":
            return None, words_per_run
        if key in ['w', 'b']:
            return key, words_per_run
        if key == 's':
            current_index = WORD_OPTIONS.index(words_per_run)
            next_index = (current_index + 1) % len(WORD_OPTIONS)
            words_per_run = WORD_OPTIONS[next_index]

def setup_colors(theme):
    if theme == 'w':
        init_pair(1, 0, 2) 
        init_pair(2, 0, 1) 
        init_pair(3, 0, 7) 
        init_pair(4, 0, 3)
        init_pair(5, 7, 0) 
        return {
            'correct_col': color_pair(1),
            'incorrect_col': color_pair(2),
            'not_typed_col': color_pair(3),
            'stats_bg_col': color_pair(4),
            'stats_text_col': color_pair(4),
            'instruction_col': color_pair(5)
        }
    else:
        init_pair(1, 2, 0)
        init_pair(2, 1, 0)
        init_pair(3, 7, 0) 
        init_pair(5, 7, 0) 
        return {
            'correct_col': color_pair(1),
            'incorrect_col': color_pair(2),
            'not_typed_col': color_pair(3),
            'stats_bg_col': color_pair(3),
            'stats_text_col': color_pair(3),
            'instruction_col': color_pair(5)
        }

def main(stdscr):
    curs_set(0)
    start_color()
    
    words_per_run = DEFAULT_WORDS_PER_RUN
    
    result = show_main_menu(stdscr, words_per_run=words_per_run)
    if result[0] is None: 
        return
    
    theme, words_per_run = result
    colors = setup_colors(theme)

    while True: 
        lines_per_run = (words_per_run + 4) // 5
        
        if len(tgtWords) < words_per_run:
            stdscr.clear()
            stdscr.addstr(2, 8, "not enough words")
            stdscr.addstr(3, 8, "press any key to exit")
            try:
                stdscr.getkey()
            except:
                pass
            break

        sl = random.sample(tgtWords, words_per_run)

        tgt = ""
        for i, w in enumerate(sl):
            if i < len(sl)-1:
                tgt += w + " "
            else:
                tgt += w

        total_len = len(tgt)
        lines = split_text_to_lines(tgt, lines_per_run)

        tgt_no_trailing = ""
        for line in lines:
            if line:
                tgt_no_trailing += line

        line_boundaries = []
        pos = 0
        for line in lines:
            if line:
                line_boundaries.append((pos, pos + len(line)))
                pos += len(line)

        usr = []
        stdscr.clear()

        sT = None
        runTest = True

        while runTest:
            char_i = 0
            line_start_positions = [0]
            
            current_pos = 0
            for line in lines:
                if line:
                    current_pos += len(line)
                    line_start_positions.append(current_pos)

            for li in range(lines_per_run):
                ln = lines[li]
                stdscr.move(2 + li, 2)
                stdscr.clrtoeol()

                if ln: 
                    L = len(ln)
                    for i in range(L):
                        ch = ln[i]
                        
                        if char_i < len(usr):
                            if usr[char_i] == ch:
                                col = colors['correct_col']
                            else:
                                col = colors['incorrect_col']
                        else:
                            col = colors['not_typed_col']

                        stdscr.addch(2 + li, 2 + i, ch, col)
                        char_i += 1

            length = len(usr)

            if sT:
                el = T() - sT
                if el > 0:
                    correct_chars = 0
                    for i in range(min(length, len(tgt_no_trailing))):
                        if usr[i] == tgt_no_trailing[i]:
                            correct_chars += 1
                    
                    spd = int((correct_chars / 5) / (el / 60.0))
                else:
                    spd = 0
            else:
                spd = 0

            if length > 0:
                corr = 0
                for i in range(length):
                    if i < len(tgt_no_trailing) and usr[i] == tgt_no_trailing[i]:
                        corr += 1
                acc = int(100 * corr / length) if length > 0 else 100
            else:
                acc = 100

            for i in range(9, 12):
                stdscr.move(i, 0)
                stdscr.clrtoeol()
            
            if theme == 'w':
                box_width = 24
                box_x = 2
                box_y = 8 
                box_height = 4
                
                for row in range(box_y + 1, box_y + box_height - 1):
                    stdscr.addstr(row, box_x + 1, " " * (box_width - 4), colors['stats_bg_col'])
                
                stdscr.addstr(9, 4, "speed     " + str(spd).rjust(3) + " wpm", colors['stats_text_col']) 
                stdscr.addstr(10, 4, "clean     " + str(acc).rjust(3) + " %", colors['stats_text_col']) 
            else:
                stdscr.addstr(9, 4, " speed     " + str(spd).rjust(3) + " wpm", colors['stats_text_col']) 
                stdscr.addstr(10, 4, " clean     " + str(acc).rjust(3) + " %", colors['stats_text_col']) 
            
            stdscr.refresh()

            if length == len(tgt_no_trailing):
                stdscr.addstr(12, 2, "esc to main menu, enter for next", colors['instruction_col'])
                stdscr.refresh()
                while True:
                    try:
                        k = stdscr.getkey()
                    except:
                        continue
                    if k == "\n":
                        break
                    elif k == "\x1B": 
                        runTest = False
                        break
                break

            try:
                k = stdscr.getkey()
            except:
                continue

            if k == "\x1B":
                runTest = False
                break

            if k == "\n" and length > 0:
                break

            if k in ("KEY_BACKSPACE", "\b", "\x7f"):
                if usr:
                    usr.pop()
                continue

            if len(k) > 1:
                continue

            if k == " ":
                if length < len(tgt_no_trailing):
                    current_line = 0
                    pos_in_flat = 0
                    for i, line in enumerate(lines):
                        if length >= pos_in_flat + len(line):
                            pos_in_flat += len(line)
                            current_line += 1
                        else:
                            break
                    
                    if (current_line < len(lines) - 1 and 
                        length == pos_in_flat + len(lines[current_line]) and
                        lines[current_line]): 
                        pass
                    elif length < len(tgt_no_trailing) and tgt_no_trailing[length] == " ":
                        pass
                    else:
                        continue
            
            if sT is None:
                sT = T()

            usr.append(k)
        
        if runTest == False: 
            new_theme, new_words = show_main_menu(stdscr, theme, words_per_run)
            if new_theme is None:
                break
            if new_theme != theme: 
                theme = new_theme
                words_per_run = new_words
                colors = setup_colors(theme)
            else:
                words_per_run = new_words


if __name__ == "__main__":
    wrapper(main)
