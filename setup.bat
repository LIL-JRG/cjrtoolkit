@echo off

echo Installing requirements, please wait
pip install -r requirements.txt > nul
python -m spacy download es_core_news_sm > nul
echo Done. Open start.bat to run the program

pause