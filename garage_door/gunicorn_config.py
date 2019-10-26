from .pi_funcs import setup_pins

def post_fork(server, worker):
    setup_pins()
