# QABot

## ✔️ Features

## 🔧 Installation

To install QABot, follow these steps:

1. Clone the repository:

```bash
git clone https://github.com/kamikazebr/qabot.git
```

2. Navigate to the directory where the repository was downloaded

> Open [qabot.code-workspace](../../qabot.code-workspace) into VSCode

3. Install the required dependencies poetry を使って


```bash
pdm import -f poetry pyproject.toml
pdm install
```

4. Rename `.env.sample` to `.env`

5. Open the `.env` file and fill in the following variables:
   - `OPENAI_API_KEY` : Your OpenAI API key.

## 💻 Usage

1. Run `QABot` Python module in your terminal

```bash
python ./src/main.py
```

```bash
poetry run python src/main.py
```

## In API Mode

```bash
python ./src/api.py
```

```bash
poetry run python src/api.py
```

After in webapp folder

```bash
pnpm install
pnpm dev
```

or

```bash
yarn install
yarn dev
```

## Tests

- [Ask using Token Generation](packages/ml/src/tests/ray_remote_test.py)
- [Update Database Locally](packages/ml/src/tests/update_db_test.py)

## 🚀 Planned Features

## 🤖 Supported Models<a name="supported-models"></a>

Default model is **gpt-3.5-turbo**.
To use a different model, specify it through OPENAI_API_MODEL or use the command line.
GPT-4 and LLaMA compatibility testing is currently not being conducted.

## Acknowledgments

I would like to express my gratitude to the developers whose code I referenced in creating this repo.

Special thanks go to

Pengenuity @dory111111 (https://github.com/dory111111/Pengenuity.git)
