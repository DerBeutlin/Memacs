# -*- coding: utf-8 -*-
# Time-stamp: <2018-08-25 14:16:04 vk>

import unittest
import os
import datetime as dt
from memacs.railway import Railway, DBTicketParser


class TestFoo(unittest.TestCase):
    def setUp(self):
        pass

    def test_all(self):

        path = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(path, 'data/dbtickets')
        argv = "-f {} -C DB".format(path)
        memacs = Railway(argv=argv.split())
        data = memacs.test_get_entries()

        self.assertEqual(
            data[0],
            "** <2012-10-27 Sat 05:53>-<2012-10-27 Sat 10:05> [[{}/old.pdf][Train ride from KÀln Hbf to Schwaikheim]]".format(path)
        )
        self.assertEqual(data[1], "   :PROPERTIES:")
        self.assertEqual(data[2], "   :ORIGIN:      KÀln Hbf")
        self.assertEqual(data[3], "   :DESTINATION: Schwaikheim")
        self.assertEqual(data[4], "   :DEPARTURE:   <2012-10-27 Sat 05:53>")
        self.assertEqual(data[5], "   :ARRIVAL:     <2012-10-27 Sat 10:05>")
        self.assertEqual(
            data[6],
            "   :ID:          c26903013ed1d4ac68b997b876cde0431960a7fe")
        self.assertEqual(data[7], "   :END:")
        self.assertEqual(
            data[8],
            "** <2018-09-17 Mon 18:00>-<2018-09-17 Mon 19:21> [[{}/HinRueckfahrt.pdf][Train ride from Mannheim Hbf to Schwaikheim]]".format(path)
        )
        self.assertEqual(data[9], "   :PROPERTIES:")
        self.assertEqual(data[10], "   :ORIGIN:      Mannheim Hbf")
        self.assertEqual(data[11], "   :DESTINATION: Schwaikheim")
        self.assertEqual(data[12], "   :DEPARTURE:   <2018-09-17 Mon 18:00>")
        self.assertEqual(data[13], "   :ARRIVAL:     <2018-09-17 Mon 19:21>")
        self.assertEqual(
            data[14],
            "   :ID:          7f1ca158357035c01b2fa46358822767a68aa343")
        self.assertEqual(data[15], "   :END:")
        self.assertEqual(
            data[16],
            "** <2018-09-19 Wed 20:53>-<2018-09-19 Wed 22:29> [[{}/HinRueckfahrt.pdf][Train ride from Schwaikheim to Mannheim Hbf]]".format(path)
        )
        self.assertEqual(data[17], "   :PROPERTIES:")
        self.assertEqual(data[18], "   :ORIGIN:      Schwaikheim")
        self.assertEqual(data[19], "   :DESTINATION: Mannheim Hbf")
        self.assertEqual(data[20], "   :DEPARTURE:   <2018-09-19 Wed 20:53>")
        self.assertEqual(data[21], "   :ARRIVAL:     <2018-09-19 Wed 22:29>")
        self.assertEqual(
            data[22],
            "   :ID:          071b6ed3d83b5026b9b0e51bb4c48c021a9dfbeb")
        self.assertEqual(data[23], "   :END:")
        self.assertEqual(
            data[24],
            "** <2018-06-24 Sun 15:53>-<2018-06-24 Sun 17:18> [[{}/Hinfahrt.pdf][Train ride from Schwaikheim to Heidelberg Hbf]]".format(path)
        )
        self.assertEqual(data[25], "   :PROPERTIES:")
        self.assertEqual(data[26], "   :ORIGIN:      Schwaikheim")
        self.assertEqual(data[27], "   :DESTINATION: Heidelberg Hbf")
        self.assertEqual(data[28], "   :DEPARTURE:   <2018-06-24 Sun 15:53>")
        self.assertEqual(data[29], "   :ARRIVAL:     <2018-06-24 Sun 17:18>")
        self.assertEqual(
            data[30],
            "   :ID:          45155ca4119e43a71adc39a34c435904b7e81349")
        self.assertEqual(data[31], "   :END:")

    def tearDown(self):
        pass


class TestDBTicketParser:
    class TestOnlyOneDirectionTicket(unittest.TestCase):
        def setUp(self):
            parser = DBTicketParser()
            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, 'data/dbtickets', 'Hinfahrt.pdf')
            self.ticket = parser.parse_tickets(path)

        def test_there_are_the_same_number_of_stops_as_stop_times(self):
            assert len(self.ticket[0].stops) == len(self.ticket[0].stop_times)

        def test_stops(self):
            assert self.ticket[0].stops == [
                'Schwaikheim', 'Stuttgart Hbf (tief)', 'Stuttgart Hbf',
                'Heidelberg Hbf'
            ]

        def test_stop_times(self):
            assert self.ticket[0].stop_times[0] == dt.datetime(
                year=2018, month=6, day=24, hour=15, minute=53)
            assert self.ticket[0].stop_times[1] == dt.datetime(
                year=2018, month=6, day=24, hour=16, minute=15)
            assert self.ticket[0].stop_times[2] == dt.datetime(
                year=2018, month=6, day=24, hour=16, minute=36)
            assert self.ticket[0].stop_times[3] == dt.datetime(
                year=2018, month=6, day=24, hour=17, minute=18)

    class TestBothDirectionTicket(unittest.TestCase):
        def setUp(self):
            parser = DBTicketParser()
            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, 'data/dbtickets', 'HinRueckfahrt.pdf')
            self.tickets = parser.parse_tickets(path)

        def test_there_are_two_tickets(self):
            assert len(self.tickets) == 2

        def test_there_are_the_same_number_of_stops_as_stop_times(self):
            for t in self.tickets:
                assert len(t.stops) == len(t.stop_times)

        def test_stops(self):
            assert self.tickets[0].stops == [
                'Mannheim Hbf', 'Stuttgart Hbf', 'Stuttgart Hbf (tief)',
                'Schwaikheim'
            ]
            assert self.tickets[1].stops == [
                'Schwaikheim', 'Stuttgart Hbf (tief)', 'Stuttgart Hbf',
                'Mannheim Hbf'
            ]

        def test_stop_times(self):
            assert self.tickets[0].stop_times[0] == dt.datetime(
                year=2018, month=9, day=17, hour=18, minute=00)
            assert self.tickets[0].stop_times[1] == dt.datetime(
                year=2018, month=9, day=17, hour=18, minute=46)
            assert self.tickets[0].stop_times[2] == dt.datetime(
                year=2018, month=9, day=17, hour=19, minute=00)
            assert self.tickets[0].stop_times[3] == dt.datetime(
                year=2018, month=9, day=17, hour=19, minute=21)
            assert self.tickets[1].stop_times[0] == dt.datetime(
                year=2018, month=9, day=19, hour=20, minute=53)
            assert self.tickets[1].stop_times[1] == dt.datetime(
                year=2018, month=9, day=19, hour=21, minute=15)
            assert self.tickets[1].stop_times[2] == dt.datetime(
                year=2018, month=9, day=19, hour=21, minute=51)
            assert self.tickets[1].stop_times[3] == dt.datetime(
                year=2018, month=9, day=19, hour=22, minute=29)

    class TestOldTicket(unittest.TestCase):
        def setUp(self):
            parser = DBTicketParser()
            path = os.path.dirname(os.path.abspath(__file__))
            path = os.path.join(path, 'data/dbtickets', 'old.pdf')
            self.tickets = parser.parse_tickets(path)

        def test_stops(self):
            assert self.tickets[0].stops == [
                'KÀln Hbf', 'Mainz Hbf', 'Mainz Hbf', 'Stuttgart Hbf',
                'Stuttgart Hbf (tief)', 'Schwaikheim'
            ]

        def test_stop_times(self):
            assert self.tickets[0].stop_times[0] == dt.datetime(
                year=2012, month=10, day=27, hour=5, minute=53)
            assert self.tickets[0].stop_times[1] == dt.datetime(
                year=2012, month=10, day=27, hour=7, minute=38)
            assert self.tickets[0].stop_times[2] == dt.datetime(
                year=2012, month=10, day=27, hour=7, minute=46)
            assert self.tickets[0].stop_times[3] == dt.datetime(
                year=2012, month=10, day=27, hour=9, minute=24)
            assert self.tickets[0].stop_times[4] == dt.datetime(
                year=2012, month=10, day=27, hour=9, minute=45)
            assert self.tickets[0].stop_times[5] == dt.datetime(
                year=2012, month=10, day=27, hour=10, minute=5)
