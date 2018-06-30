from fabric.api import run
from fabric.context_managers import settings

def _get_manage_dot_py(host):
    return f'~/sites/{host}/virtualenv/bin/python ~/sites/{host}/source/manage.py'

def reset_database(host):
    manage_dot_py = _get_manage_dot_py(host)
    # Here is the context manager that sets the host string, in the form user@serveraddress
    # (I have hardcoded my server username, elspeth, so adjust it as necessary)
    with settings(host_string=f'elspeth@{host}'):
        run(f'{manage_dot_py} flush --noinput')

def create_session_on_server(host, email):
    manage_dot_py = _get_manage_doy_py(host)
    with settings(host_string=f'elspeth@{host}'):
        session_key = run(f'{manage_dot_py} create_session {email}')
        return session_key.strip()
