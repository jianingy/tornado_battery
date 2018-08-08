# -*- coding: utf-8 -*-
# The route helpers were originally written by
# Jeremy Kelley (http://github.com/nod).

# modified by jianing.yang (http://github.com/jianingy)

import tornado.web


class RouteFactory:
    _route_classes = dict()

    @classmethod
    def create(cls, route_name: str):
        route_cls = type(f'Route{route_name.capitalize()}',
                         (RouteManager,),
                         {'route_name': route_name})
        cls._route_classes[route_name] = route_cls
        return cls._route_classes[route_name]

    @classmethod
    def get_routes(cls, route_name: str):
        route_cls = cls._route_classes.get(route_name, None)
        if route_cls is None:
            return []
        return route_cls.get_routes()


class RouteManager(object):

    _routes = []

    def __init__(self, uri: str, name: str=None, redirect: str=None):
        self._uri = uri
        self._redirect = redirect
        self.name = name

    def __call__(self, _handler):
        """gets called when we class decorate"""
        name = self.name or _handler.__name__
        if self._redirect is not None:
            _handler = tornado.web.RedirectHandler
            self._routes.append(tornado.web.url(self._uri, _handler,
                                                dict(url=self._redirect),
                                                name=name))
        elif issubclass(_handler, tornado.web.StaticFileHandler):
            settings = {
                'path': _handler.path,
                'default_filename': _handler.default_filename,
            }
            self._routes.append(tornado.web.url(self._uri, _handler,
                                                name=name, kwargs=settings))
        else:
            self._routes.append(tornado.web.url(self._uri, _handler,
                                                name=name))
        return _handler

    @classmethod
    def get_routes(cls):
        return cls._routes


route = RouteFactory.create('default')
