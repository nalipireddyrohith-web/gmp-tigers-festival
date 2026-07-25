#!/bin/bash

echo "Backing up events.html..."

cp templates/events.html templates/events_backup.html

echo "✅ Backup created:"
ls -l templates/events_backup.html
