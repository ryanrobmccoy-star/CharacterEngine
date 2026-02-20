import re

class ClassConfig:
    def __init__(self, class_json):
        self.data = class_json
        self.core_traits = self._extract_core_traits()

    def _extract_core_traits(self):
        for table in self.data["tables"]:
            if table[0][0].startswith("Core"):
                return {row[0]: row[1] for row in table[1:]}
        return {}

    @property
    def hit_die(self):
        text = self.core_traits.get("Hit Point Die", "")
        match = re.search(r"D(\d+)", text)
        return int(match.group(1)) if match else None

    @property
    def saving_throws(self):
        text = self.core_traits.get("Saving Throw Proficiencies", "")
        return [
            s.strip()
            for s in text.replace(" and ", ",").split(",")
        ]

    @property
    def primary_ability(self):
        return self.core_traits.get("Primary Ability")
