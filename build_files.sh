#!/bin/bash

# Just copy the pre-collected static files to the Vercel output directory
mkdir -p staticfiles_build
cp -r static/* staticfiles_build/
