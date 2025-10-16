# import os
import json
# import subprocess
# import flet
# print("hello world")
# os.system("python main.py")
# # os.path.
# subprocess.run("cls", shell = True)

car = {"mark":"bmv", "speed":"200"}
car["a"] = "ssssssssssssssss"
print(car)

a1 = json.dumps(car)
print(a1)
a2 = json.loads(a1)
print(a2)