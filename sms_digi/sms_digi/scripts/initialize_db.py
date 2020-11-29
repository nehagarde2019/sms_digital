import argparse
import sys

from pyramid.paster import bootstrap, setup_logging
from sqlalchemy.exc import OperationalError

from .. import models


def setup_models(dbsession):

    dbsession.execute(
        # user data
        """
        INSERT INTO public.user( email, password) VALUES ('neha.r.garde@gmail.com', 'Pass@123');
        """

        # chemical data
        """
        INSERT INTO public.chemical(name) VALUES ('C');
        INSERT INTO public.chemical(name) VALUES ('N');
        INSERT INTO public.chemical(name) VALUES ('O');
        INSERT INTO public.chemical(name) VALUES ('AI');
        """

        # commodity data
        """
        INSERT INTO public.commodity(name, inventory, price, chemical_composition) 
        VALUES ('Plate & Structural', 200, 20.5,'[ {"id": 1, "percentage": 25} ,
                                                    {"id": 2, "percentage": 25},
                                                    {"unknown": 50}]' );

        INSERT INTO public.commodity(name, inventory, price, chemical_composition) 
        VALUES ('Plates', 2000, 20.5,'[ {"id": 1, "percentage": 25} ,
                                                    {"id": 2, "percentage": 25},
                                                    {"unknown": 50}]' );

        """)


def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'config_uri',
        help='Configuration file, e.g., development.ini',
    )
    return parser.parse_args(argv[1:])


def main(argv=sys.argv):
    args = parse_args(argv)
    setup_logging(args.config_uri)
    env = bootstrap(args.config_uri)

    try:
        with env['request'].tm:
            dbsession = env['request'].dbsession
            setup_models(dbsession)
    except OperationalError:
        print('''
Pyramid is having a problem using your SQL database.  The problem
might be caused by one of the following things:

1.  You may need to initialize your database tables with `alembic`.
    Check your README.txt for description and try to run it.

2.  Your database server may not be running.  Check that the
    database server referred to by the "sqlalchemy.url" setting in
    your "development.ini" file is running.
            ''')
