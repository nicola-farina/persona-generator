from personas.models.attributes import Attributes


class UserDataSource(object):
    def __init__(self,
                 source_name: str,
                 source_user_id: str,
                 username: str = None,
                 attributes: Attributes = None):
        self.source_name = source_name
        self.source_user_id = source_user_id
        self.username = username
        self.attributes = attributes

    def __repr__(self):
        string = "DATA SOURCE: "
        separator = ""
        for key, value in self.__dict__.items():
            if value is not None:
                string += f"{separator}{key} = {value}"
                separator = ", "
        return string
