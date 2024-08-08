#!/bin/bash

# Run Puppeteer script with Xvfb
xvfb-run -a --server-args="-screen 0 1920x1080x24" node crawler.js --replay 0

xvfb-run -a --server-args="-screen 0 1920x1080x24" node crawler.js --replay 1

pkill -f chrome
pkill -f xvfb
rm -rf /tmp/.*
