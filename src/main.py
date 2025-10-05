from FileSystem import FileSystem
from flet import *

def main(page:Page):

    LocalStorage = FileSystem()

    page.add()
app(target=main)