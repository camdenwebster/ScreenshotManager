# ScreenshotManager
ScreenshotManager is a tool designed to help test automation engineers manage screenshots used in automated testing.

## Features
- **Upload Screenshots**: Upload screenshot files to the system.
- **Manage Ignore Regions**: Add, edit, and delete ignore regions for each screenshot. Ignore regions represent segments of the image that should be ignored during snapshot testing/image comparison operations.
- **Manage Languages**: Specify the languages that are compatible with each screenshot.
- **Manage Operating System Versions**: Specify the operating system versions that are compatible with each screenshot.
- **Audit Log**: Automatically log deletions of screenshots, operating system versions, and ignore regions.

![ScreenshotManager-demo](https://github.com/user-attachments/assets/540c4262-cba0-4daf-aa5b-335df4d6571b)

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/camdenwebster/ScreenshotManager.git
    cd ScreenshotManager
    ```
2. Create a virtual environment and activate it:
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```
3. Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
    
## Usage
1. Run the Flask application:
    ```bash
    flask run
    ```
2. Open your web browser and navigate to `http://127.0.0.1:5000/`.

## Database Schema
> [!NOTE]
> This project was a result of a college database class, and therefore I'll include some details about the SQLite database configruation:

The database schema includes the following tables:
- **screenshots**: Stores information about each screenshot.
- **IgnoreRegions**: Stores information about ignore regions for each screenshot.
- **OperatingSystems**: Stores information about operating system versions.
- **ScreenshotOperatingSystem**: Stores the relationship between screenshots and operating system versions.
- **AuditLog**: Stores audit logs for deletions of screenshots, operating system versions, and ignore regions.

## SQL Triggers
The following SQL triggers are used to log deletions in the `AuditLog` table:
- **log_screenshot_deletion**: Logs deletions of screenshots.
- **log_os_deletion**: Logs deletions of operating system versions.
- **log_ignoreregion_deletion**: Logs deletions of ignore regions.

## Indexes
Indexes are created on the following columns to improve query performance:
- **screenshots**: `filename`, `filepath`
- **IgnoreRegions**: `screenshot_id`
- **ScreenshotOperatingSystem**: `screenshot_id`, `os_id`
- **AuditLog**: `screenshot_id`, `os_id`

## Contributing
Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
