from setuptools import find_packages , setup
from typing import List

requirement_file="requirements.txt"


def get_requirements():
    with open(requirement_file) as file:
         requirement_list= file.readlines()
    requirement_list=[require_name.replace("\n" ,"")  for require_name in requirement_list]
    if "-e ." in requirement_list:
         requirement_list.remove("-e .")
    return requirement_list
      
setup(name="src" ,
      author="Rajat" ,
      author_email="rajat.k.singh64@gmail.com" ,
      version="0.0.1" ,
      packages=find_packages() ,
      install_requires=get_requirements() 
)