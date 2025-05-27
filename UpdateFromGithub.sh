#!/bin/bash
#move this file to ../
git clone https://github.com/MetinSAYGIN/BlackForge.git

cd BlackForge
chmod -x BlackForge.py
chmod -x Compare.py
chmod -x Clean.py
git pull
chmod +x BlackForge.py
chmod +x Compare.py
chmod +x Clean.py
./BlackForge.py
