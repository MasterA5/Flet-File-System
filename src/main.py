from FileSystem import FileSystem
from flet import *
import os

def main(page: Page):
    page.title = "Flet FileSystem Demo"
    page.vertical_alignment = "start"
    page.horizontal_alignment = "center"
    page.window_width = 600
    page.window_height = 600

    # Initialize FileSystem
    storage = FileSystem()

    # -----------------------------
    # 1️⃣ Save a text file
    text_file_name = "hello.txt"
    storage.save_file(text_file_name, "Hello, Flet FileSystem!", overwrite=True)

    # 2️⃣ Save a JSON file
    json_file_name = "data.json"
    json_content = {"name": "Flet", "type": "Framework", "version": 0.28}
    storage.save_file(json_file_name, json_content, overwrite=True)

    # 3️⃣ Save an image file (binary)
    image_file_name = "sample_image.png"
    # Ensure the image exists in the same folder as this script
    if os.path.exists("sample_image.png"):
        with open("sample_image.png", "rb") as img:
            image_bytes = img.read()
        storage.save_file(image_file_name, image_bytes, overwrite=True)

    # -----------------------------
    # 4️⃣ List files
    data_files, temp_files = storage.list_files(list_both_directories=True)
    list_text = f"Data Files: {data_files}\nTemp Files: {temp_files}"

    # 5️⃣ Read text and JSON files
    read_text = storage.read_file(text_file_name)
    read_json = storage.read_file(json_file_name)

    # 6️⃣ Search for files
    search_results = storage.search_files(["hello.txt", "data.json", "missing.txt"])

    # 7️⃣ Delete the text file
    delete_message = storage.delete_file(text_file_name)

    # -----------------------------
    # Display all results in Flet UI
    page.add(
        Column([
            Text("✅ Files saved successfully!", size=18, weight="bold"),
            Divider(),
            Text(f"Text file content: {read_text}"),
            Text(f"JSON file content: {read_json}"),
            Divider(),
            Text(list_text),
            Divider(),
            Text(f"Search Results: {search_results}"),
            Divider(),
            Text(f"Delete Message: {delete_message}"),
        ], spacing=10)
    )

app(target=main)
