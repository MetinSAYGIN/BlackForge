#!/bin/bash
#move this file to ../
git clone https://github.com/MetinSAYGIN/BlackForge.git

cd BlackForge
chmod -x BlackForge.py
chmod -x /Compare.py
git pull
chmod +x BlackForge.py
chmod +x Compare.py
./BlackForge.py
