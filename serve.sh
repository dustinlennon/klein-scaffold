#!/usr/bin/bash

while true; do
    pipenv run python3 -m scaffold.builder --config config.yaml
	if [ $? -ne 1 ]; then
		break
	fi
done
