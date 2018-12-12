import re


class PathProcessor:
    def __init__(self, resource_type, parent_type=None, parent_id=None, id=None):
        self.resource_type = resource_type
        self.parent_type = parent_type
        self.parent_id = parent_id
        self.id = id
        self.path_list = None

    def path(self):
        self.path_list = self.path_list or self.__process_path_list()
        return '/'.join(self.path_list)

    def __process_path_list(self):
        path_list = ['']
        if self.parent_type and self.parent_id:
            path_list.append(self.url_for_type(self.parent_type))
            path_list.append(self.url_for_type(self.parent_id))
            path_list.append('relationships')
        path_list.append(self.url_for_type(self.resource_type))
        if self.id:
            path_list.append(str(self.id))
        return path_list

    @staticmethod
    def url_for_type(resource_type):
        return re.sub('-', '_', str(resource_type))


def process_path(resource_type, parent_type=None, parent_id=None, id=None):
    return PathProcessor(resource_type, parent_type=parent_type, parent_id=parent_id, id=id).path()
