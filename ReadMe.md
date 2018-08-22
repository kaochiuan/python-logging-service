
### Define the systemd service unit

~/.config/systemd/user/secu_logging.service
```
[Unit]
Description=secu_logging service
After=network.target secu_logging.socket
Requires=secu_logging.socket

[Service]
Type=simple
ExecStart=/usr/bin/python3 /opt/daemon/service/secu_logging.py
TimeoutStopSec=20


[Install]
WantedBy=multi-user.target
```

### Define the systemd socket unit

~/.config/systemd/user/secu_logging.socket
```
[Unit]
Description=Logging Socket
PartOf=secu_logging.service

[Socket]
ListenStream=127.0.0.1:9020

[Install]
WantedBy=sockets.target
```


### Start Listening Socket
```
systemctl --user daemon-reload
systemctl --user start secu_logging.socket
```

### Check status
```
systemctl --user status secu_logging.socket
```

### Stop service
```
systemctl --user stop secu_logging.socket
```

### Check received content by journalctl
```
journalctl -f --user-unit secu_logging.service
```