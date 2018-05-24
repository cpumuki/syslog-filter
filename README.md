# syslog-filter
Filter syslog messages sent over netcat

- On the syslog server
`$ cat * | nc 192.168.1.4 1234`

- On the desktop client
`$ nc -l 1234 | python syslog-filter.py`
