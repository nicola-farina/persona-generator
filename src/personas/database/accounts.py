from typing import Union, List

from rejson import Path

from personas.database.connection import DatabaseConnection
from personas.database.utils import generate_id
from personas.models.account import Account


class AccountsDatabase(object):
    def __init__(self, connection: DatabaseConnection) -> None:
        self.connection = connection.connection

    @staticmethod
    def __get_key(account_id: str) -> str:
        return f"account:{account_id}"

    def save_account(self, account: Account) -> None:
        if account.account_id is None:
            account.account_id = generate_id()
        key = self.__get_key(account.account_id)
        account_dict = account.to_dict()
        self.connection.jsonset(key, Path.rootPath(), account_dict)
        # Add it to the accounts list
        self.connection.rpush("accounts", account.account_id)
        # Save a key to get the account by email
        self.connection.set(f"account_by_email:{account.email}", account.account_id)

    def get_account_by_id(self, account_id: str) -> Union[Account, None]:
        key = self.__get_key(account_id)
        account_dict = self.connection.jsonget(key, Path.rootPath())
        if account_dict:
            account = Account.from_dict(account_dict)
            return account
        else:
            return None

    def delete_account_by_id(self, account_id: str) -> None:
        key = self.__get_key(account_id)
        self.connection.delete(key)
        # Delete it from the accounts list
        self.connection.lrem("accounts", 1, account_id)

    def get_account_by_email(self, email: str) -> Union[Account, None]:
        # Get account id by email
        account_id = self.connection.get(f"account_by_email:{email}")
        if account_id:
            return self.get_account_by_id(account_id)
        else:
            return None

    def get_all_accounts(self) -> List[Account]:
        accounts = []
        for account_id in self.connection.lrange("accounts", 0, -1):
            accounts.append(self.get_account_by_id(account_id))
        return accounts
