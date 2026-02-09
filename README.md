I built **DataForge** to automatically generate synthetic datasets intelligently. Instead of producing random fake data, it first analyzes real datasets from Kaggle and learns their structure. Then it uses a local AI model, Mistral through Ollama, to create new datasets that follow the same format but contain fresh, synthetic values.

The tool saves both the original dataset and the generated versions, making it useful for testing, experiments, and machine learning projects. It also includes a graphical interface and a REST API, so the datasets can be generated either manually or through other applications.

Overall, DataForge helps me quickly create realistic synthetic data without having to build datasets from scratch.
