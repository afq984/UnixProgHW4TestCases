## Python Dependencies

* lxml
* requests
* pytest

## Installation

1. Place the instructor-provided `docroot.tbz` in this directory.
2. Run `sh install.sh`. This command extracts the `testroot/` directory and add a few files required for testing.

## Test

1. Start the webserver and point the root directory to `testroot/`.
2. Run `pytest --base-url=http://localhost:3000` (replace 3000 with the actual port the server is binded to).
