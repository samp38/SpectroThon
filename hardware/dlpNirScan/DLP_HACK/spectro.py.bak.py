#!/usr/bin/env python

import os

def run(lines):
	with open('/tmp/spectro.sh', 'w') as temporaryFile:
		temporaryFile.write('\n'.join(lines))
	
	os.system('/usr/bin/expect -c \'expect "" {spawn ssh root@192.168.0.10 \'bash -s\' < /tmp/spectro.sh;expect "*?assword:*"; send -- "\r"; expect eof}\'')

run(['pwd', 'ls']);
