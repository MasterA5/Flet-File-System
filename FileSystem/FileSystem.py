from typing import Any, Union, List, Tuple
from cryptography.fernet import Fernet
import shutil
import uuid
import json
import os


class FileSystem:
    """
    FileSystem
    ----------
    A secure file management system designed for Flet applications.
    
    Features:
    - Persistent and temporary storage support.
    - Automatic encryption/decryption using Fernet.
    - JSON and plain-text file handling.
    - File listing, editing, and deletion with safety checks.

    Environment variables required:
    - FLET_APP_STORAGE_DATA
    - FLET_APP_STORAGE_TEMP
    """

    def __init__(self):
        """Initialize storage paths and encryption key."""
        self.storage_data = os.getenv("FLET_APP_STORAGE_DATA") or os.getcwd()
        self.storage_temp = os.getenv("FLET_APP_STORAGE_TEMP") or os.path.join(self.storage_data, "temp")

        os.makedirs(self.storage_data, exist_ok=True)
        os.makedirs(self.storage_temp, exist_ok=True)

        # Locate existing encryption keys
        existing_keys = [f for f in os.listdir(self.storage_temp) if f.endswith(".key")]

        if existing_keys:
            # Use the first key found
            key_path = os.path.join(self.storage_temp, existing_keys[0])
            with open(key_path, "rb") as key_file:
                self.key = key_file.read()
        else:
            # Generate a new key and store it
            key_file_name = f"{uuid.uuid4()}.key"
            key_path = os.path.join(self.storage_temp, key_file_name)
            self.key = Fernet.generate_key()
            with open(key_path, "wb") as key_file:
                key_file.write(self.key)

        self.cipher = Fernet(self.key)

    def _get_path(self, file_name: str, temp: bool = False) -> str:
        """Return full path of a file in data or temp storage."""
        base_path = self.storage_temp if temp else self.storage_data
        return os.path.join(base_path, file_name)

    def save_file(
        self,
        file_name: str,
        file_content: Any,
        temp: bool = False,
        overwrite: bool = False,
        encrypt: bool = False
    ) -> Union[str, bool]:
        """
        Save file content into storage, supporting text, JSON, and binary files (images, audio, CSV, etc.).

        Parameters:
        - file_name: Name (and optionally path) of the file.
        - file_content: Content to write.
            * str → text file
            * dict/list → JSON file
            * bytes → binary file (image, audio, CSV in bytes)
        - temp: Save in temporary storage if True.
        - overwrite: Allow overwriting existing files.
        - encrypt: Encrypt contents using Fernet (works for text and bytes).

        Returns:
        - True if successful.
        - Error message (str) if failed.
        """
        try:
            base_dir = self.storage_temp if temp else self.storage_data
            full_path = os.path.join(base_dir, file_name)
            dir_path = os.path.dirname(full_path)

            # Create intermediate directories if needed
            if dir_path and not os.path.exists(dir_path):
                os.makedirs(dir_path, exist_ok=True)

            # Check overwrite
            if os.path.exists(full_path) and not overwrite:
                return "File already exists."

            # Determine if file is binary
            is_binary = isinstance(file_content, bytes)

            # Encrypt if requested
            if encrypt:
                if not is_binary:
                    # Convert to bytes for text content
                    file_content = str(file_content).encode("utf-8")
                encrypted_data = self.cipher.encrypt(file_content)
                file_content = b"E::" + encrypted_data
                is_binary = True  # Encrypted files always treated as binary

            # Write file
            if is_binary:
                with open(full_path, "wb") as f:
                    f.write(file_content)
            else:
                # Text or JSON
                if isinstance(file_content, (dict, list)) or file_name.endswith(".json"):
                    file_content = json.dumps(file_content, indent=4, ensure_ascii=False)
                else:
                    file_content = str(file_content)
                with open(full_path, "w", encoding="utf-8") as f:
                    f.write(file_content)

            return True

        except Exception as e:
            return f"Error saving file: {e}"

    def read_file(self, file_name: str, temp: bool = False) -> Union[str, dict, bytes]:
        """
        Read file content from storage, supporting text, JSON, and binary files.
        Automatically decrypts files starting with 'E::'.

        Parameters:
        - file_name: Name (and optionally path) of the file.
        - temp: Read from temporary storage if True.

        Returns:
        - str for text files
        - dict/list for JSON files
        - bytes for binary files (including encrypted)
        - Error message (str) if the file cannot be read
        """
        file_path = self._get_path(file_name, temp)

        if not os.path.exists(file_path):
            return "File not found"

        try:
            # Determine if binary mode is needed
            is_binary = False
            if file_name.lower().endswith((
                ".png", ".jpg", ".jpeg", ".bmp", ".gif",
                ".mp3", ".wav", ".ogg", ".flac",
                ".pdf", ".csv", ".zip", ".bin"
            )):
                is_binary = True

            # Open file
            if is_binary:
                with open(file_path, "rb") as f:
                    data = f.read()
            else:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = f.read()

            # Check for encrypted content
            if isinstance(data, bytes):
                if data.startswith(b"E::"):
                    decrypted = self.cipher.decrypt(data[3:])
                    return decrypted
                else:
                    return data
            else:
                if data.startswith("E::"):
                    decrypted = self.cipher.decrypt(data[3:].encode("utf-8"))
                    return decrypted.decode("utf-8")
                # JSON support
                if file_name.endswith(".json"):
                    return json.loads(data)
                # Plain text
                return data

        except Exception as e:
            return f"Error reading file: {e}"

    def delete_file(self, file_name: str, temp: bool = False) -> str:
        """
        Delete a file from storage.
        """
        file_path = self._get_path(file_name, temp)
        if not os.path.exists(file_path):
            return "File not found"

        try:
            os.remove(file_path)
            return f"Deleted {file_path}"
        except Exception as e:
            return f"Error deleting file: {e}"

    def list_files(
        self,
        temp: bool = False,
        list_both_directories: bool = False,
        show_details: bool = False
    ) -> Union[List[str], Tuple[List[str], List[str]], str]:
        """
        List all files in storage directories.

        Parameters:
        - temp: List only temporary storage.
        - list_both_directories: Return both data and temp storage contents.
        - show_details: Show formatted string summary.

        Returns:
        - List of file names, tuple, or formatted summary string.
        """
        try:
            data_storage_content = [
                f for f in os.listdir(self.storage_data)
            ]
            temp_storage_content = [
                f for f in os.listdir(self.storage_temp) if not f.endswith(".key")
            ]

            if not list_both_directories:
                base_path = self.storage_temp if temp else self.storage_data
                return [f for f in os.listdir(base_path) if not f.endswith(".key")]

            if show_details:
                return (
                    f"Data Storage ({len(data_storage_content)}): {data_storage_content if data_storage_content != [] else 'No Files Found'}\n"
                    f"Temp Storage ({len(temp_storage_content)}): {temp_storage_content if temp_storage_content != [] else 'No Files Found'}"
                )

            return data_storage_content, temp_storage_content

        except Exception as e:
            return [f"Error listing files: {e}"]

    def file_exists(self, file_name: str, temp: bool = False) -> bool:
        """Check if a file exists in storage."""
        return os.path.exists(self._get_path(file_name, temp))

    def edit_file(self, file_name: str, new_content: Any, temp: bool = False, encrypt: bool = False) -> str:
        """
        Edit a file by overwriting its content.
        """
        if not self.file_exists(file_name, temp):
            return "File not found"
        return self.save_file(file_name, new_content, temp=temp, overwrite=True, encrypt=encrypt)

    def clear_storage(self, temp: bool = False) -> str:
        """
        Remove all files from the selected storage directory.
        """
        base_path = self.storage_temp if temp else self.storage_data
        try:
            for file in os.listdir(base_path):
                if not file.endswith(".key"):
                    os.remove(os.path.join(base_path, file))
            return f"Cleared storage: {base_path}"
        except Exception as e:
            return f"Error clearing storage: {e}"
    
    def delete_folder(self, dir_name: str, temp: bool = False) -> str:
        """
        Delete a folder and all its contents safely without affecting parent directories.

        Parameters:
        - dir_name: Name or relative path of the folder to delete.
        - temp: If True, deletes from the temporary storage.

        Returns:
        - Message with operation result.
        """
        try:
            base_path = self.storage_temp if temp else self.storage_data
            folder_path = os.path.join(base_path, dir_name)

            if not os.path.exists(folder_path):
                return f"❌ The folder '{dir_name}/' does not exist."

            if not os.path.isdir(folder_path):
                return f"⚠️ '{dir_name}' is not a folder."

            # 🔒 Delete only the target folder and its contents
            shutil.rmtree(folder_path)

            return f"🗑️ The folder '{dir_name}/' and all its contents were deleted successfully."
        except Exception as e:
            return f"Error deleting folder '{dir_name}/': {e}"
   
    def search_files(
        self, 
        file_names: list[str],  # Ahora acepta lista de nombres
        temp: bool = False, 
        search_in_any_folders: bool = False
    ) -> dict:
        """
        Search for multiple files by name in the storage directory.

        Parameters:
        - file_names: List of file names (or partial names) to search for.
        - temp: If True, search in temporary storage.
        - search_in_any_folders: If True, search recursively in subfolders.

        Returns:
        - Dictionary where keys are file names and values are lists of full paths,
        or a string "File Not Found" if no matches are found.
        Example: {"config.json": ["data/config.json"], "test.txt": "File Not Found"}
        """
        if not isinstance(file_names, list):
            file_names = [file_names]

        base_path = self.storage_temp if temp else self.storage_data
        results = {name: [] for name in file_names}

        if not search_in_any_folders:
            files = os.listdir(base_path)
            for f in files:
                for name in file_names:
                    if name.lower() in f.lower():
                        results[name].append(os.path.join(base_path, f))
        else:
            for root, _, files in os.walk(base_path):
                for f in files:
                    for name in file_names:
                        if name.lower() in f.lower():
                            results[name].append(os.path.join(root, f))

        # Reemplazar listas vacías por "File Not Found"
        for name in results:
            if not results[name]:
                results[name] = "File Not Found"

        return results
