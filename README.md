# EducarWeb Student Transport Enrollment Automation

A Python-based automation tool that streamlines the process of enrolling students in the EducarWeb transportation system. This tool automates repetitive enrollment tasks, reducing manual effort and potential errors in the student registration process.

The automation system handles the complete workflow from logging into the EducarWeb system to processing student enrollments from a CSV file. It features intelligent form filling, automatic student verification to prevent duplicate entries, and robust error handling to ensure reliable operation. The tool uses Selenium for web automation and PyAutoGUI for backup interaction methods when traditional web automation approaches aren't sufficient.

## Repository Structure
```
.
├── automacao.py     # Core automation logic including web interactions and form filling
├── config.py        # Configuration settings for the automation
├── dados.py         # Data handling functions for CSV processing
├── iniciar.bat      # Windows batch script to start the application
├── main.py         # Application entry point and workflow orchestration
├── position.py     # Utility script for capturing mouse coordinates
└── requirements.txt # Project dependencies
```

## Usage Instructions
### Prerequisites
- Python 3.6 or higher
- Chrome web browser
- ChromeDriver compatible with your Chrome version
- Access credentials for the EducarWeb system

Required Python packages:
- python-dotenv
- selenium
- pandas
- pyautogui

### Installation

1. Clone the repository:
```bash
git clone https://github.com/theezequiel42/matricula-bot-py
cd matricula-bot-py
```

2. Create and activate a virtual environment:
```bash
# Windows
python -m venv venv
.\venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your credentials:
```
USUARIO=your_username
SENHA=your_password
```

### Quick Start

1. Prepare your student data in a CSV file with the following columns:
   - NOME (Name)
   - TURNO (Shift)
   - LINHA (Route)
   - ANO (Grade)
   Place this file in the `data/` directory as `alunos.csv`

2. Run the automation:
```bash
python main.py
```

### More Detailed Examples

1. Running position capture utility:
```bash
python position.py
# Wait 5 seconds and move your mouse to the desired screen location
```

2. Processing specific student data:
```python
from dados import ler_csv
from automacao import iniciar_navegador, fazer_login, cadastrar_aluno

# Load specific student data
alunos = ler_csv("custom_data.csv")
driver = iniciar_navegador()
fazer_login(driver)

# Process single student
aluno = alunos[0]
cadastrar_aluno(driver, aluno)
```

### Troubleshooting

Common Issues:

1. **Element Not Found Errors**
   - Problem: Selenium can't locate web elements
   - Solution: 
     ```python
     # Increase wait time in automacao.py
     wait = WebDriverWait(driver, 20)  # Increase from 10 to 20 seconds
     ```

2. **Mouse Coordinate Issues**
   - Problem: PyAutoGUI clicks wrong locations
   - Solution:
     1. Run position.py to recalibrate coordinates
     2. Update coordinates in automacao.py
     ```python
     pyautogui.moveTo(x, y)  # Update with new coordinates
     ```

3. **CSV Reading Errors**
   - Problem: Invalid data format
   - Solution: Ensure CSV uses semicolon (;) as separator and contains required columns

Debug Mode:
- Add logging by modifying automacao.py:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Data Flow
The automation system processes student enrollments through a sequential workflow that transforms CSV data into completed student registrations in the EducarWeb system.

```ascii
[CSV File] -> [Data Processing] -> [Web Login] -> [Student Search] -> [Form Filling] -> [Enrollment]
     |              |                  |               |                    |              |
     v              v                  v               v                    v              v
  Raw Data -> Structured Data -> Auth Session -> Verification -> Auto-filled Forms -> Confirmation
```

Component Interactions:
1. dados.py reads and validates CSV data
2. main.py orchestrates the workflow sequence
3. automacao.py handles web interactions using Selenium
4. Position detection provides fallback interaction methods
5. Web forms are filled using both Selenium and PyAutoGUI
6. Error handling ensures graceful failure recovery
7. Verification prevents duplicate enrollments