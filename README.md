# Python_Pic_Viewer

Can drop or open to view image and gif.

Right click to open the file, use the left and right arrows or click on the left and right parts of the window to switch images;

Press the T key to sort by time, press the S key to sort by size, and press the N key to sort by name.

## Build And Contribute

### When environment existing

If you have the environment, please `cd` to this fold and run

```shell
poetry init
```
Run.
```shell
poetry run python ./Python_Pic_Viewer.py
```

If not, please continue.

### Install [pipx](https://pipx.pypa.io/stable/installation/)
```shell
pip install --user pipx
```
It is possible (even most likely) the above finishes with a WARNING looking similar to this:

> WARNING: The script pipx.exe is installed in `<USER folder>\AppData\Roaming\Python\Python3x\Scripts` which is not on PATH

```shell
cd <USER folder>\AppData\Roaming\Python\Python3x\Scripts
.\pipx.exe ensurepath
```
### Install [Poetry](https://python-poetry.org/docs/#installing-with-pipx)

```shell
pipx install poetry
pipx ensurepath
```
You can find the Poetry in `C:/Users/<USER folder>/.local/bin/poetry.exe` 

### Open with Pycharm

### Build Executable File

Run to build.
```shell
poetry run pyinstaller -w -F -n PythonPicViewer ./Python_Pic_Viewer.py --additional-hooks-dir=.
```

Should have installed the [`pyinstaller`](https://pyinstaller.org/en/v6.11.0/usage.html).
```shell
poetry add pyinstaller
```




