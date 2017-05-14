import subprocess


def runshell(cmds):
    if not isinstance(cmds, list):
        cmds = [cmds]
    for cmd in cmds:
        subprocess.run(cmd, shell=True)
