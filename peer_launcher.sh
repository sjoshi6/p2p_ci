echo -n "Enter pseudo name : peer1/peer2/peer3 only > "
read pseudo_name

echo -n "Enter my public IP Address > "
read my_ip_address

echo -n "Enter server IP Address > "
read server_ip_address

python3 peer_server.py $pseudo_name $my_ip_address $server_ip_address &
python3 peer.py $pseudo_name $my_ip_address $server_ip_address
