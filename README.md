# Better MM: a better* Google Music Manager

<!-- TOC -->

- [Background](#background)
- [Installation](#installation)
- [Usage](#usage)
- [Process](#process)
- [Cross-Platform Warning](#cross-platform-warning)
- [Status](#status)

<!-- /TOC -->

> __Note__: This has only been tested in Windows with Python 3. [More info](#cross-platform-warning).

## Background

BetterMM uses the gmusicapi to provide a command line interface to Google Music Manager, a tool for uploading your music library to Google Music. gmusicapi is an unofficial Python interface for Google Music.

Google's Music Manager makes for a good background utility, however, the functionality is somewhat limited and those with larger libraries may want to tweak their uploading options. BetterMM uses dates that music files were added by (think recently added) to specify which files will be uploaded. It does not use modification times. This is another big difference between BetterMM and Music Manager: minor tag changes do not reschedule uploads. See [Cross-Platform Warning](#cross-platform-warning) for more on this.

## Installation

1. `git clone https://github.com/cofinley/BetterMM.git`
2. `cd BetterMM/`
3. `pip install -r requirements.txt`

- For use in virtualenv, do this before step 3:
    1. For Python 3.3+: python -m venv venv (
        - If Python version below 3.3 (`python --version`):
            1. `pip install virtualenv`
            2. `virtualenv venv`
    2. `venv\Scripts\activate`
        - For Unix: `venv/bin/activate`

## Usage

`python run.py`

If using virtualenv, activate first: `venv\Scripts\activate`.

Use `-v` or `--verbose` flags to specify date ranges later on (no need to on the first run).

## Process

This process outlines the first run of the script. Subsequent runs, if not in verbose mode, will not prompt you for music directory or date ranges.

1. Enter in music directory
2. Enter in a date range of music added (if desired)
    - How far back and how recent files were added to directory
3. Follow Google oauth instructions
4. Program searches for flacs, mp3s
    - Only takes files which are within the given date range
        - If no range given, all files considered
5. Upload to Google Music
6. Log saved to logs/log_files/

## Cross-Platform Warning

At the time of writing this, I have only used BetterMM with Windows. The python function used to get file creation times, [getctime()](https://docs.python.org/3.3/library/os.path.html#os.path.getctime), gets the file _creation_ time in Windows, but only gets the file _modification_ time in Unix systems. The point of BetterMM was to not reupload music files just because of a small, insignificant tag change. Only looking at modification time will reupload music after these tag changes and voids this distinction from Music Manager. There is a Mac workaround which I plan on implementing (testing is another story).

## Status

- April 11, 2017: Mac and Linux currently unsupported. Album art will not upload, a [known issue](https://github.com/simon-weber/gmusicapi/issues/242) in the gmusicapi library.

---

\* says me