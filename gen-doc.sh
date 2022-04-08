#!/bin/zsh

./project.py run \
  -m pdoc \
  -d google \
  --logo "https://avatars.githubusercontent.com/u/100195108?s=70&v=4" \
  --logo-link "https://github.com/dev4py" \
  --favicon "https://www.python.org/static/favicon.ico" \
  --no-search \
  -o docs \
  dev4py.utils
