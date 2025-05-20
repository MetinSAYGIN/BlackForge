#!/bin/bash
#move this file to ../

chmod -x BlackForge/BlackForge.py
chmod -x BlackForge/Compare.py
git pull
chmod +x BlackForge/BlackForge.py
chmod +x BlackForge/Compare.py
./BlackForge/BlackForge.py
