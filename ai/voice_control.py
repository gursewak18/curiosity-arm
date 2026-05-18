"""Voice command placeholder for autonomous robotics stages."""


class VoiceCommandParser:
    def parse(self, text: str) -> str:
        normalized = text.strip().lower()
        if "pick" in normalized:
            return "pick"
        if "reset" in normalized:
            return "reset"
        return "unknown"

