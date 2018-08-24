## UnixStreamServer(Unix domain socket) Solution

### 1. Put logging program to right location

/opt/daemon/service/secu_unix_stream_logging.py

### 2. Define the systemd service unit

~/.config/systemd/user/secu_logging.service
```
[Unit]
Description=secu_logging service

[Service]
Type=simple
Restart=on-failure
RestartSec=3
TimeoutStopSec=20
ExecStart=/usr/bin/python3 /opt/daemon/service/secu_unix_stream_logging.py

[Install]
WantedBy=multi-user.target
```
* auto start when system start-up, replace [Install] section by following
    * **WantedBy=default.target**

### 3. Start Logging Service
```
systemctl --user daemon-reload
systemctl --user start secu_logging.service
```

if you want to make your service auto start-up when system boot
```
systemctl --user enable secu_logging.service
```

### 4. Check status
```
systemctl --user status secu_logging.service
```

### 5. Stop service
```
systemctl --user stop secu_logging.service
```

## TCP Server Solution

### 1. Put logging program to right location
/opt/daemon/service/secu_logging.py

### 2. Define the systemd service unit

~/.config/systemd/user/secu_logging.service
```
[Unit]
Description=secu_logging service
After=network.target secu_logging.socket
Requires=secu_logging.socket

[Service]
Type=simple
Restart=on-failure
RestartSec=3
TimeoutStopSec=20
ExecStart=/usr/bin/python3 /opt/daemon/service/secu_logging.py

[Install]
WantedBy=multi-user.target
```

* auto start when system start-up, replace [Install] section by following
    * **WantedBy=default.target**

### 3. Define the systemd socket unit

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

### 4. Check status
```
systemctl --user status secu_logging.socket
```

### 5. Stop service
```
systemctl --user stop secu_logging.socket
```

### 6. Start Listening Socket
```
systemctl --user daemon-reload
systemctl --user start secu_logging.socket
```

if you want to make your service auto start-up when system boot
```
systemctl --user enable secu_logging.service
```

## Check service received messages

### journalctl
```
journalctl -f --user-unit secu_logging.service
```


## Reference

* [systemd/User@archlinux](https://wiki.archlinux.org/index.php/Systemd/User)
* [README-python-service-on-systemd-activated-socket@GitHubGist](https://gist.github.com/kylemanna/d193aaa6b33a89f649524ad27ce47c4b)