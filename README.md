# 📊 DataForge

**DataForge** is a Python-based GUI tool that automates the generation of synthetic datasets using real-world references from Kaggle and local LLMs (Mistral via Ollama). It now includes a production-ready REST API for secure, programmatic access to generated datasets.

---

## 🖼️ GUI Preview
![image](https://github.com/user-attachments/assets/19dad03b-19e0-4818-8e96-34ca87293b2f)

---

## 🚀 Features

- **Keyword-based Search**: Input a topic (e.g., "housing") and automatically fetch related datasets from Kaggle using the Kaggle API.
- **Reference Dataset Extraction**: Downloads and parses relevant Kaggle datasets.
- **Synthetic Dataset Generation**: Uses Mistral (via Ollama, running locally) to generate multiple, non-identical datasets based on the original schema.
- **Organized Storage**: Datasets are grouped into folders:
  - `/reference_datasets/` – original reference data
  - `/generated_datasets/` – AI-generated data
- **User-Friendly GUI**: Built with CustomTkinter for smooth input, progress tracking, and dataset previews.
- **Production REST API**: Secure, authenticated API for listing and downloading generated datasets from any device on your network.

---

## 📁 Folder Structure

```
DataForge/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── config.json                      # Configuration file
├── setup.py                         # Installation script
├── README.md                        # Documentation
├── LICENSE                          # License file
├── .gitignore                       # Git ignore file
├── api_server.py                    # API Server
├── src/
│   └── dataforge/
│       ├── __init__.py
│       ├── config/
│       │   ├── __init__.py
│       │   └── config_manager.py    # Configuration management
│       ├── core/
│       │   ├── __init__.py
│       │   └── dataset_generator.py # Core generation logic
│       ├── handlers/
│       │   ├── __init__.py
│       │   ├── kaggle_handler.py    # Kaggle API integration
│       │   └── mistral_handler.py   # Mistral 7B integration
│       ├── gui/
│       │   ├── __init__.py
│       │   ├── main_window.py       # Main GUI window
│       │   ├── components.py        # GUI components
│       │   └── dialogs.py           # Dialog windows
│       └── utils/
│           ├── __init__.py
│           ├── logger.py           # Logging system
│           └── helpers.py          # Utility functions
├── data/
│   ├── reference_datasets/         # Downloaded Kaggle datasets
│   └── generated_datasets/         # Generated synthetic datasets
├── logs/                           # Application logs
├── tests/                          # Unit tests
├── docs/                           # Documentation
└── dist/                           # Distribution files

```

---

## 💻 Requirements

- Python 3.8+
- pip install -r requirements.txt
- Kaggle API key (`kaggle.json`) in `~/.kaggle/`
- Ollama with Mistral model (`ollama pull mistral`)

---

## ⚙️ Setup

1. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

2. **Kaggle API setup:**
   - Place your `kaggle.json` in `~/.kaggle/` (Linux/Mac) or `%USERPROFILE%\.kaggle\` (Windows).

3. **Ollama setup:**
   - Install Ollama and pull the Mistral model:
     ```
     ollama serve
     ollama pull mistral
     ```

4. **Run the app:**
   ```
   python main.py
   ```

---

## 🖥️ How It Works

- Launch the GUI.
- Enter a keyword (e.g., `weather`, `finance`, `real estate`).
- DataForge:
  - Uses your Kaggle API key to find the most relevant dataset.
  - Downloads and extracts the data.
  - Sends a schema-based prompt to Mistral running locally in Ollama.
  - Generates 5–6 new datasets with varied but related content.
  - Outputs are saved locally and can be previewed or reused.

---

## 🔗 API Integration

### API Overview

- **Base URL:** `http://localhost:5000`
- **Authentication:** Bearer token (`Authorization: Bearer dataforge_api_2025`)
- **Endpoints:**
  - `GET /api/health` — Health check
  - `GET /api/datasets` — List all generated datasets
  - `GET /api/download//` — Download a specific CSV file
  - `GET /api/download-zip/` — Download all datasets for a keyword as a ZIP
  - `POST /api/generate` — Trigger dataset generation via API

### Example Usage

**List datasets:**
```
curl -H "Authorization: Bearer dataforge_api_2025" http://localhost:5000/api/datasets
```

**Download a file:**
```
curl -H "Authorization: Bearer dataforge_api_2025" \
     -O http://localhost:5000/api/download/healthcare/healthcare_synthetic_v1_1234567890.csv
```

**Download all datasets for a keyword as ZIP:**
```
curl -H "Authorization: Bearer dataforge_api_2025" \
     -O http://localhost:5000/api/download-zip/healthcare
```

**Trigger generation via API:**
```
curl -X POST -H "Authorization: Bearer dataforge_api_2025" \
     -H "Content-Type: application/json" \
     -d '{"keyword": "finance", "rows": 500, "variations": 6}' \
     http://localhost:5000/api/generate
```

### API Security

- The API is protected by a static API key (`algonomy` by default).
- For production, change the API key in your `config.json` and restart the server.
- By default, the API is accessible only on your local network. For remote access, see the FAQ below.

---

## 📦 FAQ

**Q: How do I access the API from another computer?**  
A:  
- Find your computer’s local IP address (e.g., `192.168.1.42`).
- Start the API server with `host='0.0.0.0'` (already set in `api_server.py`).
- On another device on the same network, use `http://192.168.1.42:5000` instead of `localhost`.
- Use the API key in the `Authorization` header.

**Q: How do I change the API key?**  
A:  
- Edit the `"api_key"` value in `config.json`.
- Restart the API server.

**Q: Can I use this API over the internet?**  
A:  
- For security, the API is intended for local network use only.
- For public access, you must add HTTPS, user authentication, and firewall rules.

---

## 🛠️ Planned Features

- [ ] Advanced API key management (multiple users, revocation)
- [ ] User roles and permissions
- [ ] Cloud deployment support
- [ ] More domain-specific prompt templates

---
## ⭐ Star the Repo

If you find this project useful, consider giving it a ⭐ to support it!
