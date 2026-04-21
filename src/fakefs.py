import hashlib
import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Optional

USERNAMES_POOL = [
    'admin', 'deploy', 'jenkins', 'dave', 'alice', 'bob',
    'ubuntu', 'devops', 'ops', 'webadmin', 'mike',
]

BASH_HISTORY_SNIPPETS = [
    'sudo apt update && sudo apt upgrade -y',
    'docker ps',
    'docker logs -f app',
    'git pull origin main',
    'systemctl restart nginx',
    'tail -f /var/log/syslog',
    'htop',
    'vim .env',
    'ssh deploy@prod-01',
    'scp backup.tgz backup-host:/mnt/backups/',
    'ps aux | grep python',
    'netstat -tulpn',
    'find / -name "*.conf" 2>/dev/null',
    'kubectl get pods -A',
    'aws s3 ls',
    'psql -U postgres -d app',
]


@dataclass
class Node:
    kind: str  # 'file' or 'dir'
    content: str = ''
    children: Dict[str, 'Node'] = field(default_factory=dict)
    mode: str = '-rw-r--r--'
    owner: str = 'root'
    group: str = 'root'
    size: int = 0
    mtime: float = field(default_factory=time.time)


def _file(content: str, mode: str = '-rw-r--r--', owner: str = 'root', group: str = 'root', mtime: Optional[float] = None) -> Node:
    return Node(
        kind='file',
        content=content,
        mode=mode,
        owner=owner,
        group=group,
        size=len(content),
        mtime=mtime if mtime is not None else time.time(),
    )


def _dir(mode: str = 'drwxr-xr-x', owner: str = 'root', group: str = 'root', mtime: Optional[float] = None) -> Node:
    return Node(
        kind='dir',
        mode=mode,
        owner=owner,
        group=group,
        size=4096,
        mtime=mtime if mtime is not None else time.time(),
    )


def _fake_shadow_hash(rng: random.Random, username: str) -> str:
    salt = ''.join(rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=8))
    hash_bytes = hashlib.sha512(f"{username}:{salt}:{rng.random()}".encode()).hexdigest()
    return f"$6${salt}${hash_bytes[:86]}"


def _fake_rsa_key(rng: random.Random) -> str:
    body = '\n'.join(
        ''.join(rng.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/', k=64))
        for _ in range(24)
    )
    return f"-----BEGIN RSA PRIVATE KEY-----\n{body}\n-----END RSA PRIVATE KEY-----\n"


def _bash_history(rng: random.Random) -> str:
    n = rng.randint(8, 20)
    return '\n'.join(rng.sample(BASH_HISTORY_SNIPPETS, min(n, len(BASH_HISTORY_SNIPPETS)))) + '\n'


class FakeFileSystem:
    """Procedurally generated fake Linux filesystem. A seed produces a stable
    tree for a given session; different seeds produce different users,
    credentials, and histories. Writes persist in-memory for the session."""

    def __init__(self, seed: Optional[str] = None, hostname: str = 'srv'):
        self.rng = random.Random(seed)
        self.hostname = hostname
        self.now = time.time()
        self.users = self._pick_users()
        self.default_user = self.users[0]
        self.root = self._build_tree()
        self.cwd: List[str] = ['', 'home', self.default_user]

    def _pick_users(self) -> List[str]:
        count = self.rng.randint(2, 4)
        return self.rng.sample(USERNAMES_POOL, count)

    def _build_tree(self) -> Node:
        now = self.now
        root = _dir(mtime=now)

        # Standard top-level layout
        for name in ('bin', 'boot', 'dev', 'lib', 'lib64', 'media', 'mnt', 'opt', 'sbin', 'srv'):
            root.children[name] = _dir(mtime=now - self.rng.uniform(86400, 86400 * 180))

        root.children['etc'] = self._build_etc()
        root.children['home'] = self._build_home()
        root.children['root'] = self._build_root_home()
        root.children['proc'] = self._build_proc()
        root.children['tmp'] = _dir(mode='drwxrwxrwt', mtime=now)
        root.children['var'] = self._build_var()
        root.children['usr'] = self._build_usr()
        return root

    def _build_etc(self) -> Node:
        now = self.now
        etc = _dir(mtime=now - 86400 * 30)
        passwd_lines = ['root:x:0:0:root:/root:/bin/bash']
        shadow_lines = [f"root:{_fake_shadow_hash(self.rng, 'root')}:19000:0:99999:7:::"]
        for i, user in enumerate(self.users):
            uid = 1000 + i
            passwd_lines.append(f"{user}:x:{uid}:{uid}:{user}:/home/{user}:/bin/bash")
            shadow_lines.append(f"{user}:{_fake_shadow_hash(self.rng, user)}:19000:0:99999:7:::")
        passwd_lines += [
            'daemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin',
            'sshd:x:110:65534::/run/sshd:/usr/sbin/nologin',
            'www-data:x:33:33:www-data:/var/www:/usr/sbin/nologin',
        ]

        etc.children['passwd'] = _file('\n'.join(passwd_lines) + '\n', mode='-rw-r--r--')
        etc.children['shadow'] = _file('\n'.join(shadow_lines) + '\n', mode='-rw-------', owner='root', group='shadow')
        etc.children['hostname'] = _file(self.hostname + '\n')
        etc.children['hosts'] = _file(
            f"127.0.0.1 localhost\n127.0.1.1 {self.hostname}\n"
            "10.0.0.1 gateway\n10.0.0.15 db-primary\n10.0.0.22 redis-cache\n"
        )
        etc.children['os-release'] = _file(
            'NAME="Ubuntu"\nVERSION="20.04.6 LTS (Focal Fossa)"\nID=ubuntu\n'
            'ID_LIKE=debian\nPRETTY_NAME="Ubuntu 20.04.6 LTS"\nVERSION_ID="20.04"\n'
        )
        etc.children['resolv.conf'] = _file('nameserver 8.8.8.8\nnameserver 1.1.1.1\n')
        etc.children['crontab'] = _file(
            '# /etc/crontab\nSHELL=/bin/sh\nPATH=/usr/local/sbin:/usr/local/bin:/sbin:/bin:/usr/sbin:/usr/bin\n'
            '17 * * * * root cd / && run-parts --report /etc/cron.hourly\n'
        )
        ssh_dir = _dir(mtime=now - 86400 * 60)
        ssh_dir.children['sshd_config'] = _file(
            '# Generated sshd_config\nPort 22\nPermitRootLogin no\nPasswordAuthentication yes\n'
        )
        etc.children['ssh'] = ssh_dir
        return etc

    def _build_home(self) -> Node:
        home = _dir(mtime=self.now)
        for user in self.users:
            home.children[user] = self._build_user_home(user)
        return home

    def _build_user_home(self, user: str) -> Node:
        now = self.now
        u = _dir(owner=user, group=user, mtime=now - self.rng.uniform(3600, 86400 * 7))
        u.children['documents'] = _dir(owner=user, group=user)
        u.children['downloads'] = _dir(owner=user, group=user)
        u.children['projects'] = _dir(owner=user, group=user)
        u.children['.bashrc'] = _file(
            "# ~/.bashrc\nexport PS1='\\u@\\h:\\w\\$ '\nalias ll='ls -la'\nalias ..='cd ..'\n",
            owner=user, group=user,
        )
        u.children['.profile'] = _file(
            "# ~/.profile\nif [ -f ~/.bashrc ]; then . ~/.bashrc; fi\n",
            owner=user, group=user,
        )
        u.children['.bash_history'] = _file(_bash_history(self.rng), mode='-rw-------', owner=user, group=user)

        ssh = _dir(mode='drwx------', owner=user, group=user)
        ssh.children['authorized_keys'] = _file(
            f"ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQ{''.join(self.rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))} {user}@workstation\n",
            mode='-rw-------', owner=user, group=user,
        )
        ssh.children['id_rsa'] = _file(_fake_rsa_key(self.rng), mode='-rw-------', owner=user, group=user)
        ssh.children['known_hosts'] = _file(
            'github.com ssh-rsa AAAAB3NzaC1yc2EAAAABIwAAAQEA...\n',
            owner=user, group=user,
        )
        u.children['.ssh'] = ssh

        if self.rng.random() < 0.5:
            u.children['.env'] = _file(
                f"DB_PASSWORD={''.join(self.rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=20))}\n"
                f"API_KEY=sk-{''.join(self.rng.choices('abcdefghijklmnopqrstuvwxyz0123456789', k=32))}\n",
                mode='-rw-------', owner=user, group=user,
            )
        return u

    def _build_root_home(self) -> Node:
        r = _dir(mode='drwx------')
        r.children['.bash_history'] = _file(
            'apt update\napt upgrade -y\nsystemctl restart sshd\nexit\n',
            mode='-rw-------',
        )
        return r

    def _build_proc(self) -> Node:
        p = _dir()
        p.children['cpuinfo'] = _file(
            'processor\t: 0\nvendor_id\t: GenuineIntel\nmodel name\t: Intel(R) Xeon(R) CPU E5-2670\n'
            'cpu MHz\t\t: 2600.000\ncache size\t: 20480 KB\n'
        )
        p.children['meminfo'] = _file(
            'MemTotal:        2048000 kB\nMemFree:         1024000 kB\nMemAvailable:    1536000 kB\nBuffers:          128000 kB\n'
        )
        p.children['version'] = _file('Linux version 5.4.0-150-generic (buildd@lcy02-amd64-080)\n')
        p.children['uptime'] = _file(f"{self.rng.uniform(100000, 900000):.2f} {self.rng.uniform(100000, 900000):.2f}\n")
        return p

    def _build_var(self) -> Node:
        v = _dir()
        log = _dir()
        log.children['auth.log'] = _file(
            f"Jan 15 10:30:22 {self.hostname} sshd[1234]: Accepted password for "
            f"{self.default_user} from 192.168.1.{self.rng.randint(2, 254)} port 54321 ssh2\n"
        )
        log.children['syslog'] = _file(
            f"Jan 15 10:30:22 {self.hostname} kernel: [   0.000000] Linux version 5.4.0-150-generic\n"
        )
        log.children['dpkg.log'] = _file('2024-01-15 09:11:22 startup packages configure\n')
        v.children['log'] = log
        v.children['www'] = _dir()
        v.children['lib'] = _dir()
        v.children['spool'] = _dir()
        return v

    def _build_usr(self) -> Node:
        u = _dir()
        u.children['bin'] = _dir()
        u.children['lib'] = _dir()
        u.children['local'] = _dir()
        u.children['share'] = _dir()
        return u

    # --- Path utilities ---

    def _resolve(self, path: str) -> Optional[List[str]]:
        if path.startswith('/'):
            parts: List[str] = ['']
            rest = path[1:]
        else:
            parts = list(self.cwd)
            rest = path
        for seg in rest.split('/'):
            if seg in ('', '.'):
                continue
            if seg == '..':
                if len(parts) > 1:
                    parts.pop()
                continue
            if seg == '~':
                parts = ['', 'home', self.default_user]
                continue
            parts.append(seg)
        return parts

    def _lookup(self, parts: List[str]) -> Optional[Node]:
        node = self.root
        for seg in parts[1:]:
            if node.kind != 'dir':
                return None
            node = node.children.get(seg)
            if node is None:
                return None
        return node

    def _join(self, parts: List[str]) -> str:
        if len(parts) == 1:
            return '/'
        return '/' + '/'.join(parts[1:])

    # --- Public API ---

    def pwd(self) -> str:
        return self._join(self.cwd)

    def cd(self, target: str) -> str:
        if not target or target == '~':
            self.cwd = ['', 'home', self.default_user]
            return ''
        parts = self._resolve(target)
        node = self._lookup(parts)
        if node is None:
            return f"bash: cd: {target}: No such file or directory\n"
        if node.kind != 'dir':
            return f"bash: cd: {target}: Not a directory\n"
        self.cwd = parts
        return ''

    def list(self, target: Optional[str] = None, show_all: bool = False, long: bool = False) -> str:
        parts = self._resolve(target) if target else list(self.cwd)
        node = self._lookup(parts)
        if node is None:
            return f"ls: cannot access '{target}': No such file or directory\n"
        if node.kind == 'file':
            name = parts[-1] if len(parts) > 1 else '/'
            return self._format_entry(name, node, long) + '\n'
        entries = sorted(node.children.items())
        if not show_all:
            entries = [(n, x) for n, x in entries if not n.startswith('.')]
        if long:
            lines = [self._format_entry(name, child, long=True) for name, child in entries]
            total = sum(child.size for _, child in entries) // 1024 + 4
            return f"total {total}\n" + '\n'.join(lines) + ('\n' if lines else '')
        return '  '.join(name for name, _ in entries) + '\n'

    def _format_entry(self, name: str, node: Node, long: bool) -> str:
        if not long:
            return name
        from datetime import datetime
        ts = datetime.fromtimestamp(node.mtime).strftime('%b %d %H:%M')
        links = 2 if node.kind == 'dir' else 1
        return f"{node.mode} {links} {node.owner:<8} {node.group:<8} {node.size:>7} {ts} {name}"

    def read(self, target: str) -> str:
        parts = self._resolve(target)
        node = self._lookup(parts)
        if node is None:
            return f"cat: {target}: No such file or directory\n"
        if node.kind == 'dir':
            return f"cat: {target}: Is a directory\n"
        return node.content

    def exists(self, target: str) -> bool:
        return self._lookup(self._resolve(target)) is not None

    def write(self, target: str, content: str, owner: Optional[str] = None) -> str:
        parts = self._resolve(target)
        if len(parts) < 2:
            return f"cannot write {target}\n"
        parent = self._lookup(parts[:-1])
        if parent is None or parent.kind != 'dir':
            return f"no such directory: {'/'.join(parts[:-1]) or '/'}\n"
        parent.children[parts[-1]] = _file(content, owner=owner or self.default_user, group=owner or self.default_user)
        return ''

    def touch(self, target: str, owner: Optional[str] = None) -> str:
        if self.exists(target):
            parts = self._resolve(target)
            node = self._lookup(parts)
            if node:
                node.mtime = time.time()
            return ''
        return self.write(target, '', owner=owner)
