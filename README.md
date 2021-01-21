# ExcelDash

ExcelDash is a simple but powerful Dash-powered graphical tool for visualising Excel data. This application was created for Roy Hill mine maintainers and features a data viewer and a suite of customizable graphs with several goals:

- Making data reporting more engaging and interesting.
- Allowing for trends and patterns in data to be discovered more easily.
- Helps to simplify concepts and convey technical information in ways that allow anyone to understand.

*Everyone loves colours!*  A diagram that is colourful is also very visually appealing, and when people are drawn to an image, they are more likely to notice details that they didn't see before.

## How to Run

Clone the repository and initialize a Python virtual environment at the root directory.

```bash
git clone https://github.com/ForsakenIdol/ExcelDash.git
cd ExcelDash
python3 -m venv venv
source venv/Scripts/activate
```

Install `wheel`, and then the other dependencies, with `pip`.

```bash
pip install wheel
pip install -r requirements.txt
```

Start the application. The entrypoint for this application is the file `dash_app.py`. The graphs require a large amount of processing power, so this process might take a while.

```bash
python dash_app.py
```

## Collaborating

This is the first time I've used `dash` to create a web app, and so there may be some not-so-good practises or missed optimization opportunities! Everyone is welcome to contribute to this application, however. Just follow the guidelines below.

1. If you find a bug or issue, open it on the repository's issue tracker. For example, if 3D graph doesn't load, open the issue `3D graph not loading` and give some background information on the issue in the description.
2. If your pull request fixes an issue, reference the issue number in your branch name and in your pull request. For example, if the issue you opened in #1 was given the number `#5`, your branch could be called `#5-3d-graph-not-loading`. Be verbose in your branch names and commit messages.
3. I reserve the final decision on whether to merge pull requests. This may change in the future.
