import re
import demoji
import string


def remove_emoji(text: str) -> str:
    regex_pattern = re.compile(pattern="["
                                        u"\U0001F170-\U0001F18F"  # Emoji letters
                                        "]+", flags=re.UNICODE)

    text = demoji.replace(text, repl="")
    text = regex_pattern.sub(u"", text)
    return text


def remove_leading_trailing_spaces(text: str) -> str:
    return text.strip()


def remove_symbols(text: str) -> str:
    excluded_list = string.punctuation + string.digits
    table = str.maketrans("", "", excluded_list)
    return text.translate(table)


if __name__ == "__main__":
    demoji.download_codes()
