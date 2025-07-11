import os
import sys
import webbrowser
import threading
import time


def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8000")


def main():
    if getattr(sys, "frozen", False):
        application_path = os.path.dirname(sys.executable)
    else:
        application_path = os.path.dirname(os.path.abspath(file))

    os.chdir(application_path)
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "alarm_manager.settings")

    from django.core.wsgi import get_wsgi_application
    from wsgiref.simple_server import make_server

    application = get_wsgi_application()
    threading.Thread(target=open_browser).start()

    with make_server("127.0.0.1", 8000, application) as httpd:
        print("Сервер Django запущен на http://127.0.0.1:8000")
        httpd.serve_forever()


if __name__ == "__main__":
    main()
