# CodeWeaver

CodeWeaver is a Python application designed to automate file updates based on AI responses. It monitors a specific file for changes, processes the content, and updates project files accordingly using Git for version control.

## Installation

1. Clone this repository:
   ```
   git clone https://github.com/yourusername/codeweaver.git
   ```

2. Navigate to the project directory:
   ```
   cd codeweaver
   ```

3. Install the package:
   ```
   pip install -e .
   ```

## Usage

1. Run the CodeWeaver application:
   ```
   weaver
   ```

2. The application will create a default configuration if one doesn't exist. Review and modify the `.weaver/config.json` file if needed.

3. Edit the `weaver.md` file in your project root to add or update files. The application will automatically detect changes and process them.

4. CodeWeaver will create Git branches, stage changes, and attempt to merge them automatically. If conflicts occur, it will open VS Code (code-server) for manual resolution.

5. Check the logs in the `.weaver/logs` directory for detailed information about each update process.

## Configuration

The `.weaver/config.json` file contains the following settings:

- `project_root`: The root directory of your project
- `logs_folder`: Directory for storing log files
- `backups_folder`: Directory for storing file backups
- `monitored_file`: The file to monitor for changes (default: `weaver.md`)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License.