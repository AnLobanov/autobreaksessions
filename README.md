# autobreaksessions
Resets suspended Cisco ASA VPN sessions that have no traffic and are not pinged. By default, the timeout is 5 minutes. This means that the problem will be solved within 5-10 minutes.
The script has auto and manual mode.
## Auto mode
The script resets all sessions that match the criteria.
Enabled at startup via confirmation or argument "auto"
```
python autobreaksessions.py auto
```
## Manual mode
The script will ask you if it is possible to reset the found session.
Enabled at startup via confirmation or argument "manual"
```
python autobreaksessions.py manual
```
