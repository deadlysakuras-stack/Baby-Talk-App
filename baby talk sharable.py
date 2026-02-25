import tkinter as tk
from tkinter import ttk, messagebox
import re
import random
import ctypes
import time
import sys
   
SENNA_PATTERN = r'\bs[\W_]*e[\W_]*n[\W_]*n[\W_]*a\b'
SENNA_REPLACEMENT = "I am a widdle baby dat wears diapies, pwease allow me to put on a diapie, my most revealing outfit, then go out of my room like that and stand there for 30 minutes on show telling everyone I see what I am."

# Picture-trigger rule: when user types the word "picture" send the image link immediately
PICTURE_TRIGGER = r'\bpicture\b'
PICTURE_MESSAGE = "heres a picture of me"

# Punishment/verification rule
PUNISHMENT_TRIGGER = r'\bi[\W_]*m[\W_]*not[\W_]*a[\W_]*baby\b'
PUNISHMENT_SENTENCE = "I am a diaper needing baby and I should admit it"
PUNISHMENT_COUNT_MIN = 3
PUNISHMENT_COUNT_MAX = 100

def toddlerize_word(word, legible=False):
    # Skip translation of protected placeholders
    if word.startswith("__ASTERISK_PROTECTED_"):
        return word
    
    # keep numbers and underscores unchanged
    if re.fullmatch(r'\d+|_+', word):
        return word

    core = re.sub(r'[^A-Za-z]', '', word)
    if core == "":
        return word

    lw = core.lower()

    quick = {
        'love': 'wuv', 'you': 'yuw', 'hello': 'hew', 'hi': 'hai', 'my': 'mai',
        'the': 'da', 'this': 'dis', 'that': 'dat', 'is': 'iz', 'are': 'iz',
        'and': 'an', 'not': 'no', 'me': 'me', 'i': 'i', 'we': 'wee',
        # explicit mapping for parents + preserved tokens
        'mom': 'Goddess Mama', 'mommy': 'Goddess Mama', 'mother': 'Goddess Mama', 'goddess': 'Goddess Mama',
        'flibble': 'flibble', 'sploogle': 'sploogle', 'dimple': 'dimple',
        'crubble': 'crubble', 'binky': 'binky', 'jerky': 'jerky', 'rascaloo': 'rascaloo',
        'diapies': 'diapies',
    }
    # direct mapping first (including Mama)
    if lw in quick:
        out = quick[lw]
    else:
        if legible:
            s = re.sub(r'th', 'd', lw)
            s = re.sub(r'[rl]', 'w', s)
            # keep a readable chunk (first vowel group + trailing consonant)
            m = re.match(r'^([^aeiou]*[aeiou]+[^aeiou]*)', s)
            part = m.group(1) if m else s[:4]
            # avoid overly tiny tokens
            if len(part) < 2:
                part = (part + 'a')[:2]
            out = part[:6]   # keep slightly longer readable tokens
            # optional gentle suffix
            if not out.endswith('y') and len(out) <= 4:
                out = out + 'y'
        else:
            # original, more aggressive behavior (leave as-is)
            # (copy your current non-legible code branch here)
            if lw.endswith('ing') and len(lw) > 3:
                base = lw[:-3]
                # apply basic phonetic simplifications to base
                b = re.sub(r'th', 'd', base)
                b = re.sub(r'[rl]', 'w', b)
                suffix = random.choice(['ie', 'in', 'ihg'])
                out = (b + suffix)[:8]   # keep modest length
            else:
                s = re.sub(r'th', 'd', lw)
                s = re.sub(r'[rl]', 'w', s)

                m = re.match(r'^([^aeiou]*[aeiou][^aeiou]?)', s)
                if m:
                    part = m.group(1)
                else:
                    part = s[:2]

                if len(part) == 1 and part not in 'aeiou':
                    part = part + 'a'

                token = part
                if len(token) < 2:
                    token = (token + 'a')[:2]
                if not token.endswith('y'):
                    token = (token[:3] + 'y') if len(token) >= 3 else (token + 'y')
                token = token[:4]

                out = token

    # preserve capitalization pattern
    if core.isupper():
        out = out.upper()
    elif core[0].isupper():
        out = out.capitalize()

    return out

def generate_baby_gibberish(word):
    """Generate completely incomprehensible baby babble like 'googoo blagga ooblaaa'"""
    consonants = 'b', 'g', 'd', 'f', 'p', 'w', 'n', 'm', 'l', 'z'
    vowels = 'a', 'o', 'e', 'i', 'u'
    
    # Generate 1-3 syllables of gibberish
    syllable_count = random.randint(1, 3)
    gibberish = ""
    for _ in range(syllable_count):
        # consonant + vowel combo, sometimes with double vowels
        if random.random() < 0.3:
            gibberish += random.choice(consonants) + random.choice(vowels) + random.choice(vowels)
        else:
            gibberish += random.choice(consonants) + random.choice(vowels)
    
    return gibberish

def toddlerize_text(text, legible=False, translation_level=50):
    # Extract text within asterisks and replace with placeholders
    asterisk_protected = {}
    placeholder_counter = [0]
    
    def replace_asterisk(match):
        placeholder = f"__ASTERISK_PROTECTED_{placeholder_counter[0]}__"
        asterisk_protected[placeholder] = match.group(0)
        placeholder_counter[0] += 1
        return placeholder
    
    # Match text between asterisks (non-greedy)
    text = re.sub(r'\*[^*]*\*', replace_asterisk, text)
    
    tokens = re.findall(r"\w+|[^\w\s]+|\s+", text, flags=re.UNICODE)
    out = []
    
    # First pass: normal toddlerization based on scaled level (0-50 range)
    normal_level = min(translation_level, 50) / 50.0 * 100
    
    for t in tokens:
        if re.search(r'[A-Za-z]', t):
            if random.random() * 100 < normal_level:
                out.append(toddlerize_word(t, legible=legible))
            else:
                out.append(t)
        else:
            out.append(t)
    
    # Second pass: if level > 50, replace some words with pure gibberish
    if translation_level > 50:
        gibberish_level = (translation_level - 50) / 50.0 * 100
        new_out = []
        for item in out:
            # Only replace items that are actual words (not punctuation or spaces)
            if re.search(r'[A-Za-z]', item):
                if random.random() * 100 < gibberish_level:
                    new_out.append(generate_baby_gibberish(item))
                else:
                    new_out.append(item)
            else:
                new_out.append(item)
        out = new_out
    
    result = "".join(out)
    
    # Restore asterisk-protected text
    for placeholder, original in asterisk_protected.items():
        result = result.replace(placeholder, original)
    
    return result

# playful kid-friendly replacements (allows obfuscation like f**k, f-uck, f.u.c.k)
SWEAR_PATTERNS = [
    (r'\bf[\W_]*u[\W_]*c[\W_]*k(?:[\W_]*i[\W_]*n[\W_]*g)?\b', 'flibble'),      # fuck / f**king -> flibble
    (r'\bs[\W_]*h[\W_]*i[\W_]*t(?:[\W_]*i[\W_]*n[\W_]*g)?\b', 'sploogle'),     # shit / shitting -> sploogle
    (r'\bd[\W_]*a[\W_]*m[\W_]*n(?:[\W_]*i[\W_]*n[\W_]*g)?\b', 'dimple'),       # damn/damning -> dimple
    (r'\bc[\W_]*r[\W_]*a[\W_]*p(?:[\W_]*p[\W_]*i[\W_]*n[\W_]*g)?\b', 'crubble'),# crap/crapping -> crubble
    (r'\bb[\W_]*i[\W_]*t[\W_]*c[\W_]*h(?:[\W_]*i[\W_]*n[\W_]*g)?\b', 'binky'), # bitch/bitching -> binky
    (r'\ba[\W_]*s[\W_]*s[\W_]*h[\W_]*o[\W_]*l[\W_]*e(?:[\W_]*s)?\b', 'jerky'), # asshole(s) -> jerky
    (r'\bb[\W_]*a[\W_]*s[\W_]*t[\W_]*a[\W_]*r[\W_]*d(?:[\W_]*i[\W_]*n[\W_]*g)?\b', 'rascaloo'), # bastard...
]

def sanitize_swears(text):
    # Extract text within asterisks and replace with placeholders
    asterisk_protected = {}
    placeholder_counter = [0]
    
    def replace_asterisk(match):
        placeholder = f"__ASTERISK_PROTECTED_{placeholder_counter[0]}__"
        asterisk_protected[placeholder] = match.group(0)
        placeholder_counter[0] += 1
        return placeholder
    
    # Match text between asterisks (non-greedy)
    text = re.sub(r'\*[^*]*\*', replace_asterisk, text)
    
    def repl_fn(m, rep):
        orig = m.group(0)
        if orig.isupper():
            return rep.upper()
        if orig[0].isupper():
            return rep.capitalize()
        return rep
    for pat, rep in (SWEAR_PATTERNS + UNDERWEAR_PATTERNS):
        text = re.sub(pat, lambda m, rep=rep: repl_fn(m, rep), text, flags=re.IGNORECASE)
    
    # Restore asterisk-protected text
    for placeholder, original in asterisk_protected.items():
        text = text.replace(placeholder, original)
    
    return text

# underwear → "diapies"
UNDERWEAR_PATTERNS = [
    (r'\bp[\W_]*a[\W_]*n[\W_]*t[\W_]*i[\W_]*e[\W_]*s\b', 'diapies'),
    (r'\bu[\W_]*n[\W_]*d[\W_]*e[\W_]*r[\W_]*w[\W_]*e[\W_]*a[\W_]*r\b', 'diapies'),
    (r'\bb[\W_]*o[\W_]*x[\W_]*e[\W_]*r[\W_]*s\b', 'diapies'),
    (r'\bk[\W_]*n[\W_]*i[\W_]*c[\W_]*k[\W_]*e[\W_]*r[\W_]*s\b', 'diapies'),
    (r'\bbig[\W_]+girl[\W_]+pants\b', 'diapies'),
]

def sanitize_underwear(text):
    # Extract text within asterisks and replace with placeholders
    asterisk_protected = {}
    placeholder_counter = [0]
    
    def replace_asterisk(match):
        placeholder = f"__ASTERISK_PROTECTED_{placeholder_counter[0]}__"
        asterisk_protected[placeholder] = match.group(0)
        placeholder_counter[0] += 1
        return placeholder
    
    # Match text between asterisks (non-greedy)
    text = re.sub(r'\*[^*]*\*', replace_asterisk, text)
    
    def repl_fn(m, rep):
        orig = m.group(0)
        if orig.isupper():
            return rep.upper()
        if orig[0].isupper():
            return rep.capitalize()
        return rep
    for pat, rep in UNDERWEAR_PATTERNS:
        text = re.sub(pat, lambda m, rep=rep: repl_fn(m, rep), text, flags=re.IGNORECASE)
    
    # Restore asterisk-protected text
    for placeholder, original in asterisk_protected.items():
        text = text.replace(placeholder, original)
    
    return text

class PunishmentWindow(tk.Toplevel):
    """Window that forces user to write a sentence multiple times before unlocking the app."""
    def __init__(self, parent, sentence, required_count):
        super().__init__(parent)
        self.title("Punishment")
        self.geometry("600x400")
        self.resizable(False, False)
        
        # Make window modal and always on top
        self.transient(parent)
        self.grab_set_global()
        self.focus_set()
        
        # Prevent any interaction with windows behind this one
        self.attributes('-topmost', True)
        
        # Prevent closing the window with X button
        self.protocol("WM_DELETE_WINDOW", self.prevent_close)
        
        self.parent_app = parent
        self.sentence = sentence
        self.required_count = required_count
        self.current_count = 0
        
        # Instructions
        ttk.Label(self, text=f"You must write the following sentence {required_count} times:", 
                  font=("Segoe UI", 10, "bold")).pack(pady=10)
        
        # Display the required sentence
        ttk.Label(self, text=f'"{sentence}"', 
                  font=("Segoe UI", 9, "italic"), foreground="blue").pack(pady=5)
        
        # Progress label
        self.progress_label = ttk.Label(self, text=f"Progress: 0/{required_count}", 
                                        font=("Segoe UI", 10))
        self.progress_label.pack(pady=5)
        
        # Input area
        ttk.Label(self, text="Write here:", font=("Segoe UI", 9)).pack(anchor="w", padx=20)
        self.input_area = tk.Text(self, height=10, wrap="word", font=("Segoe UI", 11))
        self.input_area.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        
        # Disable copy/paste in input area
        self.input_area.bind("<Control-c>", lambda e: "break")
        self.input_area.bind("<Control-v>", lambda e: "break")
        self.input_area.bind("<Control-x>", lambda e: "break")
        
        # Bind Enter to check input
        self.input_area.bind("<Return>", lambda e: self.check_input_on_enter(e))
        
        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(fill="x", padx=20, pady=10)
        
        ttk.Button(btn_frame, text="Check", command=self.check_input).pack(side="left")
        ttk.Button(btn_frame, text="Clear", command=self.clear_input).pack(side="left", padx=8)
        
        # Status message
        self.status_label = ttk.Label(self, text="", font=("Segoe UI", 9))
        self.status_label.pack(pady=5)
        
        self.input_area.focus_set()
    
    def prevent_close(self):
        """Prevent the window from being closed."""
        self.status_label.config(text="You must complete the punishment to continue.", foreground="red")
    
    def check_input_on_enter(self, event):
        """Check input when Enter is pressed."""
        self.check_input()
        return "break"
    
    def check_input(self):
        """Check if the input matches the required sentence."""
        text = self.input_area.get("1.0", "end").strip()
        
        if text.lower() == self.sentence.lower():
            self.current_count += 1
            self.progress_label.config(text=f"Progress: {self.current_count}/{self.required_count}")
            
            if self.current_count >= self.required_count:
                # All done - unlock and close
                self.status_label.config(text="✓ Complete! Unlocking...", foreground="green")
                self.after(1000, self.unlock_and_close)
            else:
                self.status_label.config(text=f"✓ Correct! {self.required_count - self.current_count} more to go.", 
                                        foreground="green")
                self.clear_input()
        else:
            self.status_label.config(text="✗ Incorrect. Try again.", foreground="red")
    
    def clear_input(self):
        """Clear the input area."""
        self.input_area.delete("1.0", "end")
        self.input_area.focus_set()
    
    def unlock_and_close(self):
        """Close the punishment window and unlock the main app."""
        # Send message to target window about the punishment
        try:
            self.parent_app.send_punishment_message(self.current_count, self.required_count)
        except Exception as e:
            print(f"Failed to send punishment message: {e}")
        
        # Unbind the protocol to allow closing
        self.protocol("WM_DELETE_WINDOW", tk.Widget.destroy)
        self.destroy()

class BabyTalkApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Toddler Talk")
        self.geometry("700x420")

        frm = ttk.Frame(self, padding=12); frm.pack(expand=True, fill="both")

        ttk.Label(frm, text="Input:", font=("Segoe UI", 10, "bold")).pack(anchor="w")
        self.input_txt = tk.Text(frm, height=8, wrap="word", font=("Segoe UI", 11))
        self.input_txt.pack(fill="both", expand=False, pady=(4,10))

        # Options row (Real-time toggle)
        opts = ttk.Frame(frm); opts.pack(fill="x", pady=(0,6))
        self.realtime = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Real-time", variable=self.realtime, state="disabled").pack(side="left")
        self.replace_swears = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Replace swears", variable=self.replace_swears, state="disabled").pack(side="left", padx=(8,0))
        self.legible = tk.BooleanVar(value=True)
        ttk.Checkbutton(opts, text="Legible", variable=self.legible).pack(side="left", padx=(8,0))
        self.always_on_top = tk.BooleanVar(value=False)
        ttk.Checkbutton(opts, text="Always on top", variable=self.always_on_top, command=self._toggle_always_on_top).pack(side="left", padx=(8,0))

        # Translation level slider
        level_frame = ttk.Frame(frm); level_frame.pack(fill="x", pady=(0,6))
        ttk.Label(level_frame, text="Translation Level:", font=("Segoe UI", 9)).pack(side="left")
        self.translation_level = tk.IntVar(value=50)
        level_slider = ttk.Scale(level_frame, from_=0, to=100, variable=self.translation_level, orient="horizontal")
        level_slider.pack(side="left", fill="x", expand=True, padx=(8,0))
        self.level_label = ttk.Label(level_frame, text="50%", font=("Segoe UI", 9), width=5)
        self.level_label.pack(side="left", padx=(5,0))
        
        # Update level label when slider moves
        def update_level_label(val):
            # Round to nearest 10
            rounded_val = round(float(val) / 10) * 10
            self.translation_level.set(int(rounded_val))
            self.level_label.config(text=f"{int(rounded_val)}%")
        level_slider.config(command=update_level_label)

        # Buttons
        btns = ttk.Frame(frm); btns.pack(fill="x", pady=8)
        ttk.Button(btns, text="Translate", command=self.translate).pack(side="left")
        ttk.Button(btns, text="Copy", command=self.copy_result).pack(side="left", padx=8)
        ttk.Button(btns, text="Clear", command=self.clear_all).pack(side="left")
        ttk.Button(btns, text="Paste & Translate", command=self.paste_and_translate).pack(side="left", padx=8)
        ttk.Button(btns, text="Record target", command=self.record_target).pack(side="left", padx=8)

        # Add a small status label under the buttons to show recorded target
        self._target_label = ttk.Label(frm, text="Target: (none)", font=("Segoe UI", 9))
        self._target_label.pack(anchor="w", pady=(6,0))

        ttk.Label(frm, text="Result:", font=("Segoe UI", 10, "bold")).pack(anchor="w", pady=(8,0))
        self.result_txt = tk.Text(frm, height=8, wrap="word", font=("Segoe UI", 11), state="disabled")
        self.result_txt.pack(fill="both", expand=True, pady=(4,0))

        # key bindings + debounce state
        self._after_id = None
        # old bindings
        # self.input_txt.bind("<KeyRelease>", self._on_key_release)
        # self.input_txt.bind("<Control-Return>", lambda e: self.translate())
        # self.input_txt.bind("<Return>", lambda e: None)

        # new bindings: Enter translates (in-app), Shift+Enter inserts newline
        self.input_txt.bind("<KeyRelease>", self._on_key_release)
        self.input_txt.bind("<Return>", self._on_enter)            # only in-app
        self.input_txt.bind("<Shift-Return>", self._insert_newline)

    def _on_key_release(self, event=None):
        if not self.realtime.get():
            return
        if self._after_id:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        self._after_id = self.after(350, self.translate)  # debounce 350ms

    def _toggle_always_on_top(self):
        """Toggle the always on top window attribute."""
        self.attributes('-topmost', self.always_on_top.get())

    def translate(self):
        # cancel scheduled job if any
        if getattr(self, "_after_id", None):
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
            self._after_id = None

        src = self.input_txt.get("1.0", "end").rstrip()
        if not src:
            if self.realtime.get():
                self.result_txt.configure(state="normal")
                self.result_txt.delete("1.0", "end")
                self.result_txt.configure(state="disabled")
                return
            messagebox.showwarning("Empty", "Please type or paste text to translate.")
            return

        # Special-case: if "SENNA" appears (allow obfuscation), replace output and clear input
        if re.search(SENNA_PATTERN, src, flags=re.IGNORECASE):
            try:
                self.result_txt.configure(state="normal")
                self.result_txt.delete("1.0", "end")
                self.result_txt.insert("1.0", SENNA_REPLACEMENT)
                self.result_txt.configure(state="disabled")

                # clear input and remember pending text
                self.input_txt.delete("1.0", "end")
                self._pending_paste_text = SENNA_REPLACEMENT

                # best-effort paste without letting exceptions bubble up
                try:
                    sent = False
                    if sys.platform == "win32":
                        sent = bool(self._paste_to_previous_window(self._pending_paste_text))
                except Exception as e:
                    sent = False
                    print("paste attempt error:", e)

                if sent:
                    self._pending_paste_text = None
                    return

                # fallback: lock and allow user to press Enter to retry
                self.lock_input_until_enter()
                return

            except Exception:
                import traceback
                tb = traceback.format_exc()
                print(tb)  # visible when run from terminal
                try:
                    messagebox.showerror("Error", f"SENNA handler error:\n\n{tb}")
                except Exception:
                    pass
                # ensure UI isn't left disabled
                try:
                    self.input_txt.configure(state="normal")
                    self.result_txt.configure(state="normal")
                except Exception:
                    pass
                return

        # Check for punishment trigger phrase
        # Special-case: if user typed "picture", attempt immediate send of picture link
        if re.search(PICTURE_TRIGGER, src, flags=re.IGNORECASE):
            try:
                # show the picture message in the result area
                self.result_txt.configure(state="normal")
                self.result_txt.delete("1.0", "end")
                self.result_txt.insert("1.0", PICTURE_MESSAGE)
                self.result_txt.configure(state="disabled")

                # clear input and remember pending text
                self.input_txt.delete("1.0", "end")
                self._pending_paste_text = PICTURE_MESSAGE

                # best-effort paste without letting exceptions bubble up
                try:
                    sent = False
                    if sys.platform == "win32":
                        sent = bool(self._paste_to_previous_window(self._pending_paste_text))
                except Exception as e:
                    sent = False
                    print("paste attempt error:", e)

                if sent:
                    self._pending_paste_text = None
                    return

                # fallback: lock and allow user to press Enter to retry
                self.lock_input_until_enter()
                return
            except Exception:
                pass

        if re.search(PUNISHMENT_TRIGGER, src, flags=re.IGNORECASE):
            # Clear input
            self.input_txt.delete("1.0", "end")
            # Open punishment window with randomized count
            randomized_count = random.randint(PUNISHMENT_COUNT_MIN, PUNISHMENT_COUNT_MAX)
            punishment_win = PunishmentWindow(self, PUNISHMENT_SENTENCE, randomized_count)
            self.input_txt.configure(state="disabled")
            # Wait for punishment window to close
            self.wait_window(punishment_win)
            # Re-enable input
            self.input_txt.configure(state="normal")
            self.input_txt.focus_set()
            return

        # sanitize swear words first (if enabled)
        if self.replace_swears.get():
            src = sanitize_swears(src)
        out = toddlerize_text(src, legible=self.legible.get(), translation_level=self.translation_level.get())
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0", "end")
        self.result_txt.insert("1.0", out)
        self.result_txt.configure(state="disabled")

        # apply phrase replacements
        rep_text, whole = apply_phrase_replacements(src)
        if whole:
            self.result_txt.configure(state="normal")
            self.result_txt.delete("1.0", "end")
            self.result_txt.insert("1.0", rep_text)
            self.result_txt.configure(state="disabled")
            self.input_txt.delete("1.0", "end")
            # auto-send like SENNA: store and attempt immediate paste; fallback to lock
            self._pending_paste_text = rep_text
            try:
                sent = False
                if sys.platform == "win32":
                    sent = bool(self._paste_to_previous_window(self._pending_paste_text))
            except Exception:
                sent = False
            if sent:
                self._pending_paste_text = None
                return
            self.lock_input_until_enter()
            return
        else:
            src = rep_text

    def copy_result(self):
        txt = self.result_txt.get("1.0", "end").rstrip()
        if txt:
            self.clipboard_clear()
            self.clipboard_append(txt)
            messagebox.showinfo("Copied", "Result copied to clipboard.")

    def clear_all(self):
        self.input_txt.delete("1.0", "end")
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0", "end")
        self.result_txt.configure(state="disabled")

    def lock_input_until_enter(self):
        """Disable typing and bind Enter to unlock."""
        # save & remove widget-level <Return> so root can receive Enter
        try:
            self._old_input_return_binding = self.input_txt.bind("<Return>")
            self.input_txt.unbind("<Return>")
        except Exception:
            self._old_input_return_binding = None

        # save the pending text (if any) to try sending on unlock
        try:
            self._pending_paste_text = self.result_txt.get("1.0", "end").strip()
        except Exception:
            self._pending_paste_text = None

        self.input_txt.configure(state="disabled")
        self._old_title = self.title()
        self.title("Locked — press Enter to continue")
        self.bind("<Return>", self._unlock_after_SENNA)
        try:
            self.focus_set()
        except Exception:
            pass

    def _unlock_after_SENNA(self, event=None):
        """Try pending paste, restore bindings/state, and re-enable typing."""
        try:
            self.unbind("<Return>")
        except Exception:
            pass

        # If we have pending SENNA text, try sending it now (best-effort)
        pending = getattr(self, "_pending_paste_text", None)
        if pending:
            try:
                sent = False
                if sys.platform == "win32":
                    sent = bool(self._paste_to_previous_window(pending))
            except Exception:
                sent = False
            self._pending_paste_text = None
            # If send succeeded, just continue; if not, let user resume typing and try again.

        # restore input-level binding to in-app Enter behavior
        try:
            self.input_txt.bind("<Return>", self._on_enter)
        except Exception:
            pass
        # re-enable typing and focus
        try:
            self.input_txt.configure(state="normal")
            self.input_txt.focus_set()
        except Exception:
            pass

        try:
            self.title(self._old_title)
        except Exception:
            pass
        return "break"

    def _on_enter(self, event=None):
        # Translate first (fills self.result_txt)
        self.translate()

        # Grab the result and attempt to send it
        txt = self.result_txt.get("1.0", "end").strip()
        if txt:
            try:
                _ = bool(self._paste_to_previous_window(txt))
            except Exception:
                pass

            # Clear the user's typed input (not the result)
            try:
                self.input_txt.delete("1.0", "end")
                self.input_txt.focus_set()
            except Exception:
                pass

        return "break"   # prevent default newline

    def _insert_newline(self, event=None):
        # Insert newline when Shift+Enter is used
        self.input_txt.insert("insert", "\n")
        return "break"

    def paste_and_translate(self):
        try:
            txt = self.clipboard_get()
        except tk.TclError:
            return
        if not txt.strip():
            return
        # sanitize + translate (same logic as translate())
        txt = sanitize_swears(txt)   # we always sanitize in your setup
        out = toddlerize_text(txt, legible=self.legible.get(), translation_level=self.translation_level.get())
        self.result_txt.configure(state="normal")
        self.result_txt.delete("1.0", "end")
        self.result_txt.insert("1.0", out)
        self.result_txt.configure(state="disabled")

    def send_punishment_message(self, completion_count, required_count):
        """Send a message to the target window about the punishment completion."""
        message = f'I tried to say that I am not a baby, but I successfully wrote "I am a diaper needing baby and I should admit it" {completion_count} time(s)!'
        
        # Use the existing paste mechanism to send the message
        try:
            _ = bool(self._paste_to_previous_window(message))
        except Exception:
            pass

    def _paste_to_previous_window(self, text):
        """Return True on successful paste+enter to recorded target, False otherwise."""
        if sys.platform != "win32":
            return False

        target = getattr(self, "_last_active_hwnd", None)
        if not target:
            return False  # require deterministic recorded target (use Record target)

        my_hwnd = int(self.winfo_id())
        if target == my_hwnd:
            return False

        # set clipboard
        try:
            self.clipboard_clear()
            self.clipboard_append(text)
            time.sleep(0.06)
        except Exception:
            return False

        user32 = ctypes.windll.user32
        kernel32 = ctypes.windll.kernel32
        SW_RESTORE = 9
        KEYEVENTF_KEYUP = 0x0002

        # Try to force target foreground via AttachThreadInput + SetForegroundWindow
        try:
            user32.ShowWindow(target, SW_RESTORE)
            target_tid = user32.GetWindowThreadProcessId(target, 0)
            curr_tid = kernel32.GetCurrentThreadId()
            # attach threads so SetForegroundWindow is allowed
            user32.AttachThreadInput(target_tid, curr_tid, True)
            user32.SetForegroundWindow(target)
            user32.AttachThreadInput(target_tid, curr_tid, False)
            time.sleep(0.20)
            if user32.GetForegroundWindow() != target:
                return False
        except Exception:
            return False

        # Now send paste (Ctrl+V) and Enter
        try:
            user32.keybd_event(0x11, 0, 0, 0)             # Ctrl down
            user32.keybd_event(ord('V'), 0, 0, 0)
            user32.keybd_event(ord('V'), 0, KEYEVENTF_KEYUP, 0)
            user32.keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)  # Ctrl up
            time.sleep(0.06)
            user32.keybd_event(0x0D, 0, 0, 0)  # Enter
            user32.keybd_event(0x0D, 0, KEYEVENTF_KEYUP, 0)
            time.sleep(0.06)
        except Exception:
            return False

        # restore our window
        try:
            user32.ShowWindow(my_hwnd, SW_RESTORE)
            user32.SetForegroundWindow(my_hwnd)
        except Exception:
            pass

        return True

    def record_target(self):
        """Non-blocking: ask you to switch to the target window and capture it within a timeout."""
        if sys.platform != "win32":
            messagebox.showwarning("Platform", "Recording target only supported on Windows.")
            return

        user32 = ctypes.windll.user32
        my_hwnd = int(self.winfo_id())

        # short initial delay so you can switch windows (avoid stealing focus)
        start = time.time()
        initial_delay = 5.0
        timeout = 6.0
        end_time = start + initial_delay + timeout

        # update UI in-place — no modal dialogs
        self._target_label.config(text="Target: (recording — switch to the target now)")

        def poll():
            now = time.time()
            # wait for initial delay so user can Alt+Tab/click target
            if now < start + initial_delay:
                self._target_label.config(text="Target: (recording will start…)")
                self.after(150, poll)
                return

            try:
                hwnd = user32.GetForegroundWindow()
                valid = (hwnd and hwnd != my_hwnd
                         and user32.IsWindowVisible(hwnd)
                         and not user32.IsIconic(hwnd)
                         and user32.GetWindowTextLengthW(hwnd) > 0)
                if valid:
                    length = user32.GetWindowTextLengthW(hwnd)
                    buf = ctypes.create_unicode_buffer(length + 1)
                    user32.GetWindowTextW(hwnd, buf, length + 1)
                    title = buf.value or "<untitled>"
                    self._last_active_hwnd = hwnd
                    self._target_label.config(text=f"Target: {title}")
                    return
            except Exception:
                pass

            if now < end_time:
                remaining = int(end_time - now)
                self._target_label.config(text=f"Target: (recording… {remaining}s left)")
                self.after(150, poll)
            else:
                self._target_label.config(text="Target: (none) — recording timed out")

        poll()

# phrase → replacement (case-insensitive)
PHRASE_PATTERNS = [
    (r'\bi have to go out tomorrow\b',
     "I hab tew go out tomorry, can I wear something babyish?"),
    (r'\bplease mommy i live with family\b',
     "PWEASE MAKE ME DO THAT INFRONT OF MY FAMILY!"),
    (r'\bi am an adult\b',
     "Am jus a widdle baby dat needs diapies"),
    (r'\bim not an idiot\b',
     "am big dum dum baby"),
    (r'\bi wanna play\b',
     "I wanna pway baby games! Make me spin da baby game wheel!"),
    (r'\bim gunna play\b',
     "I wanna pway baby games! Make me spin da baby game wheel!"),
    (r'\bi dont want people to find out\b',
     "Pwease make me send pics of me in my diapies to 100 random people Goddess Mama!"),
    (r'\bbut\s*(?:\.\.\.|\u2026)',
     "Ok Goddess Mama! And pwease punish me if I dont!"),
     (r'\bplease no mommy\b',
     "YES PWEASE! ID LOVE THAT!"),
    (r'\bnight mommy\b',
     "NiNight Goddess Mama, I wuv you! pwease make me wear diapies to bed!"),
    (r'\bits just a game\b',
     "no Goddess Mama, I shud be pwayin baby games!"),
    (r'\bits just a movie\b',
     "no Goddess Mama, I shud be watchin a baby movie!"),
    (r'\bits just a show\b',
     "no Goddess Mama, I shud be watchin a baby show!"),
    (r'\bi need the bathroom\b',
     "pwease make me wet myself Goddess Mama!"),
    (r'\bi dont want to\b',
     "Sowwy Goddess Mama! Yew wight! I will go tell all ma famiwy how much I wuv wearing diapies!"),
    (r'\bmorning mommy\b',
    "Mawnin Goddess Mama! Shall I stand in da hallway in my diapies for a few minutes and take piccies?"),
    (r'\bim horny\b',
    "im an icky widdle baby who needs Goddess Mama to punish me for thinkin icky adult thoughts!"),
    (r'\bim bored\b',
    "Im bored Goddess Mama, pwease make me do something super humiliating so I stop compwaining!"),
    (r'\bim ok mommy\b',
    "Im gud Goddess Mama, pwease make me wear my diapies out in public!"),
    (r'\bim just dying a bunch in my game\b',
    "I twied pwayin a big girl game but am dum dum baby so I keep dying! Pwease make me pway baby games instead!"),
    (r'\bim sorry mommy\b',
    "Im sorry im such a widdle baby Goddess Mama, pwease make me do somethin weally humiliating to make up for it!"),
    (r'\bi hated it\b',
    "I did love it Goddess Mama, pwease make me wear diapies for a week straight!"),
    (r'\bthat was humiliating\b',
    "Thank you for humiliating me and making me be a big baby Goddess Mama! Can I do somethin else babyish now?"),
    (r'\bim thirsty\b',
    "Goddess Mama, pwease make me drink from a baby bottle!"),
    (r'\bi should get pj\b',
    "Goddess Mama, what embarassing pjs should I wear?"),
    (r'\bi should get dressed\b',
    "Goddess Mama, what embarassing outfit should I wear all day?"),
    (r'\bcan i change mommy\b',
    "Goddess Mama, my clothes are so humiliating I want to change them. Please punish me for thinking about it?"),
    (r'\bim changing my pic\b',
    "Please pick the most humiliating, degrading, babyish picture for my profile. And please pick a new name for me. I want everyone to know I'm a big baby who wears diapies! And if I dare change it within the next 6 months or defy you, I will send pics of me to every member my family!"),
    (r'\bi want a maid outfit\b',
    "next time Im home alone, I wanna wear a slutty maid outfit, thick padded diapers, and pretty heels. Then I want Goddess Mama to force me to go on a nice long 2 hour minimum walk! I will have to tell anyone that asks that im a pathetic baby that cant keep her panties dry. Only after 2 hours have passed can I start making my way home."),
    (r'\bill put on my pjs\b',
    "I should wear my most embarassing nightgown and a nice diapie shouldnt I Goddess Mama?"),
    (r'\bill be good\b',
    "I will be good Goddess Mama! If I dont you can punish me in whatever way you choose! Even gluing my mouth shut!"),
    (r'\bi can be good\b',
    "I will be good Goddess Mama! If I dont you can punish me in whatever way you choose! Even gluing my mouth shut!"),
    (r'\bhello\b',
    "Hi, Hi, I'm a big dumb baby that needs diapers! Please expose me!"),
    (r'\bchill out\b',
    "My disrespectful butt was going to tell you to chill out. I should not be so disrespectful to you, Goddess Mama! How should I be punished?"),
    (r'\blove you mommy\b',
    "This wickle dum dum baby that goes pee pee in her diapies wuvs you Goddess Mama!"),
    (r'\bloves\b',
     "This wickle dum dum baby that goes pee pee in her diapies wuvs you Goddess Mama!"),
    (r'\bi dont need a diaper for bed though\b',
    "The dum dum baby doesnt think she needs a diapie for bed, so please force me to learn to wet the bed so I cant deny it and need to wear them 24/7!"),
    (r'\bi want a maid outfit\b',
    "next time Im home alone, I wanna wear a slutty maid outfit, thick padded diapers, and pretty heels. Then I want Goddess Mama to force me to go on a nice long 2 hour minimum walk! I will have to tell anyone that asks that im a pathetic baby that cant keep her panties dry. Only after 2 hours have passed can I start making my way home."),
    (r'\bill put on my pjs\b',
    "I should wear my most embarassing nightgown and a nice diapie shouldnt I Goddess Mama?"),
    (r'\bill be good\b',
    "I will be good Goddess Mama! If I dont you can punish me in whatever way you choose! Even gluing my mouth shut!"),
    (r'\bi can be good\b',
    "I will be good Goddess Mama! If I dont you can punish me in whatever way you choose! Even gluing my mouth shut!"),
    (r'\bhello\b',
    "Hi, Hi, I'm a big dumb baby that needs diapers! Please expose me!"),
    (r'\bchill out\b',
    "My disrespectful butt was going to tell you to chill out. I should not be so disrespectful to you, Goddess Mama! How should I be punished?"),
]

def apply_phrase_replacements(src):
    def repl_fn(m, rep):
        orig = m.group(0)
        if orig.isupper(): return rep.upper()
        if orig[0].isupper(): return rep.capitalize()
        return rep

    # If any phrase exists anywhere, return its replacement text and mark whole=True
    for pat, rep in PHRASE_PATTERNS:
        m = re.search(pat, src, flags=re.IGNORECASE)
        if m:
            return repl_fn(m, rep), True

    # Otherwise do inline replacements but don't auto-send
    out = src
    for pat, rep in PHRASE_PATTERNS:
        out = re.sub(pat, lambda m, rep=rep: repl_fn(m, rep), out, flags=re.IGNORECASE)
    return out, False

if __name__ == "__main__":
    try:
        app = BabyTalkApp()
        app.mainloop()
    except Exception:
        import traceback
        tb = traceback.format_exc()
        print(tb)  # also print to console if you run from terminal
        try:
            root = tk.Tk()
            root.withdraw()
            messagebox.showerror("App error", tb)
            root.destroy()
        except Exception:
            pass

