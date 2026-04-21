import asyncio
import random
import shlex
from dataclasses import dataclass
from datetime import datetime
from typing import Callable, Dict, List, Optional

from .fakefs import FakeFileSystem


@dataclass
class CommandContext:
    fs: FakeFileSystem
    hostname: str
    username: str
    session_info: Dict
    rng: random.Random


Handler = Callable[[List[str], CommandContext], str]

INSULTS = [
    "Nice try, script kiddie — you'll need more than that.",
    "Is that the best you've got? My cat writes better exploits.",
    "Your persistence is admirable. Your technique is not.",
    "Logging every keystroke. Say hi to the SOC team.",
    "You're being studied. Feel free to entertain us further.",
]


def _parse(line: str) -> List[str]:
    try:
        return shlex.split(line)
    except ValueError:
        return line.split()


class CommandProcessor:
    """Dispatches shell commands against a fake filesystem and applies the RL
    agent's chosen action (ALLOW / DELAY / FAKE / INSULT / BLOCK)."""

    def __init__(self, fs: FakeFileSystem, hostname: str, username: str, rng: Optional[random.Random] = None):
        self.fs = fs
        self.hostname = hostname
        self.username = username
        self.rng = rng or random.Random()
        self.handlers: Dict[str, Handler] = {
            'ls': self._ls,
            'dir': self._ls,
            'pwd': lambda _a, _c: _c.fs.pwd() + '\n',
            'whoami': lambda _a, c: f"{c.username}\n",
            'hostname': lambda _a, c: f"{c.hostname}\n",
            'id': lambda _a, c: f"uid=1000({c.username}) gid=1000({c.username}) groups=1000({c.username}),27(sudo)\n",
            'cat': self._cat,
            'head': self._head,
            'tail': self._tail,
            'less': self._cat,
            'more': self._cat,
            'cd': self._cd,
            'echo': self._echo,
            'uname': self._uname,
            'ps': self._ps,
            'top': self._top,
            'netstat': self._netstat,
            'ss': self._netstat,
            'ifconfig': self._ifconfig,
            'ip': self._ip,
            'who': self._who,
            'w': self._who,
            'last': self._last,
            'history': self._history,
            'uptime': self._uptime,
            'df': self._df,
            'du': self._du,
            'free': self._free,
            'wget': self._download,
            'curl': self._download,
            'env': self._env,
            'export': lambda _a, _c: '',
            'clear': lambda _a, _c: '',
            'exit': lambda _a, _c: '__EXIT__',
            'logout': lambda _a, _c: '__EXIT__',
            'sudo': self._sudo,
            'touch': self._touch,
            'mkdir': self._mkdir,
            'rm': self._rm,
            'chmod': lambda _a, _c: '',
            'chown': lambda _a, _c: '',
            'find': self._find,
            'grep': self._grep,
            'which': self._which,
            'true': lambda _a, _c: '',
            'false': lambda _a, _c: '',
            ':': lambda _a, _c: '',
        }

    def context(self, session_info: Dict) -> CommandContext:
        return CommandContext(
            fs=self.fs,
            hostname=self.hostname,
            username=self.username,
            session_info=session_info,
            rng=self.rng,
        )

    async def execute(self, command: str, action: str, session_info: Dict) -> str:
        ctx = self.context(session_info)
        if action == 'DELAY':
            await asyncio.sleep(self.rng.uniform(1.5, 3.5))
            return self._run(command, ctx)
        if action == 'FAKE':
            return self._fake(command, ctx)
        if action == 'INSULT':
            return self._insult(ctx) + self._run(command, ctx)
        if action == 'BLOCK':
            return (
                f"\n[SECURITY NOTICE] Your IP ({session_info.get('client_ip', 'unknown')}) "
                "has been reported. Session terminated.\n"
            )
        return self._run(command, ctx)

    def _run(self, command: str, ctx: CommandContext) -> str:
        parts = _parse(command)
        if not parts:
            return ''
        cmd = parts[0]
        args = parts[1:]
        handler = self.handlers.get(cmd)
        if handler is None:
            if '/' in cmd or cmd.startswith('./'):
                return f"bash: {cmd}: No such file or directory\n"
            return f"{cmd}: command not found\n"
        return handler(args, ctx)

    def _fake(self, command: str, ctx: CommandContext) -> str:
        parts = _parse(command)
        if not parts:
            return ''
        cmd = parts[0]
        if cmd in ('wget', 'curl'):
            return self._download(parts[1:], ctx)
        if cmd in ('bash', 'sh', 'zsh') and '-c' in parts:
            return ''  # silent "success"
        if cmd in ('python', 'python3', 'perl', 'ruby') and '-c' in parts:
            return ''
        if cmd == 'nc' or cmd == 'netcat':
            return f"listening on [any] {ctx.rng.randint(1024, 65535)} ...\n"
        if cmd == 'chmod':
            return ''
        if cmd == 'cat' and len(parts) > 1:
            return self._cat(parts[1:], ctx)
        return self._run(command, ctx)

    def _insult(self, ctx: CommandContext) -> str:
        line = ctx.rng.choice(INSULTS)
        return f"# {line}\n"

    # --- Individual command implementations ---

    def _ls(self, args: List[str], ctx: CommandContext) -> str:
        show_all = any('a' in a for a in args if a.startswith('-'))
        long = any('l' in a for a in args if a.startswith('-'))
        targets = [a for a in args if not a.startswith('-')]
        if not targets:
            return ctx.fs.list(show_all=show_all, long=long)
        out = []
        for t in targets:
            if len(targets) > 1:
                out.append(f"{t}:")
            out.append(ctx.fs.list(t, show_all=show_all, long=long).rstrip('\n'))
        return '\n'.join(out) + '\n'

    def _cat(self, args: List[str], ctx: CommandContext) -> str:
        if not args:
            return ''
        return ''.join(ctx.fs.read(a) for a in args)

    def _head(self, args: List[str], ctx: CommandContext) -> str:
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] in ('-n', '--lines') and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
                continue
            files.append(args[i])
            i += 1
        if not files:
            return ''
        out = []
        for f in files:
            content = ctx.fs.read(f)
            out.append(''.join(content.splitlines(keepends=True)[:n]))
        return ''.join(out)

    def _tail(self, args: List[str], ctx: CommandContext) -> str:
        n = 10
        files = []
        i = 0
        while i < len(args):
            if args[i] in ('-n', '--lines') and i + 1 < len(args):
                try:
                    n = int(args[i + 1])
                except ValueError:
                    pass
                i += 2
                continue
            if args[i] == '-f':
                i += 1
                continue
            files.append(args[i])
            i += 1
        if not files:
            return ''
        out = []
        for f in files:
            lines = ctx.fs.read(f).splitlines(keepends=True)
            out.append(''.join(lines[-n:]))
        return ''.join(out)

    def _cd(self, args: List[str], ctx: CommandContext) -> str:
        return ctx.fs.cd(args[0] if args else '')

    def _echo(self, args: List[str], _ctx: CommandContext) -> str:
        return ' '.join(args) + '\n'

    def _uname(self, args: List[str], ctx: CommandContext) -> str:
        if any('a' in a for a in args if a.startswith('-')):
            return f"Linux {ctx.hostname} 5.4.0-150-generic #167-Ubuntu SMP x86_64 GNU/Linux\n"
        if any('r' in a for a in args if a.startswith('-')):
            return "5.4.0-150-generic\n"
        if any('n' in a for a in args if a.startswith('-')):
            return f"{ctx.hostname}\n"
        return "Linux\n"

    def _ps(self, args: List[str], ctx: CommandContext) -> str:
        if any('aux' in a or 'ef' in a for a in args):
            header = "USER       PID %CPU %MEM    VSZ   RSS TTY      STAT START   TIME COMMAND\n"
            rows = [
                "root         1  0.0  0.1 225484  9876 ?        Ss   Jan15   0:01 /sbin/init",
                "root       123  0.0  0.0      0     0 ?        I<   Jan15   0:00 [kthreadd]",
                f"{ctx.username:<10} {ctx.rng.randint(800, 2000):>4}  0.1  0.3  12345  6789 pts/0    Ss   10:30   0:00 -bash",
                "www-data   789  0.2  1.5 113456 15876 ?        S    Jan15   2:34 nginx: worker process",
                "mysql     1011  0.5  4.2 987654 43210 ?        Ssl  Jan15  15:22 /usr/sbin/mysqld",
                "redis      512  0.1  0.8  56789  8192 ?        Ssl  Jan15   0:42 /usr/bin/redis-server",
            ]
            return header + '\n'.join(rows) + '\n'
        return "  PID TTY          TIME CMD\n  123 pts/0    00:00:00 bash\n  456 pts/0    00:00:00 ps\n"

    def _top(self, _args: List[str], ctx: CommandContext) -> str:
        now = datetime.now().strftime('%H:%M:%S')
        return (
            f"top - {now} up 12 days,  3:14,  1 user,  load average: 0.15, 0.10, 0.05\n"
            "Tasks: 156 total,   1 running, 155 sleeping,   0 stopped\n"
            "%Cpu(s):  2.3 us,  1.2 sy,  0.0 ni, 96.5 id\n"
            "MiB Mem :   2000.0 total,   1024.0 free,    488.0 used,    488.0 buff/cache\n"
            "    PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n"
            "      1 root      20   0  225484   9876   6543 S   0.0   0.5   0:01.23 systemd\n"
            f"    {ctx.rng.randint(800, 2000):>4} {ctx.username:<8} 20   0   12345   6789   3210 S   0.0   0.3   0:00.45 bash\n"
        )

    def _netstat(self, _args: List[str], ctx: CommandContext) -> str:
        rip = f"192.168.1.{ctx.rng.randint(2, 254)}"
        return (
            "Active Internet connections (w/o servers)\n"
            "Proto Recv-Q Send-Q Local Address           Foreign Address         State\n"
            f"tcp        0      0 10.0.0.15:22            {rip}:54321        ESTABLISHED\n"
            "tcp        0      0 10.0.0.15:80            10.0.0.1:45678          TIME_WAIT\n"
            "tcp        0      0 127.0.0.1:3306          0.0.0.0:*               LISTEN\n"
        )

    def _ifconfig(self, _args: List[str], ctx: CommandContext) -> str:
        return (
            "eth0: flags=4163<UP,BROADCAST,RUNNING,MULTICAST>  mtu 1500\n"
            f"        inet 10.0.0.{ctx.rng.randint(10, 200)}  netmask 255.255.255.0  broadcast 10.0.0.255\n"
            "        ether 02:42:0a:00:00:0f  txqueuelen 1000  (Ethernet)\n"
            "lo: flags=73<UP,LOOPBACK,RUNNING>  mtu 65536\n"
            "        inet 127.0.0.1  netmask 255.0.0.0\n"
        )

    def _ip(self, args: List[str], ctx: CommandContext) -> str:
        if args and args[0] in ('a', 'addr', 'address'):
            return self._ifconfig([], ctx)
        if args and args[0] in ('r', 'route'):
            return "default via 10.0.0.1 dev eth0\n10.0.0.0/24 dev eth0 proto kernel scope link\n"
        return "Usage: ip [ OPTIONS ] OBJECT { COMMAND | help }\n"

    def _who(self, _args: List[str], ctx: CommandContext) -> str:
        now = datetime.now().strftime('%Y-%m-%d %H:%M')
        return f"{ctx.username:<8} pts/0        {now} ({ctx.session_info.get('client_ip','unknown')})\n"

    def _last(self, _args: List[str], ctx: CommandContext) -> str:
        return (
            f"{ctx.username}    pts/0    {ctx.session_info.get('client_ip','unknown')}   "
            f"{datetime.now().strftime('%a %b %d %H:%M')}   still logged in\n"
            f"root      tty1                         {datetime.now().strftime('%a %b %d')}  08:12 - 08:45 (00:33)\n"
        )

    def _history(self, _args: List[str], ctx: CommandContext) -> str:
        content = ctx.fs.read(f"/home/{ctx.username}/.bash_history")
        if content.startswith('cat:'):
            return ''
        return '\n'.join(f"  {i+1}  {line}" for i, line in enumerate(content.splitlines())) + '\n'

    def _uptime(self, _args: List[str], _ctx: CommandContext) -> str:
        now = datetime.now().strftime('%H:%M:%S')
        return f" {now} up 12 days,  3:14,  1 user,  load average: 0.15, 0.10, 0.05\n"

    def _df(self, _args: List[str], _ctx: CommandContext) -> str:
        return (
            "Filesystem     1K-blocks    Used Available Use% Mounted on\n"
            "/dev/sda1       41943040 8388608  33554432  20% /\n"
            "tmpfs            1024000       0   1024000   0% /dev/shm\n"
            "/dev/sdb1      104857600 52428800  52428800  50% /data\n"
        )

    def _du(self, args: List[str], _ctx: CommandContext) -> str:
        target = args[-1] if args and not args[-1].startswith('-') else '.'
        return f"4.0K\t{target}\n"

    def _free(self, _args: List[str], _ctx: CommandContext) -> str:
        return (
            "              total        used        free      shared  buff/cache   available\n"
            "Mem:        2048000      512000     1024000       32000      512000     1536000\n"
            "Swap:       1024000           0     1024000\n"
        )

    def _download(self, args: List[str], ctx: CommandContext) -> str:
        url = next((a for a in args if a.startswith('http')), None)
        if not url:
            return "usage: wget URL\n"
        host = url.split('/')[2] if '//' in url else 'host'
        filename = url.rsplit('/', 1)[-1] or 'index.html'
        ip = f"93.184.{ctx.rng.randint(0, 255)}.{ctx.rng.randint(0, 255)}"
        size = ctx.rng.randint(512, 8192)
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        return (
            f"--{now}--  {url}\n"
            f"Resolving {host}... {ip}\n"
            f"Connecting to {host}|{ip}|:80... connected.\n"
            "HTTP request sent, awaiting response... 200 OK\n"
            f"Length: {size} [application/octet-stream]\n"
            f"Saving to: '{filename}'\n\n"
            f"{filename} 100%[===================>] {size:>6}  --.-KB/s    in 0s\n\n"
            f"{now} ({ctx.rng.uniform(1, 8):.1f} MB/s) - '{filename}' saved [{size}/{size}]\n"
        )

    def _env(self, _args: List[str], ctx: CommandContext) -> str:
        return (
            f"USER={ctx.username}\nHOME=/home/{ctx.username}\nSHELL=/bin/bash\n"
            f"PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin\n"
            f"LANG=en_US.UTF-8\nTERM=xterm-256color\nHOSTNAME={ctx.hostname}\n"
        )

    def _sudo(self, args: List[str], ctx: CommandContext) -> str:
        if not args:
            return "usage: sudo COMMAND\n"
        return f"[sudo] password for {ctx.username}: \nSorry, try again.\nsudo: 1 incorrect password attempt\n"

    def _touch(self, args: List[str], ctx: CommandContext) -> str:
        for a in args:
            if a.startswith('-'):
                continue
            msg = ctx.fs.touch(a, owner=ctx.username)
            if msg:
                return msg
        return ''

    def _mkdir(self, args: List[str], _ctx: CommandContext) -> str:
        return ''  # pretend success

    def _rm(self, args: List[str], _ctx: CommandContext) -> str:
        return ''  # pretend success; never actually delete anything

    def _find(self, args: List[str], ctx: CommandContext) -> str:
        start = args[0] if args and not args[0].startswith('-') else '.'
        name = None
        for i, a in enumerate(args):
            if a == '-name' and i + 1 < len(args):
                name = args[i + 1].strip('"\'')
        return self._walk(start, name, ctx)

    def _walk(self, start: str, name_pattern: Optional[str], ctx: CommandContext) -> str:
        import fnmatch
        parts = ctx.fs._resolve(start)
        node = ctx.fs._lookup(parts)
        if node is None:
            return f"find: '{start}': No such file or directory\n"
        out: List[str] = []
        stack = [(parts, node)]
        while stack:
            p, n = stack.pop()
            path = ctx.fs._join(p)
            if name_pattern is None or fnmatch.fnmatch(p[-1] if len(p) > 1 else '/', name_pattern):
                out.append(path)
            if n.kind == 'dir':
                for cname, cnode in n.children.items():
                    stack.append((p + [cname], cnode))
            if len(out) > 500:
                break
        return '\n'.join(out) + '\n'

    def _grep(self, args: List[str], ctx: CommandContext) -> str:
        files = [a for a in args if not a.startswith('-')]
        if len(files) < 2:
            return ''
        pattern = files[0]
        out = []
        for f in files[1:]:
            content = ctx.fs.read(f)
            if content.startswith('cat:') or content.startswith('grep:'):
                continue
            for line in content.splitlines():
                if pattern in line:
                    out.append(f"{f}:{line}" if len(files) > 2 else line)
        return '\n'.join(out) + ('\n' if out else '')

    def _which(self, args: List[str], _ctx: CommandContext) -> str:
        if not args:
            return ''
        return f"/usr/bin/{args[0]}\n"
