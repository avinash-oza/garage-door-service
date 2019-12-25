from .pi_funcs import setup_pins, cleanup_pins


def post_fork(server, worker):
    setup_pins()


def on_exit(server):
    cleanup_pins()
