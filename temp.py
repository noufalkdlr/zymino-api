tags = [
    {"name": "correct payment", "category": "POSITIVE", "group": "payment"},
    {"name": "payment deley", "category": "NEGATIVE", "group": "payment"},
    {"name": "rude behavior", "category": "NEGATIVE", "group": "behavior"},
]


def validate_tags(tags):
    groups = [tag["group"] for tag in tags]

    if len(groups) != len(set(groups)):
        seen = set()
        duplicates = set(x for x in groups if x in seen or seen.add(x))
        return seen, duplicates

    return tags


unique, duplicate = validate_tags(tags)
print(unique)
print(duplicate)
