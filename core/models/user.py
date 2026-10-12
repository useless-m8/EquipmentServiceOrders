class User:
    def __init__(
        self, user_id: int, name: str, email: str,
        is_active: bool = True,
    ) -> None:
        if type(user_id) is not int or user_id <= 0:
            raise ValueError("ID пользователя должен быть положительным.")
        if not name.strip() or "@" not in email or not email.strip():
            raise ValueError("Укажите имя и email пользователя.")
        if type(is_active) is not bool:
            raise ValueError("Активность пользователя должна быть bool.")
        self.id = user_id
        self.name = name.strip()
        self.email = email.strip()
        self.is_active = is_active

    def __str__(self) -> str:
        status = "активен" if self.is_active else "неактивен"
        return f"{self.id}. {self.name}, {self.email} ({status})"
