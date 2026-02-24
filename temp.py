# class Tag:
#     def __init__(self, name, group, category):
#         self.name = name
#         self.group = group
#         self.category = category


# a = Tag("payment correct", "payment", "good")
# b = Tag("payment delay", "payment", "bad")
# c = Tag("rude bevavior", "behavior", "bad")
# d = Tag("good bevavior", "behavior", "good")
# tags = [d, c]


# def validate_tags(tags):
#     groups = []
#     for tag in tags:
#         groups.append(tag.group)

#     if len(groups) != len(set(groups)):
#         seen = set()
#         duplicates = set(x for x in groups if x in seen or seen.add(x))
#         print(
#             f"You cannot select conflicting tags from the same category: {', '.join(duplicates)}"
#         )
#     else:
#         print("OK")


# validate_tags(tags)
