# Email and Password Extractor

## Description
Email and Password Extractor is a Python-based GUI application that allows users to extract email and password combinations from text files within a selected folder. The application features a user-friendly interface built using Tkinter, supports multi-threaded processing for efficiency, and removes duplicate entries before saving the results.

## Features
- Select a folder containing `.txt` files.
- Enter keywords to filter the extracted data.
- Uses multiple text encodings to ensure maximum compatibility.
- Multi-threaded processing for faster execution.
- Duplicate removal to save unique email-password pairs.
- Gradient UI with progress tracking and logging.
- Option to save or copy results after processing.

## Installation
### Requirements
Make sure you have Python installed. This script requires Python 3.6 or newer.

### Dependencies
Install the required Python libraries before running the application:

```sh
pip install tk
```

## Usage
1. Run the script:
   ```sh
   python extractor.py
   ```
2. Select the folder containing `.txt` files.
3. Enter keywords to filter the extracted data (comma-separated).
4. Click "Start Processing" to extract email-password pairs.
5. View progress and logs in the application window.
6. Copy results to clipboard or save them as a `.txt` file.

## Code Overview
The application consists of:
- **GUI Interface**: Built with Tkinter, featuring a gradient background, input fields, buttons, a log box, and a progress bar.
- **Multi-threading**: Uses `threading` and `concurrent.futures` to handle multiple files efficiently.
- **Regex Filtering**: Extracts email-password pairs based on predefined patterns.
- **Encoding Handling**: Supports different encodings to ensure compatibility with various text files.
- **Result Processing**: Removes duplicate entries before saving the results.

## Example Output
```
[INFO] Folder selected: C:/Users/Example/Files
[INFO] Processing... Please wait.
[INFO] Found: example@email.com:password123 in file1.txt
[INFO] Found: test@domain.com:pass456 in file2.txt
[INFO] Process Completed Successfully in 5.23 seconds.
```

## License
This project is licensed under the MIT License.

## Contributing
Feel free to fork the repository and submit pull requests for improvements or bug fixes.

## Contact
For any issues or suggestions, please open an issue in the repository.

---

Enjoy extracting securely and efficiently!

