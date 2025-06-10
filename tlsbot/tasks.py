from celery import shared_task
import subprocess
import sys
import os
import fcntl


@shared_task
def run_tls_bot():
    try:
        python_path = sys.executable  
        subprocess.run([python_path, "manage.py", "run_tlsbot"], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Bot xətası: {e}")


# @shared_task
# def run_tls_bot():
#     python_path = sys.executable
#     project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
#     try:
#         subprocess.run([python_path, "manage.py", "run_tlsbot"], cwd=project_dir, check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Bot xətası: {e}")


# @shared_task(bind=True, ignore_result=True)
# def run_tls_bot(self):
#     lock_file = '/tmp/tlsbot.lock'
#     with open(lock_file, 'w') as f:
#         try:
#             fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
#             python_path = sys.executable
#             subprocess.run([python_path, "manage.py", "run_tlsbot"], check=True)
#         except BlockingIOError:
#             print("⚠️ Bot artıq çalışır, bu çağırış atlanır.")


