# RIPv1 Protocol
## What commands to type for init
  1. direnv allow
  2. bash start.sh
  
## API:
  1. Create router: python3 Router.py <name>
  2. Show table: python3 table.py <name>
  3. Add link: python3 add_link.py <name1> <name2>
  4. Delete link: python3 delete_link.py <name1> <name2>
  5. Send packet: python3 send_packet.py <Router_name_from> <Router_name_to> <Message without whitespaces>

## To stop
  1. Ctrl-c on all routers
  2. bash stop.sh
