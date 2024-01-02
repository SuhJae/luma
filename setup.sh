docker-compose up -d

# When compleate, use db_restore.py to restore the database
cd tools || exit
python3 db_restore.py
