def register_user(name, age=18, *skills, active=True, **metadata):
    print(name, age, skills, active, metadata)

register_user("Renato")
register_user("Renato", 35, "Python", "C#", active=False, country="Portugal")