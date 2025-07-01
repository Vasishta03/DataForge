# 📊 DataForge

**DataForge** is a Python tool that helps teams quickly generate usable datasets using AI. It fetches real data from Kaggle, creates fake but realistic versions using an LLM, and makes them securely accessible via GUI and API. Perfect for safe prototyping and model testing.

---

## 🚀 Features

- 🔍 **Keyword-based Search**: Input a topic (e.g., "housing") and automatically fetch related datasets from Kaggle using the Kaggle API.
- 📥 **Reference Dataset Extraction**: Automatically downloads and parses relevant Kaggle datasets.
- 🤖 **Synthetic Dataset Generation**: Uses Mistral (via Ollama, running locally) to generate multiple, non-identical datasets based on the original schema.
- 🗂️ **Organized Storage**: Datasets are grouped into folders:
  - `/kaggle_datasets/` – original reference data
  - `/generated_datasets/` – AI-generated data
- 🖥️ **User-Friendly GUI**: Built with CustomTkinter for smooth input, progress tracking, and dataset previews.

---

## 🖼️ GUI Preview

> <img width="1051" alt="{28538D5B-E1CF-499B-B2E3-C66A00EEF1ED}" src="https://github.com/user-attachments/assets/d4e775cb-1f64-473e-814d-f55085751b4c" />

---

## 🔧 How It Works

1. Launch the GUI.
2. Enter a keyword (e.g., `weather`, `finance`, `real estate`).
3. DataForge:
   - Uses your Kaggle API key to find the most relevant dataset.
   - Downloads and extracts the data.
   - Sends a schema-based prompt to Mistral running locally in Ollama.
   - Generates 5–6 new datasets with varied but related content.
4. Outputs are saved locally and can be previewed or reused.

---

## 📁 Folder Structure

```plaintext
DataForge/
├── main.py                          # Application entry point
├── requirements.txt                 # Python dependencies
├── config.json                      # Configuration file
├── setup.py                         # Installation script
├── README.md                        # Documentation
├── LICENSE                          # License file
├── .gitignore                       # Git ignore file
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

```bash
pip install -r requirements.txt
```

---

## ⚙️ Setup

1. Set up your Kaggle API key (`kaggle.json`) in `~/.kaggle/`.
2. Install [Ollama](https://ollama.com/) and pull the Mistral model:

   ```bash
   ollama run mistral
   ```
3. Run the app:

   ```bash
   python main.py
   ```

---

## 📌 Notes

* The synthetic datasets are **not exact replicas** but are **schema-aware variants** created by a locally run Mistral model.
* The dataset generation time varies based on:

  * Size of the original Kaggle dataset
  * Number of synthetic datasets requested
* API endpoints are **not yet implemented** — this will be included in the next release.

---

## 🛠️ Planned Features (v2)

* ✅ Dataset download via API
* ⏳ REST API endpoints to access generated datasets
* ✅ Column selector and schema editor before generation
* ✅ Export logs and metadata with each dataset
* ✅ Lightweight CPU model support

---

## 📄 License

MIT License

---

## 👤 Author

[Vasishta Nandipati](https://github.com/Vasishta03)

---

## 🙌 Contributions

Feel free to open issues, suggest features, or fork the repo. All ideas are welcome!

