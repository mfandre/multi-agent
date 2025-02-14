# Start

> python -m venv .venv 
>
> pip install -r requirements.txt 


# pygraphviz - MACOS ONLY

python3 -m pip install \
                --config-settings="--global-option=build_ext" \
                --config-settings="--global-option=-I$(brew --prefix graphviz)/include/" \
                --config-settings="--global-option=-L$(brew --prefix graphviz)/lib/" \
                pygraphviz