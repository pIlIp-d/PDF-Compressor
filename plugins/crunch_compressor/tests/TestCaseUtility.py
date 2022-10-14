import subprocess


def run_subprocess_and_get_output(args: list) -> tuple[int, str, str]:
    p = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    return p.returncode, str(output), str(err)
