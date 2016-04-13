echo -n "Enter pseudo name : peer1/peer2/peer3 only > "
read pseudo_name
python peer_server.py $pseudo_name &
python peer.py $pseudo_name
