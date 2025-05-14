# tasks/conf_example.py

from airflow.decorators import task

@task
def print_env(**kwargs):
    conf = kwargs['dag_run'].conf if 'dag_run' in kwargs else {}
    env = conf.get('env', 'default-env')  # dùng .get để tránh lỗi nếu không có
    print(f"ENV = {env}")
    return env
