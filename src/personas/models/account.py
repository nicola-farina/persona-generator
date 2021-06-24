from __future__ import annotations


class Account(object):
    def __init__(self,
                 email: str,
                 name: str,
                 account_id: str = None,
                 hashed_psw: bytes = None) -> None:
        self.email = email
        self.name = name
        self.account_id = account_id
        self.hashed_psw = hashed_psw

    def to_dict(self) -> dict:
        return {
            "account_id": self.account_id,
            "email": self.email,
            "name": self.name,
            "hashed_psw": self.hashed_psw.decode("utf-8")
        }

    @classmethod
    def from_dict(cls, properties: dict) -> Account:
        allowed_fields = ("account_id", "email", "name", "hashed_psw")
        allowed_attributes = {k: v for k, v in properties.items() if k in allowed_fields}
        allowed_attributes["hashed_psw"] = str.encode(allowed_attributes["hashed_psw"])
        return cls(**allowed_attributes)

    def __repr__(self):
        string = f"ID: {self.account_id}; EMAIL: {self.email}; NAME: {self.name}"
        return string

    def __eq__(self, other: Account):
        return self.account_id == other.account_id