from __future__ import division, print_function, unicode_literals
from .base import Num2Word_Base


class Num2Word_BG(Num2Word_Base):
    def setup(self):
        self.negword = "минус"
        self.pointword = "запетая"
        self.exclude_title = ["и", "запетая", "минус"]

        self.mid_num_words = [
            (1000, "хиляда"),
            (100, "сто"),
            (90, "деветдесет"),
            (80, "осемдесет"),
            (70, "седемдесет"),
            (60, "шестдесет"),
            (50, "петдесет"),
            (40, "четиридесет"),
            (30, "тридесет"),
            (20, "двадесет"),
            (19, "деветнадесет"),
            (18, "осемнадесет"),
            (17, "седемнадесет"),
            (16, "шестнадесет"),
            (15, "петнадесет"),
            (14, "четиринадесет"),
            (13, "тринадесет"),
            (12, "дванадесет"),
            (11, "единадесет"),
            (10, "десет"),
            (9, "девет"),
            (8, "осем"),
            (7, "седем"),
            (6, "шест"),
            (5, "пет"),
            (4, "четири"),
            (3, "три"),
            (2, "две"),
            (1, "едно"),
            (0, "нула"),
        ]

        self.high_num_words = [
            (10**30, "квинтилион", "квинтилиона"),
            (10**24, "квадрилион", "квадрилиона"),
            (10**18, "трилион", "трилиона"),
            (10**12, "билион", "билиона"),
            (10**9, "милиард", "милиарда"),
            (10**6, "милион", "милиона"),
            (10**3, "хиляда", "хиляди"),
        ]

        self.ordinals = {
            1: "първи",
            2: "втори",
            3: "трети",
            4: "четвърти",
            5: "пети",
            6: "шести",
            7: "седми",
            8: "осми",
            9: "девети",
            10: "десети",
            11: "единадесети",
            12: "дванадесети",
            20: "двадесети",
            100: "стотен",
            200: "двустотен",
            300: "тристотен",
            1000: "хиляден"
        }

    def to_cardinal(self, value):
        try:
            val = int(value)
        except ValueError:
            return value

        if val == 0:
            return "нула"

        str_val = str(val)
        chunks = []
        while str_val:
            chunks.append(int(str_val[-3:]))
            str_val = str_val[:-3]
        
        chunks = chunks[::-1]
        words = []
        
        for i, chunk in enumerate(chunks):
            if chunk == 0:
                continue
                
            magnitude = 10 ** (3 * (len(chunks) - 1 - i))
            
            scale_name = ""
            if magnitude >= 1000:
                for s_val, s_sing, s_pl in self.high_num_words:
                    if s_val == magnitude:
                        scale_name = s_sing if chunk == 1 else s_pl
                        break

            chunk_text = self._convert_triplet(chunk, magnitude)
            
            if chunk_text:
                words.append(chunk_text)
            if scale_name:
                words.append(scale_name)

        # Global logic for "и" between chunks (e.g. 1001 -> hilyada i edno)
        # We only add global "i" if the last chunk is small (<100) or round hundreds?
        # A simple check: if result > 1 word and "и" is missing in the last part.
        
        if len(words) > 1:
            # Flatten to check the last word connector
            full_sentence = " ".join(words)
            # If the sentence doesn't have "и" near the end, we might need it.
            # However, for simplicity and fixing your error, let's rely on 
            # the fact that usually triplets handle internal "and".
            # We add an external "and" only if the last chunk was < 100.
            
            last_chunk = chunks[-1]
            if last_chunk < 100 and last_chunk > 0:
                 # Check if "и" is already there (e.g. 21 -> dvadeset i edno)
                 # If last_chunk is < 20 or round tens, it won't have "и".
                 # If last_chunk is 21, it HAS "и".
                 
                 last_segment = words[-1]
                 if " и " not in last_segment:
                     words.insert(-1, "и")

        return " ".join(words)

    def _convert_triplet(self, num, magnitude):
        if num == 0:
            return ""

        # Collect raw words first, then join them with "и" logic later
        parts = []
        hundreds = num // 100
        remainder = num % 100
        
        # 1. Hundreds
        if hundreds > 0:
            if hundreds == 1:
                parts.append("сто")
            elif hundreds == 2:
                parts.append("двеста")
            elif hundreds == 3:
                parts.append("триста")
            else:
                base = self._get_base_cardinal(hundreds)
                parts.append(base + "стотин")

        # 2. Tens/Units
        if remainder > 0:
            # Gender logic
            gender_suffix_1 = "едно"
            gender_suffix_2 = "две"

            if magnitude == 1000:
                # 1000 -> "hilyada" (no 'one'), but 2000 -> "dve hilyadi"
                if num == 1: return "" # Don't say "edna" for 1000
                gender_suffix_1 = "една"
                gender_suffix_2 = "две"
            elif magnitude >= 1000000:
                gender_suffix_1 = "един"
                gender_suffix_2 = "два"

            if remainder < 20:
                if remainder == 1:
                    parts.append(gender_suffix_1)
                elif remainder == 2:
                    parts.append(gender_suffix_2)
                else:
                    parts.append(self._get_base_cardinal(remainder))
            else:
                tens = remainder // 10
                units = remainder % 10
                parts.append(self._get_base_cardinal(tens * 10))
                if units > 0:
                    # Note: We do NOT add "и" here. We add it in the join step below.
                    if units == 1:
                        parts.append(gender_suffix_1)
                    elif units == 2:
                        parts.append(gender_suffix_2)
                    else:
                        parts.append(self._get_base_cardinal(units))

        # Join Logic: In a triplet, "и" is placed before the LAST element 
        # if there are multiple elements.
        # e.g. [100, 20, 1] -> 100 20 i 1
        # e.g. [20, 1] -> 20 i 1
        # e.g. [100, 1] -> 100 i 1
        
        if len(parts) > 1:
            parts.insert(-1, "и")

        return " ".join(parts)

    def _get_base_cardinal(self, val):
        for num, name in self.mid_num_words:
            if num == val:
                return name
        return ""

    def to_ordinal(self, value):
        try:
            val = int(value)
        except ValueError:
            return value
            
        if val in self.ordinals:
            return self.ordinals[val]
            
        cardinal = self.to_cardinal(value)
        words = cardinal.split()
        if not words: return ""
        
        last_word = words[-1]
        
        # Morphological replacements for ordinals
        replacements = [
            ("едно", "първи"),
            ("една", "първа"),
            ("един", "първи"),
            ("две", "втори"),
            ("два", "втори"),
            ("три", "трети"),
            ("четири", "четвърти"),
            ("пет", "пети"),
            ("шест", "шести"),
            ("седем", "седми"),
            ("осем", "осми"),
            ("девет", "девети"),
            ("десет", "десети"),
            ("надесет", "надесети"), # covers 11-19
            ("десет", "десети"), # covers 20, 30... (dvadeset -> dvadeseti)
            ("стотин", "стотен"),
            ("хиляда", "хиляден"),
            ("милион", "милионен")
        ]
        
        found = False
        for suffix, replacement in replacements:
            if last_word.endswith(suffix):
                # Handle special case where -deset becomes -deseti (simple append)
                if suffix == "десет" and not last_word.endswith("надесет"):
                     words[-1] = last_word + "и"
                elif suffix == "надесет":
                     words[-1] = last_word + "и"
                else:
                     # Replace the suffix
                     words[-1] = last_word[:-len(suffix)] + replacement
                found = True
                break
        
        if not found:
            words[-1] = last_word + "-ти"

        return " ".join(words)