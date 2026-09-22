first_name = "ada"
last_name = "lovelace"
full_name = f"{first_name} {last_name}"
print(full_name)

print(f"Hello, {full_name.title()}!")

message = f"Hello, {full_name.title()}!"
print(message)

print("Python")
print("\tPython")

print("Languages:\nPython\nJavaScript")

#右剥除空格rstrip
favorite_language = "python "
favorite_language
favorite_language.rstrip()


favorite_language = "python "
favorite_language = favorite_language.rstrip()
favorite_language
#左剥除空格rstrip、全剥除空格strip
favorite_language = "  python "
favorite_language.rstrip()
favorite_language.lstrip()
favorite_language.strip()


#删除前缀
nostarch_url = 'https://nostarch.com'
nostarch_url.removeprefix('https://')

simple_url = nostarch_url.removeprefix('https://')
