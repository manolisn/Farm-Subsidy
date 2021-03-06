# -*- coding: utf-8 -*-
"""


"""
import sys

from optparse import make_option

from django.template.defaultfilters import slugify
from django.core.management.base import BaseCommand
from django.db import connection, transaction

from data import countryCodes
from data.models import Location


class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--country', '-c', dest='country',
        help='ISO country name'),
    )
    help = 'Normalizeation scripts for the farm data'

    def make_slug(self, parent, name):
        """Given a Location instance (parent) and a name, make a new slug value"""
        path_list = [o.name for o in parent.get_ancestors()]
        path_list.append(name)
        slug = "/".join([slugify(n) for n in path_list])
        return slug

    def dict_fetchall(self, cursor):
        if not cursor.description:
            return {}
        description = [x[0] for x in cursor.description]
        rows = []
        for row in cursor.fetchall():
            rows.append(dict(zip(description, row)))
        return rows

    def geo1(self):
        geo1_sql = """
        SELECT TRIM(r.geo1) dgeo1, p.year as dyear, r.countrypayment as country, SUM(p.amounteuro) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN data_payment p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE p.year !=0
        AND r.countrypayment IN (%(country_in_sql)s)
        AND p.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, Dyear, country;
        """ % {'country_in_sql': self.country_in_sql}

        geo1_sql_all_years = """
        SELECT TRIM(r.geo1) dgeo1, 0 as Dyear, r.countrypayment as country, SUM(p.total) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN (
            SELECT globalrecipientidx, SUM(amounteuro) as total
            FROM data_payment
            WHERE countrypayment IN (%(country_in_sql)s)
            GROUP BY globalrecipientidx
            ) as p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE r.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, Dyear, country;
        """ % {'country_in_sql': self.country_in_sql}
        cursor = connection.cursor()

        cursor.execute(geo1_sql)
        transaction.commit_unless_managed()
        rows = self.dict_fetchall(cursor)
        cursor.execute(geo1_sql_all_years)
        transaction.commit_unless_managed()
        all_years = self.dict_fetchall(cursor)
        # for row in all_years:
        #     print row
        rows += all_years
        # import sys
        # sys.exit()

        for row in rows:
            if not row['total']:
                row['total'] = 0

            Location().add_root(geo_type='geo1',
                            name=row['dgeo1'].strip(),
                            country=row['country'],
                            slug=self.make_slug(Location(), row['dgeo1']),
                            total=row['total'],
                            recipients=row['count'],
                            average=row['total'] / float(row['count']),
                            lat=row['lat'],
                            lon=row['lng'],
                            year=row['dyear'],
                            )

    def geo2(self):
        """

        """

        geo2_sql = """
        SELECT TRIM(r.geo1) dgeo1, TRIM(r.geo2) dgeo2, p.year as dyear, r.countrypayment as country, SUM(p.amounteuro) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN data_payment p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE geo2 IS NOT NULL
        AND r.countrypayment IN (%(country_in_sql)s)
        AND p.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, dgeo2, dyear, country;
        """ % {'country_in_sql': self.country_in_sql}

        geo2_sql_all_years = """
        SELECT TRIM(r.geo1) dgeo1, TRIM(r.geo2) dgeo2, 0 as dyear, r.countrypayment as country, SUM(p.total) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN (
            SELECT globalrecipientidx, SUM(amounteuro) as total
            FROM data_payment
            WHERE countrypayment IN (%(country_in_sql)s)
            GROUP BY globalrecipientidx
            ) as p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE geo2 IS NOT NULL
        AND r.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, dgeo2, dyear, country;
        """ % {'country_in_sql': self.country_in_sql}
        cursor = connection.cursor()

        cursor.execute(geo2_sql)
        transaction.commit_unless_managed()
        rows = self.dict_fetchall(cursor)
        cursor.execute(geo2_sql_all_years)
        transaction.commit_unless_managed()
        rows += self.dict_fetchall(cursor)

        for row in rows:
            parent_slug = self.make_slug(Location(), row['dgeo1'])
            parent = Location.objects.get(
                name=row['dgeo1'].strip(),
                slug=parent_slug,
                year=row['dyear'],
                country=row['country'],
                geo_type='geo1')

            if not row['total']:
                row['total'] = 0

            child = parent.add_child(geo_type='geo2',
                            name=row['dgeo2'],
                            country=row['country'],
                            total=row['total'],
                            recipients=row['count'],
                            average=row['total'] / float(row['count']),
                            lat=row['lat'],
                            lon=row['lng'],
                            year=row['dyear']
            )
            child.slug = self.make_slug(child, row['dgeo2'])
            child.save()

    def geo3(self):
        """

        """

        geo3_sql = """
        SELECT TRIM(r.geo1) dgeo1, TRIM(r.geo2) dgeo2, TRIM(r.geo3) dgeo3, p.year as dyear, r.countrypayment as country, SUM(p.amounteuro) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN data_payment p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE geo2 IS NOT NULL
        AND geo3 IS NOT NULL
        AND r.countrypayment IN (%(country_in_sql)s)
        AND p.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, dgeo2, dgeo3, dyear, country;
        """ % {'country_in_sql': self.country_in_sql}

        geo3_sql_all_years = """
        SELECT TRIM(r.geo1) dgeo1, TRIM(r.geo2) dgeo2, TRIM(r.geo3) dgeo3, 0 as dyear, r.countrypayment as country, SUM(p.amounteuro) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN data_payment p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE geo2 IS NOT NULL
        AND geo3 IS NOT NULL
        AND r.countrypayment IN (%(country_in_sql)s)
        AND p.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, dgeo2, dgeo3, dyear, country;
        """ % {'country_in_sql': self.country_in_sql}
        cursor = connection.cursor()

        cursor.execute(geo3_sql)
        transaction.commit_unless_managed()
        rows = self.dict_fetchall(cursor)
        cursor.execute(geo3_sql_all_years)
        transaction.commit_unless_managed()
        rows += self.dict_fetchall(cursor)

        for row in rows:
            grandparent_slug = self.make_slug(Location(), row['dgeo1'])
            grandparent = Location.objects.get(
                name=row['dgeo1'],
                year=row['dyear'],
                slug=grandparent_slug,
                country=row['country'],
                geo_type='geo1')

            parent_slug = self.make_slug(grandparent, row['dgeo2'])
            parent_slug = "/".join([grandparent_slug, parent_slug])

            parent = Location.objects.get(
                name=row['dgeo2'],
                year=row['dyear'],
                slug=parent_slug,
                country=row['country'],
                geo_type='geo2')

            if not row['total']:
                row['total'] = 0

            child = parent.add_child(geo_type='geo3',
                            name=row['dgeo3'],
                            country=row['country'],
                            total=row['total'],
                            recipients=row['count'],
                            average=row['total'] / float(row['count']),
                            lat=row['lat'],
                            lon=row['lng'],
                            year=row['dyear']
            )
            child.slug = self.make_slug(child, row['dgeo3'])
            child.save()

    def geo4(self):
        """

        """

        geo4_sql = """
        SELECT TRIM(r.geo1) dgeo1, TRIM(r.geo2) dgeo2, TRIM(r.geo3) dgeo3, TRIM(r.geo4) dgeo4, p.year as dyear, r.countrypayment as country, SUM(p.amounteuro) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN data_payment p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE geo2 IS NOT NULL
        AND geo3 IS NOT NULL
        AND geo4 IS NOT NULL
        AND r.countrypayment IN (%(country_in_sql)s)
        AND p.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, dgeo2, dgeo3, dgeo4, dyear, country;
        """ % {'country_in_sql': self.country_in_sql}

        geo4_sql_all_years = """
        SELECT TRIM(r.geo1) dgeo1, TRIM(r.geo2) dgeo2, TRIM(r.geo3) dgeo3, TRIM(r.geo4) dgeo4, 0 as dyear, r.countrypayment as country, SUM(p.amounteuro) as total, COUNT(r.globalrecipientidx) as count, AVG(r.lat) as lat, AVG(r.lng) as lng
        FROM data_recipient r
        JOIN data_payment p
        ON r.globalrecipientidx=p.globalrecipientidx
        WHERE geo2 IS NOT NULL
        AND geo3 IS NOT NULL
        AND geo4 IS NOT NULL
        AND r.countrypayment IN (%(country_in_sql)s)
        AND p.countrypayment IN (%(country_in_sql)s)
        GROUP BY dgeo1, dgeo2, dgeo3, dgeo4, dyear, country;
        """ % {'country_in_sql': self.country_in_sql}
        cursor = connection.cursor()

        cursor.execute(geo4_sql)
        rows = self.dict_fetchall(cursor)
        cursor.execute(geo4_sql_all_years)
        rows += self.dict_fetchall(cursor)

        for row in rows:
            great_grandparent_slug = self.make_slug(Location(), row['dgeo1'])
            great_grandparent = Location.objects.get(
                name=row['dgeo1'],
                year=row['dyear'],
                slug=great_grandparent_slug,
                country=row['country'],
                geo_type='geo1')

            grandparent_slug = self.make_slug(great_grandparent, row['dgeo2'])
            grandparent_slug = "/".join([great_grandparent_slug, grandparent_slug])

            Location.objects.get(
                name=row['dgeo2'],
                year=row['dyear'],
                slug=grandparent_slug,
                country=row['country'],
                geo_type='geo2')

            parent_slug = self.make_slug(Location(), row['dgeo3'])
            parent_slug = "/".join([grandparent_slug, parent_slug])

            parent = Location.objects.get(
                name=row['dgeo3'],
                year=row['dyear'],
                slug=parent_slug,
                country=row['country'],
                geo_type='geo3')

            if not row['total']:
                row['total'] = 0
            child = parent.add_child(geo_type='geo4',
                            name=row['dgeo4'],
                            country=row['country'],
                            total=row['total'],
                            recipients=row['count'],
                            average=row['total'] / float(row['count']),
                            lat=row['lat'],
                            lon=row['lng'],
                            year=row['dyear']
            )
            child.slug = self.make_slug(child, row['dgeo4'])
            child.save()

    def handle(self, **options):
        # stdout stuff is a hack to allow clean test output
        old_out = sys.stdout
        sys.stdout = options.get('stdout', sys.stdout)
        country = options.get('country')
        if country == "EU":
            self.country = countryCodes.country_codes()
        else:
            self.country = [country]

        self.country_in_sql = ",".join(["'%s'" % c for c in self.country])

        print "deleting all locations"
        Location.objects.filter(country__in=self.country).delete()

        print "Making geo1"
        self.geo1()
        print "Making geo2"
        self.geo2()
        print "Making geo3"
        self.geo3()
        print "Making geo4"
        self.geo4()
        transaction.commit_unless_managed()

        sys.stdout = old_out
