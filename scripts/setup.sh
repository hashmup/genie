#!/bin/sh
setupIfNecessary() {
    if [ ! -d "~/.pyenv" ]; then
        git clone https://github.com/pyenv/pyenv.git ~/.pyenv
        echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bash_profile
        echo 'export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bash_profile
        echo -e 'if command -v pyenv 1>/dev/null 2>&1; then\n  eval "$(pyenv init -)"\nfi' >> ~/.bash_profile
        exec "$SHELL"
        pyenv install anaconda3-4.3.0
        pyenv local anaconda3-4.3.0
        pyenv rehash
    fi

    # install required libraries
    pip install textx
    pip install pandas
    pip install jinja2
}
setupIfNecessary
