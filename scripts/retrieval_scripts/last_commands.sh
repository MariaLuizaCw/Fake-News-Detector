## Retrive Google
python ./scripts/retrieval_scripts/retrieval_google.py --start_id 0 --end_id 1
python ./scripts/retrieval_scripts/retrieval_google.py --start_id 2 --end_id 10
python ./scripts/retrieval_scripts/retrieval_google.py --start_id 1 --end_id 2
nohup python ./scripts/retrieval_scripts/retrieval_google.py --start_id 10 --end_id 2000 > logs/retrieval_google.log 2>&1 &


## Retrieve DDGO
python scripts/retrieval_ddgo.py --start_id 0 --end_id 10
nohup python scripts/retrieval_ddgo.py --start_id 10 --end_id 2000 > logs/retrieval_ddgo.log 2>&1 &
nohup python scripts/retrieval_ddgo.py --start_id 0 --end_id 2000 > logs/retrieval_ddgo_2.log 2>&1 &
nohup python scripts/retrieval_ddgo.py --start_id 2000 --end_id 5000 > logs/retrieval_ddgo_2000_5000.log 2>&1 &
nohup python scripts/retrieval_ddgo.py --start_id 2000 --end_id 5000 > logs/retrieval_ddgo_2000_5000_2.log 2>&1 &