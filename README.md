# Helpful-python-scripts

A collection of small, useful Python and PowerShell scripts designed for automation, productivity, and scraping tasks.

## 📂 Included Scripts

| File | Description |
|------|-------------|
| `Optimize-Windows.ps1` | PowerShell script to tweak Windows performance and settings. |
| `android_remote_view_and_record.py` | Python script to remotely view and record an Android device’s screen. |
| `job_results.csv` | Sample CSV data used by the scraping tools. |
| `jobsscrapper.py` | Python script that scrapes job listings (or similar) and writes results to `job_results.csv`. |
| `screenshots.py` | Python script that takes periodic screenshots (every 5 minutes) and saves them to a `screenshots/` folder. |
| `server.py` | Basic Python server script (perhaps for testing or local automation). |
| `topicgenerator.py` | Python script to generate topic ideas for content or other uses. |

## ✅ How to Use

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Brian432-cpu/Helpful-python-scripts.git
   cd Helpful-python-scripts
(Optional) Create a virtual environment for Python usage:

python -m venv venv
source venv/bin/activate   # on Linux/macOS
# or
venv\Scripts\activate      # on Windows

Install any dependencies (if required for a specific script):

pip install -r requirements.txt

Note: You may need to create a requirements.txt listing any libraries used (e.g., selenium, requests, opencv-python, etc.).

Run a script:

python screenshots.py

Replace with any script file you want to run.

🛠 Usage Notes & Tips

Modify the screenshot folder path in screenshots.py as needed (default: ./screenshots/).

Ensure you have appropriate permissions when running Optimize-Windows.ps1 (run PowerShell as Administrator).

For Android remote view/record, you may need additional setup (like enabling USB debugging, installing ADB, or using a particular library).

jobsscrapper.py may require updating the target URL or scraping logic if website changes.

Feel free to extend, adapt, or contribute new helper scripts to the collection.

📋 Contributions & License

Contributions are welcome! Feel free to submit pull requests adding new scripts or improving existing ones.

Please add descriptive commit messages and update the README if you add new tools.

License: Feel free to choose a license (e.g., MIT) if you want open use and sharing.

🔍 About the Author

Created by Brian432-cpu. This repository serves as a toolkit of mini-automations and helper utilities to streamline tasks and experiments.

Thanks for checking out this repository — hope you find something here useful & inspiring! 🎉
