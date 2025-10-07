# 🗂️ Flet File System

### A lightweight Python utility to simplify file handling in **Flet** applications — no need to use `with open()` anymore!

---

## 🚀 Overview

**Flet File System** is a small but powerful utility that makes working with files in Flet apps effortless.
It handles **reading, writing, editing, deleting, encrypting, and searching files** automatically — all using pure **Python** and the **cryptography** library.

Supports both **persistent** and **temporary** storage and works seamlessly with **text, JSON, images, audio, CSV, PDFs, and other binary files**.

---

## ✨ Features

* 🔐 **Built-in encryption** using the `cryptography` library (Fernet).
* 📁 **Automatic directory handling** for both persistent and temporary storage.
* 💾 **Easy file operations** — read, write, edit, delete, list, and search files with a single method call.
* 🧩 **JSON support** — automatically encodes and decodes JSON files.
* 🖼️ **Binary file support** — save and read images, audio, CSVs, PDFs, etc.
* 🧹 **Storage management** — clear entire directories safely.
* 🧠 **Smart defaults** — uses environment variables (`FLET_APP_STORAGE_DATA` / `FLET_APP_STORAGE_TEMP`) or creates fallback paths automatically.
* ⚙️ **Fully compatible with Flet**, works inside any Flet page or app.

---

## 🧰 Installation

```bash
pip install cryptography flet[all]
```

### ➕ Add To `pyproject.toml`
```toml
dependencies = [
  "flet==0.28.3",
  "cryptography" # <- Needed For Encrypt Files
]
```

> **Note:** The `FileSystem` class can also be used standalone in non-Flet projects (requires `flet>=0.28.3`).

---

## 💡 Example Usage

```python
from flet import *
from FileSystem import FileSystem  # your FileSystem class

def main(page: Page):
    fs = FileSystem()

    # Save an encrypted text file
    fs.save_file(
        file_name="Hello.txt",
        file_content="Hello Flet!",
        encrypt=True,
        overwrite=True
    )

    # Save an image
    with open("example.png", "rb") as f:
        image_bytes = f.read()
    fs.save_file("images/example_saved.png", image_bytes, overwrite=True)

    # Read the encrypted text file
    content = fs.read_file("Hello.txt")

    # Read the image
    saved_image = fs.read_file("images/example_saved.png")
    with open("example_copy.png", "wb") as f:
        f.write(saved_image)

    page.add(
        Column([
            Text("✅ Text and image files saved and read successfully!"),
            Text(f"Decrypted content: {content}")
        ])
    )

app(target=main)
```

---

## 🧱 Methods Overview

| Method            | Description                                                           |
| ----------------- | --------------------------------------------------------------------- |
| `save_file()`     | Save a file (text, JSON, or binary) with optional encryption.         |
| `read_file()`     | Read and decrypt file contents automatically.                         |
| `edit_file()`     | Modify an existing file easily.                                       |
| `delete_file()`   | Remove a file from storage.                                           |
| `delete_folder()` | Delete an entire folder safely.                                       |
| `list_files()`    | List files from data and/or temp directories.                         |
| `search_files()`  | Search one or multiple files by name, with optional recursive search. |
| `file_exists()`   | Check if a file exists.                                               |
| `clear_storage()` | Delete all files from a directory safely.                             |

---

## 🧪 Tested On

| Platform  | Status |
|-----------|---------|
| Android   | ✅ |
| Windows   | ✅ |
| iOS       | ❌ |
| macOS     | ❌ |
| Linux     | ❌ |


## 🔐 Encryption

Encryption is handled automatically with the **Fernet** algorithm from the `cryptography` library.
Each `FileSystem` instance generates or reuses a `.key` file stored securely inside the **temp** directory.

---

## 🧩 Environment Variables

| Variable                | Description                                     |
| ----------------------- | ----------------------------------------------- |
| `FLET_APP_STORAGE_DATA` | Path for persistent data storage.               |
| `FLET_APP_STORAGE_TEMP` | Path for temporary storage and encryption keys. |

Fallback directories are created automatically if these variables are not set.

---

## 🧹 Example Outputs

```python
# Save JSON
fs.save_file("demo.json", {"name": "Flet", "type": "Framework"}, encrypt=False)

# List files
data_files, temp_files = fs.list_files(list_both_directories=True)
print(data_files, temp_files)
```

Output:

```
['demo.json'] 'No Files Found'
```

---

## 📂 Detailed Directory Info

```python
data = fs.list_files(list_both_directories=True, show_details=True)
print(data)
```

Output:

```
Data Storage (1): ['demo.json']
Temp Storage (0): 'No Files Found'
```

---

## 🛠️ Requirements

* **Python 3.10+**
* **Flet**
* **cryptography**

---

## 📄 License

MIT License — free to use and modify.

---

## 💬 Author

Developed by **MasterA5437S** — making Flet development easier, one utility at a time 💙

---

## 🤝 Contributing

Contributions are **welcome and encouraged**! 🎉

To contribute:

1. **Fork** the repository.
2. **Create a new branch** for your feature or fix.
3. **Commit your changes** with clear, descriptive messages.
4. **Submit a Pull Request** explaining what you’ve added or improved.

You can also open **issues** for bugs, suggestions, or improvements.
All contributions — from fixing typos to adding new features — are greatly appreciated 💪

> Together we can make Flet development faster, safer, and more enjoyable!
