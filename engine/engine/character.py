from engine.skills import SKILL_TO_ABILITY

ABILITY_FULL = {
    "STR": "Strength",
    "DEX": "Dexterity",
    "CON": "Constitution",
    "INT": "Intelligence",
    "WIS": "Wisdom",
    "CHA": "Charisma"
}


class Character:
    def __init__(self, payload, class_config):
        self.payload = payload
        self.config = class_config

        self.level = payload["level"]
        self.abilities = payload["abilities"]

        self.mods = {
            k: (v - 10) // 2
            for k, v in self.abilities.items()
        }

        self.prof_bonus = 2 + (self.level - 1) // 4

    # ------------------------
    # Core Calculations
    # ------------------------

    def hit_points(self):
        hit_die = self.config.hit_die
        con_mod = self.mods["CON"]

        first = hit_die + con_mod
        avg_per_level = (hit_die // 2) + 1 + con_mod

        return first + (self.level - 1) * avg_per_level

    def armor_class(self):
        return 10 + self.mods["DEX"]

    def saving_throws(self):
        saves = {}

        for short, mod in self.mods.items():
            full = ABILITY_FULL[short]

            if full in self.config.saving_throws:
                saves[short] = mod + self.prof_bonus
            else:
                saves[short] = mod

        return saves

    # ------------------------
    # Spellcasting
    # ------------------------

    def spellcasting_mod(self):
        primary = self.config.primary_ability
        short = primary[:3].upper()
        return self.mods[short]

    def spell_save_dc(self):
        return 8 + self.prof_bonus + self.spellcasting_mod()

    def spell_attack_bonus(self):
        return self.prof_bonus + self.spellcasting_mod()

    # ------------------------
    # Skills
    # ------------------------

    def skills(self):
        computed = {}
        chosen = set(self.payload.get("skill_proficiencies", []))

        for skill, ability in SKILL_TO_ABILITY.items():
            mod = self.mods[ability]
            proficient = skill in chosen

            total = mod + (self.prof_bonus if proficient else 0)

            computed[skill] = {
                "total": total,
                "proficient": proficient
            }

        return computed

    # ------------------------
    # Final Build
    # ------------------------

    def build(self):
        return {
            "name": self.payload["name"],
            "class": self.payload["class"],
            "subclass": self.payload["subclass"],
            "level": self.level,
            "abilities": self.abilities,
            "mods": self.mods,
            "prof_bonus": self.prof_bonus,
            "hp": self.hit_points(),
            "ac": self.armor_class(),
            "saving_throws": self.saving_throws(),
            "spell_dc": self.spell_save_dc(),
            "spell_attack": self.spell_attack_bonus(),
            "skills": self.skills(),
            "spells": self.payload["spells"]
        }
