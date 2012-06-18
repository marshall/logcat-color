import re

class Profile(object):
    __profiles__ = {}

    @classmethod
    def get_profile(cls, name):
        return cls.__profiles__.get(name, None)

    def __init__(self, name=None, tags=None, priorities=None, filters=None,
            buffers=None):
        self.name = name
        self.__profiles__[name] = self

        self.init_tags(tags)
        self.init_priorities(priorities)
        self.init_filters(filters)
        self.buffers = buffers

    def init_tags(self, tags):
        self.tags = None
        self.tag_colors = None
        if isinstance(tags, dict):
            self.tags = tags.keys()
            self.tag_colors = tags
        elif isinstance(tags, (list, tuple)):
            self.tags = tags
        elif tags:
            self.tags = (tags)

    def init_priorities(self, priorities):
        self.priorities = None
        if isinstance(priorities, (list, tuple)):
            self.priorities = priorities
        elif priorities:
            self.priorities = (priorities)

    def init_filters(self, filters):
        self.filters = []
        if not filters:
            return

        for filter in filters:
            if isinstance(filter, str):
                self.filters.append(self.regex_filter(filter))
            else:
                self.filters.append(filter)

    def regex_filter(self, regex):
        pattern = re.compile(regex)
        return lambda tag, priority, message: re.search(pattern, message)

    def include(self, tag, priority, message):
        if self.tags and tag not in self.tags:
            return False

        if self.priorities and priority not in self.priorities:
            return False

        if self.filters:
            for filter in self.filters:
                if filter(tag, priority, message):
                    return True
            return False

        return True

    def get_buffers(self):
        return self.buffers

    def get_tag_colors(self):
        return self.tag_colors
