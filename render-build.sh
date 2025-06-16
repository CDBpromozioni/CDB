#!/usr/bin/env bash

# Installa dipendenze Python
pip install -r requirements.txt

# Installa i browser di Playwright
playwright install --with-deps
