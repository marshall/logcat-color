import re

RegexType = type(re.compile(""))

class Profile(object):
    __profiles__ = {}

    @classmethod
    def get_profile(cls, name):
        return cls.__profiles__.get(name, None)

    def __init__(self, name=None, tags=None, priorities=None, filters=None,
            buffers=None, wrap=True, device=None, emulator=None, format=None,
            packages=None):
        if not name:
            raise Exception("Profile is missing a name")

        self.name = name
        self.__profiles__[name] = self

        self.init_tags(tags)
        self.init_priorities(priorities)
        self.init_filters(filters)
        self.init_packages(packages)
        self.buffers = buffers
        self.wrap = wrap
        self.device = device
        self.emulator = emulator
        self.format = format

    def init_packages(self, packages):

        self.pid_map = {}
        self.package_search = {}
        
        if packages:
            for package in packages:
                search_string = 'Start proc ' + package
                regex = re.compile(search_string + ".*?pid=(\\d+)", re.IGNORECASE|re.DOTALL)
                self.package_search[package] = (search_string, regex)

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

        if not isinstance(filters, (list, tuple)):
            filters = [filters]

        for filter in filters:
            if isinstance(filter, (str, RegexType)):
                self.filters.append(self.regex_filter(filter))
            else:
                self.filters.append(filter)

    def regex_filter(self, regex):
        pattern = regex
        if not isinstance(regex, RegexType):
            pattern = re.compile(regex)

        def __filter(data):
            if "message" not in data:
                return True
            return pattern.search(data["message"])
        return __filter

    def process_new_pid(self, data):
        string = data.get('message')
        if string and string.startswith('Start proc'):
            for package in self.package_search:
                match = self.package_search[package][1].search(string)
                if match:
                    self.pid_map[package] = match.group(1)

    def include(self, data):
        if not data:
            raise Exception("data should not be None")

        self.process_new_pid(data)  #process pid

        if self.tags and data.get("tag") not in self.tags:
            return False

        if self.priorities and data.get("priority") not in self.priorities:
            return False

        if self.package_search and data.get("pid") not in self.pid_map.values():
            return False

        if not self.filters:
            return True

        for filter in self.filters:
            if not filter(data):
                return False

        return True
