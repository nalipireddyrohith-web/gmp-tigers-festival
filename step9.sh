#!/bin/bash

echo "===== EVENTS.HTML INFO ====="
wc -l templates/events.html

echo ""
echo "===== FIRST 40 LINES ====="
head -40 templates/events.html

echo ""
echo "===== LAST 20 LINES ====="
tail -20 templates/events.html

echo ""
echo "Saving full file..."

cp templates/events.html events_before_redesign.txt

echo "✅ Done"
