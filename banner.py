import random
from datetime import datetime

def generate_banner(username="user"):
  
    banners = [
        f"""
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-91-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

  System information as of {datetime.now().strftime('%a %b %d %H:%M:%S UTC %Y')}

  System load:  0.08              Processes:             123
  Usage of /:   45.2% of 9.78GB   Users logged in:       0
  Memory usage: 23%               IPv4 address for eth0: 192.168.1.100
  Swap usage:   0%

 * Super-optimized for small spaces - read how we shrank the memory
   footprint of MicroK8s to make it the smallest full K8s around.

   https://ubuntu.com/blog/microk8s-memory-optimisation

12 updates can be applied immediately.
To see these additional updates run: apt list --upgradable

Last login: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')} from 192.168.1.50
{username}@webserver:~$ """,

        f"""
Linux webserver 5.4.0-91-generic #102-Ubuntu SMP Fri Nov 5 16:31:28 UTC 2021 x86_64

The programs included with the Ubuntu system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Ubuntu comes with ABSOLUTELY NO WARRANTY, to the extent permitted by
applicable law.

{username}@webserver:~$ """,

        f"""
Welcome to Ubuntu 20.04.3 LTS (GNU/Linux 5.4.0-91-generic x86_64)

 * Documentation:  https://help.ubuntu.com
 * Management:     https://landscape.canonical.com
 * Support:        https://ubuntu.com/advantage

New release '22.04.1 LTS' available.
Run 'do-release-upgrade' to upgrade to it.

Last login: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')} from 10.0.0.1
{username}@database-server:~$ """,

        f"""
CentOS Linux release 7.9.2009 (Core)
Kernel 3.10.0-1160.el7.x86_64 on an x86_64

{username}@prod-server:~$ """,

        f"""
Welcome to Debian GNU/Linux 10 (buster)!

The programs included with the Debian GNU/Linux system are free software;
the exact distribution terms for each program are described in the
individual files in /usr/share/doc/*/copyright.

Debian GNU/Linux comes with ABSOLUTELY NO WARRANTY, to the extent
permitted by applicable law.
Last login: {datetime.now().strftime('%a %b %d %H:%M:%S %Y')} from 172.16.1.10
{username}@mail-server:~$ """
    ]
    
    return random.choice(banners)

def generate_motd():
    """Generate realistic message of the day"""
    motds = [
        """
===============================================================================
                            CORPORATE NETWORK ACCESS
===============================================================================
WARNING: This system is for authorized users only. All activities are logged
and monitored. Unauthorized access is strictly prohibited and will be 
prosecuted to the full extent of the law.

By continuing, you acknowledge that you have read and agree to comply with
the company's IT security policies and acceptable use guidelines.

For technical support, contact: it-support@company.com
===============================================================================
        """,
        """
===============================================================================
                              PRODUCTION SERVER
===============================================================================
NOTICE: This is a production environment. All changes must be approved through
the change management process. Emergency contacts:

- Network Operations: +1-555-0123
- Database Team: +1-555-0124  
- Security Team: +1-555-0125

Scheduled maintenance window: Sundays 02:00-06:00 EST
===============================================================================
        """,
        """
===============================================================================
                               WEB SERVER CLUSTER
===============================================================================
Server: web-prod-03.company.com
Environment: Production
Load Balancer: Active
Database Connection: Established
Cache Status: Operational

Monitoring Dashboard: https://monitor.company.com
Documentation: https://wiki.company.com/webserver
===============================================================================
        """
    ]
    
    return random.choice(motds)