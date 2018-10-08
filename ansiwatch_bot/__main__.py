#! /usr/bin/env python
if __name__ == '__main__':
    from .app import main
    main()
else:
    from .wsgi import application
