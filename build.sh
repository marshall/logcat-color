#!/bin/sh

bundle exec jekyll build

if [[ ! -h ~/.pow/`basename $PWD` ]]; then
    PROJECT_PATH=$PWD
    cd ~/.pow
    ln -s "$PROJECT_PATH"
fi
