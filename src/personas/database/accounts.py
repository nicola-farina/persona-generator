from personas.database.abstract import Database


class AccountsDatabase(Database):
    def __init__(self):
        super().__init__()
